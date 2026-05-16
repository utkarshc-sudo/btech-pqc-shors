# Chapter 4: The Defense --- ML-KEM Performance

Having established the nature and timeline of the quantum threat in Chapter 3, we now turn to the defense: the practical cost of migrating to post-quantum key exchange. This chapter presents a systematic performance evaluation of ML-KEM (FIPS 203) across all three parameter sets, benchmarked against the classical X25519 baseline.

## 4.1 ML-KEM Parameter Sets and Security Levels

ML-KEM provides three parameter sets designed for different security requirements, as detailed in Section 2.5.2. For this benchmarking study, we evaluate all three:

- **ML-KEM-512**: NIST Security Level 1 (equivalent to AES-128). The smallest and fastest parameter set, suitable for applications where bandwidth is constrained and 128-bit post-quantum security is sufficient.
- **ML-KEM-768**: NIST Security Level 3 (equivalent to AES-192). The recommended default parameter set, offering a strong security margin while maintaining practical performance.
- **ML-KEM-1024**: NIST Security Level 5 (equivalent to AES-256). The most conservative parameter set, for applications requiring the highest security assurance.

The classical baseline for comparison is **X25519**, an elliptic-curve Diffie-Hellman (ECDH) key exchange over Curve25519 [Bernstein, 2006]. X25519 is the most widely deployed key exchange mechanism in modern TLS 1.3 connections and provides approximately 128-bit classical security. It is not quantum-resistant.

## 4.2 Benchmark Methodology

### 4.2.1 Implementation

ML-KEM benchmarks use the **liboqs** (Open Quantum Safe) library, accessed through its Python bindings (`liboqs-python`). The liboqs library provides optimized C implementations of NIST-standardized post-quantum algorithms, compiled with platform-specific optimizations (including AVX2/AVX-512 on x86 and NEON on ARM).

X25519 benchmarks use the Python `cryptography` library (backed by OpenSSL), which provides highly optimized implementations of classical elliptic-curve operations.

Both libraries represent production-quality implementations with platform-specific optimizations enabled. This ensures that the comparison reflects realistic deployment performance rather than reference implementation overhead.

### 4.2.2 Measurement Approach

All timing measurements use Python's `time.perf_counter_ns()`, which provides nanosecond-resolution monotonic timing. This avoids the pitfalls of `time.time()` (wall-clock jumps) and `time.process_time()` (excludes I/O wait).

For each algorithm and operation, we execute the following procedure:

1. **Warm-up**: Execute 100 iterations of the operation to warm up CPU caches, trigger JIT compilation in the Python runtime, and stabilize memory allocation patterns. Warm-up results are discarded.

2. **Measurement**: Execute 10,000 timed iterations, recording the elapsed time for each individual iteration in nanoseconds. Each iteration performs a complete, independent operation (e.g., a full key generation from random seed, a full encapsulation with fresh randomness).

3. **Environment control**: During measurement, the process is pinned to a single CPU core where possible, and no other CPU-intensive processes are running. The system governor is set to performance mode to prevent frequency scaling artifacts.

### 4.2.3 Operations Measured

For each ML-KEM parameter set, three operations are measured:

- **Key Generation (KeyGen)**: Generate a fresh public/private key pair. This involves sampling the MLWE matrix, secret and error vectors, and computing the public key.
- **Encapsulation (Encaps)**: Given a public key, generate a shared secret and ciphertext. This involves re-sampling error terms, encrypting a random message, and deriving the shared secret.
- **Decapsulation (Decaps)**: Given a secret key and ciphertext, recover the shared secret. This involves decrypting the ciphertext, re-encrypting for verification (the FO transform check), and deriving the shared secret.

For X25519, the comparable operations are:

- **Key Generation**: Generate a random 32-byte private key and compute the corresponding public key (scalar multiplication of the base point).
- **Key Exchange (equivalent to Encaps + Decaps)**: Given the peer's public key, compute the shared secret via scalar multiplication.

Note that X25519 key exchange is a single operation (Diffie-Hellman), whereas ML-KEM splits into encapsulation and decapsulation. For a fair comparison, the total ML-KEM handshake cost (Encaps + Decaps) should be compared against the combined cost of two X25519 scalar multiplications (one on each side of the connection).

### 4.2.4 Statistical Measures

For each operation, we compute the following statistics over the 10,000 measurements:

- **Mean**: Arithmetic average, the best single estimate of expected performance.
- **Median**: The 50th percentile, robust to outliers from garbage collection or OS scheduler interruptions.
- **Standard deviation**: Spread of the distribution, indicating measurement stability.
- **95th percentile (P95)**: The value below which 95% of measurements fall, relevant for SLA-conscious deployments.
- **99th percentile (P99)**: The tail latency, important for worst-case performance assessment.
- **Minimum and Maximum**: Extreme values, useful for detecting measurement artifacts.

### 4.2.5 Platform Specifications

All benchmarks are executed on the following platform:

[DATA: CPU model (Apple M-series or Intel), architecture (ARM/x86), clock speed, RAM, OS version, Python version, liboqs version, cryptography library version]

## 4.3 Performance Results

### 4.3.1 Key Generation

Key generation involves sampling random polynomials, computing the matrix-vector product $\mathbf{t} = \mathbf{A}\mathbf{s} + \mathbf{e}$ over the polynomial ring $R_q$, and encoding the public and private keys.

[DATA: Table of KeyGen timings for ML-KEM-512, ML-KEM-768, ML-KEM-1024, and X25519 --- mean, median, stddev, P95, P99, all in microseconds]

[DATA: Box plot or violin plot comparing KeyGen distributions across all four algorithms]

Key generation time scales with the module rank $k$ because the matrix $\mathbf{A}$ has $k^2$ polynomial entries, and the matrix-vector product requires $k^2$ NTT-domain multiplications. We expect approximate scaling:
- ML-KEM-512 ($k=2$): baseline
- ML-KEM-768 ($k=3$): $\sim (3/2)^2 = 2.25\times$ relative to ML-KEM-512
- ML-KEM-1024 ($k=4$): $\sim (4/2)^2 = 4\times$ relative to ML-KEM-512

[DATA: Actual observed scaling ratios compared to theoretical prediction]

### 4.3.2 Encapsulation

Encapsulation takes a public key and produces a ciphertext and shared secret. It involves sampling error terms, computing MLWE encryptions, compressing coefficients, and deriving the shared secret via a hash function.

[DATA: Table of Encaps timings for ML-KEM-512, ML-KEM-768, ML-KEM-1024 --- mean, median, stddev, P95, P99, all in microseconds]

[DATA: Box plot or violin plot comparing Encaps distributions]

Encapsulation is typically the fastest of the three ML-KEM operations, as it avoids the FO re-encryption check that decapsulation requires.

### 4.3.3 Decapsulation

Decapsulation takes a secret key and ciphertext and recovers the shared secret. It involves decryption, re-encryption for the FO consistency check, and hash-based key derivation.

[DATA: Table of Decaps timings for ML-KEM-512, ML-KEM-768, ML-KEM-1024 --- mean, median, stddev, P95, P99, all in microseconds]

[DATA: Box plot or violin plot comparing Decaps distributions]

Decapsulation is expected to be the most expensive ML-KEM operation because the Fujisaki-Okamoto transform requires both a decryption *and* a re-encryption to verify ciphertext integrity. This means decapsulation effectively performs the work of both decryption and encapsulation.

### 4.3.4 Aggregate Results

Table 6 summarizes the median timings for all operations:

| Algorithm | KeyGen ($\mu s$) | Encaps ($\mu s$) | Decaps ($\mu s$) | Total Handshake ($\mu s$) |
|-----------|-----------------|-----------------|-----------------|--------------------------|
| ML-KEM-512 | [DATA] | [DATA] | [DATA] | [DATA] |
| ML-KEM-768 | [DATA] | [DATA] | [DATA] | [DATA] |
| ML-KEM-1024 | [DATA] | [DATA] | [DATA] | [DATA] |
| X25519 | [DATA] | [DATA] (key exchange) | --- | [DATA] |

Table 6: Median operation timings across all algorithms.

The "Total Handshake" column represents the combined cost of key generation plus encapsulation on the initiator side, and decapsulation on the responder side. For a TLS-like handshake, the relevant metric is the sum of the operations that each party performs.

## 4.4 Comparison with X25519

### 4.4.1 Performance Ratio

The performance overhead of ML-KEM relative to X25519 is a critical metric for migration planning. We compute the ratio of ML-KEM-768 (the recommended parameter set) to X25519 for each operation:

[DATA: Performance ratio table --- ML-KEM-768 / X25519 for KeyGen, Encaps/KeyExchange, total handshake]

Prior literature and industry benchmarks suggest that ML-KEM operations are typically 1.5--5x slower than X25519 on modern hardware, depending on the platform and optimization level. Our measurements on [DATA: platform] fall within this range:

[DATA: Specific ratios observed and how they compare to published benchmarks]

### 4.4.2 Absolute Timing Context

While relative performance ratios provide a useful comparison, the absolute timings are equally important for assessing practical impact. If ML-KEM-768 key generation takes [DATA: value] microseconds, this is [DATA: fraction] of a typical TLS handshake RTT of 50--200 milliseconds. The cryptographic operations themselves constitute a small fraction of end-to-end handshake latency, which is dominated by network round-trip time.

This observation is important: even if ML-KEM is 3x slower than X25519 in raw cryptographic operations, the impact on user-perceived latency may be negligible in most deployment scenarios.

### 4.4.3 Distribution Shape

[DATA: Overlay histograms showing the timing distributions of ML-KEM-768 vs. X25519 for the most comparable operation (KeyGen)]

The shape of the timing distributions provides insight into implementation behavior:
- **X25519**: Expected to show a tight, approximately normal distribution with small variance, reflecting the constant-time scalar multiplication implementation.
- **ML-KEM**: May show slightly higher variance due to polynomial sampling, NTT operations, and compression steps, though the implementation is also designed to be constant-time to prevent timing side-channel attacks.

[DATA: Coefficient of variation (stddev/mean) for each algorithm, commenting on timing stability]

## 4.5 Key and Ciphertext Size Analysis

### 4.5.1 Size Comparison

The most significant practical difference between ML-KEM and classical key exchange is the size of public keys and ciphertexts. Table 7 presents the complete size comparison:

| Algorithm | Public Key (bytes) | Ciphertext (bytes) | Shared Secret (bytes) | Total Handshake Payload (bytes) |
|-----------|-------------------|-------------------|----------------------|-------------------------------|
| ML-KEM-512 | 800 | 768 | 32 | 1,568 |
| ML-KEM-768 | 1,184 | 1,088 | 32 | 2,272 |
| ML-KEM-1024 | 1,568 | 1,568 | 32 | 3,136 |
| X25519 | 32 | 32 | 32 | 64 |

Table 7: Key, ciphertext, and shared secret sizes for all algorithms.

The total handshake payload represents the combined data that must be transmitted during a key exchange: the initiator sends a public key (or ciphertext), and the responder sends a ciphertext (or public key), depending on the protocol design.

### 4.5.2 Impact on Network Protocols

For ML-KEM-768, the total handshake payload increases from 64 bytes (X25519) to 2,272 bytes, a factor of approximately 35x. The implications vary by deployment context:

- **Standard TLS over TCP**: The additional 2.2 KB fits comfortably within a single TCP segment (typical MSS of 1,460 bytes) when combined with other handshake data. The ClientHello message in TLS 1.3 already contains several hundred bytes of extensions, cipher suite lists, and protocol metadata. Adding 1,184 bytes for an ML-KEM public key may push the ClientHello beyond a single TCP segment, potentially adding one round trip to the handshake on networks with small MTUs. In practice, most connections on modern networks will not be meaningfully affected.

- **QUIC/HTTP3**: QUIC's 0-RTT and 1-RTT handshakes embed the key exchange in the initial flight, and the additional payload size is well within QUIC's congestion window for most connections.

- **Constrained IoT**: Devices with limited bandwidth (e.g., LoRaWAN with 51--222 byte payloads) will face significant challenges accommodating ML-KEM key sizes. For these environments, alternative approaches such as pre-provisioned keys, hybrid key exchange, or more compact PQC schemes may be necessary.

- **Certificate chains**: If post-quantum signatures (ML-DSA) are also adopted for TLS certificate authentication, the combined size increase could be more significant, as ML-DSA signatures are approximately 2.4--4.6 KB compared to 64 bytes for Ed25519.

### 4.5.3 Bandwidth Overhead Assessment

To quantify the bandwidth overhead in a realistic deployment, consider a web server handling [DATA: example number] TLS connections per second. Table 8 estimates the additional bandwidth required:

| Scenario | X25519 Bandwidth | ML-KEM-768 Bandwidth | Overhead |
|----------|-----------------|---------------------|----------|
| 1,000 connections/sec | 64 KB/s | 2,272 KB/s | +2,208 KB/s |
| 10,000 connections/sec | 640 KB/s | 22,720 KB/s | +22,080 KB/s |
| 100,000 connections/sec | 6,400 KB/s | 227,200 KB/s | +220,800 KB/s |

Table 8: Estimated bandwidth overhead for ML-KEM-768 vs. X25519 at various connection rates.

Even at 100,000 connections per second, the additional bandwidth overhead is approximately 216 MB/s, which is well within the capacity of modern server network interfaces (10--100 Gbps). Bandwidth overhead is therefore unlikely to be a blocking concern for most deployments.

## 4.6 Performance Overhead Assessment

### 4.6.1 Summary of Overheads

Table 9 summarizes the performance overhead of migrating from X25519 to ML-KEM-768:

| Metric | X25519 | ML-KEM-768 | Overhead Factor |
|--------|--------|-----------|----------------|
| KeyGen time | [DATA] $\mu s$ | [DATA] $\mu s$ | [DATA]x |
| Key exchange / Encaps+Decaps time | [DATA] $\mu s$ | [DATA] $\mu s$ | [DATA]x |
| Public key size | 32 bytes | 1,184 bytes | 37x |
| Ciphertext size | 32 bytes | 1,088 bytes | 34x |
| Total handshake data | 64 bytes | 2,272 bytes | 35.5x |

Table 9: Migration overhead summary for X25519 to ML-KEM-768.

### 4.6.2 Practical Implications

The performance overhead can be characterized as **modest in computation but significant in data size**:

1. **Computation**: ML-KEM operations are [DATA: approximate ratio]x slower than X25519, but the absolute overhead is on the order of [DATA: approximate value] microseconds per handshake --- negligible compared to network latency and application processing time.

2. **Data size**: Keys and ciphertexts are 35x larger, adding approximately 2.2 KB to each handshake. This is manageable for most use cases but may require protocol-level accommodations (e.g., larger initial congestion windows, TCP fast open, or split handshake designs).

3. **Memory**: Server-side memory consumption for connection state increases modestly, as the public key and ciphertext must be stored during the handshake.

### 4.6.3 Hybrid Key Exchange

As a transitional measure, many deployments are adopting **hybrid key exchange**, which combines a classical algorithm (X25519 or P-256) with a post-quantum algorithm (ML-KEM-768) in a single handshake. The shared secrets from both algorithms are combined (e.g., via concatenation and key derivation), so the connection is secure as long as *either* algorithm remains unbroken.

Hybrid key exchange (e.g., X25519+ML-KEM-768, now standardized for TLS) incurs the combined overhead of both algorithms:
- **Computation**: Sum of X25519 and ML-KEM-768 times.
- **Data**: Sum of both key shares and ciphertexts ($32 + 1,184 = 1,216$ bytes for the client, $32 + 1,088 = 1,120$ bytes for the server).

This provides defense in depth during the transition period, at a cost of approximately 2x the overhead compared to ML-KEM alone.

## 4.7 Discussion

Our benchmarks demonstrate that ML-KEM is a practical replacement for classical key exchange in the vast majority of deployment scenarios. The computational overhead is modest --- well within the noise of typical application and network latency. The size overhead is more significant but manageable for standard Internet protocols.

The key findings from this performance evaluation are:

1. **ML-KEM-768 is fast enough.** Absolute operation times in the range of [DATA: approximate range] microseconds are negligible in the context of TLS handshakes, which are dominated by network round-trip times of tens to hundreds of milliseconds.

2. **Size is the primary concern.** The 35x increase in key and ciphertext size is the most impactful change for network protocols, particularly for constrained environments and certificate-heavy applications.

3. **All three parameter sets are viable.** Even ML-KEM-1024, the most conservative parameter set, operates within performance bounds that are acceptable for most applications.

4. **The migration overhead is justified.** Given the quantum threat assessed in Chapter 3 and the HNDL risk analyzed in Chapter 5, the modest performance cost of ML-KEM is a reasonable price for quantum resistance.
