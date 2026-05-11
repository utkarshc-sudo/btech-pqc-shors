# Project Plan: Bridging the Quantum Threat and Post-Quantum Defense

## Overview

**Title**: Bridging the Quantum Threat and Post-Quantum Defense: An Empirical Study of Shor's Algorithm on Real Quantum Hardware and ML-KEM-768 Performance

**Duration**: 12 weeks (BTech Project-I)

**Objective**: Demonstrate both halves of the quantum cryptography story — (1) the concrete threat via Shor's algorithm on IBM Quantum hardware, and (2) the practical defense cost via ML-KEM-768 benchmarks — then synthesize the gap and migration implications.

---

## Phase 1: The Quantum Threat (Weeks 1–7)

### Week 1 — Qiskit Setup and Quantum Basics
- Verify Qiskit installation, simulator, and IBM Quantum account access
- Learn qubit, gate, and measurement basics hands-on
- Build and run a Bell state circuit (demonstrate entanglement)
- **Deliverable**: Working Bell state notebook cell, CONCEPTS.md updated with qubits/gates/entanglement

### Week 2 — Quantum Fourier Transform (QFT)
- Build QFT from scratch (Hadamard + controlled-rotation decomposition)
- Verify against Qiskit's built-in QFT for n=3, n=4 qubits
- Understand why QFT is the heart of Shor's period-finding
- **Deliverable**: QFT implementation in `src/shors/circuit.py`, correctness tests

### Week 3 — Shor's Algorithm for N=15 (Simulator)
- Implement modular exponentiation circuit for a=7, N=15
- Build the full Shor's circuit: Hadamard → controlled-U → inverse QFT → measure
- Classical post-processing: continued fractions to extract period r=4
- Factor: gcd(7^2 ± 1, 15) = {3, 5}
- Run on Aer simulator with 1024+ shots, verify success rate
- **Deliverable**: `src/shors/circuit.py`, `src/shors/classical.py`, `src/shors/run_simulator.py`, pytest tests

### Week 4 — Shor's on IBM Quantum Hardware (N=15)
- Submit the N=15 circuit to a real IBM Quantum backend
- Run 100+ shots, analyze success rate vs. simulator
- Document noise effects: decoherence, gate errors, measurement errors
- **Deliverable**: `src/shors/run_hardware.py`, raw results in `results/raw/`, success rate analysis

### Week 5 — Shor's for N=21 (Expected Failure)
- Attempt N=21 (a=2, r=6) on hardware
- Circuit requires more qubits and deeper depth → noise dominates
- Document why it fails: qubit count, circuit depth, error rates
- Compare simulator (should work) vs. hardware (should fail or degrade significantly)
- **Deliverable**: N=21 results, noise analysis, comparison plots

### Week 6 — Resource Extrapolation for RSA-2048
- Cite Gidney & Ekerå (2021): ~20 million noisy qubits, ~8 hours for RSA-2048
- Compare with current IBM hardware capabilities (~1000+ qubits, high error rates)
- Estimate the gap: orders of magnitude in qubit count and error correction
- Discuss quantum error correction overhead (surface codes)
- **Deliverable**: Extrapolation analysis in notebook, figures for report

### Week 7 — Half 1 Report Draft
- Write report sections: Introduction, Background, Shor's Threat Analysis
- Generate all Phase 1 figures from raw data
- Peer review and revisions
- **Deliverable**: `report/01_introduction.md` through `report/03_threat_shors.md`, figures

---

## Phase 2: The Post-Quantum Defense (Weeks 8–10)

### Week 8 — ML-KEM Setup and Verification
- Verify liboqs-python installation with ML-KEM-768
- Run keygen → encapsulate → decapsulate cycle
- Verify against NIST Known Answer Tests (KAT) if available
- Understand MLWE hardness assumption at a conceptual level
- **Deliverable**: Working ML-KEM hello-world, CONCEPTS.md updated with lattice/MLWE section

### Week 9 — Benchmark Harness
- Build systematic benchmark for ML-KEM-512, ML-KEM-768, ML-KEM-1024
- Baseline comparison against X25519 (ECDH) using `cryptography` library
- Measure: keygen time, encapsulate time, decapsulate time
- Measure: public key size, ciphertext size, shared secret size
- 10,000+ iterations per operation for statistical significance
- **Deliverable**: `src/mlkem/benchmark.py`, `src/mlkem/compare_x25519.py`, raw CSVs

### Week 10 — Comparative Analysis
- Statistical analysis: mean, median, p95, p99, standard deviation
- Distribution plots (histograms, box plots) for each operation
- Size comparison tables
- Performance ratio: ML-KEM-768 vs. X25519
- **Deliverable**: `src/analysis/plots.py`, `src/analysis/stats.py`, all benchmark figures

---

## Phase 3: Synthesis and Delivery (Weeks 11–12)

### Week 11 — Synthesis
- Connect threat (how close is RSA-2048 to being broken?) with defense (what does ML-KEM cost?)
- Key argument: PQC overhead is modest (2-5x in time, larger keys), while the quantum threat is approaching
- "Migrate now" argument: crypto agility, NIST timeline, harvest-now-decrypt-later attacks
- **Deliverable**: `report/05_synthesis.md`, synthesis figures

### Week 12 — Final Polish
- Complete all report sections including conclusion and future work
- Final figure quality pass
- Presentation slides for viva
- Ensure full reproducibility (clean clone → make install → run everything)
- **Deliverable**: Complete report, presentation slides, final commit

---

## Scope Exclusions (Future Work)

The following are explicitly out of scope and will be listed as future work in the report:
- TLS integration testing
- Post-quantum signatures (ML-DSA, SLH-DSA)
- Other PQC families (HQC, BIKE, Classic McEliece)
- Full quantum error correction implementation
- Shor's algorithm for N > 21 (unless N=21 succeeds on hardware)

---

## Key References

- Shor, P. (1994). Algorithms for quantum computation.
- Gidney, C. & Ekerå, M. (2021). How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits.
- NIST FIPS 203 (2024). ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism).
- IBM Quantum. (2024-2025). Hardware specifications and Qiskit documentation.
