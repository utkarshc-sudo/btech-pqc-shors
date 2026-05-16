"""Quantum circuits for Shor's algorithm.

Contains:
- QFT (Quantum Fourier Transform) and inverse QFT
- Controlled modular exponentiation gates
- Full Shor's circuit for factoring N
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


def qft_rotations(circuit, n):
    """Apply QFT rotations to the first n qubits of the circuit.

    The QFT decomposes into:
    1. Hadamard on qubit j
    2. Controlled-R_k rotations from qubit j, controlled by qubits j+1, ..., n-1
    3. Repeat for each qubit
    """
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        # Controlled rotation: R_k where k = n - qubit + 1
        k = n - qubit
        circuit.cp(np.pi / 2**k, qubit, n)
    qft_rotations(circuit, n)


def swap_registers(circuit, n):
    """Reverse the order of qubits (required at end of QFT)."""
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)
    return circuit


def qft_circuit(n):
    """Build a Quantum Fourier Transform circuit on n qubits.

    The QFT maps computational basis states to frequency basis states:
        |j⟩ → (1/√N) Σ_k  e^(2πi·j·k/N) |k⟩    where N = 2^n

    Args:
        n: Number of qubits.

    Returns:
        QuantumCircuit implementing the n-qubit QFT.
    """
    qc = QuantumCircuit(n, name=f"QFT_{n}")
    qft_rotations(qc, n)
    swap_registers(qc, n)
    return qc


def inverse_qft_circuit(n):
    """Build the inverse QFT circuit on n qubits.

    The inverse QFT is used in Shor's algorithm to convert the
    periodic state back into a measurable form.

    Args:
        n: Number of qubits.

    Returns:
        QuantumCircuit implementing the n-qubit inverse QFT.
    """
    qc = qft_circuit(n)
    inv_qc = qc.inverse()
    inv_qc.name = f"QFT†_{n}"
    return inv_qc


def _c_amod15(a, power):
    """Controlled multiplication by a mod 15, repeated 2^power times.

    For N=15, we hardcode the unitary for each valid base a.
    This is standard practice for small demonstrations of Shor's —
    the general modular exponentiation circuit would require many more gates.

    Valid values of a: 2, 4, 7, 8, 11, 13 (must be coprime to 15).

    Args:
        a: Base for modular exponentiation.
        power: The gate implements a^(2^power) mod 15.

    Returns:
        QuantumCircuit as a controlled gate.
    """
    assert a in [2, 4, 7, 8, 11, 13], f"a={a} not coprime to 15"
    U = QuantumCircuit(4, name=f"{a}^{2**power} mod 15")
    for _ in range(2**power):
        if a in [2, 13]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a in [7, 8]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [4, 11]:
            U.swap(1, 3)
            U.swap(0, 2)
        if a in [7, 11, 13]:
            for q in range(4):
                U.x(q)
    gate = U.to_gate()
    c_gate = gate.control(1)
    return c_gate


def _c_amod21(a, power):
    """Controlled multiplication by a mod 21, repeated 2^power times.

    For N=21, hardcoded unitaries for valid bases.

    Args:
        a: Base for modular exponentiation (must be coprime to 21).
        power: The gate implements a^(2^power) mod 21.

    Returns:
        QuantumCircuit as a controlled gate.
    """
    assert a in [2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20], \
        f"a={a} not coprime to 21"
    n_work = 5  # need 5 qubits to represent values up to 20
    U = QuantumCircuit(n_work, name=f"{a}^{2**power} mod 21")

    # Build the permutation matrix for x -> a*x mod 21
    # for the subspace {1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20}
    # We construct via repeated squaring of the base permutation
    val = pow(a, 2**power, 21)

    # Apply the permutation as a sequence of swaps and X gates
    # This is a simplified approach: we encode the permutation
    # as a unitary matrix and decompose it
    # For the demonstration, we use Qiskit's unitary simulator approach
    from qiskit.quantum_info import Operator

    # Build the 2^5 x 2^5 unitary for multiplication by val mod 21
    dim = 2**n_work
    mat = np.zeros((dim, dim), dtype=complex)
    for x in range(dim):
        if x < 21 and np.gcd(x, 21) == 1:
            # Map x -> (val * x) mod 21
            y = (val * x) % 21
            mat[y, x] = 1.0
        else:
            # Identity on states outside {0..20} coprime to 21
            mat[x, x] = 1.0

    U = QuantumCircuit(n_work, name=f"{a}^{2**power} mod 21")
    U.unitary(Operator(mat), range(n_work))
    gate = U.to_gate()
    c_gate = gate.control(1)
    return c_gate


def shors_circuit(N, a, n_count=None):
    """Build the full Shor's algorithm circuit for factoring N.

    Circuit structure:
    1. Counting register: n_count qubits, initialized to |0⟩, Hadamard applied
    2. Work register: enough qubits to represent values mod N
    3. Controlled modular exponentiation: a^(2^j) mod N for each counting qubit j
    4. Inverse QFT on counting register
    5. Measure counting register

    Args:
        N: Number to factor (15 or 21).
        a: Base for modular exponentiation (must be coprime to N).
        n_count: Number of counting qubits. Defaults to 2*ceil(log2(N)).

    Returns:
        QuantumCircuit for Shor's algorithm.
    """
    # Determine qubit counts
    n_work = int(np.ceil(np.log2(N)))
    if N == 15:
        n_work = 4  # need 4 qubits for mod 15
    elif N == 21:
        n_work = 5  # need 5 qubits for mod 21

    if n_count is None:
        n_count = 2 * n_work  # standard: 2n counting qubits for n-bit N

    # Create registers
    counting = QuantumRegister(n_count, name='count')
    work = QuantumRegister(n_work, name='work')
    classical = ClassicalRegister(n_count, name='meas')
    qc = QuantumCircuit(counting, work, classical,
                        name=f"Shor(N={N}, a={a})")

    # Initialize work register to |1⟩ (set qubit 0)
    qc.x(work[0])

    # Apply Hadamard to all counting qubits (create superposition)
    for q in range(n_count):
        qc.h(counting[q])

    # Controlled modular exponentiation
    for q in range(n_count):
        if N == 15:
            c_gate = _c_amod15(a, q)
        elif N == 21:
            c_gate = _c_amod21(a, q)
        else:
            raise ValueError(f"N={N} not supported (only 15 and 21)")
        qc.append(c_gate, [counting[q]] + list(work))

    # Apply inverse QFT to counting register
    iqft = inverse_qft_circuit(n_count)
    qc.append(iqft, counting)

    # Measure counting register
    qc.measure(counting, classical)

    return qc
