# device_database.py

DEVICE_DATABASE = {

    "led": {
        "name": "LED Circuit",
        "category": "Basic Electronics",
        "template": "led",
        "aliases": [
            "led",
            "light emitting diode",
            "led circuit",
            "led resistor"
        ],
        "description": "A basic LED circuit using a current-limiting resistor."
    },

    "voltage_divider": {
        "name": "Voltage Divider",
        "category": "Basic Electronics",
        "template": "voltage_divider",
        "aliases": [
            "voltage divider",
            "potential divider",
            "resistor divider"
        ],
        "description": "A resistor network used to obtain a fraction of an input voltage."
    },

    "rc_filter": {
        "name": "RC Low-Pass Filter",
        "category": "Filters",
        "template": "rc_filter",
        "aliases": [
            "rc filter",
            "rc low pass",
            "low pass filter",
            "rc low-pass filter"
        ],
        "description": "A resistor-capacitor network that attenuates high-frequency signals."
    },

    "rl_circuit": {
        "name": "RL Circuit",
        "category": "AC / Transient Circuits",
        "template": "rl_circuit",
        "aliases": [
            "rl circuit",
            "resistor inductor",
            "rl"
        ],
        "description": "A circuit containing a resistor and inductor."
    },

    "rlc_circuit": {
        "name": "RLC Circuit",
        "category": "AC Circuits",
        "template": "rlc_circuit",
        "aliases": [
            "rlc circuit",
            "rlc",
            "resistor inductor capacitor"
        ],
        "description": "A circuit containing resistor, inductor and capacitor."
    },

    "common_emitter": {
        "name": "Common Emitter Amplifier",
        "category": "Amplifiers",
        "template": "common_emitter",
        "aliases": [
            "common emitter",
            "common emitter amplifier",
            "ce amplifier",
            "transistor amplifier"
        ],
        "description": "A BJT amplifier configuration with voltage gain and phase inversion."
    },

    "opamp": {
        "name": "Inverting Op-Amp",
        "category": "Operational Amplifiers",
        "template": "opamp",
        "aliases": [
            "op amp",
            "opamp",
            "inverting op amp",
            "inverting amplifier",
            "operational amplifier"
        ],
        "description": "An op-amp amplifier where the output is inverted relative to the input."
    },

    "bridge_rectifier": {
        "name": "Full-Wave Bridge Rectifier",
        "category": "Power Electronics",
        "template": "bridge_rectifier",
        "aliases": [
            "bridge rectifier",
            "full wave rectifier",
            "full-wave bridge",
            "rectifier"
        ],
        "description": "A four-diode circuit used to convert AC into pulsating DC."
    },

    "zener_regulator": {
        "name": "Zener Voltage Regulator",
        "category": "Power Electronics",
        "template": "zener_regulator",
        "aliases": [
            "zener regulator",
            "zener voltage regulator",
            "voltage regulator",
            "zener diode regulator"
        ],
        "description": "A simple regulator using a Zener diode to maintain approximately constant voltage."
    },

    "transistor_switch": {
        "name": "Transistor Switch",
        "category": "Switching Circuits",
        "template": "transistor_switch",
        "aliases": [
            "transistor switch",
            "bjt switch",
            "transistor switching"
        ],
        "description": "A transistor used as an electronic ON/OFF switch."
    },

    "555_timer": {
        "name": "555 Timer Oscillator",
        "category": "Timers and Oscillators",
        "template": "555_timer",
        "aliases": [
            "555 timer",
            "ne555",
            "timer circuit",
            "555 oscillator",
            "astable 555"
        ],
        "description": "A 555 timer configured as an astable oscillator."
    },

    "fire_detection": {
        "name": "Fire Detection System",
        "category": "Safety System",
        "template": "fire_detection",
        "aliases": [
            "fire detection",
            "fire detection system",
            "fire alarm",
            "smoke detection",
            "smoke detector",
            "smoke alarm"
        ],
        "description": "An educational low-voltage fire/smoke detection prototype."
    },

    "security_alarm": {
        "name": "Security Emergency Alarm",
        "category": "Security System",
        "template": "security_alarm",
        "aliases": [
            "security alarm",
            "security system",
            "emergency alarm",
            "emergency call",
            "security emergency call system",
            "panic button"
        ],
        "description": "An educational emergency/security alarm prototype."
    },

    "street_light": {
        "name": "Automatic Street Light",
        "category": "Automation",
        "template": "street_light",
        "aliases": [
            "automatic street light",
            "automatic light",
            "street light",
            "ldr light",
            "ldr street light"
        ],
        "description": "An automatic light controller using an LDR sensor."
    },

    "temperature_fan": {
        "name": "Temperature Controlled Fan",
        "category": "Automation",
        "template": "temperature_fan",
        "aliases": [
            "temperature controlled fan",
            "temperature fan",
            "automatic fan",
            "temperature control"
        ],
        "description": "A temperature-based fan control system."
    },

    "battery_charger": {
        "name": "12V Battery Charger",
        "category": "Power Electronics",
        "template": "battery_charger",
        "aliases": [
            "battery charger",
            "12v battery charger",
            "battery charging circuit",
            "12 volt charger"
        ],
        "description": "An educational block-level 12V battery charging system."
    },

    "walkie_talkie": {
        "name": "Walkie-Talkie Communication System",
        "category": "Wireless Communication",
        "template": "walkie_talkie",
        "aliases": [
            "walkie talkie",
            "walkie-talkie",
            "wireless communication",
            "two way radio",
            "two-way radio",
            "security communication"
        ],
        "description": "A block-level wireless communication architecture."
    }
}