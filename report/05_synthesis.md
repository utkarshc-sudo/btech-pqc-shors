# Chapter 5: Synthesis

The preceding two chapters have examined the quantum threat (Chapter 3) and the post-quantum defense (Chapter 4) as separate investigations. This chapter bridges the two, synthesizing the findings into a coherent assessment of the cryptographic transition. We analyze the threat timeline, quantify the migration cost, argue for crypto agility, review NIST's compliance deadlines, and provide recommendations for organizations planning their post-quantum transition.

## 5.1 Timeline Analysis: When Will Quantum Computers Break RSA-2048?

### 5.1.1 The Resource Gap

Our experimental results in Chapter 3 provide a concrete, ground-level perspective on the gap between current quantum hardware and cryptographically relevant quantum computation (CRQC). Table 10 summarizes the key dimensions of this gap:

| Dimension | N=15 (Demonstrated) | N=21 (Attempted) | RSA-2048 (Required) | Gap (Current to RSA-2048) |
|-----------|---------------------|-------------------|---------------------|--------------------------|
| Total qubits | 12 | 15 | $\sim 20 \times 10^6$ | $\sim 10^6\times$ |
| Circuit depth (gates) | [DATA: N=15 depth] | [DATA: N=21 depth] | $\sim 10^8$--$10^9$ | $\sim 10^6\times$ |
| Error correction | None (NISQ) | None (NISQ) | Surface code, $d=27$ | Qualitative |
| Success rate | [DATA]% (hardware) | [DATA]% (hardware) | $> 99\%$ (required) | Qualitative |

Table 10: Scaling from experimental demonstrations to RSA-2048.

The gap is approximately four orders of magnitude in qubit count and six orders of magnitude in circuit depth. These are engineering challenges, not fundamental physical barriers, but they are formidable engineering challenges.

### 5.1.2 Projected Timelines

The quantum computing community does not have consensus on when a CRQC will emerge. We can organize the range of expert opinions into three scenarios:

**Optimistic Scenario (CRQC by 2035--2040)**. This scenario assumes:
- Continued exponential growth in qubit counts (doubling every 1--2 years).
- Breakthrough improvements in error rates, reaching $\sim 10^{-4}$ consistently within 5 years.
- Successful demonstration of fault-tolerant logical qubits at scale by 2030.
- Modular quantum computing architectures connecting multiple processors.
- Significant government and private investment acceleration (as seen with the US CHIPS and Science Act, EU Quantum Flagship, and major corporate investments).

Under these assumptions, the 20 million physical qubits required could be reached through modular architectures connecting approximately 15,000--20,000 processors of 1,000 qubits each, a significant but not inconceivable engineering effort given a 10--15 year timeline.

**Moderate Scenario (CRQC by 2040--2050)**. This is the consensus view among many quantum computing researchers and reflects a more conservative assessment of the engineering challenges:
- Qubit counts continue to grow, but scaling is not purely exponential; engineering challenges introduce plateaus.
- Error correction at scale is demonstrated by 2030--2035 but remains expensive (high overhead ratios).
- Algorithmic improvements (such as Regev's 2023 multi-dimensional approach) partially offset hardware limitations.
- The first "useful" fault-tolerant computations (e.g., molecular simulation) are achieved before a CRQC, driving continued investment.

**Conservative Scenario (CRQC post-2050)**. This scenario accounts for potential obstacles:
- Fundamental decoherence or fabrication challenges limit qubit scaling.
- Error correction overhead proves higher than current estimates.
- Quantum computing investment plateaus if near-term commercial applications disappoint.
- No breakthrough algorithms emerge that significantly reduce resource requirements.

### 5.1.3 Implications for Cryptographic Planning

Regardless of which scenario materializes, the planning implications are similar due to the long timescales involved in cryptographic migration:

- Under the **optimistic** scenario, any data encrypted today with RSA or ECC and requiring confidentiality beyond 2035--2040 is at risk. This includes most government classified data, long-term financial records, health records, and trade secrets.
- Under the **moderate** scenario, data requiring confidentiality beyond 2040--2050 is at risk. This still encompasses a significant fraction of sensitive data, particularly in government and healthcare contexts where retention requirements span decades.
- Under the **conservative** scenario, the risk is reduced but not eliminated. Additionally, cryptographic transitions typically take longer than anticipated (the transition from SHA-1 to SHA-2, for example, was first recommended in 2005 and was still not complete in many systems by 2017), suggesting that migration should begin well in advance.

## 5.2 Migration Cost: Performance Overhead of ML-KEM

### 5.2.1 Computational Cost

Our benchmark results in Chapter 4 demonstrate that the computational overhead of ML-KEM-768 relative to X25519 is [DATA: approximate ratio]x for individual operations. In absolute terms, the additional per-handshake cost is on the order of [DATA: approximate value] microseconds.

To contextualize this cost, consider that a typical TLS 1.3 handshake involves:
1. **Network latency**: 1 RTT of 10--200 ms (depending on geographic distance and network conditions).
2. **TLS protocol overhead**: Certificate chain transmission and validation, cipher suite negotiation, and record-layer framing.
3. **Cryptographic operations**: Key exchange, signature verification, symmetric key derivation.

The cryptographic operations in step 3 typically account for less than 1% of the total handshake time in a standard web browsing scenario. Even if ML-KEM triples the cost of step 3, the impact on total handshake latency is negligible.

### 5.2.2 Bandwidth Cost

The more significant cost is bandwidth. Replacing X25519 with ML-KEM-768 adds approximately 2.2 KB to each TLS handshake. For a high-traffic web service handling 50,000 new TLS connections per second, this represents an additional bandwidth consumption of approximately 110 MB/s (880 Mbps). While this is within the capacity of modern server infrastructure, it is not zero-cost, particularly for:

- **Content delivery networks (CDNs)** handling millions of connections per second globally.
- **Mobile networks** with per-byte pricing and bandwidth constraints.
- **IoT deployments** with severely constrained link-layer frame sizes.

### 5.2.3 Integration Cost

Beyond raw performance, the migration to post-quantum cryptography involves significant systems-integration effort:

- **Protocol updates**: TLS, SSH, IPsec, S/MIME, and other protocols must be updated to support ML-KEM. TLS 1.3 with ML-KEM hybrid key exchange is already standardized (RFC 9180 for HPKE, and draft-ietf-tls-hybrid-design), and major browsers and servers have begun experimental deployment.

- **Library upgrades**: Cryptographic libraries (OpenSSL, BoringSSL, NSS, Bouncy Castle, etc.) must incorporate ML-KEM implementations. OpenSSL 3.5 includes initial PQC support, and the OQS project provides drop-in integrations.

- **Hardware security modules (HSMs)**: Many organizations perform key operations in hardware. HSMs must be updated with PQC algorithm support, which may require firmware or hardware upgrades.

- **Certificate infrastructure**: If post-quantum signatures are adopted alongside post-quantum key exchange, the entire PKI chain (root CAs, intermediaries, end-entity certificates) must be updated. This is arguably the most complex and longest-lead-time component of the transition.

- **Compliance and audit**: Regulated industries must update compliance frameworks, document the transition, and potentially obtain re-certification (e.g., FIPS 140-3 validation for cryptographic modules).

## 5.3 The Crypto Agility Argument

**Crypto agility** is the design principle that cryptographic algorithms, parameters, and protocols should be easily replaceable without requiring fundamental architectural changes to the systems that use them. The post-quantum transition is the strongest argument yet for crypto agility.

### 5.3.1 Historical Precedents

The history of cryptography is marked by algorithm transitions, each of which proved more difficult and slower than anticipated:

- **DES to AES (1999--2010s)**: DES was known to be inadequate by the late 1990s (it was broken by brute force in 1999). AES was standardized in 2001. Yet DES and 3DES persisted in many systems for over a decade, and NIST only formally deprecated 3DES in 2023.

- **MD5 to SHA-1 to SHA-256 (2004--2017)**: Weaknesses in MD5 were published in 2004, and collision attacks in 2007. SHA-1 collisions were produced by Google in 2017. Despite years of warnings, both algorithms remained in widespread use long after they were known to be insecure.

- **RSA-1024 to RSA-2048 (2010--present)**: NIST recommended moving to 2048-bit RSA keys by 2010. As of 2025, most systems have completed this transition, but it took 15 years and is still not universal.

Each of these transitions was simpler than the post-quantum transition (they involved drop-in replacements of the same algorithmic type), yet each took a decade or more. The PQC transition is qualitatively harder because it changes the mathematical foundation of the algorithms and significantly alters key and ciphertext sizes.

### 5.3.2 Designing for Agility

Crypto agility in the context of post-quantum migration requires:

1. **Algorithm negotiation**: Protocols should support dynamic selection of cryptographic algorithms, allowing new algorithms to be added and deprecated algorithms removed without protocol changes. TLS already supports this through cipher suites and key share extensions.

2. **Abstraction layers**: Applications should interact with cryptography through well-defined abstractions (e.g., "perform key exchange" rather than "perform X25519"), allowing the underlying algorithm to change without application-level modifications.

3. **Hybrid deployment**: During the transition period, systems should support hybrid key exchange (classical + post-quantum) to provide security even if either algorithm is compromised.

4. **Key and certificate management**: PKI systems should support multiple algorithm types simultaneously, including mixed-algorithm certificate chains.

5. **Testing and validation**: Automated testing should verify interoperability across algorithm transitions, including backward compatibility with legacy systems.

## 5.4 NIST Transition Timeline and Compliance

### 5.4.1 NIST Guidelines

NIST has published explicit guidance on the post-quantum transition timeline for federal agencies and, by extension, for the broader industry:

- **2024**: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA) are published as final standards.

- **2025--2030**: Federal agencies are expected to begin inventorying their cryptographic usage, identifying systems that use vulnerable algorithms, and planning migration schedules. NIST's "Migration to Post-Quantum Cryptography" project (NCCoE) is providing practical guidance and reference architectures.

- **2030 (target)**: NIST has indicated a target of deprecating 112-bit classical security (RSA-2048, ECC P-256) for new deployments by 2030. This does not mean these algorithms will be immediately withdrawn, but new systems should use post-quantum algorithms.

- **2035 (target)**: Full deprecation of classical public-key algorithms for all federal use, including legacy systems. After this date, RSA and classical ECC should no longer be used in any federal system, even in hybrid mode.

### 5.4.2 Industry Response

Major technology companies have already begun deploying post-quantum cryptography:

- **Google**: Deployed hybrid X25519+ML-KEM-768 key exchange in Chrome (Canary and then stable channels) beginning in 2023--2024. Google reports that PQC key exchange is now used in a significant fraction of Chrome TLS connections.

- **Apple**: Announced the PQ3 protocol for iMessage in 2024, using a hybrid ratcheting scheme incorporating ML-KEM-768.

- **Cloudflare**: Enabled post-quantum key exchange support across its global CDN network, reporting minimal performance impact at scale.

- **Signal**: Implemented the PQXDH protocol, incorporating ML-KEM-768 into its end-to-end encrypted messaging protocol.

These early deployments provide real-world validation that PQC migration is technically feasible and practically manageable at Internet scale.

## 5.5 Harvest Now, Decrypt Later: Why Migration Must Start Now

### 5.5.1 Formalizing the Threat Window

Returning to the inequality from Section 1.3:

$$T_{\text{migration}} + T_{\text{confidentiality}} > T_{\text{quantum}}$$

We can now populate these parameters with data-informed estimates:

- **$T_{\text{migration}}$**: Based on historical precedents (Section 5.3.1) and the complexity of the PQC transition, realistic estimates range from 5 to 15 years for large organizations and critical infrastructure. Even for agile organizations, 3--5 years is a minimum to complete cryptographic inventory, testing, staged rollout, and legacy system updates.

- **$T_{\text{confidentiality}}$**: This is domain-specific:
  - Classified government intelligence: 25--75 years
  - Healthcare records (HIPAA): 50+ years (lifetime of patient)
  - Financial records: 7--25 years
  - Trade secrets: Variable, potentially indefinite
  - Personal communications: 5--20 years (subjective but non-trivial)

- **$T_{\text{quantum}}$**: 10--30 years based on the scenarios in Section 5.1.

Table 11 evaluates the inequality for several scenarios:

| Scenario | $T_{\text{migration}}$ | $T_{\text{confidentiality}}$ | $T_{\text{quantum}}$ | Sum $>$ Quantum? | Risk Assessment |
|----------|----------------------|---------------------------|---------------------|-----------------|----------------|
| Government/classified | 10 years | 50 years | 15 years | 60 > 15 | **Critical** |
| Healthcare | 7 years | 50 years | 20 years | 57 > 20 | **Critical** |
| Financial services | 5 years | 10 years | 25 years | 15 < 25 | Moderate |
| Consumer web services | 3 years | 5 years | 25 years | 8 < 25 | Low |
| Government/classified (optimistic Q) | 10 years | 50 years | 30 years | 60 > 30 | **Critical** |

Table 11: HNDL threat assessment across scenarios.

For organizations handling data with long confidentiality requirements, the HNDL threat is critical under *all* plausible quantum timelines. Even for the most conservative quantum timeline estimate (30 years), government and healthcare data encrypted today is at risk.

### 5.5.2 The Cost of Inaction

The cost of failing to migrate in time is asymmetric: migrating early incurs a modest, quantifiable performance overhead (as measured in Chapter 4), while migrating late potentially exposes retroactive decryption of all previously captured data. This is a classic risk-management scenario where the cost of the mitigating action is small relative to the potential loss.

Moreover, early migration provides:
- **Defense in depth**: Even if the quantum timeline proves longer than expected, post-quantum algorithms provide security against potential classical cryptanalytic breakthroughs against RSA or ECC.
- **Standards compliance**: Organizations that migrate early avoid the last-minute rush when deprecation deadlines arrive, reducing the risk of errors and vulnerabilities during hurried transitions.
- **Interoperability**: Early adopters gain experience with PQC and can help shape deployment best practices, protocol designs, and testing frameworks.

## 5.6 Recommendations

Based on our analysis of the quantum threat (Chapter 3), the defense performance profile (Chapter 4), and the synthesis in this chapter, we offer the following recommendations for organizations planning their post-quantum cryptographic transition:

### 5.6.1 Immediate Actions (2024--2026)

1. **Conduct a cryptographic inventory.** Identify all systems, protocols, libraries, and data stores that use RSA, ECC, or other quantum-vulnerable algorithms. Prioritize by data sensitivity and confidentiality duration.

2. **Assess HNDL exposure.** For each system, evaluate whether the data it protects could be subject to harvest-now-decrypt-later attacks. Prioritize systems where $T_{\text{confidentiality}}$ exceeds 10 years.

3. **Begin library and dependency upgrades.** Ensure that cryptographic libraries in use support (or are on a path to support) ML-KEM and ML-DSA. OpenSSL 3.5, BoringSSL, and language-specific libraries are adding PQC support.

4. **Implement hybrid key exchange for high-priority systems.** Deploy X25519+ML-KEM-768 hybrid key exchange in TLS connections protecting the most sensitive data. This provides immediate post-quantum protection with zero risk of regression (if ML-KEM were broken, X25519 still provides classical security).

### 5.6.2 Medium-Term Actions (2026--2030)

5. **Migrate all key exchange to ML-KEM or hybrid.** Extend post-quantum key exchange to all TLS, SSH, and VPN connections. Deprecate non-hybrid classical-only key exchange for new deployments.

6. **Plan certificate migration.** Assess the impact of post-quantum signatures on PKI infrastructure. Begin testing ML-DSA certificates in non-production environments.

7. **Update HSMs and key management systems.** Ensure that hardware security modules and key management services support PQC algorithms. Plan for firmware or hardware upgrades where necessary.

8. **Develop crypto agility capabilities.** Implement algorithm abstraction layers, automated testing for algorithm transitions, and monitoring for deprecated algorithm usage.

### 5.6.3 Long-Term Actions (2030--2035)

9. **Complete the transition.** Remove classical-only key exchange and signature algorithms from all systems. Transition from hybrid to pure post-quantum key exchange where performance and interoperability allow.

10. **Monitor the cryptanalytic landscape.** Stay informed of advances in both quantum computing (which may accelerate the threat timeline) and lattice cryptanalysis (which could affect the security of ML-KEM). Be prepared to switch algorithms if necessary --- this is where crypto agility pays off.

11. **Participate in standardization.** Contribute operational experience and performance data to the ongoing NIST standardization process, including the evaluation of additional PQC families (HQC, Code-based schemes, etc.).

## 5.7 Summary

The synthesis of our threat and defense analyses leads to a clear conclusion: **the performance cost of post-quantum migration is modest, the threat timeline is uncertain but plausible within the confidentiality requirements of sensitive data, and the risk-reward calculation strongly favors early action.** ML-KEM-768 provides quantum resistance at a computational cost of [DATA: approximate ratio]x relative to X25519, with the primary practical impact being increased key and ciphertext sizes (~35x). These costs are manageable for the vast majority of deployment scenarios and are a small price to pay for protection against the quantum threat.
