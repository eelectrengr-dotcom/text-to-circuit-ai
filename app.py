import streamlit as st

from parser import parse_circuit

from calculator import (
    calculate_current,
    calculate_power,
    voltage_divider,
    format_resistance
)

from circuit_generator import (
    generate_series_circuit,
    generate_voltage_divider
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Text to Circuit AI Assistant",
    page_icon="⚡",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
    }

    .subtitle {
        font-size: 18px;
        color: #aaaaaa;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="main-title">⚡ Text to Circuit AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Describe an electrical circuit in simple English '
    'and generate a circuit diagram.'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# INPUT
# ==================================================

user_text = st.text_area(
    "Describe your circuit",
    placeholder=(
        "Example: Create a 5V circuit with "
        "a 1k resistor and capacitor."
    ),
    height=120
)


generate_button = st.button(
    "⚡ Generate Circuit",
    type="primary",
    use_container_width=True
)


# ==================================================
# PROCESS
# ==================================================

if generate_button:

    if not user_text.strip():

        st.warning(
            "Please describe a circuit first."
        )

        st.stop()

    # ==============================================
    # Parse text
    # ==============================================

    circuit = parse_circuit(user_text)

    st.divider()

    # ==============================================
    # DETECTED COMPONENTS
    # ==============================================

    st.subheader("🔧 Detected Components")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"🔋 **Voltage Source:** "
            f"{circuit['voltage']} V"
        )

        if circuit["resistors"]:

            for i, resistance in enumerate(
                circuit["resistors"]
            ):

                st.write(
                    f"🔲 **R{i + 1}:** "
                    f"{format_resistance(resistance)}"
                )

        if circuit["capacitor_detected"]:

            if circuit["capacitors"]:

                st.write(
                    f"🔵 **Capacitor:** "
                    f"{circuit['capacitors'][0]} µF"
                )

            else:

                st.write(
                    "🔵 **Capacitor:** Detected"
                )

    with col2:

        if circuit["led"]:

            st.write(
                "💡 **LED:** Detected"
            )

        if circuit["diode"]:

            st.write(
                "➡️ **Diode:** Detected"
            )

        if circuit["switch"]:

            st.write(
                "🔘 **Switch:** Detected"
            )

        st.write(
            f"🔗 **Circuit Type:** "
            f"{circuit['circuit_type'].title()}"
        )

    # ==============================================
    # VOLTAGE DIVIDER
    # ==============================================

    if (
        circuit["circuit_type"]
        == "voltage divider"
        and len(circuit["resistors"]) >= 2
    ):

        r1 = circuit["resistors"][0]

        r2 = circuit["resistors"][1]

        voltage = circuit["voltage"]

        vout = voltage_divider(
            voltage,
            r1,
            r2
        )

        st.divider()

        st.subheader(
            "📐 Voltage Divider Calculation"
        )

        st.write(
            f"**Input Voltage:** {voltage} V"
        )

        st.write(
            f"**R1:** {format_resistance(r1)}"
        )

        st.write(
            f"**R2:** {format_resistance(r2)}"
        )

        st.success(
            f"Output Voltage = {vout:.2f} V"
        )

        # ==========================================
        # DIAGRAM
        # ==========================================

        st.subheader(
            "🔌 Generated Circuit"
        )

        drawing = generate_voltage_divider(
            voltage,
            r1,
            r2
        )

        st.image(
            drawing.get_imagedata("png"),
            caption="Generated Circuit"
        )

        # ==========================================
        # EXPLANATION
        # ==========================================

        st.subheader(
            "💡 Explanation"
        )

        st.info(
            "The two resistors form a voltage divider. "
            "The output voltage is taken from the "
            "connection between R1 and R2."
        )

    # ==============================================
    # NORMAL CIRCUIT
    # ==============================================

    else:

        st.divider()

        st.subheader(
            "🔌 Generated Circuit"
        )

        capacitor_value = None

        if circuit["capacitors"]:

            capacitor_value = (
                circuit["capacitors"][0]
            )

        drawing = generate_series_circuit(
            voltage=circuit["voltage"],
            resistors=circuit["resistors"],
            capacitor=circuit["capacitor_detected"],
            capacitor_value=capacitor_value,
            led=circuit["led"],
            diode=circuit["diode"],
            switch=circuit["switch"]
        )

        st.image(
            drawing.get_imagedata("png"),
            caption="Generated Circuit"
        )

        # ==========================================
        # CALCULATIONS
        # ==========================================

        if circuit["resistors"]:

            total_resistance = sum(
                circuit["resistors"]
            )

            current = calculate_current(
                circuit["voltage"],
                total_resistance
            )

            power = calculate_power(
                circuit["voltage"],
                current
            )

            st.subheader(
                "📐 Basic Calculation"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Total Resistance",
                    format_resistance(
                        total_resistance
                    )
                )

            with c2:

                st.metric(
                    "Current",
                    f"{current:.4f} A"
                )

            with c3:

                st.metric(
                    "Power",
                    f"{power:.4f} W"
                )

        # ==========================================
        # EXPLANATION
        # ==========================================

        st.subheader(
            "💡 Circuit Explanation"
        )

        explanation = (
            f"This circuit uses a "
            f"{circuit['voltage']} V voltage source."
        )

        if circuit["resistors"]:

            explanation += (
                f" It contains "
                f"{len(circuit['resistors'])} "
                f"resistor(s)."
            )

        if circuit["capacitor_detected"]:

            explanation += (
                " The capacitor stores electrical "
                "energy and can be used for filtering "
                "or timing applications."
            )

        if circuit["led"]:

            explanation += (
                " The LED converts electrical energy "
                "into light."
            )

        if circuit["diode"]:

            explanation += (
                " The diode allows current to flow "
                "primarily in one direction."
            )

        if circuit["switch"]:

            explanation += (
                " The switch is used to control "
                "the circuit connection."
            )

        st.info(explanation)

        # ==========================================
        # VALIDATION
        # ==========================================

        st.subheader(
            "✅ Circuit Validation"
        )

        if (
            circuit["led"]
            and not circuit["resistors"]
        ):

            st.warning(
                "⚠️ Warning: The LED does not have "
                "a current-limiting resistor. "
                "Normally, a resistor should be used "
                "with an LED."
            )

        elif (
            circuit["capacitor_detected"]
            and not circuit["capacitors"]
        ):

            st.warning(
                "⚠️ Capacitor detected, but no "
                "capacitance value was specified."
            )

        else:

            st.success(
                "✓ Basic circuit structure detected "
                "successfully."
            )