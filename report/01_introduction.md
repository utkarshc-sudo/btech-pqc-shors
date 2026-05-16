# Chapter 1: Introduction

## 1.1 The Quantum Computing Threat to Modern Cryptography

The security infrastructure of the modern digital world rests on a small set of mathematical assumptions. The RSA cryptosystem, introduced by Rivest, Shamir, and Adleman in 1978, derives its security from the presumed computational intractability of factoring the product of two large prime numbers [Rivest et al., 1978]. Elliptic-curve cryptography (ECC), which underpins widely deployed key-exchange protocols such as X25519 and ECDH, relies on the difficulty of the elliptic-curve discrete logarithm problem (ECDLP). Together, these two families of algorithms protect virtually all encrypted communication on the Internet, from TLS connections securing web browsing to the digital signatures authenticating software updates.

In 1994, Peter Shor demonstrated that a sufficiently large, fault-tolerant quantum computer could solve both integer factorization and discrete logarithm problems in polynomial time [Shor, 1994]. Shor's algorithm achieves an exponential speedup over the best-known classical factoring algorithms: whereas the general number field sieve runs in sub-exponential time $L_N[1/3, c]$, Shor's algorithm factors an $n$-bit integer in $O(n^2 \log n \log \log n)$ time using $O(n)$ logical qubits. This result was initially of purely theoretical interest, as practical quantum computers with the required capabilities were decades away. However, the intervening thirty years have seen dramatic advances in quantum hardware, and the question has shifted from *whether* quantum computers will threaten cryptographic security to *when*.

As of 2025, the most advanced quantum processors exceed 1,000 physical qubits. IBM's Condor processor reached 1,121 superconducting qubits in late 2023, and the company's roadmap projects processors with over 100,000 qubits by the end of this decade [IBM, 2024]. Google's Willow processor, announced in late 2024, demonstrated significant improvements in quantum error correction, achieving below-threshold error rates on a surface code for the first time. While these devices remain far from the estimated 20 million noisy qubits required to factor a 2048-bit RSA key [Gidney and Ekera, 2021], the trajectory of progress demands proactive preparation rather than reactive response.

The threat is not merely hypothetical. Nation-state adversaries and sophisticated threat actors are widely believed to be engaged in "harvest now, decrypt later" (HNDL) campaigns: intercepting and storing encrypted traffic today with the expectation that future quantum computers will enable retroactive decryption. Data with long confidentiality requirements --- medical records, state secrets, financial transactions, intellectual property --- is vulnerable to this strategy. If a quantum computer capable of breaking RSA-2048 emerges even ten years from now, any data encrypted under RSA or ECC and captured in the interim will be compromised.

## 1.2 The NIST Post-Quantum Cryptography Standardization

Recognizing the urgency of this threat, the National Institute of Standards and Technology (NIST) initiated a formal process to standardize post-quantum cryptographic (PQC) algorithms. The timeline of this effort underscores both the complexity of the problem and the deliberate pace of cryptographic standardization:

- **December 2016**: NIST issued a call for proposals for quantum-resistant public-key cryptographic algorithms, requesting submissions for key encapsulation mechanisms (KEMs) and digital signature schemes [NIST, 2016].

- **2017--2019 (Rounds 1--2)**: NIST received 82 complete and proper submissions across both categories. Through two rounds of public evaluation, involving analysis from the global cryptographic research community, the field was narrowed to 15 candidates entering Round 2 and subsequently 7 finalists and 8 alternates entering Round 3.

- **July 2020 (Round 3)**: The third-round candidates were announced, comprising four finalists (CRYSTALS-Kyber, CRYSTALS-Dilithium, FALCON, and SPHINCS+) and four alternates for further consideration (BIKE, Classic McEliece, HQC, and SIKE).

- **July 2022**: NIST announced the first set of algorithms selected for standardization. CRYSTALS-Kyber was selected as the primary KEM, CRYSTALS-Dilithium and FALCON as the primary digital signature schemes, and SPHINCS+ as a hash-based signature scheme offering conservative security assumptions. Notably, SIKE, a finalist based on supersingular isogeny problems, was broken by a classical attack shortly after Round 3 selection --- a stark reminder that cryptographic assumptions require extensive scrutiny [Castryck and Decru, 2022].

- **August 13, 2024**: NIST published the final standards as Federal Information Processing Standards: **FIPS 203** (ML-KEM, the Module-Lattice-Based Key Encapsulation Mechanism, derived from CRYSTALS-Kyber), **FIPS 204** (ML-DSA, the Module-Lattice-Based Digital Signature Algorithm, derived from CRYSTALS-Dilithium), and **FIPS 205** (SLH-DSA, the Stateless Hash-Based Digital Signature Algorithm, derived from SPHINCS+) [NIST, 2024].

- **2024--2025**: A fourth round of evaluation continues for additional KEM candidates (BIKE, Classic McEliece, HQC) to provide algorithm diversity and hedge against future cryptanalytic breakthroughs against lattice-based schemes. HQC was selected for standardization as an additional KEM in 2025.

This eight-year standardization process reflects the high bar that cryptographic standards must meet: not only must the algorithms resist known quantum attacks, but they must also withstand classical cryptanalysis, perform efficiently across diverse deployment environments, and integrate with existing protocol frameworks.

## 1.3 The "Harvest Now, Decrypt Later" Threat Model

The HNDL threat model represents perhaps the most immediate and actionable motivation for the transition to post-quantum cryptography. Unlike most cybersecurity threats, which require the adversary to possess offensive capabilities *at the time of the attack*, HNDL decouples data collection from data exploitation across a potentially unbounded time horizon.

Consider the following scenario. An adversary with access to network traffic --- through passive wiretapping at an Internet exchange point, compromised network infrastructure, or state-level signals intelligence capabilities --- records TLS-encrypted sessions today. These sessions are protected by ECDHE key exchange and AES-256 symmetric encryption. The symmetric key is safe from quantum attack (Grover's algorithm provides at most a quadratic speedup, equivalent to halving the effective key length, so AES-256 retains 128-bit post-quantum security). However, if the ephemeral ECDHE key exchange is broken retrospectively, the adversary can recover the symmetric session key and decrypt the entire recorded session.

The HNDL risk is characterized by the inequality:

$$T_{\text{migration}} + T_{\text{confidentiality}} > T_{\text{quantum}}$$

where $T_{\text{migration}}$ is the time required to deploy post-quantum cryptography across all relevant systems, $T_{\text{confidentiality}}$ is the duration for which the data must remain confidential, and $T_{\text{quantum}}$ is the time until a cryptographically relevant quantum computer (CRQC) becomes operational. If this inequality holds --- that is, if the sum of migration time and required confidentiality exceeds the timeline to a CRQC --- then data encrypted today is at risk.

Estimates for these parameters vary, but the qualitative conclusion is robust. $T_{\text{migration}}$ is typically measured in years to decades for large organizations and critical infrastructure. $T_{\text{confidentiality}}$ for sensitive government or healthcare data is often 25--50 years or more. $T_{\text{quantum}}$ is highly uncertain but commonly estimated at 10--30 years by experts in the quantum computing community. Under most reasonable assumptions, the inequality holds, and the HNDL threat is real.

This analysis motivates immediate action: even if a CRQC is 15 years away, organizations handling data with 20-year confidentiality requirements that face a 5-year migration timeline are already past the point at which they should have begun the transition.

## 1.4 Project Objectives

This project takes an empirical, two-pronged approach to the quantum cryptographic transition. Rather than treating the quantum threat and the post-quantum defense in isolation, we investigate both sides of the problem and synthesize the findings into actionable conclusions. The specific objectives are:

1. **Demonstrate the quantum threat concretely.** We implement Shor's algorithm using IBM's Qiskit framework and execute it on both quantum simulators and real IBM Quantum hardware. By factoring small integers ($N = 15$ and $N = 21$), we observe the algorithm's behavior on current noisy intermediate-scale quantum (NISQ) devices, quantify success rates and noise-induced degradation, and extrapolate the resource requirements for cryptographically relevant instances (RSA-2048).

2. **Benchmark the post-quantum defense.** We systematically measure the performance of ML-KEM (FIPS 203) across all three parameter sets (ML-KEM-512, ML-KEM-768, ML-KEM-1024) and compare against the classical baseline X25519. Our benchmarks cover key generation, encapsulation, and decapsulation operations, as well as key and ciphertext sizes, providing a comprehensive assessment of the practical cost of migration.

3. **Synthesize the threat and defense.** By combining the quantum threat timeline with the defense performance profile, we assess the urgency and feasibility of the cryptographic transition. We analyze the performance overhead that organizations can expect when migrating from classical to post-quantum key exchange, and we situate this analysis within the NIST compliance timeline and the HNDL threat model.

## 1.5 Report Structure

The remainder of this report is organized as follows:

**Chapter 2: Background** provides the theoretical foundations for both halves of the study. We review quantum computing fundamentals (qubits, gates, circuits, measurement), the RSA cryptosystem and its integer factoring assumption, Shor's algorithm and its reduction of factoring to quantum period-finding, lattice-based cryptography and the Module Learning With Errors (MLWE) problem, the ML-KEM specification (FIPS 203), and the current landscape of quantum hardware.

**Chapter 3: The Threat --- Shor's Algorithm on Quantum Hardware** presents our experimental implementation and execution of Shor's algorithm. We describe the circuit design for $N = 15$ and $N = 21$, present results from both the Aer simulator and IBM Quantum hardware, analyze the impact of quantum noise on algorithm success rates, and extrapolate the resource requirements for RSA-2048 based on the estimates of Gidney and Ekera [2021].

**Chapter 4: The Defense --- ML-KEM Performance** details our benchmarking methodology and results for ML-KEM-512, ML-KEM-768, and ML-KEM-1024. We present timing distributions for key generation, encapsulation, and decapsulation across 10,000 iterations, compare against X25519 as a classical baseline, and analyze the key and ciphertext size overhead.

**Chapter 5: Synthesis** bridges the threat and defense analyses. We discuss the quantum threat timeline, the migration cost profile, the case for crypto agility, NIST's compliance deadlines, and the harvest-now-decrypt-later risk. We conclude with practical recommendations for organizations planning their post-quantum transition.

**Chapter 6: Conclusion** summarizes our findings, states the contributions of this work, acknowledges limitations, and identifies directions for future research including TLS integration testing, post-quantum digital signatures, and additional PQC algorithm families.
