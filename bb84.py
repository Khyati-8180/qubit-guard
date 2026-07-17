"""
QuBit Guard — Core BB84 Protocol Engine
Handles bit/basis generation, quantum measurement simulation, eavesdropper logic,
and returns rich per-qubit detail for visualization.
"""
import random

BASES = ['+', 'x']


def generate_bits(n):
    return [random.randint(0, 1) for _ in range(n)]


def generate_bases(n):
    return [random.choice(BASES) for _ in range(n)]


def measure(bit, sent_base, measure_base):
    """If bases match, the correct bit is read.
    If bases mismatch, the result is random - this is the quantum uncertainty
    that makes eavesdropping detectable."""
    if sent_base == measure_base:
        return bit
    return random.randint(0, 1)


def run_bb84(n=16, eve_present=False, eve_intercept_prob=1.0):
    """
    Runs a full BB84 round and returns a rich result dictionary, including a
    per-qubit breakdown (self.qubits) used for animation and table rendering.
    """
    alice_bits = generate_bits(n)
    alice_bases = generate_bases(n)
    bob_bases = generate_bases(n)

    eve_bases = [None] * n
    eve_bits = [None] * n
    bits_after_eve = list(alice_bits)
    bases_seen_by_bob_input = list(alice_bases)

    if eve_present:
        for i in range(n):
            if random.random() < eve_intercept_prob:
                e_base = random.choice(BASES)
                eve_bases[i] = e_base
                eve_bit = measure(alice_bits[i], alice_bases[i], e_base)
                eve_bits[i] = eve_bit
                bits_after_eve[i] = eve_bit
                bases_seen_by_bob_input[i] = e_base

    bob_measurements = [
        measure(bits_after_eve[i], bases_seen_by_bob_input[i], bob_bases[i])
        for i in range(n)
    ]

    qubits = []
    matching_indices = []
    alice_key, bob_key = [], []
    errors = 0

    for i in range(n):
        bases_match = alice_bases[i] == bob_bases[i]
        in_key = bases_match
        mismatch = False

        if in_key:
            matching_indices.append(i)
            alice_key.append(alice_bits[i])
            bob_key.append(bob_measurements[i])
            if alice_bits[i] != bob_measurements[i]:
                mismatch = True
                errors += 1

        qubits.append({
            "index": i,
            "alice_bit": alice_bits[i],
            "alice_basis": alice_bases[i],
            "eve_present_here": eve_bases[i] is not None,
            "eve_basis": eve_bases[i],
            "eve_bit": eve_bits[i],
            "bob_basis": bob_bases[i],
            "bob_bit": bob_measurements[i],
            "bases_match": bases_match,
            "in_key": in_key,
            "mismatch": mismatch,
        })

    error_rate = (errors / len(alice_key) * 100) if alice_key else 0.0

    return {
        "n": n,
        "eve_present": eve_present,
        "qubits": qubits,
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_measurements": bob_measurements,
        "matching_indices": matching_indices,
        "alice_key": alice_key,
        "bob_key": bob_key,
        "errors": errors,
        "error_rate": error_rate,
        "eavesdropper_detected": error_rate > 10.0
    }


if __name__ == "__main__":
    result = run_bb84(n=8, eve_present=True)
    for q in result["qubits"]:
        print(q)
    print("Error Rate: {:.2f}%".format(result["error_rate"]))