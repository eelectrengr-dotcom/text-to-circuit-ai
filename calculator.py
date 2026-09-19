# calculator.py

import re
import math


def extract_voltage(text, default=5.0):

    match = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:v|volt|volts)',
        text.lower()
    )

    if match:
        return float(match.group(1))

    return default


def extract_resistance(text, default=220.0):

    match = re.search(
        r'(\d+(?:\.\d+)?)\s*(k|kohm|kω|ohm|ohms|Ω)',
        text.lower()
    )

    if not match:
        return default

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit in ["k", "kohm", "kω"]:
        value *= 1000

    return value


def extract_capacitance(text, default=0.000001):

    match = re.search(
        r'(\d+(?:\.\d+)?)\s*(uf|µf|nf|pf)',
        text.lower()
    )

    if not match:
        return default

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit in ["uf", "µf"]:
        return value * 1e-6

    if unit == "nf":
        return value * 1e-9

    if unit == "pf":
        return value * 1e-12

    return default


def led_calculation(text):

    voltage = extract_voltage(text, 5.0)
    resistance = extract_resistance(text, 220.0)

    led_voltage = 2.0

    current = (voltage - led_voltage) / resistance

    if current < 0:
        current = 0

    return [
        f"Supply voltage = {voltage:.2f} V",
        f"Resistor = {resistance:.0f} Ω",
        f"Assumed LED forward voltage = {led_voltage:.1f} V",
        f"LED current ≈ {current * 1000:.2f} mA",
        f"Formula: I = (Vs - Vf) / R"
    ]


def voltage_divider_calculation(text):

    voltage = extract_voltage(text, 12.0)

    r1 = 10000
    r2 = 10000

    output = voltage * r2 / (r1 + r2)

    return [
        f"Input voltage = {voltage:.2f} V",
        f"R1 = {r1 / 1000:.1f} kΩ",
        f"R2 = {r2 / 1000:.1f} kΩ",
        f"Output voltage ≈ {output:.2f} V",
        "Formula: Vout = Vin × R2 / (R1 + R2)"
    ]


def rc_calculation(text):

    resistance = extract_resistance(text, 10000)
    capacitance = extract_capacitance(text, 1e-6)

    cutoff = 1 / (2 * math.pi * resistance * capacitance)

    return [
        f"Resistance = {resistance:.0f} Ω",
        f"Capacitance = {capacitance:.2e} F",
        f"Cutoff frequency ≈ {cutoff:.2f} Hz",
        "Formula: fc = 1 / (2πRC)"
    ]


def generic_calculation():

    return [
        "Component values should be selected according to the specific circuit requirements.",
        "The displayed design is intended for educational demonstration."
    ]


def calculate(template, text):

    if template == "led":
        return led_calculation(text)

    if template == "voltage_divider":
        return voltage_divider_calculation(text)

    if template == "rc_filter":
        return rc_calculation(text)

    return generic_calculation()