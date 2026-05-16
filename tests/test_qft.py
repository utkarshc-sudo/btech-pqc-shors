"""Tests for QFT circuit correctness."""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import QFT as QiskitQFT

from src.shors.circuit import qft_circuit


class TestQFT:
    def test_qft_3_matches_qiskit(self):
        """Our 3-qubit QFT should produce the same state as Qiskit's QFT."""
        n = 3
        our_qft = qft_circuit(n)
        qiskit_qft = QiskitQFT(n)

        # Test on several input states
        for input_val in range(2**n):
            # Prepare input state |input_val⟩
            init_ours = QuantumCircuit(n)
            init_qiskit = QuantumCircuit(n)
            for bit in range(n):
                if (input_val >> bit) & 1:
                    init_ours.x(bit)
                    init_qiskit.x(bit)

            init_ours.compose(our_qft, inplace=True)
            init_qiskit.compose(qiskit_qft, inplace=True)

            sv_ours = Statevector.from_instruction(init_ours)
            sv_qiskit = Statevector.from_instruction(init_qiskit)

            # States should be equivalent (up to global phase)
            fidelity = abs(sv_ours.inner(sv_qiskit))**2
            assert fidelity > 0.999, (
                f"QFT mismatch for input |{input_val}⟩: fidelity={fidelity:.6f}"
            )

    def test_qft_4_matches_qiskit(self):
        """Our 4-qubit QFT should match Qiskit's."""
        n = 4
        our_qft = qft_circuit(n)
        qiskit_qft = QiskitQFT(n)

        for input_val in [0, 1, 5, 10, 15]:
            init_ours = QuantumCircuit(n)
            init_qiskit = QuantumCircuit(n)
            for bit in range(n):
                if (input_val >> bit) & 1:
                    init_ours.x(bit)
                    init_qiskit.x(bit)

            init_ours.compose(our_qft, inplace=True)
            init_qiskit.compose(qiskit_qft, inplace=True)

            sv_ours = Statevector.from_instruction(init_ours)
            sv_qiskit = Statevector.from_instruction(init_qiskit)

            fidelity = abs(sv_ours.inner(sv_qiskit))**2
            assert fidelity > 0.999, (
                f"QFT-4 mismatch for |{input_val}⟩: fidelity={fidelity:.6f}"
            )

    def test_qft_on_uniform_superposition(self):
        """QFT of uniform superposition |+...+⟩ should give |0...0⟩."""
        n = 3
        qc = QuantumCircuit(n)
        for i in range(n):
            qc.h(i)  # create uniform superposition
        qc.compose(qft_circuit(n), inplace=True)

        sv = Statevector.from_instruction(qc)
        probs = sv.probabilities()

        # |0⟩ should have probability ~1
        assert probs[0] > 0.99, f"Expected |000⟩ with high prob, got {probs[0]:.4f}"


class TestShorsCircuitSimulator:
    def test_shors_n15_a7_finds_factors(self):
        """Shor's for N=15, a=7 should find factors 3×5 on simulator."""
        from src.shors.circuit import shors_circuit
        from src.shors.classical import process_shor_result
        from qiskit_aer import AerSimulator
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

        qc = shors_circuit(N=15, a=7, n_count=8)
        sim = AerSimulator()
        pm = generate_preset_pass_manager(backend=sim, optimization_level=1)
        qc_t = pm.run(qc)
        result = sim.run(qc_t, shots=2048).result()
        counts = result.get_counts()

        analysis = process_shor_result(counts, 8, 7, 15)
        assert analysis['factors_found'], (
            f"Failed to find factors of 15: {analysis}"
        )
        assert (3, 5) in analysis['factors_found']

    def test_shors_n15_a11_finds_factors(self):
        """Shor's for N=15, a=11 should also find factors."""
        from src.shors.circuit import shors_circuit
        from src.shors.classical import process_shor_result
        from qiskit_aer import AerSimulator
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

        qc = shors_circuit(N=15, a=11, n_count=8)
        sim = AerSimulator()
        pm = generate_preset_pass_manager(backend=sim, optimization_level=1)
        qc_t = pm.run(qc)
        result = sim.run(qc_t, shots=2048).result()
        counts = result.get_counts()

        analysis = process_shor_result(counts, 8, 11, 15)
        assert analysis['factors_found']
        assert (3, 5) in analysis['factors_found']
