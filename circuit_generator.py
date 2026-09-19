# circuit_generator.py
#
# Dark-themed schematic circuit generator.
# Renders electronic schematic diagrams for basic circuits as well as 
# smart systems using component symbols instead of high-level block boxes.

import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle


# =====================================================
# PALETTE  (kept in sync with app.py's CSS variables)
# =====================================================

BG_COLOR = "#0d1117"          # figure background (transparent-ish dark)
PANEL_COLOR = "#111722"       # matches .diagram-card background
WIRE_COLOR = "#4f8cff"        # matches app accent blue (.connection border)
WIRE_MUTED = "#3a4a63"
TEXT_COLOR = "#f2f5f8"
MUTED_TEXT = "#93a3b8"

RESISTOR_COLOR = "#f5a623"
CAPACITOR_COLOR = "#38bdf8"
DIODE_COLOR = "#a78bfa"
LED_COLOR = "#fb7185"
LED_RAY_COLOR = "#fbbf24"
GROUND_COLOR = "#93a3b8"
BATTERY_COLOR = "#34d399"
TRANSISTOR_COLOR = "#4f8cff"
IC_COLOR = "#a78bfa"
BLOCK_FILL = "#161d2b"


# =====================================================
# CANVAS
# =====================================================

def make_figure(width=12, height=6):
    fig, ax = plt.subplots(figsize=(width, height))

    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    return fig, ax


def title(fig, text, subtitle=None):
    fig.suptitle(
        text,
        fontsize=18,
        fontweight="bold",
        color=TEXT_COLOR,
        y=0.97,
    )

    if subtitle:
        fig.text(
            0.5, 0.905,
            subtitle,
            ha="center",
            fontsize=10.5,
            color=MUTED_TEXT,
        )


def save_figure(fig):
    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        dpi=180,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)
    buffer.seek(0)

    return buffer.getvalue()


# =====================================================
# PRIMITIVES & SCHEMATIC SYMBOLS
# =====================================================

def wire(ax, x1, y1, x2, y2, color=WIRE_COLOR, lw=2.2, style="-"):
    """Standard schematic conductor wire."""
    ax.plot([x1, x2], [y1, y2], linewidth=lw, color=color, linestyle=style)


def node_dot(ax, x, y, color=WIRE_COLOR):
    ax.add_patch(Circle((x, y), 0.05, color=color, zorder=5))


def resistor(ax, x, y, label="R", vertical=False):
    if vertical:
        rect = Rectangle(
            (x - 0.18, y - 0.45),
            0.36,
            0.9,
            fill=True,
            facecolor=BLOCK_FILL,
            edgecolor=RESISTOR_COLOR,
            linewidth=2.2,
        )
        ax.add_patch(rect)
        ax.text(x + 0.3, y, label, ha="left", va="center", color=TEXT_COLOR,
                fontsize=10, fontweight="bold")
    else:
        rect = Rectangle(
            (x - 0.45, y - 0.18),
            0.9,
            0.36,
            fill=True,
            facecolor=BLOCK_FILL,
            edgecolor=RESISTOR_COLOR,
            linewidth=2.2,
        )
        ax.add_patch(rect)
        ax.text(x, y + 0.35, label, ha="center", va="bottom", color=TEXT_COLOR,
                fontsize=10, fontweight="bold")


def ldr_sensor(ax, x, y, label="LDR"):
    resistor(ax, x, y, label, vertical=True)
    # Light arrows pointing toward resistor
    ax.annotate("", xy=(x - 0.25, y + 0.1), xytext=(x - 0.65, y + 0.4),
                arrowprops=dict(arrowstyle="->", color=LED_RAY_COLOR, lw=1.5))
    ax.annotate("", xy=(x - 0.25, y - 0.1), xytext=(x - 0.65, y + 0.2),
                arrowprops=dict(arrowstyle="->", color=LED_RAY_COLOR, lw=1.5))


def thermistor_sensor(ax, x, y, label="NTC"):
    resistor(ax, x, y, label, vertical=True)
    ax.plot([x - 0.35, x + 0.35], [y - 0.4, y + 0.4], color=RESISTOR_COLOR, linewidth=1.8)
    ax.text(x - 0.4, y + 0.3, "-t°", color=RESISTOR_COLOR, fontsize=9, fontweight="bold")


def capacitor(ax, x, y, label="C", vertical=False):
    if vertical:
        ax.plot([x - 0.45, x + 0.45], [y + 0.12, y + 0.12],
                linewidth=3.2, color=CAPACITOR_COLOR, solid_capstyle="round")
        ax.plot([x - 0.45, x + 0.45], [y - 0.12, y - 0.12],
                linewidth=3.2, color=CAPACITOR_COLOR, solid_capstyle="round")
        ax.text(x + 0.55, y, label, ha="left", va="center", color=TEXT_COLOR,
                fontsize=10, fontweight="bold")
    else:
        ax.plot([x - 0.12, x - 0.12], [y - 0.45, y + 0.45],
                linewidth=3.2, color=CAPACITOR_COLOR, solid_capstyle="round")
        ax.plot([x + 0.12, x + 0.12], [y - 0.45, y + 0.45],
                linewidth=3.2, color=CAPACITOR_COLOR, solid_capstyle="round")
        ax.text(x, y + 0.65, label, ha="center", color=TEXT_COLOR,
                fontsize=10, fontweight="bold")


def diode(ax, x, y, label="D", color=DIODE_COLOR, vertical=False):
    if vertical:
        triangle = Polygon(
            [[x - 0.3, y + 0.25], [x + 0.3, y + 0.25], [x, y - 0.25]],
            closed=True, fill=True, facecolor=BLOCK_FILL, edgecolor=color, linewidth=2.2
        )
        ax.add_patch(triangle)
        ax.plot([x - 0.3, x + 0.3], [y - 0.25, y - 0.25], linewidth=2.4, color=color, solid_capstyle="round")
        ax.text(x + 0.45, y, label, ha="left", va="center", color=TEXT_COLOR, fontsize=10, fontweight="bold")
    else:
        triangle = Polygon(
            [[x - 0.35, y - 0.3], [x - 0.35, y + 0.3], [x + 0.25, y]],
            closed=True, fill=True, facecolor=BLOCK_FILL, edgecolor=color, linewidth=2.2
        )
        ax.add_patch(triangle)
        ax.plot([x + 0.25, x + 0.25], [y - 0.35, y + 0.35], linewidth=2.4, color=color, solid_capstyle="round")
        ax.text(x, y + 0.6, label, ha="center", color=TEXT_COLOR, fontsize=10, fontweight="bold")


def battery(ax, x, y, label="VCC"):
    ax.plot([x - 0.12, x - 0.12], [y - 0.55, y + 0.55],
            linewidth=4.5, color=BATTERY_COLOR, solid_capstyle="round")
    ax.plot([x + 0.12, x + 0.12], [y - 0.3, y + 0.3],
            linewidth=2.4, color=BATTERY_COLOR, solid_capstyle="round")
    ax.text(x, y + 0.85, label, ha="center", color=TEXT_COLOR,
            fontsize=10.5, fontweight="bold")


def led(ax, x, y, label="LED", vertical=False):
    diode(ax, x, y, label, color=LED_COLOR, vertical=vertical)
    if vertical:
        for dx, dy in [(0.2, -0.1), (0.35, -0.25)]:
            ax.plot([x + dx, x + dx + 0.25], [y + dy, y + dy + 0.25], linewidth=1.5, color=LED_RAY_COLOR)
    else:
        for dx, dy in [(0.35, 0.3), (0.45, 0.1)]:
            ax.plot([x + dx, x + dx + 0.32], [y + dy, y + dy + 0.32], linewidth=1.6, color=LED_RAY_COLOR)


def ground(ax, x, y):
    ax.plot([x, x], [y, y - 0.35], linewidth=2.2, color=GROUND_COLOR)
    ax.plot([x - 0.3, x + 0.3], [y - 0.35, y - 0.35], linewidth=2.2, color=GROUND_COLOR)
    ax.plot([x - 0.2, x + 0.2], [y - 0.48, y - 0.48], linewidth=2.2, color=GROUND_COLOR)
    ax.plot([x - 0.1, x + 0.1], [y - 0.61, y - 0.61], linewidth=2.2, color=GROUND_COLOR)


def npn_transistor(ax, x, y, label="Q1 (NPN)"):
    # Base vertical line
    ax.plot([x - 0.15, x - 0.15], [y - 0.35, y + 0.35], linewidth=3.0, color=TRANSISTOR_COLOR)
    # Base input lead
    ax.plot([x - 0.6, x - 0.15], [y, y], linewidth=2.0, color=WIRE_COLOR)
    # Collector lead
    ax.plot([x - 0.15, x + 0.25], [y + 0.15, y + 0.45], linewidth=2.0, color=WIRE_COLOR)
    ax.plot([x + 0.25, x + 0.25], [y + 0.45, y + 0.7], linewidth=2.0, color=WIRE_COLOR)
    # Emitter lead + Arrow
    ax.plot([x - 0.15, x + 0.25], [y - 0.15, y - 0.45], linewidth=2.0, color=WIRE_COLOR)
    ax.plot([x + 0.25, x + 0.25], [y - 0.45, y - 0.7], linewidth=2.0, color=WIRE_COLOR)
    ax.annotate("", xy=(x + 0.22, y - 0.42), xytext=(x + 0.05, y - 0.28),
                arrowprops=dict(arrowstyle="->", color=TRANSISTOR_COLOR, lw=2))
    # Outer circle
    ax.add_patch(Circle((x, y), 0.65, fill=False, edgecolor=TRANSISTOR_COLOR, linewidth=1.8))
    ax.text(x + 0.8, y, label, ha="left", va="center", color=TEXT_COLOR, fontsize=9.5, fontweight="bold")


def buzzer(ax, x, y, label="Buzzer"):
    # Cylinder sound element
    ax.add_patch(Circle((x, y), 0.4, fill=True, facecolor=BLOCK_FILL, edgecolor=LED_COLOR, linewidth=2))
    ax.plot([x - 0.4, x + 0.4], [y + 0.4, y + 0.4], linewidth=2.5, color=LED_COLOR)
    ax.text(x, y - 0.65, label, ha="center", va="top", color=TEXT_COLOR, fontsize=9.5, fontweight="bold")


def relay_module(ax, x, y, label="Relay Switch"):
    patch = FancyBboxPatch((x - 0.6, y - 0.5), 1.2, 1.0, boxstyle="round,pad=0.02",
                           fill=True, facecolor=BLOCK_FILL, edgecolor=BLOCK_EDGE_ALT, linewidth=2)
    ax.add_patch(patch)
    # Coil representation
    ax.plot([x - 0.3, x - 0.3], [y - 0.3, y + 0.3], linewidth=2, color=RESISTOR_COLOR, linestyle="--")
    # Switch contacts
    ax.plot([x + 0.1, x + 0.3], [y - 0.2, y + 0.2], linewidth=2, color=TEXT_COLOR)
    node_dot(ax, x + 0.1, y - 0.2, color=TEXT_COLOR)
    node_dot(ax, x + 0.3, y + 0.2, color=TEXT_COLOR)
    ax.text(x, y + 0.7, label, ha="center", va="bottom", color=TEXT_COLOR, fontsize=9.5, fontweight="bold")


def ic_chip(ax, x, y, width, height, label="IC"):
    patch = FancyBboxPatch((x - width/2, y - height/2), width, height, boxstyle="round,pad=0.03",
                           fill=True, facecolor=BLOCK_FILL, edgecolor=IC_COLOR, linewidth=2.2)
    ax.add_patch(patch)
    ax.text(x, y, label, ha="center", va="center", color=TEXT_COLOR, fontsize=11, fontweight="bold")


def switch_spst(ax, x, y, label="SW"):
    node_dot(ax, x - 0.4, y)
    node_dot(ax, x + 0.4, y)
    ax.plot([x - 0.4, x + 0.3], [y, y + 0.3], linewidth=2.2, color=TEXT_COLOR)
    ax.text(x, y + 0.4, label, ha="center", va="bottom", color=TEXT_COLOR, fontsize=9.5, fontweight="bold")


def caption(ax, x, y, text, color=MUTED_TEXT, fontsize=10.5, weight="normal"):
    ax.text(x, y, text, ha="center", color=color, fontsize=fontsize, fontweight=weight)


# =====================================================
# BASIC CIRCUITS
# =====================================================

def led_circuit():
    fig, ax = make_figure()
    title(fig, "5V LED Circuit", "Current-limiting resistor in series with an LED")

    battery(ax, 1.2, 3, "5V")
    wire(ax, 1.2, 3.6, 3, 3.6)
    resistor(ax, 3.5, 3.6, "220Ω")
    wire(ax, 3.95, 3.6, 5.2, 3.6)
    led(ax, 5.7, 3.6)
    wire(ax, 6.05, 3.6, 8.5, 3.6)
    wire(ax, 8.5, 3.6, 8.5, 2)
    ground(ax, 8.5, 2)

    caption(ax, 5.7, 2.4, "Current-limiting resistor")

    return save_figure(fig)


def voltage_divider():
    fig, ax = make_figure()
    title(fig, "Voltage Divider", "Two resistors sharing the input voltage")

    battery(ax, 2, 4.5, "Vin")
    wire(ax, 2, 3.9, 2, 3.2)
    resistor(ax, 2, 2.7, "R1")
    wire(ax, 2, 2.25, 2, 1.8)
    resistor(ax, 2, 1.3, "R2")
    wire(ax, 2, 0.85, 2, 0.5)
    ground(ax, 2, 0.5)

    wire(ax, 2, 2, 6, 2)
    node_dot(ax, 2, 2)

    ax.text(6.15, 2, "Vout", fontsize=13, fontweight="bold", color=TEXT_COLOR, va="center")

    caption(ax, 7.4, 1.15, "Vout = Vin × R2 / (R1 + R2)")

    return save_figure(fig)


def rc_filter():
    fig, ax = make_figure()
    title(fig, "RC Low-Pass Filter", "Attenuates frequencies above the cutoff")

    ax.text(0.9, 3, "Vin", fontsize=12, fontweight="bold", color=TEXT_COLOR)
    wire(ax, 1.5, 3, 3, 3)
    resistor(ax, 3.5, 3, "R")
    wire(ax, 3.95, 3, 5.5, 3)
    node_dot(ax, 5.5, 3)
    wire(ax, 5.5, 3, 5.5, 2.1)
    capacitor(ax, 5.5, 1.5, "C")
    wire(ax, 5.5, 0.8, 5.5, 0.5)
    ground(ax, 5.5, 0.5)
    wire(ax, 5.5, 3, 8, 3)

    ax.text(8.15, 3, "Vout", fontsize=12, fontweight="bold", color=TEXT_COLOR)
    caption(ax, 7, 1.4, "fc = 1 / (2πRC)")

    return save_figure(fig)


def rl_circuit():
    fig, ax = make_figure()
    title(fig, "RL Circuit", "Resistor and inductor in series")

    battery(ax, 1.2, 3, "Vin")
    wire(ax, 1.2, 3.6, 3, 3.6)
    resistor(ax, 3.5, 3.6, "R")
    wire(ax, 3.95, 3.6, 5, 3.6)

    # Render Inductor coil loop symbol
    ax.plot([5, 5.3, 5.6, 5.9, 6.2, 6.5], [3.6, 3.9, 3.3, 3.9, 3.3, 3.6], color=RESISTOR_COLOR, lw=2.2)
    ax.text(5.75, 4.2, "L (Inductor)", ha="center", color=TEXT_COLOR, fontweight="bold", fontsize=10)

    wire(ax, 6.5, 3.6, 8, 3.6)
    wire(ax, 8, 3.6, 8, 1.5)
    ground(ax, 8, 1.5)

    return save_figure(fig)


def rlc_circuit():
    fig, ax = make_figure()
    title(fig, "Series RLC Circuit", "Resistor, inductor and capacitor in series")

    battery(ax, 1, 3, "Vin")
    wire(ax, 1, 3.6, 2.5, 3.6)
    resistor(ax, 3, 3.6, "R")
    wire(ax, 3.45, 3.6, 4.5, 3.6)

    # Inductor coil
    ax.plot([4.5, 4.8, 5.1, 5.4, 5.7, 6.0], [3.6, 3.9, 3.3, 3.9, 3.3, 3.6], color=RESISTOR_COLOR, lw=2.2)
    ax.text(5.25, 4.2, "L", ha="center", color=TEXT_COLOR, fontweight="bold", fontsize=10)

    wire(ax, 6.0, 3.6, 7.2, 3.6)
    capacitor(ax, 7.5, 3.6, "C")
    wire(ax, 7.8, 3.6, 9, 3.6)
    wire(ax, 9, 3.6, 9, 1.5)
    ground(ax, 9, 1.5)

    return save_figure(fig)


# =====================================================
# AMPLIFIER CIRCUITS
# =====================================================

def common_emitter():
    fig, ax = make_figure()
    title(fig, "Common Emitter Amplifier", "Voltage amplification with phase inversion")

    battery(ax, 1, 3, "Vin")
    wire(ax, 1, 3.6, 1.8, 3.6)
    capacitor(ax, 2.2, 3.6, "Cin")
    wire(ax, 2.5, 3.6, 4.4, 3.6)
    node_dot(ax, 4.4, 3.6)

    # Bias Resistor RB to VCC
    wire(ax, 4.4, 3.6, 4.4, 4.5)
    resistor(ax, 4.4, 4.95, "RB", vertical=True)
    wire(ax, 4.4, 5.4, 7.5, 5.4)
    ax.text(7.6, 5.4, "+VCC (9V)", color=BATTERY_COLOR, fontweight="bold", va="center")

    # Transistor
    npn_transistor(ax, 5.0, 3.6, "Q1 (BC547)")

    # Emitter Ground
    wire(ax, 5.25, 2.9, 5.25, 1.8)
    ground(ax, 5.25, 1.8)

    # Collector Load Resistor RC
    wire(ax, 5.25, 4.3, 5.25, 4.5)
    resistor(ax, 5.25, 4.95, "RC", vertical=True)
    wire(ax, 5.25, 5.4, 5.25, 5.4)
    node_dot(ax, 5.25, 5.4)

    # Output Coupling
    node_dot(ax, 5.25, 4.3)
    wire(ax, 5.25, 4.3, 7.2, 4.3)
    capacitor(ax, 7.6, 4.3, "Cout")
    wire(ax, 8.0, 4.3, 9.5, 4.3)
    ax.text(9.7, 4.3, "Vout", fontsize=12, fontweight="bold", color=TEXT_COLOR, va="center")

    return save_figure(fig)


def opamp():
    fig, ax = make_figure()
    title(fig, "Inverting Op-Amp", "Output is inverted relative to the input")

    triangle = Polygon(
        [[5, 2], [5, 4], [8, 3]],
        closed=True,
        fill=True,
        facecolor=BLOCK_FILL,
        edgecolor=IC_COLOR,
        linewidth=2.2,
    )
    ax.add_patch(triangle)

    ax.text(5.35, 3.55, "-", fontsize=18, color=TEXT_COLOR, fontweight="bold")
    ax.text(5.35, 2.3, "+", fontsize=18, color=TEXT_COLOR, fontweight="bold")

    ax.text(0.9, 3.6, "Vin", color=TEXT_COLOR, fontsize=11, fontweight="bold")
    wire(ax, 1.5, 3.6, 2.7, 3.6)
    resistor(ax, 3.2, 3.6, "Rin")
    wire(ax, 3.7, 3.6, 5, 3.6)
    node_dot(ax, 4.3, 3.6)

    wire(ax, 8, 3, 9.5, 3)
    ax.text(9.7, 3, "Vout", color=TEXT_COLOR, fontsize=11, fontweight="bold")

    node_dot(ax, 8.8, 3)
    wire(ax, 8.8, 3, 8.8, 5)
    wire(ax, 8.8, 5, 6.2, 5)
    resistor(ax, 5.5, 5, "Rf")
    wire(ax, 4.8, 5, 4.3, 5)
    wire(ax, 4.3, 5, 4.3, 3.6)

    wire(ax, 5, 2.3, 4.2, 2.3)
    ground(ax, 4.2, 2.3)

    caption(ax, 6.5, 1, "Gain = -Rf / Rin")

    return save_figure(fig)


# =====================================================
# POWER ELECTRONICS
# =====================================================

def bridge_rectifier():
    fig, ax = make_figure()
    title(fig, "Full-Wave Bridge Rectifier", "Converts AC into pulsating DC")

    positions = [
        (4, 4, "D1"),
        (7, 4, "D2"),
        (4, 2, "D3"),
        (7, 2, "D4"),
    ]

    for x, y, label in positions:
        diode(ax, x, y, label)

    wire(ax, 4, 4.35, 4, 5)
    wire(ax, 4, 5, 7, 5)
    wire(ax, 7, 5, 7, 4.35)

    wire(ax, 4, 1.65, 4, 1)
    wire(ax, 4, 1, 7, 1)
    wire(ax, 7, 1, 7, 1.65)

    ax.text(1.4, 3, "AC Input", fontweight="bold", color=TEXT_COLOR)
    wire(ax, 2.4, 3, 3.65, 3)
    wire(ax, 7.35, 3, 8.5, 3)
    ax.text(8.7, 3, "DC Output", fontweight="bold", color=TEXT_COLOR)

    return save_figure(fig)


def zener_regulator():
    fig, ax = make_figure()
    title(fig, "Zener Voltage Regulator", "Maintains an approximately constant output voltage")

    battery(ax, 1.5, 3.5, "Vin")
    wire(ax, 1.5, 4.1, 3, 4.1)
    resistor(ax, 3.5, 4.1, "Rs")
    wire(ax, 3.95, 4.1, 6, 4.1)
    node_dot(ax, 6, 4.1)

    diode(ax, 6, 2.5, "Zener", vertical=True)
    wire(ax, 6, 4.1, 6, 2.95)
    wire(ax, 6, 2.05, 6, 1)
    ground(ax, 6, 1)

    wire(ax, 6, 4.1, 8.5, 4.1)
    ax.text(8.65, 4.1, "Vout (Vz)", fontsize=12, color=TEXT_COLOR, fontweight="bold")

    return save_figure(fig)


def transistor_switch():
    fig, ax = make_figure()
    title(fig, "Transistor Switch", "Transistor used as an electronic ON/OFF switch")

    ax.text(0.7, 3.5, "Control (Vin)", fontweight="bold", color=TEXT_COLOR)
    wire(ax, 2.1, 3.5, 3.2, 3.5)
    resistor(ax, 3.7, 3.5, "RB")
    wire(ax, 4.2, 3.5, 4.8, 3.5)

    npn_transistor(ax, 5.4, 3.5, "Q1 Switch")

    # Load connected to VCC
    wire(ax, 5.65, 4.2, 5.65, 4.8)
    resistor(ax, 5.65, 5.25, "LOAD", vertical=True)
    wire(ax, 5.65, 5.7, 8.0, 5.7)
    ax.text(8.2, 5.7, "+VCC", color=BATTERY_COLOR, fontweight="bold")

    # Emitter Ground
    wire(ax, 5.65, 2.8, 5.65, 2.0)
    ground(ax, 5.65, 2.0)

    caption(ax, 6, 1.0, "Transistor operates between Cutoff (OFF) and Saturation (ON)")

    return save_figure(fig)


def timer_555():
    fig, ax = make_figure()
    title(fig, "555 Timer Astable Oscillator", "Generates a continuous square wave")

    ic_chip(ax, 6.0, 3.2, 3.2, 2.4, "NE555 Timer")

    # Power rail
    wire(ax, 1.5, 5.2, 8.5, 5.2)
    ax.text(1.2, 5.2, "+VCC", color=BATTERY_COLOR, fontweight="bold", ha="right", va="center")

    # Timing network
    resistor(ax, 3.0, 4.4, "RA", vertical=True)
    resistor(ax, 3.0, 3.0, "RB", vertical=True)
    capacitor(ax, 3.0, 1.6, "C", vertical=True)

    wire(ax, 3.0, 5.2, 3.0, 4.85)
    wire(ax, 3.0, 3.95, 3.0, 3.45)
    wire(ax, 3.0, 2.55, 3.0, 1.72)
    wire(ax, 3.0, 1.48, 3.0, 1.0)
    ground(ax, 3.0, 1.0)

    # Connections to 555 pins
    node_dot(ax, 3.0, 4.2)
    wire(ax, 3.0, 4.2, 4.4, 4.2)
    ax.text(4.5, 4.2, "Pin 7 (DIS)", color=MUTED_TEXT, fontsize=8.5, va="center")

    node_dot(ax, 3.0, 2.7)
    wire(ax, 3.0, 2.7, 4.4, 2.7)
    ax.text(4.5, 2.7, "Pin 2/6 (TRIG/THR)", color=MUTED_TEXT, fontsize=8.5, va="center")

    # Output Pin 3
    wire(ax, 7.6, 3.2, 9.5, 3.2)
    ax.text(9.7, 3.2, "Square Wave Output", fontsize=11, fontweight="bold", color=TEXT_COLOR, va="center")

    return save_figure(fig)


# =====================================================
# SMART SYSTEMS (FULL COMPONENT SCHEMATICS)
# =====================================================

def street_light():
    fig, ax = make_figure()
    title(fig, "Automatic Street Light Schematic",
          "LDR & Resistor divider drives NPN Transistor to switch Street Lamp")

    # 9V Rail
    wire(ax, 1.5, 5.2, 9.5, 5.2)
    ax.text(1.2, 5.2, "+9V VCC", color=BATTERY_COLOR, fontweight="bold", ha="right", va="center")

    # Voltage Divider: R1 (top) and LDR (bottom)
    resistor(ax, 3.0, 4.4, "R1 (10kΩ)", vertical=True)
    ldr_sensor(ax, 3.0, 2.6, "LDR")

    wire(ax, 3.0, 5.2, 3.0, 4.85)
    wire(ax, 3.0, 3.95, 3.0, 3.05)
    node_dot(ax, 3.0, 3.5)

    wire(ax, 3.0, 2.15, 3.0, 1.4)
    ground(ax, 3.0, 1.4)

    # Base connection to NPN Transistor
    wire(ax, 3.0, 3.5, 4.2, 3.5)
    resistor(ax, 4.7, 3.5, "RB (1kΩ)")
    wire(ax, 5.25, 3.5, 5.6, 3.5)

    npn_transistor(ax, 6.2, 3.5, "Q1 (BC547)")

    # Emitter to ground
    wire(ax, 6.45, 2.8, 6.45, 1.4)
    ground(ax, 6.45, 1.4)

    # Collector Load: Relay / Street Lamp
    wire(ax, 6.45, 4.2, 6.45, 4.4)
    relay_module(ax, 6.45, 4.8, "Relay Switch")
    wire(ax, 6.45, 5.2, 6.45, 5.2)

    # Street Lamp connected via relay contacts
    wire(ax, 7.1, 4.8, 8.5, 4.8)
    led(ax, 9.0, 4.8, "Street Lamp")
    wire(ax, 9.35, 4.8, 9.8, 4.8)
    wire(ax, 9.8, 4.8, 9.8, 1.4)
    ground(ax, 9.8, 1.4)

    caption(ax, 6.0, 0.6, "In darkness, LDR resistance increases → Base voltage rises → Q1 turns ON → Relay activates Lamp")

    return save_figure(fig)


def fire_detection():
    fig, ax = make_figure()
    title(fig, "Educational Fire Detection Circuit Schematic",
          "NTC Thermistor sensor drives Transistor switch to activate Buzzer and Warning LED")

    # +5V Rail
    wire(ax, 1.5, 5.2, 9.5, 5.2)
    ax.text(1.2, 5.2, "+5V VCC", color=BATTERY_COLOR, fontweight="bold", ha="right", va="center")

    # Thermistor Sensor Divider
    thermistor_sensor(ax, 3.0, 4.4, "NTC Thermistor")
    resistor(ax, 3.0, 2.6, "R1 (10kΩ)", vertical=True)

    wire(ax, 3.0, 5.2, 3.0, 4.85)
    wire(ax, 3.0, 3.95, 3.0, 3.05)
    node_dot(ax, 3.0, 3.5)

    wire(ax, 3.0, 2.15, 3.0, 1.4)
    ground(ax, 3.0, 1.4)

    # Base connection
    wire(ax, 3.0, 3.5, 4.2, 3.5)
    resistor(ax, 4.7, 3.5, "RB (1kΩ)")
    wire(ax, 5.15, 3.5, 5.5, 3.5)

    npn_transistor(ax, 6.1, 3.5, "Q1 Transistor")

    # Emitter to ground
    wire(ax, 6.35, 2.8, 6.35, 1.4)
    ground(ax, 6.35, 1.4)

    # Collector loads (Buzzer & Red LED in parallel)
    wire(ax, 6.35, 4.2, 6.35, 4.5)
    node_dot(ax, 6.35, 4.5)

    # Branch 1: Buzzer
    wire(ax, 6.35, 4.5, 7.5, 4.5)
    buzzer(ax, 7.5, 3.7, "Buzzer")
    wire(ax, 7.5, 4.5, 7.5, 5.2)

    # Branch 2: Warning LED
    wire(ax, 6.35, 4.5, 9.0, 4.5)
    resistor(ax, 9.0, 3.7, "220Ω", vertical=True)
    wire(ax, 9.0, 3.25, 9.0, 2.8)
    led(ax, 9.0, 2.4, "Red LED", vertical=True)
    wire(ax, 9.0, 2.0, 9.0, 1.4)
    ground(ax, 9.0, 1.4)

    caption(ax, 6.0, 0.6, "Heat drops NTC resistance → Voltage rises → Transistor turns ON → Buzzer & LED trigger", weight="bold")

    return save_figure(fig)


def security_alarm():
    fig, ax = make_figure()
    title(fig, "Security Emergency Alarm Circuit Schematic",
          "Sensor Switch triggers 555 Timer Latch to sound Alarm Buzzer")

    # Power line
    wire(ax, 1.0, 5.2, 9.5, 5.2)
    ax.text(0.8, 5.2, "+9V VCC", color=BATTERY_COLOR, fontweight="bold", ha="right", va="center")

    # Trigger Switch & Pull-up resistor
    resistor(ax, 2.5, 4.3, "R_pullup (10kΩ)", vertical=True)
    wire(ax, 2.5, 5.2, 2.5, 4.75)
    wire(ax, 2.5, 3.85, 2.5, 3.5)
    node_dot(ax, 2.5, 3.5)

    switch_spst(ax, 2.5, 2.6, "Trigger Switch")
    wire(ax, 2.5, 2.2, 2.5, 1.4)
    ground(ax, 2.5, 1.4)

    # IC 555 Timer Monostable / Latch
    ic_chip(ax, 5.5, 3.5, 3.0, 2.4, "NE555 Alarm Timer")

    wire(ax, 2.5, 3.5, 4.0, 3.5)
    ax.text(4.1, 3.5, "Pin 2 (TRIG)", color=MUTED_TEXT, fontsize=8.5, va="center")

    # Pin 3 Output to Transistor Switch
    wire(ax, 7.0, 3.5, 7.6, 3.5)
    resistor(ax, 8.0, 3.5, "1kΩ")
    wire(ax, 8.45, 3.5, 8.7, 3.5)

    npn_transistor(ax, 9.3, 3.5, "Q1 Driver")
    wire(ax, 9.55, 2.8, 9.55, 1.4)
    ground(ax, 9.55, 1.4)

    # Alarm Buzzer on Collector
    wire(ax, 9.55, 4.2, 9.55, 4.6)
    buzzer(ax, 9.55, 4.8, "Alarm Siren")
    wire(ax, 9.55, 5.2, 9.55, 5.2)

    caption(ax, 6.0, 0.6, "Opening/closing sensor triggers 555 timer output pin HIGH to activate Alarm Siren")

    return save_figure(fig)


def temperature_fan():
    fig, ax = make_figure()
    title(fig, "Temperature Controlled Fan Schematic",
          "NTC Thermistor circuit drives MOSFET / Transistor to power DC Cooling Fan")

    wire(ax, 1.5, 5.2, 9.5, 5.2)
    ax.text(1.2, 5.2, "+12V VCC", color=BATTERY_COLOR, fontweight="bold", ha="right", va="center")

    # Sensor divider
    thermistor_sensor(ax, 3.0, 4.4, "NTC Temp Sensor")
    resistor(ax, 3.0, 2.6, "R_set (10kΩ)", vertical=True)

    wire(ax, 3.0, 5.2, 3.0, 4.85)
    wire(ax, 3.0, 3.95, 3.0, 3.05)
    node_dot(ax, 3.0, 3.5)

    wire(ax, 3.0, 2.15, 3.0, 1.4)
    ground(ax, 3.0, 1.4)

    # Drive Gate / Base
    wire(ax, 3.0, 3.5, 4.5, 3.5)
    resistor(ax, 5.0, 3.5, "1kΩ")
    wire(ax, 5.45, 3.5, 6.0, 3.5)

    npn_transistor(ax, 6.6, 3.5, "Q1 (Power NPN/MOSFET)")
    wire(ax, 6.85, 2.8, 6.85, 1.4)
    ground(ax, 6.85, 1.4)

    # DC Motor Load
    wire(ax, 6.85, 4.2, 6.85, 4.4)
    ax.add_patch(Circle((6.85, 4.7), 0.4, fill=True, facecolor=BLOCK_FILL, edgecolor=WIRE_COLOR, linewidth=2))
    ax.text(6.85, 4.7, "FAN\nMotor", ha="center", va="center", color=TEXT_COLOR, fontsize=8.5, fontweight="bold")
    wire(ax, 6.85, 5.1, 6.85, 5.2)

    # Flyback protection diode across motor
    wire(ax, 8.2, 4.3, 8.2, 5.2)
    node_dot(ax, 8.2, 5.2)
    diode(ax, 8.2, 4.7, "D1 Flyback", vertical=True)
    wire(ax, 8.2, 4.3, 6.85, 4.3)
    node_dot(ax, 6.85, 4.3)

    caption(ax, 6.0, 0.6, "As temperature rises, NTC resistance drops → Gate voltage turns ON MOSFET → Fan spins")

    return save_figure(fig)


def battery_charger():
    fig, ax = make_figure()
    title(fig, "12V Lead-Acid / Li-Ion Battery Charger Schematic",
          "Voltage Regulator LM317 configured for Constant Voltage / Current Limiting")

    # Input DC Voltage
    battery(ax, 1.5, 3.5, "18V DC Input")
    wire(ax, 1.5, 4.1, 1.5, 5.0)
    wire(ax, 1.5, 5.0, 3.5, 5.0)
    wire(ax, 1.5, 2.9, 1.5, 1.4)
    ground(ax, 1.5, 1.4)

    # LM317 Voltage Regulator IC
    ic_chip(ax, 5.0, 5.0, 2.5, 1.4, "LM317 Regulator")

    # Current Sense / Voltage set resistor
    wire(ax, 6.25, 5.0, 7.2, 5.0)
    resistor(ax, 7.7, 5.0, "R_sense (0.8Ω)")
    wire(ax, 8.15, 5.0, 9.2, 5.0)

    # Battery output
    wire(ax, 9.2, 5.0, 9.2, 4.2)
    battery(ax, 9.2, 3.5, "12V Battery")
    wire(ax, 9.2, 2.9, 9.2, 1.4)
    ground(ax, 9.2, 1.4)

    # Protection Diode
    diode(ax, 6.8, 3.7, "D1 Protect", color=DIODE_COLOR)
    wire(ax, 5.0, 4.3, 5.0, 3.7)
    wire(ax, 5.0, 3.7, 6.45, 3.7)
    wire(ax, 7.15, 3.7, 9.2, 3.7)
    node_dot(ax, 9.2, 3.7)

    caption(ax, 6.0, 0.6, "LM317 regulates charging voltage & limits current to safely charge the 12V battery")

    return save_figure(fig)


def walkie_talkie():
    """RF Transceiver block schematic diagram."""
    fig, ax = make_figure(width=12, height=6.5)
    title(fig, "Walkie-Talkie Transceiver Schematic",
          "RF Stage, Transmit/Receive Paths, and Shared Antenna")

    # Microphone input stage
    ax.add_patch(Circle((1.0, 4.75), 0.35, fill=True, facecolor=BLOCK_FILL, edgecolor=TEXT_COLOR, linewidth=2))
    ax.text(1.0, 4.75, "MIC", ha="center", va="center", color=TEXT_COLOR, fontsize=9, fontweight="bold")
    wire(ax, 1.35, 4.75, 2.0, 4.75)
    ic_chip(ax, 3.0, 4.75, 1.8, 1.1, "Audio Amp")

    # Transmit RF IC
    wire(ax, 3.9, 4.75, 4.8, 4.75)
    ic_chip(ax, 5.7, 4.75, 1.8, 1.1, "RF TX Stage")

    # Antenna (Shared)
    wire(ax, 6.6, 4.75, 8.0, 4.75)
    wire(ax, 8.0, 4.75, 8.0, 3.5)

    # Antenna triangle symbol
    polygon = Polygon([[8.0, 3.5], [7.7, 4.2], [8.3, 4.2]], closed=True, color=BATTERY_COLOR)
    ax.add_patch(polygon)
    ax.text(8.0, 4.4, "ANT", color=BATTERY_COLOR, fontweight="bold", ha="center")

    # Receive RF IC & Speaker
    wire(ax, 8.0, 3.5, 8.0, 2.0)
    wire(ax, 8.0, 2.0, 6.6, 2.0)
    ic_chip(ax, 5.7, 2.0, 1.8, 1.1, "RF RX Stage")

    wire(ax, 4.8, 2.0, 3.9, 2.0)
    ic_chip(ax, 3.0, 2.0, 1.8, 1.1, "Audio Amp")

    wire(ax, 2.1, 2.0, 1.4, 2.0)
    # Speaker symbol
    ax.add_patch(Rectangle((0.8, 1.65), 0.6, 0.7, fill=True, facecolor=BLOCK_FILL, edgecolor=TEXT_COLOR, linewidth=2))
    ax.text(1.1, 2.0, "SPK", ha="center", va="center", color=TEXT_COLOR, fontsize=9, fontweight="bold")

    # PTT Switch
    switch_spst(ax, 5.7, 3.3, "PTT Switch")

    caption(ax, 6.0, 0.65, "PTT Switch toggles RF paths between Transmit (top) and Receive (bottom)")

    return save_figure(fig)


# =====================================================
# GENERIC DIAGRAM (fallback)
# =====================================================

def generic_system(result):
    fig, ax = make_figure()
    title(fig, result.get("device_name", "Electronic Circuit"))

    components = result.get("components", [])

    if not components:
        battery(ax, 2.0, 3.0, "VCC")
        wire(ax, 2.0, 3.6, 5.0, 3.6)
        resistor(ax, 5.5, 3.6, "R")
        wire(ax, 5.95, 3.6, 8.5, 3.6)
        ground(ax, 8.5, 2.0)
        return save_figure(fig)

    battery(ax, 1.5, 3.0, "VCC")
    wire(ax, 1.5, 3.6, 3.0, 3.6)

    max_items = min(len(components), 4)
    start_x = 3.5
    spacing = 1.8

    for i in range(max_items):
        comp = components[i]
        c_type = str(comp.get("type") or comp.get("name") or "").lower()
        c_val = str(comp.get("value") or "")
        curr_x = start_x + i * spacing

        if "led" in c_type:
            led(ax, curr_x, 3.6, label=c_val or "LED")
        elif "diode" in c_type:
            diode(ax, curr_x, 3.6, label=c_val or "D")
        elif "cap" in c_type:
            capacitor(ax, curr_x, 3.6, label=c_val or "C")
        else:
            resistor(ax, curr_x, 3.6, label=c_val or "R")

        if i < max_items - 1:
            wire(ax, curr_x + 0.45, 3.6, curr_x + spacing - 0.45, 3.6)

    wire(ax, start_x + (max_items - 1) * spacing + 0.45, 3.6, 9.5, 3.6)
    wire(ax, 9.5, 3.6, 9.5, 2.0)
    ground(ax, 9.5, 2.0)

    return save_figure(fig)


# =====================================================
# MAIN DISPATCHER
# =====================================================

_GENERATORS = {
    "led": led_circuit,
    "voltage_divider": voltage_divider,
    "rc_filter": rc_filter,
    "rl_circuit": rl_circuit,
    "rlc_circuit": rlc_circuit,
    "common_emitter": common_emitter,
    "opamp": opamp,
    "bridge_rectifier": bridge_rectifier,
    "zener_regulator": zener_regulator,
    "transistor_switch": transistor_switch,
    "555_timer": timer_555,
    "fire_detection": fire_detection,
    "security_alarm": security_alarm,
    "street_light": street_light,
    "temperature_fan": temperature_fan,
    "battery_charger": battery_charger,
    "walkie_talkie": walkie_talkie,
}


def generate_circuit(template, result=None):
    generator = _GENERATORS.get(template)

    if generator:
        return generator()

    return generic_system(result or {})