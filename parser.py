import re


def parse_circuit(text):

    text_lower = text.lower()

    circuit = {
        "voltage": 5.0,

        "resistors": [],

        "capacitors": [],

        "capacitor_detected": False,

        "led": False,

        "diode": False,

        "switch": False,

        "circuit_type": "series"
    }

    # ==========================================
    # Detect Voltage
    # ==========================================

    voltage_match = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:v|volt|volts)',
        text_lower
    )

    if voltage_match:
        circuit["voltage"] = float(
            voltage_match.group(1)
        )

    # ==========================================
    # Detect Resistors
    # ==========================================

    resistor_matches = re.findall(
        r'(\d+(?:\.\d+)?)\s*'
        r'(k|kohm|kohms|kω|ω|ohm|ohms)',
        text_lower
    )

    for value, unit in resistor_matches:

        value = float(value)

        if unit in ["k", "kohm", "kohms", "kω"]:
            value *= 1000

        circuit["resistors"].append(value)

    # ==========================================
    # Detect Capacitor
    # ==========================================

    capacitor_words = [
        "capacitor",
        "capacitors",
        "capacitance"
    ]

    if any(word in text_lower for word in capacitor_words):

        circuit["capacitor_detected"] = True

        capacitor_matches = re.findall(
            r'(\d+(?:\.\d+)?)\s*'
            r'(uf|µf|nf|pf)',
            text_lower
        )

        for value, unit in capacitor_matches:

            value = float(value)

            if unit == "nf":
                value /= 1000

            elif unit == "pf":
                value /= 1_000_000

            circuit["capacitors"].append(value)

    # ==========================================
    # Detect LED
    # ==========================================

    if "led" in text_lower:

        circuit["led"] = True

    # ==========================================
    # Detect Diode
    # ==========================================

    if "diode" in text_lower:

        circuit["diode"] = True

    # ==========================================
    # Detect Switch
    # ==========================================

    if "switch" in text_lower:

        circuit["switch"] = True

    # ==========================================
    # Detect Circuit Type
    # ==========================================

    if "voltage divider" in text_lower:

        circuit["circuit_type"] = "voltage divider"

    elif "parallel" in text_lower:

        circuit["circuit_type"] = "parallel"

    elif "series" in text_lower:

        circuit["circuit_type"] = "series"

    # ==========================================
    # Automatic Detection
    # ==========================================

    # If voltage divider is not explicitly mentioned
    # but there are two resistors and divider words,
    # treat it as voltage divider.

    if (
        "divider" in text_lower
        and len(circuit["resistors"]) >= 2
    ):

        circuit["circuit_type"] = "voltage divider"

    return circuit