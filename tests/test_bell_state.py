"""Tests for Week 1: Bell state circuit correctness."""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def run_circuit(qc, shots=4096):
    """Run a circuit on Aer simulator and return counts."""
    sim = AerSimulator()
    return sim.run(qc, shots=shots).result().get_counts()


def test_bell_phi_plus():
    """Bell |Phi+> should produce only |00> and |11>."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    counts = run_circuit(qc)

    assert "01" not in counts, f"Got unexpected |01>: {counts}"
    assert "10" not in counts, f"Got unexpected |10>: {counts}"
    assert "00" in counts
    assert "11" in counts

    total = sum(counts.values())
    ratio_00 = counts["00"] / total
    assert 0.4 < ratio_00 < 0.6, f"|00> fraction {ratio_00} outside [0.4, 0.6]"


def test_bell_psi_plus():
    """Bell |Psi+> should produce only |01> and |10>."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.x(1)
    qc.measure([0, 1], [0, 1])

    counts = run_circuit(qc)

    assert "00" not in counts, f"Got unexpected |00>: {counts}"
    assert "11" not in counts, f"Got unexpected |11>: {counts}"
    assert "01" in counts
    assert "10" in counts


def test_product_state_all_four_outcomes():
    """H on both qubits (no CNOT) should give all 4 outcomes ~25% each."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.h(1)
    qc.measure([0, 1], [0, 1])

    counts = run_circuit(qc, shots=8192)
    total = sum(counts.values())

    for outcome in ["00", "01", "10", "11"]:
        assert outcome in counts, f"Missing outcome |{outcome}>"
        ratio = counts[outcome] / total
        assert 0.20 < ratio < 0.30, f"|{outcome}> fraction {ratio} outside [0.20, 0.30]"
