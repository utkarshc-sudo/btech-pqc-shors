# Concepts: Plain-English Guide

This document explains the core concepts behind this project in plain language. It will be expanded each week as we cover new material.

---

## 1. Qubits

A classical bit is either 0 or 1. A **qubit** (quantum bit) can be in a **superposition** — think of it as simultaneously being 0 and 1 with certain probabilities. When you measure a qubit, the superposition "collapses" and you get a definite 0 or 1, but the probabilities of each outcome are determined by the qubit's quantum state.

Mathematically, a qubit's state is written |ψ⟩ = α|0⟩ + β|1⟩, where α and β are complex numbers and |α|² + |β|² = 1. The probability of measuring 0 is |α|², and the probability of measuring 1 is |β|².

## 2. Superposition

**Superposition** means a qubit exists in a combination of states at once. The Hadamard gate (H) creates superposition from a definite state: it transforms |0⟩ into (|0⟩ + |1⟩)/√2, giving equal probability of measuring 0 or 1.

Why this matters: if you apply H to n qubits, you create a superposition of all 2ⁿ possible n-bit strings simultaneously. This is how quantum computers explore many possibilities "at once."

## 3. Entanglement

When two qubits are **entangled**, measuring one instantly determines the other, no matter how far apart they are. The classic example is the **Bell state**: (|00⟩ + |11⟩)/√2. If you measure the first qubit and get 0, the second is guaranteed to be 0 too.

Entanglement is not just a curiosity — it's a computational resource. Shor's algorithm relies on entanglement between the "input" register and the "output" register to create correlations that reveal the period of a function.

## 4. Quantum Interference

**Interference** is what makes quantum computing powerful. Just as waves can add up (constructive interference) or cancel out (destructive interference), quantum amplitudes can be arranged so that wrong answers cancel and correct answers reinforce.

The Quantum Fourier Transform uses interference to amplify states whose frequencies match the period we're looking for, while suppressing everything else.

## 5. Quantum Gates

Quantum computations are performed by applying **gates** to qubits. Key gates:
- **X gate**: Flips |0⟩ to |1⟩ and vice versa (quantum NOT)
- **H gate (Hadamard)**: Creates superposition
- **CNOT gate**: Flips the target qubit if the control qubit is |1⟩ (creates entanglement)
- **Controlled-U gates**: Apply operation U to a target only if the control qubit is |1⟩
- **Rotation gates (Rz, Rk)**: Rotate the phase of a qubit by a specific angle

## 6. Quantum Fourier Transform (QFT)

The **QFT** is the quantum version of the discrete Fourier transform. It converts a quantum state from the "time domain" to the "frequency domain." Given an input state that has a hidden periodicity, the QFT concentrates the probability amplitude onto states corresponding to that period.

The QFT on n qubits:
1. Apply H to the first qubit
2. Apply controlled-rotation gates from the first qubit to each subsequent qubit
3. Repeat for each qubit
4. Swap qubit order at the end

The QFT uses only O(n²) gates compared to O(n·2ⁿ) for the classical FFT — an exponential speedup.

## 7. Shor's Algorithm: Period-Finding Reduces Factoring

**The key insight**: Factoring a number N can be reduced to finding the **period** of a modular exponentiation function.

Step by step:
1. Pick a random a < N. If gcd(a, N) > 1, we found a factor (lucky!).
2. Find the **period r** of the function f(x) = aˣ mod N. This means find the smallest r such that a^r ≡ 1 (mod N).
3. If r is even, compute gcd(a^(r/2) ± 1, N). With high probability, this gives non-trivial factors.

**Example**: N=15, a=7
- f(x) = 7ˣ mod 15: f(0)=1, f(1)=7, f(2)=4, f(3)=13, f(4)=1, ... → period r=4
- r is even, so compute gcd(7² - 1, 15) = gcd(48, 15) = 3, and gcd(7² + 1, 15) = gcd(50, 15) = 5
- 15 = 3 × 5 ✓

**Why quantum helps**: Finding the period classically is hard (essentially as hard as factoring). But a quantum computer can find the period in polynomial time using the QFT to detect the periodicity in the superposition of f(x) values.

## 8. Why RSA Is Threatened

RSA security relies on the assumption that factoring large numbers (e.g., 2048-bit products of two primes) is computationally infeasible. Shor's algorithm factors in polynomial time on a quantum computer, breaking this assumption.

Current state: IBM's largest quantum processors have ~1000+ qubits, but with high error rates. Gidney & Ekerå (2021) estimate that factoring a 2048-bit RSA key requires ~20 million noisy qubits running for ~8 hours. We're not there yet, but the direction is clear.

## 9. Module Learning With Errors (MLWE)

*[To be expanded in Week 8]*

The **Learning With Errors (LWE)** problem is: given a system of approximate linear equations over a finite field, find the secret vector. "Approximate" means each equation has a small random error term added.

**Module-LWE (MLWE)** is a structured variant where the coefficients are elements of a polynomial ring, not just integers. This structure makes operations faster (using NTT — Number Theoretic Transform) while preserving hardness.

MLWE is believed to be hard for both classical and quantum computers. No known quantum algorithm solves it efficiently. This is the security foundation of ML-KEM.

## 10. ML-KEM (Module-Lattice-Based Key Encapsulation Mechanism)

*[To be expanded in Week 8]*

**ML-KEM** (formerly CRYSTALS-Kyber) is NIST's standardized post-quantum key encapsulation mechanism (FIPS 203, 2024). It provides:
- **Key Generation**: Create a public/private key pair
- **Encapsulation**: Using someone's public key, generate a shared secret and a ciphertext
- **Decapsulation**: Using the private key, recover the shared secret from the ciphertext

Three parameter sets: ML-KEM-512 (128-bit security), ML-KEM-768 (192-bit, recommended), ML-KEM-1024 (256-bit).

The trade-off vs. classical key exchange (e.g., X25519): ML-KEM keys and ciphertexts are larger (~1 KB vs. 32 bytes), and operations are slightly slower, but the security holds against quantum attacks.
