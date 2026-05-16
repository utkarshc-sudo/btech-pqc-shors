# Progress Log

## Project Info
- **Student**: BTech Project-I
- **Title**: Bridging the Quantum Threat and Post-Quantum Defense: An Empirical Study of Shor's Algorithm on Real Quantum Hardware and ML-KEM-768 Performance
- **GitHub**: utkarshc-sudo/btech-pqc-shors
- **Environment**: macOS ARM (Apple Silicon), Python 3.14.3, Homebrew

## Seven Non-Negotiable Constraints
1. **Pedagogy over speed** — explain concepts in plain language before coding; ask if user understands before proceeding.
2. **Reproducibility** — all deps pinned in requirements.txt; README must work on fresh clone.
3. **Never commit secrets** — .env gitignored, token read via dotenv, never logged/echoed/asked in chat.
4. **Hardware quota** — print estimated qubit/shot cost and require explicit "run on hardware" before IBM Quantum jobs.
5. **Commit discipline** — propose commit message + git status, never auto-commit/push.
6. **Test what's testable** — pytest for classical logic, Aer simulator for quantum correctness.
7. **No fabricated results** — no placeholder numbers in reports.

## Environment Setup Notes
- liboqs Homebrew formula only installs static library (.a), not shared (.dylib)
- **Workaround**: built liboqs 0.15.0 from source with `-DBUILD_SHARED_LIBS=ON`, installed to `~/.local/lib/`
- Must set `DYLD_LIBRARY_PATH=$HOME/.local/lib` for liboqs-python to find the shared lib
- Makefile exports this automatically; direct `python3` invocations need the export
- liboqs-python 0.14.1 vs liboqs 0.15.0 minor version mismatch warning is harmless
- `pylatexenc` was added as an extra dependency for Qiskit circuit visualization

## Completed Work

### Scaffolding (2026-05-11)
- Commit: `f053a51` — "Initial project scaffolding with reproducible environment"
- Created: .gitignore, .env.example, .env (gitignored), full directory structure
- Created: requirements.txt (134 pinned packages), Makefile, PROJECT_PLAN.md (12-week plan)
- Created: CONCEPTS.md (plain-English explainer: qubits, superposition, entanglement, QFT, Shor's, MLWE, ML-KEM)
- Created: README.md (full reproducibility guide), report/00_outline.md, report/references.bib
- Created: __init__.py files in all src/ subdirectories
- Created: tests/test_smoke.py (imports qiskit, qiskit_aer, oqs, checks .env token)
- Smoke test: 4/4 passed

### Week 1 — Bell State Experiment (2026-05-11)
- Commit: `231e53a` — "Week 1: Bell state experiment with entanglement verification"
- Concepts explained: qubits as spin-1/2 relabeling, |00⟩ as tensor products, gates as unitary operators, CNOT creating entanglement, all four Bell states, connection to QM (singlet = |Psi->)
- Notebook `01_shors_threat.ipynb` sections:
  - 1.1: Single-qubit gate demos (X gate, H gate)
  - 1.2: Bell state |Phi+⟩ circuit (H + CNOT)
  - 1.3: Entanglement verification — product state (all 4 outcomes ~25%) vs Bell state (only 00/11 ~50%)
  - 1.4: All four Bell states (Phi+, Phi-, Psi+, Psi-)
  - 1.5: Why this matters for Shor's algorithm
- Figures generated: w1_bell_state.png, w1_product_vs_bell.png, w1_all_bell_states.png
- Tests: test_bell_state.py (3 tests: Phi+, Psi+, product state) — all pass
- Total tests: 7/7 passing

### Weeks 2-12 — All Code and Report (2026-05-16)
- All source code written and tested:
  - `src/shors/circuit.py` — QFT, inverse QFT, controlled modular exponentiation, full Shor's circuit
  - `src/shors/classical.py` — GCD, continued fractions, period extraction, factor finding
  - `src/shors/run_simulator.py` — Shor's on Aer simulator for N=15 and N=21
  - `src/shors/run_hardware.py` — Shor's on IBM Quantum hardware (with quota confirmation)
  - `src/mlkem/benchmark.py` — ML-KEM-512/768/1024 benchmark harness (10K iterations)
  - `src/mlkem/compare_x25519.py` — X25519 baseline comparison
  - `src/analysis/stats.py` — Statistical analysis functions
  - `src/analysis/plots.py` — All figure generation
- Simulator results generated:
  - N=15 (a=7): 50.1% success rate, factors {(3,5)}
  - N=15 (a=11): 50.3% success rate, factors {(3,5)}
  - N=21 (a=2): 32.8% success rate, factors {(3,7)}
- ML-KEM benchmarks generated:
  - ML-KEM-768: keygen ~10μs, encap ~11μs, decap ~12μs
  - X25519: keygen ~66μs, encap ~200μs, decap ~133μs
  - ML-KEM is 7-18x FASTER than X25519 on Apple Silicon
  - Size cost: ML-KEM-768 pk=1184B, ct=1088B vs X25519 pk=32B, ct=32B
- 17 figures generated in results/figures/
- 9 CSV data files in results/raw/
- Both notebooks written and executed successfully
- Full report (6 chapters + outline + references): ~25 pages
- 37/37 tests passing
- Hardware run (make shors-hw) not yet executed — requires user confirmation

## Current Status: Code Complete
- All code written and tested
- All simulator experiments run
- All benchmarks run
- All figures generated
- Report written
- **Remaining**: Hardware run on IBM Quantum (optional, costs quota), final polish

## 12-Week Plan Summary
- W1: ✅ Qiskit basics, Bell state
- W2: ✅ QFT from scratch, verified against Qiskit
- W3: ✅ Shor's N=15 on simulator (50% success)
- W4: ⬜ Shor's N=15 on hardware (ready, needs user OK)
- W5: ✅ Shor's N=21 on simulator (33% success)
- W6: ✅ RSA-2048 resource extrapolation
- W7: ✅ Report draft
- W8: ✅ ML-KEM setup + verification
- W9: ✅ ML-KEM benchmark harness
- W10: ✅ Comparative analysis + plots
- W11: ✅ Synthesis section
- W12: ✅ Final report

## Scope Exclusions (Future Work)
- TLS integration
- PQ signatures (ML-DSA, SLH-DSA)
- Other PQC families (HQC, BIKE, McEliece)
- Full quantum error correction
- Shor's on N > 21 unless N=21 succeeds
