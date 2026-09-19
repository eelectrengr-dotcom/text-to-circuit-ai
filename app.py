# app.py
# Text-to-Circuit AI Assistant
# Professional Streamlit dashboard

from datetime import datetime

import streamlit as st

from ai_parser import analyze_with_ai, search_component_prices, slugify_template, MODEL_NAME
from device_detector import find_device
from circuit_generator import generate_circuit
from calculator import calculate
from validator import validate_result, validate_template, safety_message


def render_html_table(headers, rows):
    """
    Builds an HTML <table> as a single unbroken line of text (no
    embedded newlines or leading indentation).

    Streamlit's st.markdown() runs its input through a Markdown
    parser even with unsafe_allow_html=True. When HTML is written as
    a multi-line, deeply-indented f-string (as this table used to
    be), a blank-line/indentation quirk in that parser can split the
    HTML into two blocks — the opening tags render fine as raw HTML,
    but a lone closing tag like "</tbody>" on its own line gets
    treated as ordinary text and shows up literally in the UI instead
    of closing the table. Keeping everything on one line sidesteps
    that entirely.

    headers: list[str]
    rows: list[list[tuple[str value, str|None css_class]]]
    """
    thead = "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"

    body_rows = []
    for row in rows:
        cells = "".join(
            f'<td class="{cls}">{value}</td>' if cls else f"<td>{value}</td>"
            for value, cls in row
        )
        body_rows.append(f"<tr>{cells}</tr>")

    return (
        '<table class="component-table">'
        f"<thead>{thead}</thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
    )


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Text-to-Circuit AI Assistant",
    page_icon="⚡",
    layout="wide",
)


# =========================================================
# PROFESSIONAL DARK UI
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #0b0f16;
        color: #e7ecf3;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #0a0e14;
        border-right: 1px solid #202938;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.6rem;
        padding-left: 1.3rem;
        padding-right: 1.3rem;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        margin-top: 0.4rem;
        margin-bottom: 0.6rem;
    }

    .sidebar-card {
        padding: 12px 14px;
        border-radius: 12px;
        border: 1px solid #202938;
        background: #10151f;
        margin-bottom: 4px;
    }

    .sidebar-label {
        color: #8491a3;
        text-transform: uppercase;
        letter-spacing: .6px;
        font-size: 10.5px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    section[data-testid="stSidebar"] button {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 12.5px !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: 9px !important;
        border: 1px solid #202938 !important;
        background: #111722 !important;
        color: #c7d1e0 !important;
    }

    section[data-testid="stSidebar"] button:hover {
        border-color: #4f8cff !important;
        color: #ffffff !important;
    }

    .sidebar-footnote {
        color: #6b7688;
        font-size: 11.5px;
        line-height: 1.55;
        padding: 4px 2px 0 2px;
    }

    /* ---------- HERO ---------- */

    .hero {
        padding: 30px 34px;
        border-radius: 20px;
        border: 1px solid #2a3a52;
        background:
            radial-gradient(circle at top right,
                rgba(79,140,255,.22),
                transparent 45%),
            radial-gradient(circle at bottom left,
                rgba(124,147,255,.10),
                transparent 40%),
            linear-gradient(135deg, #131b29, #0c111b);
        box-shadow: 0 8px 30px rgba(0,0,0,.35);
        margin-bottom: 22px;
    }

    .hero-title {
        font-size: 42px;
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -0.9px;
        margin: 0;
        background: linear-gradient(90deg, #ffffff 0%, #d7e6ff 45%, #8fb4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        color: #aab6c9;
        font-size: 16px;
        margin-top: 10px;
        margin-bottom: 0;
    }

    .status-row {
        display: flex;
        gap: 8px;
        margin-top: 18px;
        flex-wrap: wrap;
    }

    .status {
        padding: 6px 12px;
        border-radius: 999px;
        border: 1px solid #2f3d54;
        background: linear-gradient(180deg, #131c2b, #0e151f);
        color: #cfd9ea;
        font-size: 12px;
        font-weight: 500;
    }

    /* ---------- SECTION HEADERS ---------- */

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: #f2f5f8;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .section-caption {
        color: #8f9bab;
        font-size: 13px;
        margin-bottom: 12px;
    }

    /* ---------- INPUT CARD ---------- */

    .input-card {
        padding: 18px 20px 6px 20px;
        border-radius: 16px;
        border: 1px solid #263142;
        background: #111722;
        margin-bottom: 12px;
    }

    /* ---------- RESULT CARDS ---------- */

    .info-card {
        padding: 17px 18px;
        border-radius: 15px;
        border: 1px solid #263142;
        background: #111722;
        min-height: 105px;
    }

    .info-label {
        color: #8491a3;
        text-transform: uppercase;
        letter-spacing: .7px;
        font-size: 11px;
        font-weight: 700;
    }

    .info-value {
        color: #f2f5f8;
        font-size: 18px;
        font-weight: 700;
        margin-top: 8px;
    }

    .info-value.status-good {
        color: #34d399;
    }

    .info-value.status-info {
        color: #4f8cff;
    }

    .info-sub {
        color: #7c8aa0;
        font-size: 11.5px;
        margin-top: 4px;
    }

    /* ---------- COMPONENT TABLE ---------- */

    .component-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #263142;
    }

    .component-table th {
        background: #151c27;
        color: #8fa3c7;
        text-transform: uppercase;
        letter-spacing: .5px;
        font-size: 10.5px;
        font-weight: 700;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 1px solid #263142;
    }

    .component-table td {
        padding: 11px 14px;
        font-size: 13.5px;
        color: #d3dae4;
        border-bottom: 1px solid #1b2330;
        background: #111722;
    }

    .component-table tr:last-child td {
        border-bottom: none;
    }

    .component-table td.name-cell {
        font-weight: 700;
        color: #f2f5f8;
        white-space: nowrap;
    }

    .component-table td.value-cell {
        color: #4f8cff;
        font-weight: 600;
        white-space: nowrap;
    }

    /* ---------- CALCULATION ROWS ---------- */

    .component-card {
        padding: 13px 15px;
        margin-bottom: 9px;
        border-radius: 12px;
        border: 1px solid #263142;
        background: #151c27;
        color: #d3dae4;
        font-size: 13.5px;
    }

    /* ---------- EXPLANATION ---------- */

    .text-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #263142;
        background: #111722;
        line-height: 1.7;
        color: #d3dae4;
    }

    .principle-preview {
        padding: 16px 18px;
        border-radius: 14px;
        border: 1px solid #263142;
        background: linear-gradient(135deg, #121a28, #0f151f);
        color: #c7d1e0;
        font-size: 13.5px;
        line-height: 1.6;
        margin-top: 14px;
    }

    .principle-preview .principle-label {
        color: #8fa3c7;
        text-transform: uppercase;
        letter-spacing: .6px;
        font-size: 10.5px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    /* ---------- DIAGRAM ---------- */

    .diagram-card {
        padding: 6px;
        border-radius: 16px;
        border: 1px solid #263142;
        background: #0d1117;
        overflow: hidden;
    }

    /* ---------- CONNECTION ---------- */

    .connection {
        padding: 10px 13px;
        border-left: 3px solid #4f8cff;
        background: #131a25;
        border-radius: 0 9px 9px 0;
        margin-bottom: 7px;
        color: #cbd5e1;
        font-size: 13px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #687588;
        font-size: 12px;
        padding: 15px 0 5px;
    }

    /* ---------- BUTTONS ---------- */

    div.stButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 700;
    }

    /* ---------- TABS ---------- */

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 9px 9px 0 0;
        padding: 10px 16px;
        height: auto;
    }

    .stTabs [data-baseweb="tab"] p {
        font-size: 17px !important;
        font-weight: 650 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">⚡ Text-to-Circuit AI Assistant</div>
        <div class="hero-subtitle">
            AI-powered electronics design, circuit visualization,
            component identification and engineering learning platform.
        </div>
        <div class="status-row">
            <span class="status">🤖 Gemini AI</span>
            <span class="status">📐 Circuit Visualization</span>
            <span class="status">🧮 Engineering Calculations</span>
            <span class="status">🔌 Component Analysis</span>
            <span class="status">💰 Live Price Search</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_TEXT = "Create a 5V circuit with a 220 ohm resistor and LED in series."

if "circuit_request" not in st.session_state:
    st.session_state.circuit_request = DEFAULT_TEXT


# =========================================================
# SETTINGS (inline — no sidebar)
# =========================================================

if "auto_fetch_prices" not in st.session_state:
    # Off by default: auto-fetch makes a SECOND Gemini call per
    # analysis, which burns a limited/free API quota twice as fast.
    st.session_state.auto_fetch_prices = False

if "price_region" not in st.session_state:
    st.session_state.price_region = ""

with st.expander("⚙️ Settings & About", expanded=False):

    settings_col, about_col = st.columns(2)

    with settings_col:
        st.markdown("**💰 Price Search**")
        st.checkbox(
            "Auto-fetch prices after each analysis",
            key="auto_fetch_prices",
            help=(
                "This makes a SECOND Gemini API call per analysis, on "
                "top of the one used to read your prompt — so it uses "
                "your quota twice as fast. If you're on a limited/free "
                "key and want more prompts to work before hitting a "
                "rate limit, leave this off and fetch prices manually "
                "from the Prices & Availability tab instead."
            ),
        )
        st.text_input(
            "Region / country (optional)",
            key="price_region",
            placeholder="e.g. India, USA, UK",
            help="Improves price relevance. Leave blank for a general USD estimate.",
        )

    with about_col:
        st.markdown("**🧩 How this works**")
        st.markdown(
            f"""
            <div class="sidebar-card">
                <div style="margin-bottom:6px;">🤖 <b>AI Engine</b> &nbsp;—&nbsp; Google Gemini ({MODEL_NAME}), an LLM</div>
                <div style="margin-bottom:6px;">🔎 <b>Price Search</b> &nbsp;—&nbsp; Gemini + Google Search grounding</div>
                <div style="margin-bottom:6px;">📐 <b>Diagram Engine</b> &nbsp;—&nbsp; Python</div>
                <div>🖥️ <b>Interface</b> &nbsp;—&nbsp; Streamlit</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# INPUT
# =========================================================

st.markdown(
    '<div class="section-title">Describe your circuit or electronic system</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-caption">'
    "Use natural language. You can describe a circuit, device or practical system."
    "</div>",
    unsafe_allow_html=True,
)

with st.container(border=True):

    user_text = st.text_area(
        "Circuit / Device Request",
        height=105,
        label_visibility="collapsed",
        key="circuit_request",
        placeholder=(
            "Example: Design a fire detection system with "
            "a smoke sensor, buzzer and warning LED."
        ),
    )

    analyze_button = st.button(
        "⚡  Analyze & Generate",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# REPORT BUILDER
# =========================================================

def build_report_text(ai_result, calculations, safety, template):
    lines = []

    lines.append("TEXT-TO-CIRCUIT AI ASSISTANT — DESIGN REPORT")
    lines.append("=" * 50)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"Device / Circuit : {ai_result.get('device_name', 'N/A')}")
    lines.append(f"Category         : {ai_result.get('category', 'N/A')}")
    lines.append(f"Template         : {template}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("COMPONENTS")
    lines.append("-" * 50)
    for component in ai_result.get("components", []):
        c_name = component.get("type") or component.get("name") or component.get("id") or "Unknown"
        c_val = component.get("value", "N/A")
        c_unit = component.get("unit", "")
        c_full_val = f"{c_val} {c_unit}".strip() if c_val != "N/A" else "N/A"
        c_purpose = component.get("purpose") or component.get("description") or "Not specified"
        lines.append(f"- {c_name} ({c_full_val}): {c_purpose}")

    lines.append("")
    lines.append("-" * 50)
    lines.append("CONNECTIONS")
    lines.append("-" * 50)
    for connection in ai_result.get("connections", []):
        lines.append(f"- {connection}")

    lines.append("")
    lines.append("-" * 50)
    lines.append("WORKING PRINCIPLE")
    lines.append("-" * 50)
    lines.append(ai_result.get("explanation", "No explanation available."))

    lines.append("")
    lines.append("-" * 50)
    lines.append("CALCULATIONS")
    lines.append("-" * 50)
    for calculation in calculations:
        lines.append(f"- {calculation}")

    lines.append("")
    lines.append("-" * 50)
    lines.append("SAFETY")
    lines.append("-" * 50)
    lines.append(safety)

    notes = ai_result.get("safety_notes", "")
    if notes:
        lines.append("")
        lines.append(notes)

    return "\n".join(lines)


# =========================================================
# PROCESS REQUEST
# =========================================================

if analyze_button:

    if not user_text.strip():
        st.warning("Please enter a circuit or device description.")
        st.stop()

    with st.spinner("🤖 Gemini is understanding your electronics request..."):

        try:
            ai_result = analyze_with_ai(user_text)

        except Exception as e:
            st.error("AI connection failed.")
            st.code(str(e))
            st.info(
                "Check that GEMINI_API_KEY is correctly configured "
                "in your .env file."
            )
            st.stop()

    if ai_result.get("parse_failed"):
        # analyze_with_ai() already retried once internally with a
        # stricter/shorter prompt — both attempts failed to produce
        # valid JSON. Show exactly why instead of a vague dead-end,
        # since this is a live-response issue (usually the model's
        # output got cut off), not a "your prompt has no components"
        # problem.
        st.warning(
            "Gemini responded, but its answer couldn't be turned into "
            "a circuit."
        )
        st.write("•", ai_result.get("parse_failure_reason", "Unknown parsing error."))
        with st.expander("🔍 View Gemini's raw response"):
            st.code(ai_result.get("raw_response", "(empty)"))
        st.info("Try again, or simplify the request slightly and re-run.")
        st.stop()

    # -----------------------------------------------------
    # LOCAL VERIFIED TEMPLATE MATCH
    # -----------------------------------------------------

    local_device = find_device(user_text)

    if local_device:
        ai_result["device_name"] = local_device["name"]
        ai_result["category"] = local_device["category"]
        ai_result["template"] = local_device["template"]
    elif not ai_result.get("template"):
        # AI didn't give us a template slug (e.g. malformed response) —
        # derive one from whatever device name it did produce, so the
        # request still gets a diagram via the generic renderer instead
        # of dead-ending here.
        ai_result["template"] = slugify_template(ai_result.get("device_name"))

    # This is a genuine signal, not a fabricated score: it reflects
    # whether the request matched a known alias in the verified
    # device database (a hand-drawn schematic) or was interpreted
    # freely by the AI (rendered with the generic circuit engine).
    matched_locally = local_device is not None
    is_verified_template = validate_template(ai_result["template"])

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------
    # Only a genuinely blocking problem (no components at all) stops
    # the app now. An unrecognized/custom template is no longer
    # blocking — it just renders with the generic circuit engine and
    # gets labeled "AI-Inferred" instead of "Verified Match" below.

    issues = validate_result(ai_result)

    if issues:
        st.warning("Couldn't build a circuit from that description yet.")

        for issue in issues:
            st.write("•", issue)

        st.stop()

    if not is_verified_template:
        st.info(
            "This isn't one of the hand-drawn example circuits, so it's "
            "rendered with the general-purpose circuit engine below. "
            "Double-check the diagram and values before building it."
        )

    template = ai_result["template"]

    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    calculations = calculate(template, user_text)
    ai_result["calculations"] = calculations

    # -----------------------------------------------------
    # SAFETY
    # -----------------------------------------------------

    safety = safety_message(template)

    # Persist the result so it survives reruns triggered by OTHER
    # widgets — e.g. clicking "Fetch live prices" inside a tab.
    # Without this, Streamlit's "rerun the whole script" model meant
    # analyze_button was False on that rerun and this entire results
    # section (including the button you just clicked) disappeared.
    st.session_state.result = {
        "ai_result": ai_result,
        "calculations": calculations,
        "safety": safety,
        "template": template,
        "matched_locally": matched_locally,
        "is_verified_template": is_verified_template,
    }
    # A fresh analysis invalidates any previously fetched price data.
    st.session_state.pop("price_data", None)

    # Auto-fetch prices right away (unless turned off in the sidebar)
    # so the Prices tab is already filled in the moment it's opened,
    # instead of waiting for a separate button click.
    if st.session_state.get("auto_fetch_prices", True):
        with st.spinner("🔎 Researching component prices online..."):
            try:
                st.session_state.price_data = search_component_prices(
                    ai_result.get("components", []),
                    region=st.session_state.get("price_region", ""),
                )
            except Exception as e:
                st.session_state.price_data = {"error": str(e)}


if st.session_state.get("result"):

    ai_result = st.session_state.result["ai_result"]
    calculations = st.session_state.result["calculations"]
    safety = st.session_state.result["safety"]
    template = st.session_state.result["template"]
    matched_locally = st.session_state.result["matched_locally"]
    is_verified_template = st.session_state.result["is_verified_template"]

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    st.success("✓ Analysis completed successfully")

    # -----------------------------------------------------
    # RESULT SUMMARY
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Design Summary</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Device / Circuit</div>
                <div class="info-value">{ai_result["device_name"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Category</div>
                <div class="info-value">{ai_result["category"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Verified Template</div>
                <div class="info-value">
                    ✓ {template.replace("_", " ").title()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        if matched_locally:
            status_html = (
                '<div class="info-value status-good">✓ Verified Match</div>'
                '<div class="info-sub">Matched a known device alias</div>'
            )
        else:
            status_html = (
                '<div class="info-value status-info">🤖 AI-Inferred</div>'
                '<div class="info-sub">Template chosen from free-form text</div>'
            )

        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Design Status</div>
                {status_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Components</div>
                <div class="info-value">🔌 {len(ai_result.get("components", []))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c6:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Connections</div>
                <div class="info-value">🧵 {len(ai_result.get("connections", []))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # -----------------------------------------------------
    # MAIN CONTENT
    # -----------------------------------------------------

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🔌 Components",
            "📐 Circuit Diagram",
            "🧠 Working Principle",
            "🧮 Calculations",
            "⚠️ Safety",
            "💰 Prices & Availability",
        ]
    )

    # =====================================================
    # COMPONENTS
    # =====================================================

    with tab1:

        left, right = st.columns([1.3, 1])

        with left:

            st.markdown("### Detected Components")

            components = ai_result.get("components", [])

            if components:

                rows = []
                for component in components:
                    # Robust fallback extraction to handle AI variations ('type', 'name', 'id')
                    name = component.get("type") or component.get("name") or component.get("id") or "Unknown"

                    # Combine value and unit properly
                    val = component.get("value", "")
                    unit = component.get("unit", "")
                    full_value = f"{val} {unit}".strip() if val else "N/A"

                    # Purpose or description fallback
                    purpose = component.get("purpose") or component.get("description") or "Not specified"

                    rows.append([
                        (name, "name-cell"),
                        (full_value, "value-cell"),
                        (purpose, None),
                    ])

                st.markdown(
                    render_html_table(["Component", "Value", "Purpose"], rows),
                    unsafe_allow_html=True,
                )

            else:
                st.info("No components detected.")

        with right:

            st.markdown("### Connection Flow")

            connections = ai_result.get("connections", [])

            if connections:

                for connection in connections:
                    st.markdown(
                        f'<div class="connection">→ {connection}</div>',
                        unsafe_allow_html=True,
                    )

            else:
                st.info("No connection description available.")

    # =====================================================
    # DIAGRAM
    # =====================================================

    with tab2:

        st.markdown(
            f"### 📐 {ai_result['device_name']}"
        )

        st.caption(
            "Generated using the application's verified circuit/template engine."
        )

        try:

            image_bytes = generate_circuit(
                template,
                ai_result,
            )

            st.markdown(
                '<div class="diagram-card">',
                unsafe_allow_html=True,
            )

            st.image(
                image_bytes,
                use_container_width=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

            report_text = build_report_text(ai_result, calculations, safety, template)

            dl1, dl2 = st.columns(2)

            with dl1:
                st.download_button(
                    "⬇️ Download Circuit Diagram",
                    data=image_bytes,
                    file_name=f"{template}_circuit.png",
                    mime="image/png",
                    use_container_width=True,
                )

            with dl2:
                st.download_button(
                    "📄 Download Full Report",
                    data=report_text,
                    file_name=f"{template}_report.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            explanation_preview = ai_result.get("explanation", "")
            if explanation_preview:
                preview = explanation_preview.strip()
                if len(preview) > 320:
                    preview = preview[:320].rsplit(" ", 1)[0] + "…"

                st.markdown(
                    f"""
                    <div class="principle-preview">
                        <div class="principle-label">🧠 Working Principle</div>
                        {preview}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption("See the full explanation in the Working Principle tab.")

        except Exception as e:

            st.error("The circuit diagram could not be generated.")

            st.code(str(e))

    # =====================================================
    # WORKING PRINCIPLE
    # =====================================================

    with tab3:

        st.markdown("### 🧠 Working Principle")

        explanation = ai_result.get(
            "explanation",
            "No explanation available.",
        )

        st.markdown(
            f'<div class="text-card">{explanation}</div>',
            unsafe_allow_html=True,
        )

    # =====================================================
    # CALCULATIONS
    # =====================================================

    with tab4:

        st.markdown("### 🧮 Engineering Calculations")

        calculations = ai_result.get("calculations", [])

        if calculations:

            for index, calculation in enumerate(calculations, 1):

                st.markdown(
                    f"""
                    <div class="component-card">
                        <b>{index}.</b> {calculation}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.info(
                "This system does not currently require a "
                "numerical calculation in the application."
            )

    # =====================================================
    # SAFETY
    # =====================================================

    with tab5:

        st.markdown("### ⚠️ Safety Information")

        st.warning(safety)

        notes = ai_result.get("safety_notes", "")

        if notes:
            st.markdown(
                f'<div class="text-card">{notes}</div>',
                unsafe_allow_html=True,
            )

    # =====================================================
    # PRICES & AVAILABILITY (live web search via Gemini)
    # =====================================================

    with tab6:

        st.markdown("### 💰 Component Prices & Availability")
        st.caption(
            f"Powered by Google Gemini ({MODEL_NAME}) with Google Search "
            "grounding — the same LLM used to read your prompt also "
            "searches the web for current prices and availability."
        )

        region = st.session_state.get("price_region", "")
        st.caption(
            f"Region: **{region or 'not set (general USD estimate)'}** "
            "— change this in the **⚙️ Settings & About** panel above the input box."
        )

        refresh = st.button(
            "🔎 Fetch Live Prices",
            key="fetch_prices_btn",
            use_container_width=True,
            help="Makes one extra Gemini API call to search the web for "
                 "current prices and availability of the components above.",
        )

        if refresh:
            components_for_search = ai_result.get("components", [])
            with st.spinner("🌐 Searching the web for current prices..."):
                try:
                    st.session_state.price_data = search_component_prices(
                        components_for_search, region=region
                    )
                except Exception as e:
                    st.session_state.price_data = {"error": str(e)}

        price_data = st.session_state.get("price_data")

        if price_data is None:
            # Reached whenever prices haven't been fetched yet for this
            # analysis — the default, since auto-fetch is off by default
            # to conserve API quota (see Settings & About above).
            st.info(
                "Click **Fetch Live Prices** to search the web for "
                "current pricing and availability of the components "
                "detected above. This uses one extra API call."
            )


        elif price_data.get("error"):
            st.error(price_data["error"])
            st.caption(
                "This is a live-search failure, not a bug in the app — "
                "see the message above for the specific cause "
                "(rate limit, invalid key, or unsupported model)."
            )

        elif price_data.get("results"):

            rows = []
            for item in price_data["results"]:
                comp = item.get("component", "Unknown")
                price = item.get("estimated_price", "N/A")
                availability = item.get("availability", "N/A")
                notes = item.get("notes", "")

                rows.append([
                    (comp, "name-cell"),
                    (price, "value-cell"),
                    (availability, None),
                    (notes, None),
                ])

            st.markdown(
                render_html_table(
                    ["Component", "Est. Price", "Availability", "Notes"], rows
                ),
                unsafe_allow_html=True,
            )

            sources = price_data.get("sources", [])
            if sources:
                st.markdown("##### Sources")
                for s in sources:
                    st.markdown(f"- [{s['title']}]({s['url']})")

            st.caption(
                "Prices are AI-researched estimates, not live quotes. "
                "Always confirm on the retailer's page before buying."
            )

        elif price_data.get("raw_response"):
            st.warning(
                "Got a response, but it wasn't in the expected table "
                "format. Showing it as-is:"
            )
            st.write(price_data["raw_response"])

        else:
            st.info("No components available to search for.")

    # =====================================================
    # AI DATA
    # =====================================================

    st.divider()

    with st.expander("🔍 View AI Analysis Data"):


        st.caption(
            "Developer/debug view showing the structured response "
            "returned by the AI."
        )

        st.json(ai_result)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        ⚡ Text-to-Circuit AI Assistant
        &nbsp;•&nbsp;
        AI-Powered Electronics Design & Learning Platform
        <br><br>
        Educational electronics assistant — always verify component
        ratings and circuit connections before building real hardware.
    </div>
    """,
    unsafe_allow_html=True,
)