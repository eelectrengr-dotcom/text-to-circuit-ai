# device_detector.py

import re

from device_database import DEVICE_DATABASE

# Generic words that carry no device-identifying signal. Stripped out
# before comparing "leftover" words against a matched device's vocabulary.
STOPWORDS = {
    "a", "an", "the", "with", "of", "in", "on", "for", "to", "and", "or",
    "using", "make", "build", "design", "create", "circuit", "system",
    "simple", "basic", "is", "that", "this", "it", "i", "want", "need",
    "please", "can", "you", "me", "my", "small", "please",
}

# If a local alias only accounts for a fraction of the request and the
# rest isn't explained by that device's own vocabulary, we don't trust
# the match — see find_device() below.
MIN_CONTEXT_OVERLAP = 0.15


def normalize_text(text):
    return " ".join(text.lower().strip().split())


def _tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def find_device(text):
    text_norm = normalize_text(text)

    best_match = None
    best_score = 0
    best_alias = None

    for key, device in DEVICE_DATABASE.items():

        for alias in device["aliases"]:

            alias_l = alias.lower()

            if alias_l in text_norm:

                score = len(alias_l)

                if score > best_score:
                    best_score = score
                    best_match = device.copy()
                    best_match["key"] = key
                    best_alias = alias_l

    if not best_match:
        return None

    # ---------------------------------------------------------------
    # Guard against a short, generic alias (e.g. "led circuit") being
    # swallowed inside a much longer, more specific request that is
    # actually describing a different system entirely (e.g. a PIR
    # motion-sensor circuit that happens to also contain an LED).
    #
    # We only trust the match if whatever text is LEFT OVER after
    # removing the alias and common filler words is reasonably
    # explained by this device's own vocabulary (its name, category,
    # description and aliases). If the leftover words are foreign to
    # this device (e.g. "motion", "pir", "sensor" for a plain LED
    # circuit), we back off and let the AI's own classification stand
    # instead of overriding it.
    # ---------------------------------------------------------------

    text_words = _tokenize(text_norm) - STOPWORDS
    alias_words = _tokenize(best_alias)
    leftover = text_words - alias_words - STOPWORDS

    if leftover:
        device_vocab_text = " ".join([
            best_match.get("name", ""),
            best_match.get("category", ""),
            best_match.get("description", ""),
            " ".join(best_match.get("aliases", [])),
        ])
        device_vocab = _tokenize(device_vocab_text)

        overlap = len(leftover & device_vocab) / len(leftover)

        if overlap < MIN_CONTEXT_OVERLAP:
            return None

    return best_match


def get_supported_devices():
    return [
        {
            "name": device["name"],
            "category": device["category"],
            "template": device["template"]
        }
        for device in DEVICE_DATABASE.values()
    ]
