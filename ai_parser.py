import os
import json
import re
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model used for everything (analysis + price search).
# If you start getting 404 "model not found" errors, check
# https://ai.google.dev/gemini-api/docs/models for the current
# valid model name and update this constant.
MODEL_NAME = "gemini-3.6-flash"

GEMINI_BASE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
)

# How many times to retry a request that failed with 429 (rate limit /
# quota exceeded), and how long to wait between retries. Gemini's free
# tier has tight per-minute limits, so a couple of short retries often
# succeeds without the user having to click anything again.
MAX_429_RETRIES = 2
RETRY_BACKOFF_SECONDS = 3


# =========================================================
# SHARED HELPERS
# =========================================================

def extract_json(text):
    """
    Extract JSON from text safely.
    Handles Markdown code blocks, raw text, and text with
    citations/prose wrapped around a JSON block (common when
    Google Search grounding is enabled).
    """
    if not text:
        return None

    cleaned = re.sub(r'```json\s*', '', text)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Try to find a JSON object
    match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Try to find a JSON array (used by the price search response)
    match = re.search(r'(\[.*\])', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    return None


def slugify_template(name):
    """
    Turn an arbitrary AI-generated device name into a safe
    snake_case slug to use as a 'template' key, e.g.
    'Solar Panel Charge Controller' -> 'solar_panel_charge_controller'.
    Falls back to 'custom_circuit' if nothing usable is given.
    """
    if not name:
        return "custom_circuit"

    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return slug or "custom_circuit"


def _error_message(status_code, body_text):
    """Turn a Gemini HTTP error into a clear, actionable message."""
    try:
        detail = json.loads(body_text).get("error", {}).get("message", body_text)
    except Exception:
        detail = body_text

    if status_code == 429:
        return (
            "Gemini API rate limit / quota exceeded (429). "
            "You've used up your current quota for this key — this is "
            "not a bug, it's Google throttling requests. Wait a minute "
            "and try again, or check your plan & billing at "
            "https://aistudio.google.com/apikey. "
            f"Details: {detail}"
        )
    if status_code == 404:
        return (
            f"Gemini model '{MODEL_NAME}' not found (404). "
            "Check https://ai.google.dev/gemini-api/docs/models for a "
            "currently valid model name and update MODEL_NAME in "
            f"ai_parser.py. Details: {detail}"
        )
    if status_code in (401, 403):
        return (
            f"Gemini API authentication/permission error ({status_code}). "
            "Check that GEMINI_API_KEY in .env is correct, active, and "
            f"has access to this model. Details: {detail}"
        )
    return f"Gemini API error ({status_code}): {detail}"


def _call_gemini(payload):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is missing in .env")

    headers = {"Content-Type": "application/json"}
    url = f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}"

    attempt = 0
    while True:
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429 and attempt < MAX_429_RETRIES:
            attempt += 1
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
            continue

        raise RuntimeError(_error_message(response.status_code, response.text))


def _first_text_part(data):
    try:
        candidate = data["candidates"][0]
        parts = candidate["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
        finish_reason = candidate.get("finishReason", "")
        return text, finish_reason
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected response structure from Gemini API: {e}")


# =========================================================
# MAIN CIRCUIT ANALYSIS
# =========================================================

def _build_analysis_payload(prompt: str, strict: bool = False) -> dict:
    base_rules = (
        "- device_name: short human-readable name of the circuit/device\n"
        "- category: short category, e.g. 'Power Electronics', 'Automation'\n"
        "- template: a lowercase snake_case slug identifying this circuit, "
        "e.g. 'solar_charge_controller'. If the request closely matches a "
        "well-known circuit type, use its common name as the slug.\n"
        "- voltage: the supply voltage as a number (best estimate if not stated)\n"
        "- components: list of objects each with type, value, unit, purpose. "
        "Include every component needed for a working circuit — power "
        "source, sensors, actuators, protection/support parts (resistors, "
        "capacitors, transistors/driver ICs) — not just the parts the user "
        "named explicitly.\n"
        "- connections: list of short strings describing how components "
        "connect, in the order current/signal flows, e.g. "
        "'Battery positive -> Resistor R1 -> LED anode'. Cover every "
        "component listed above.\n"
        "- explanation: plain-English working principle\n"
        "- safety_notes: practical safety guidance for building/testing this circuit\n"
        "- calculations: list of short strings with any relevant formulas or "
        "estimated values (empty list if genuinely not applicable)\n"
    )

    if strict:
        # Used only as a retry after a parse failure/truncation. Keeps
        # the same schema but caps every field's length so the whole
        # JSON object comfortably fits the token budget and can't get
        # cut off mid-string again.
        length_rules = (
            "Keep this SHORT and complete — it's more important that the "
            "JSON is valid and finishes than that it's detailed: "
            "at most 6 items in components, at most 8 items in connections, "
            "explanation in 1-2 sentences, safety_notes in 1 sentence, "
            "at most 3 items in calculations.\n"
        )
    else:
        length_rules = (
            "explanation: 2-4 sentences. safety_notes: 1-3 sentences.\n"
        )

    system_instruction = (
        "You are an expert electronics design assistant embedded in an app "
        "called Text-to-Circuit AI Assistant. Users will describe ANY "
        "circuit, device, or electronic system in plain, casual, possibly "
        "vague or incomplete language — not just textbook circuits. Always "
        "produce your best-effort, complete, realistic design, even for "
        "unusual, hybrid, or under-specified requests. Never refuse, never "
        "ask a clarifying question, never return an empty design — make "
        "sensible, clearly-stated engineering assumptions instead.\n\n"
        "Respond with ONLY a single valid JSON object (no Markdown, no "
        "prose, no code fences) with EXACTLY these keys:\n"
        + base_rules + length_rules +
        "Never omit a key — use an empty list/string only if a field truly "
        "doesn't apply. Do not include any text outside the JSON object."
    )

    return {
        "contents": [
            {
                "parts": [
                    {"text": system_instruction},
                    {"text": f"User prompt: {prompt}"},
                ]
            }
        ],
        "generationConfig": {
            # Forces Gemini to emit raw JSON directly (no markdown fences,
            # no chatty preamble) so free-form prompts parse reliably
            # instead of silently failing extract_json() and falling
            # back to a bare "Custom Circuit" with no details.
            "responseMimeType": "application/json",
            "temperature": 0.4,
            # Generous headroom: a full circuit (device info + several
            # components + connections + explanation) in structured JSON
            # can run long. Too small a budget here caused responses to
            # get cut off mid-object, which produced INVALID JSON that
            # even the regex fallback in extract_json() couldn't recover —
            # and that failure was previously silent, showing up to the
            # user as an unexplained "no components identified".
            "maxOutputTokens": 4096 if not strict else 1500,
        },
    }


def analyze_with_ai(prompt: str) -> dict:
    """
    Sends the user's circuit/device request to Gemini and returns a
    fully-populated dict describing the circuit. Asks the model for
    EVERY field the UI needs (device_name, category, template,
    explanation, safety_notes) — not just components/voltage/
    connections — so requests that don't match one of the built-in
    example devices still come back with something the app can
    render, via the generic circuit renderer.

    If the model's response can't be parsed as valid JSON (most often
    because it was cut off before finishing), this retries ONCE with
    a stricter, shorter-output prompt. If that also fails, it returns
    the raw text plus a clear failure reason instead of silently
    discarding it — so a "no components identified" in the UI can
    actually be traced back to what happened.
    """
    for attempt, strict in enumerate([False, True]):

        payload = _build_analysis_payload(prompt, strict=strict)
        data = _call_gemini(payload)
        raw_text, finish_reason = _first_text_part(data)
        parsed_json = extract_json(raw_text)

        if parsed_json:
            parsed_json.setdefault("device_name", "Custom Circuit")
            parsed_json.setdefault("category", "AI-Generated")
            parsed_json.setdefault(
                "template", slugify_template(parsed_json.get("device_name"))
            )
            parsed_json.setdefault("components", [])
            parsed_json.setdefault("connections", [])
            parsed_json.setdefault("explanation", "No explanation available.")
            parsed_json.setdefault("safety_notes", "")
            parsed_json.setdefault("calculations", [])
            return parsed_json

        # Parsing failed on this attempt — if we haven't retried yet,
        # loop again with the stricter/shorter prompt.
        if attempt == 0:
            continue

        # Both attempts failed. Surface exactly what happened instead
        # of a bare, unexplained empty result.
        if finish_reason == "MAX_TOKENS":
            reason = (
                "Gemini's response was cut off before it finished "
                "(hit the output length limit), so it wasn't valid JSON."
            )
        else:
            reason = (
                f"Gemini's response (finishReason={finish_reason or 'unknown'}) "
                "wasn't valid JSON."
            )

        return {
            "parse_failed": True,
            "parse_failure_reason": reason,
            "raw_response": raw_text,
        }


# =========================================================
# LIVE COMPONENT PRICE / AVAILABILITY SEARCH
# =========================================================

def search_component_prices(components, region: str = "") -> dict:
    """
    Uses Gemini's built-in Google Search grounding tool to look up
    real-world approximate prices and where each component is
    available (online stores, distributors, local markets).

    This does NOT need a separate search API key — it reuses the
    same GEMINI_API_KEY, via Gemini's 'google_search' tool.

    Returns a dict: {"results": [...], "sources": [...]}
    On any failure it returns {"error": "<message>"} so the caller
    can show a graceful message instead of crashing the app.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is missing in .env"}

    if not components:
        return {"results": [], "sources": []}

    component_lines = []
    for c in components:
        name = c.get("type") or c.get("name") or c.get("id") or "component"
        value = c.get("value", "")
        unit = c.get("unit", "")
        component_lines.append(f"- {name} {value}{unit}".strip())

    region_hint = f" Prices should be relevant to: {region}." if region else (
        " If you cannot localize prices, give a general USD estimate and say so."
    )

    prompt = (
        "Search the web for current, real-world approximate prices and "
        "purchase availability for the following electronic components:\n"
        + "\n".join(component_lines)
        + "\n\n"
        + region_hint
        + " Respond with ONLY a valid JSON array (no prose, no code fences), "
        "one object per component, each with EXACTLY these keys: "
        "component, estimated_price (string, include currency), "
        "availability (string, e.g. store/distributor names or 'widely available'), "
        "notes (string, 1 short sentence, empty string if none)."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
    }

    try:
        data = _call_gemini(payload)
        raw_text, _finish_reason = _first_text_part(data)
    except Exception as e:
        return {"error": str(e)}

    parsed = extract_json(raw_text)

    # Pull grounding source links if Gemini returned them, so the UI
    # can show "where this pricing info came from".
    sources = []
    try:
        grounding = data["candidates"][0].get("groundingMetadata", {})
        for chunk in grounding.get("groundingChunks", []):
            web = chunk.get("web", {})
            if web.get("uri"):
                sources.append({"title": web.get("title", web["uri"]), "url": web["uri"]})
    except Exception:
        pass

    if isinstance(parsed, list):
        return {"results": parsed, "sources": sources}

    # Model didn't comply with the JSON-only instruction — still hand
    # back the raw text so the user sees *something* useful.
    return {"raw_response": raw_text, "sources": sources}
