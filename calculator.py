def calculate_current(voltage, resistance):

    if resistance <= 0:
        return None

    return voltage / resistance


def calculate_power(voltage, current):

    return voltage * current


def voltage_divider(voltage, r1, r2):

    if r1 + r2 == 0:
        return None

    return voltage * (
        r2 / (r1 + r2)
    )


def format_resistance(value):

    if value >= 1_000_000:

        return f"{value / 1_000_000:.2f} MΩ"

    elif value >= 1000:

        return f"{value / 1000:.2f} kΩ"

    else:

        return f"{value:.2f} Ω"