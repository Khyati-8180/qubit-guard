"""
QuBit Guard — Attack Simulation Module
Compares clean vs. eavesdropped BB84 runs to demonstrate detection.
"""
import random
from bb84 import run_bb84

def compare_with_without_eve(n=20, trials=5):
    print("=" * 50)
    print("QUBIT GUARD — Comparison: With Eve vs Without Eve")
    print("=" * 50)

    for t in range(1, trials + 1):
        clean = run_bb84(n=n, eve_present=False)
        attacked = run_bb84(n=n, eve_present=True)

        print(f"\nTrial {t}")
        print(f"  No Eve   -> Error Rate: {clean['error_rate']:.2f}%  | Detected: {clean['eavesdropper_detected']}")
        print(f"  With Eve -> Error Rate: {attacked['error_rate']:.2f}%  | Detected: {attacked['eavesdropper_detected']}")


if __name__ == "__main__":
    compare_with_without_eve()