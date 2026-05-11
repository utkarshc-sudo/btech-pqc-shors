# Report Outline

## 01 — Introduction (`01_introduction.md`)
Motivation for studying quantum threats to cryptography, the NIST PQC standardization timeline, project objectives, and report structure.

## 02 — Background (`02_background.md`)
Quantum computing fundamentals (qubits, gates, QFT), RSA and ECC security assumptions, Shor's algorithm theory, lattice-based cryptography and MLWE, ML-KEM specification overview.

## 03 — The Threat: Shor's Algorithm (`03_threat_shors.md`)
Implementation of Shor's for N=15 and N=21, simulator vs. hardware results, noise analysis, success rates, resource extrapolation to RSA-2048 citing Gidney & Ekerå (2021).

## 04 — The Defense: ML-KEM Performance (`04_defense_mlkem.md`)
Benchmark methodology, ML-KEM-512/768/1024 performance across keygen/encap/decap, comparison with X25519, key and ciphertext size analysis, statistical distributions.

## 05 — Synthesis (`05_synthesis.md`)
Connecting threat timeline with defense readiness, migration cost analysis, harvest-now-decrypt-later risk, recommendations for crypto agility.

## 06 — Conclusion (`06_conclusion.md`)
Summary of findings, contributions, limitations, and future work (TLS integration, PQ signatures, other PQC families, larger Shor's instances).

## References (`references.bib`)
BibTeX entries for all cited works.
