import schemdraw
from schemdraw import elements as elm


def generate_series_circuit(
    voltage=5,
    resistors=None,
    capacitor=False,
    capacitor_value=None,
    led=False,
    diode=False,
    switch=False
):

    if resistors is None:
        resistors = []

    drawing = schemdraw.Drawing()

    # ==========================================
    # Voltage Source
    # ==========================================

    drawing += elm.SourceV().up().label(
        f"{voltage} V"
    )

    drawing += elm.Line().right()

    # ==========================================
    # Switch
    # ==========================================

    if switch:

        drawing += (
            elm.Switch()
            .right()
            .label("SW1")
        )

        drawing += elm.Line().right()

    # ==========================================
    # Resistors
    # ==========================================

    for i, resistance in enumerate(resistors):

        if resistance >= 1000:

            label_value = f"{resistance / 1000:g}kΩ"

        else:

            label_value = f"{resistance:g}Ω"

        drawing += (
            elm.Resistor()
            .right()
            .label(
                f"R{i + 1}\n{label_value}"
            )
        )

        drawing += elm.Line().right()

    # ==========================================
    # Diode
    # ==========================================

    if diode:

        drawing += (
            elm.Diode()
            .right()
            .label("D1")
        )

        drawing += elm.Line().right()

    # ==========================================
    # LED
    # ==========================================

    if led:

        drawing += (
            elm.LED()
            .right()
            .label("LED")
        )

        drawing += elm.Line().right()

    # ==========================================
    # Capacitor
    # ==========================================

    if capacitor:

        if capacitor_value is not None:

            if capacitor_value >= 1:

                cap_label = (
                    f"C1\n{capacitor_value:g}µF"
                )

            else:

                cap_label = "C1"

        else:

            cap_label = "C1"

        drawing += (
            elm.Capacitor()
            .right()
            .label(cap_label)
        )

        drawing += elm.Line().right()

    # ==========================================
    # Return Path
    # ==========================================

    drawing += elm.Line().down()

    drawing += elm.Line().left(
        length=3
    )

    drawing += elm.Line().left(
        length=3
    )

    return drawing


def generate_voltage_divider(
    voltage,
    r1,
    r2
):

    drawing = schemdraw.Drawing()

    # ==========================================
    # Source
    # ==========================================

    drawing += (
        elm.SourceV()
        .up()
        .label(f"{voltage} V")
    )

    drawing += elm.Line().right()

    # ==========================================
    # R1
    # ==========================================

    drawing += (
        elm.Resistor()
        .right()
        .label(f"R1\n{r1:g}Ω")
    )

    # ==========================================
    # Output node
    # ==========================================

    drawing += elm.Dot()

    drawing += (
        elm.Line()
        .right()
        .label("Vout")
    )

    # ==========================================
    # R2
    # ==========================================

    drawing += (
        elm.Resistor()
        .down()
        .label(f"R2\n{r2:g}Ω")
    )

    # ==========================================
    # Return
    # ==========================================

    drawing += elm.Line().left()

    drawing += elm.Line().left()

    return drawing