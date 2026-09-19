# validator.py

from device_database import DEVICE_DATABASE


SUPPORTED_TEMPLATES = {
    device["template"]
    for device in DEVICE_DATABASE.values()
}


def validate_template(template):
    """
    True only for the ~17 curated, hand-drawn schematic templates.
    This is now used purely to label a result as 'Verified Template'
    vs 'Custom / AI-Generated' in the UI — it no longer blocks
    anything, since circuit_generator/calculator/safety_message all
    have generic fallbacks for unrecognized templates.
    """
    return template in SUPPORTED_TEMPLATES


def validate_result(result):
    """
    Only flags issues that genuinely prevent the app from doing
    anything useful:
      - no components identified at all

    A missing/unrecognized 'template' is NO LONGER a blocking issue —
    app.py assigns a fallback slug before this runs, and the generic
    circuit renderer/calculator/safety message handle any template
    string that isn't one of the built-in examples.
    """
    issues = []

    if not result.get("components"):
        issues.append(
            "No components were identified in the request. "
            "Try describing at least one component (e.g. resistor, LED, sensor)."
        )

    return issues


def safety_message(template):

    if template == "fire_detection":
        return (
            "Educational prototype only. "
            "This design is not a certified life-safety fire alarm."
        )

    if template == "battery_charger":
        return (
            "Use an appropriate charger/controller and battery protection. "
            "Do not connect an unknown battery directly to a power source."
        )

    if template == "walkie_talkie":
        return (
            "RF circuits require correct frequency, impedance matching, "
            "antenna design and legal radio operation. "
            "The displayed design is a block-level educational architecture."
        )

    return (
        "Educational demonstration only. "
        "Verify component ratings before building hardware."
    )
