"""
QuBit Guard — Polarization Icon Helper
Converts (bit, basis) pairs into human-readable arrow symbols and colors,
so users can *see* photon polarization instead of just '+' / 'x' text.
"""

# Rectilinear basis (+): bit 0 = horizontal, bit 1 = vertical
# Diagonal basis (x): bit 0 = / (45°), bit 1 = \ (135°)
ICONS = {
    ("+", 0): "↔",
    ("+", 1): "↕",
    ("x", 0): "↗",
    ("x", 1): "↖",
}

BIT_COLORS = {0: "#2563eb", 1: "#ea580c"}   # blue for 0, orange for 1
BASIS_LABEL = {"+": "Rectilinear (+)", "x": "Diagonal (x)"}


def icon_for(basis, bit):
    if basis is None or bit is None:
        return "—"
    return ICONS.get((basis, bit), "?")


def color_for(bit):
    if bit is None:
        return "#9ca3af"
    return BIT_COLORS.get(bit, "#9ca3af")


def basis_label(basis):
    return BASIS_LABEL.get(basis, "—")