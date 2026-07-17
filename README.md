# 🔐 QuBit Guard

An interactive desktop simulator for the **BB84 Quantum Key Distribution protocol**.
Watch photons travel from Alice to Bob, toggle an eavesdropper (Eve) on/off, and
see quantum mechanics detect interception in real time.

## Features
- Animated photon visualization across the quantum channel
- Step-by-step mode to walk through each qubit manually
- Color-coded basis comparison table
- Live error-rate chart with detection threshold
- History tab tracking error rates across multiple runs
- Built-in "Learn" tab explaining the protocol in plain English

## Setup
```bash
pip install -r requirements.txt
python gui_app.py
```

## Files
- `bb84.py` — core BB84 protocol engine
- `polarization.py` — converts bits/bases into arrow icons and colors
- `gui_app.py` — the CustomTkinter desktop app
