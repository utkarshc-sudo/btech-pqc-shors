# Chapter 6: Conclusion

## 6.1 Summary of Findings

This project has conducted an empirical investigation of both sides of the quantum cryptographic transition: the threat posed by Shor's algorithm to current public-key cryptography, and the practical cost of defending against that threat using the NIST-standardized ML-KEM algorithm.

**On the threat side**, we implemented Shor's algorithm from first principles using the Qiskit framework and executed it on both quantum simulators and real IBM Quantum hardware. For $N = 15$, the algorithm successfully factors the integer on the noise-free simulator with a success rate approaching 75% (three of four QFT peaks yield valid factors). On real hardware, the success rate degrades due to gate errors, decoherence, and measurement noise, but the correct factors remain identifiable above the noise floor. For $N = 21$, the algorithm succeeds on the simulator but the deeper circuit and larger qubit count push the computation beyond the practical capabilities of current NISQ hardware, illustrating the steep scaling of noise effects with circuit complexity.

Our resource extrapolation, based on the estimates of Gidney and Ekera [2021], places the requirements for factoring RSA-2048 at approximately 20 million physical qubits --- roughly four orders of magnitude beyond current hardware capabilities. This gap is large but finite, and the trajectory of quantum hardware development suggests that a cryptographically relevant quantum computer may emerge within 10 to 30 years.

**On the defense side**, we systematically benchmarked ML-KEM across all three parameter sets (ML-KEM-512, ML-KEM-768, ML-KEM-1024) and compared against the X25519 classical baseline. Our results demonstrate that ML-KEM operations perform competitively with X25519 in raw computation, with absolute per-operation times on the order of [DATA: approximate value] microseconds --- negligible relative to typical network latency. The primary practical impact of migration is the increase in key and ciphertext sizes (approximately 35x for ML-KEM-768 compared to X25519), which adds roughly 2.2 KB to each TLS handshake.

**In synthesis**, we demonstrated that the performance cost of post-quantum migration is modest and manageable for the vast majority of deployment scenarios, while the quantum threat --- particularly under the harvest-now-decrypt-later model --- is a genuine risk for data with long confidentiality requirements. The risk-reward calculation strongly favors beginning the transition to post-quantum cryptography now, well before a cryptographically relevant quantum computer emerges.

## 6.2 Contributions of This Work

This project makes the following contributions:

1. **End-to-end Shor's algorithm implementation.** We provide a complete, documented, and tested implementation of Shor's algorithm in Qiskit, covering the Quantum Fourier Transform, controlled modular exponentiation (for $N = 15$ and $N = 21$), and classical post-processing via continued fractions. The implementation is modular and extensible, suitable for educational use and as a starting point for further quantum computing experiments.

2. **Simulator-to-hardware comparison.** By executing the same circuit on both the Aer simulator and IBM Quantum hardware, we provide a direct empirical measurement of how quantum noise affects algorithmic success rates. This comparison concretely illustrates the gap between ideal quantum computation and NISQ reality.

3. **Comprehensive ML-KEM benchmarks.** Our benchmarks cover all three ML-KEM parameter sets across all three core operations (keygen, encaps, decaps), with 10,000 iterations per measurement and rigorous statistical analysis. The comparison against X25519 provides a direct measure of the migration cost in a format immediately useful for deployment planning.

4. **Integrated threat-defense analysis.** By combining the quantum threat timeline with the defense performance profile in a single study, we provide a self-contained assessment that connects the "when" of the threat with the "how much" of the defense. This integrated perspective is often absent from studies that focus on either quantum computing or post-quantum cryptography in isolation.

5. **Reproducible methodology and pedagogical resource.** All code, data, and analysis are publicly available with pinned dependency versions. The codebase, notebooks, and CONCEPTS.md serve as a hands-on introduction to both quantum computing and post-quantum cryptography, suitable for undergraduate study. A clean clone and `make install` reproduces the full environment.

## 6.3 Limitations

This work has several limitations that should be acknowledged:

1. **Small factoring instances.** Our Shor's algorithm implementation is limited to $N = 15$ and $N = 21$, which are far from cryptographically relevant. The modular exponentiation circuits for these instances are hardcoded (for $N = 15$) or use explicit unitary decomposition (for $N = 21$), rather than general modular arithmetic circuits. While this is standard practice for educational demonstrations, it means our circuits do not directly represent the structure and complexity of circuits needed for large-scale factoring.

2. **Hardware access constraints.** Our hardware experiments are limited by the quantum hardware available through free-tier IBM Quantum access. The specific backend, its calibration state on the day of execution, and the number of shots available all affect the results. Hardware performance varies between calibration cycles and across different processors.

3. **Single-platform benchmarks.** Our ML-KEM benchmarks are conducted on a single hardware platform (Apple Silicon, macOS). Performance characteristics may differ on other architectures (e.g., x86-64 with AVX-512, server-class ARM, or embedded platforms). Cross-platform benchmarking would provide a more complete performance profile.

4. **Library-level measurement.** We benchmark ML-KEM through the liboqs Python bindings, which add some overhead relative to native C calls. While this overhead is small and consistent (thus not significantly affecting relative comparisons), absolute timings may differ from those of a bare-metal or in-kernel implementation.

5. **No protocol-level measurement.** Our benchmarks measure cryptographic primitive performance in isolation. The actual impact on end-to-end protocol performance (e.g., TLS handshake latency) depends on additional factors including network conditions, certificate chain length, server load, and implementation-specific optimizations.

6. **Static analysis of quantum timeline.** Our assessment of the quantum threat timeline relies on published estimates and expert projections rather than independent modeling. The inherent uncertainty in these projections is a limitation of any work in this space.

## 6.4 Future Work

Several directions for future research emerge naturally from this project:

### 6.4.1 TLS Integration Testing

The most immediate extension would be to measure ML-KEM performance within a full TLS 1.3 handshake, using an ML-KEM-enabled TLS library (e.g., OQS-OpenSSL or BoringSSL with PQC support). This would capture protocol-level overheads including serialization, network transmission of larger key shares, and interaction with other handshake components. Of particular interest would be measuring the impact on handshake latency under realistic network conditions (varying RTT, packet loss, and bandwidth constraints).

### 6.4.2 Post-Quantum Digital Signatures

This project focused on key encapsulation (ML-KEM). The complementary component of the post-quantum transition is digital signatures. Future work should benchmark **ML-DSA** (FIPS 204, derived from CRYSTALS-Dilithium) and **SLH-DSA** (FIPS 205, derived from SPHINCS+), which are the NIST-standardized post-quantum signature algorithms. ML-DSA signatures are approximately 2.4--4.6 KB (compared to 64 bytes for Ed25519), and the impact on TLS certificate chains --- which may contain 2--3 certificates --- could be significant.

### 6.4.3 Other PQC Algorithm Families

NIST's standardization process is ongoing, with additional algorithms from different mathematical families under evaluation:

- **HQC** (Hamming Quasi-Cyclic): A code-based KEM selected for standardization in 2025, providing algorithm diversity beyond lattice-based schemes.
- **BIKE** (Bit Flipping Key Encapsulation): Another code-based KEM under continued evaluation.
- **Classic McEliece**: A code-based KEM with extremely large public keys (~1 MB) but very fast encapsulation and established security foundations dating back to 1978.

Benchmarking these alternative schemes and comparing them against ML-KEM would provide a more complete picture of the PQC landscape and inform decisions about algorithm diversity.

### 6.4.4 Quantum Error Correction

Our Shor's algorithm experiments are conducted on NISQ hardware without error correction. A natural extension would be to implement and study quantum error correction codes (e.g., the repetition code, Steane code, or small surface codes) on real hardware, to measure the overhead ratio between physical and logical qubits and to validate the error correction thresholds assumed in the Gidney-Ekera resource estimates.

### 6.4.5 Larger Shor's Instances

Extending Shor's algorithm to factor larger numbers (e.g., $N = 33$, $N = 35$, or $N = 77$) on quantum simulators and, where feasible, hardware, would provide additional data points on the scaling of noise effects. Investigating circuit optimization techniques --- such as iterative phase estimation (which uses fewer counting qubits by measuring and reusing a single qubit) --- could extend the range of factoring achievable on near-term devices.

### 6.4.6 Cross-Platform and Embedded Benchmarks

Extending ML-KEM benchmarks to x86-64 server hardware (with AVX2/AVX-512 optimizations), mobile ARM (Cortex-A series), embedded ARM (Cortex-M series), and RISC-V platforms would characterize performance across the computing spectrum. This is particularly important for assessing the feasibility of PQC deployment in IoT and constrained environments.

### 6.4.7 Hybrid Key Exchange

Implementing and benchmarking X25519+ML-KEM-768 hybrid key exchange --- as recommended by NIST and already deployed in Chrome, Firefox, and iMessage --- would measure the combined overhead of the transitional approach that most deployments will use in the near term.

## 6.5 Closing Remarks

The quantum threat to classical cryptography is not immediate, but it is approaching along a trajectory that demands proactive preparation. Our experiments demonstrate that Shor's algorithm is correct and implementable today --- the only barrier to breaking RSA at scale is quantum hardware maturity, which is a matter of engineering progress rather than fundamental physics.

Simultaneously, the post-quantum defense is mature, standardized, and performant. ML-KEM-768, published by NIST as FIPS 203 in August 2024, imposes modest computational overhead on modern hardware. The increase in key and ciphertext sizes, while non-trivial, is well within the capacity of current network infrastructure.

The message for practitioners and policymakers is clear: the cost of migrating to post-quantum cryptography is quantifiable and manageable, while the cost of waiting is uncertain and potentially catastrophic for data with long-lived confidentiality requirements. Organizations should begin their migration today, starting with cryptographic inventory, hybrid deployments, and investments in crypto agility, to ensure that their data remains secure when large-scale quantum computers eventually arrive.
