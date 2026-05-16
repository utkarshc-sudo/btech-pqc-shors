# Chapter 2: Background

This chapter provides the theoretical and technical foundations required to understand both the quantum threat to current cryptographic systems and the post-quantum defense mechanisms designed to replace them. We begin with quantum computing fundamentals, proceed through the RSA cryptosystem and Shor's algorithm, and conclude with lattice-based cryptography and the ML-KEM standard.

## 2.1 Quantum Computing Fundamentals

### 2.1.1 Qubits and Quantum States

The fundamental unit of quantum information is the **qubit** (quantum bit). Unlike a classical bit, which takes a definite value of 0 or 1, a qubit can exist in a **superposition** of both states simultaneously. Mathematically, the state of a single qubit is represented as a vector in a two-dimensional complex Hilbert space $\mathcal{H} = \mathbb{C}^2$:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$

where $\alpha, \beta \in \mathbb{C}$ are probability amplitudes satisfying the normalization constraint $|\alpha|^2 + |\beta|^2 = 1$. The states $|0\rangle$ and $|1\rangle$ form the computational basis, corresponding to the classical bit values 0 and 1. When a qubit is measured in the computational basis, the outcome is $|0\rangle$ with probability $|\alpha|^2$ and $|1\rangle$ with probability $|\beta|^2$, and the superposition collapses to the observed state.

For an $n$-qubit system, the state space is the tensor product $\mathcal{H}^{\otimes n} = \mathbb{C}^{2^n}$. A general $n$-qubit state is:

$$|\psi\rangle = \sum_{x=0}^{2^n - 1} \alpha_x |x\rangle, \quad \sum_{x=0}^{2^n - 1} |\alpha_x|^2 = 1$$

This exponential scaling of the state space is the fundamental source of quantum computational power: $n$ qubits can simultaneously encode $2^n$ amplitudes, whereas $n$ classical bits can represent only a single $n$-bit string at any given time.

### 2.1.2 Quantum Gates

Quantum computation proceeds by applying **quantum gates** --- unitary transformations --- to qubits. Unitarity ($U^\dagger U = I$) ensures that quantum operations are reversible and preserve the normalization of quantum states. The most commonly used gates include:

- **Pauli-X gate** (quantum NOT): $X|0\rangle = |1\rangle$, $X|1\rangle = |0\rangle$. This is the quantum analogue of a classical NOT gate.

- **Hadamard gate**: $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$, $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. The Hadamard gate creates superposition from a definite state and is ubiquitous in quantum algorithms.

- **Phase rotation gates**: $R_k = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i / 2^k} \end{pmatrix}$. These gates add a relative phase to the $|1\rangle$ component and are the building blocks of the Quantum Fourier Transform.

- **CNOT gate** (controlled-NOT): A two-qubit gate that flips the target qubit if and only if the control qubit is $|1\rangle$. It is the primary gate for creating entanglement. Applied to $|+\rangle|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|0\rangle$, the CNOT produces the Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.

- **Controlled-U gates**: Generalization of CNOT where an arbitrary unitary $U$ is applied to the target register, conditioned on the control qubit being $|1\rangle$. These are essential in Shor's algorithm for implementing controlled modular exponentiation.

Any quantum computation can be decomposed into a sequence of single-qubit gates and CNOT gates, a property known as **universality**. In practice, quantum hardware natively supports a specific gate set (the basis gates), and compilers decompose abstract circuits into sequences of basis gates.

### 2.1.3 Quantum Circuits and Measurement

A **quantum circuit** is a sequence of quantum gates applied to a register of qubits, read from left to right. The circuit model is the most widely used framework for describing quantum algorithms. A circuit consists of:

1. **Initialization**: All qubits start in a known state, typically $|0\rangle^{\otimes n}$.
2. **Gate application**: A sequence of unitary gates acts on one or more qubits.
3. **Measurement**: One or more qubits are measured in the computational basis, producing classical bit outcomes.

Measurement is inherently probabilistic: a quantum circuit is typically executed many times (called **shots**), and the distribution of outcomes is collected as a histogram. For algorithms like Shor's, the outcome distribution contains the information needed to extract the answer (e.g., the period of a function) through classical post-processing.

### 2.1.4 Entanglement

Two qubits are **entangled** when their joint state cannot be written as a tensor product of individual qubit states. The archetypal entangled state is the Bell state:

$$|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$$

Measuring the first qubit of $|\Phi^+\rangle$ yields $|0\rangle$ or $|1\rangle$ with equal probability, but the second qubit is then guaranteed to be in the same state. This correlation is stronger than any classical correlation can produce (as formalized by Bell's theorem) and is a computational resource exploited by quantum algorithms.

In Shor's algorithm, entanglement between the counting register and the work register encodes the periodicity of the modular exponentiation function into correlations that the Quantum Fourier Transform can subsequently extract.

### 2.1.5 Quantum Noise and Decoherence

Real quantum computers are subject to **noise**: unintended interactions between qubits and their environment that cause errors. The principal noise mechanisms are:

- **Decoherence**: Loss of quantum information over time. Characterized by $T_1$ (energy relaxation time, the timescale for a qubit in $|1\rangle$ to decay to $|0\rangle$) and $T_2$ (dephasing time, the timescale for loss of phase coherence in superposition states).

- **Gate errors**: Imperfect implementation of quantum gates, typically characterized by the gate fidelity (the overlap between the ideal and actual gate operation). Single-qubit gate error rates on current hardware are approximately $10^{-4}$ to $10^{-3}$; two-qubit gate error rates are approximately $10^{-3}$ to $10^{-2}$.

- **Measurement errors**: Misidentification of qubit states during measurement, with typical error rates of $10^{-2}$ to $10^{-1}$.

- **Crosstalk**: Unintended interactions between nearby qubits during gate operations.

These noise sources compound with circuit depth (the number of sequential gate layers) and qubit count. Current devices are classified as **noisy intermediate-scale quantum (NISQ)** computers [Preskill, 2018], meaning they have enough qubits to be beyond classical simulation for certain tasks but too much noise for fault-tolerant computation. Quantum error correction, which encodes logical qubits in many physical qubits, is necessary for fault-tolerant algorithms like Shor's at cryptographic scale.

## 2.2 RSA and the Integer Factoring Assumption

The RSA cryptosystem [Rivest et al., 1978] is among the most widely deployed public-key algorithms. Its security rests on the **integer factorization problem**: given a composite integer $N = pq$ (the product of two large primes $p$ and $q$), find $p$ and $q$.

### 2.2.1 RSA Key Generation and Operations

RSA key generation proceeds as follows:

1. Select two large primes $p$ and $q$, each approximately $n/2$ bits long.
2. Compute $N = pq$ (the modulus) and $\phi(N) = (p-1)(q-1)$ (Euler's totient).
3. Choose a public exponent $e$ coprime to $\phi(N)$ (commonly $e = 65537$).
4. Compute the private exponent $d = e^{-1} \mod \phi(N)$.
5. The public key is $(N, e)$; the private key is $(N, d)$.

Encryption of message $m$: $c = m^e \mod N$. Decryption: $m = c^d \mod N$.

The security assumption is that an adversary who knows only the public key $(N, e)$ cannot efficiently compute $d$ without knowing $\phi(N)$, and computing $\phi(N)$ requires factoring $N$. For $n = 2048$ bits (the current minimum recommended key size), the best-known classical factoring algorithm, the general number field sieve (GNFS), has a running time of:

$$L_N\left[\frac{1}{3}, \left(\frac{64}{9}\right)^{1/3}\right] = \exp\left(\left(\frac{64}{9}\right)^{1/3} (\ln N)^{1/3} (\ln \ln N)^{2/3}\right)$$

This is sub-exponential but super-polynomial, making 2048-bit RSA infeasible to break with current classical computing resources. The largest RSA modulus factored to date is RSA-250 (829 bits), achieved in 2020 using approximately 2,700 core-years of computation [Boudot et al., 2020].

### 2.2.2 The Factoring Problem and Shor's Algorithm

Shor's algorithm reduces the factoring problem to **period-finding** (also called order-finding), which can be solved efficiently on a quantum computer. This relationship is at the heart of the quantum threat to RSA and will be detailed in Section 2.3.

## 2.3 Shor's Algorithm

Shor's algorithm [Shor, 1994] factors an integer $N$ in polynomial time on a quantum computer. The algorithm consists of a classical reduction to period-finding, a quantum subroutine that finds the period using the Quantum Fourier Transform, and classical post-processing to extract the factors.

### 2.3.1 Reduction to Period-Finding

The classical reduction works as follows:

1. **Check for trivial cases.** If $N$ is even, return 2 as a factor. If $N = a^b$ for integers $a, b > 1$, return $a$.

2. **Choose a random base.** Pick a random integer $a$ with $1 < a < N$. Compute $\gcd(a, N)$; if this is greater than 1, we have found a non-trivial factor (this is unlikely but possible).

3. **Find the period.** Determine the multiplicative order $r$ of $a$ modulo $N$, defined as the smallest positive integer $r$ such that $a^r \equiv 1 \pmod{N}$.

4. **Extract factors.** If $r$ is even and $a^{r/2} \not\equiv -1 \pmod{N}$, then compute:
   $$p = \gcd(a^{r/2} + 1, N), \quad q = \gcd(a^{r/2} - 1, N)$$
   With probability at least $1/2$, at least one of $p$ or $q$ is a non-trivial factor of $N$.

5. **Repeat if necessary.** If the attempt fails (odd $r$, or $a^{r/2} \equiv -1$), choose a new random $a$ and repeat.

The probability of success in a single attempt is at least $1 - 1/2^{k-1}$ where $k$ is the number of distinct prime factors of $N$. For an RSA modulus (the product of exactly two primes), the success probability per attempt is at least $1/2$, so $O(\log N)$ repetitions suffice with high probability.

**Example.** For $N = 15$ and $a = 7$:
- The sequence $7^0, 7^1, 7^2, 7^3, 7^4 \pmod{15}$ is $1, 7, 4, 13, 1, \ldots$, giving period $r = 4$.
- Since $r$ is even: $\gcd(7^2 + 1, 15) = \gcd(50, 15) = 5$ and $\gcd(7^2 - 1, 15) = \gcd(48, 15) = 3$.
- Thus $15 = 3 \times 5$.

### 2.3.2 The Quantum Period-Finding Subroutine

The quantum part of Shor's algorithm finds the period $r$ of the function $f(x) = a^x \mod N$ using quantum parallelism and the Quantum Fourier Transform. The circuit consists of two registers:

- **Counting register**: $n_c$ qubits (typically $n_c = 2\lceil\log_2 N\rceil$), which will encode the period information.
- **Work register**: $\lceil\log_2 N\rceil$ qubits, which will hold the values of $f(x)$.

The algorithm proceeds as follows:

1. **Initialize.** Prepare the counting register in $|0\rangle^{\otimes n_c}$ and the work register in $|1\rangle$ (representing $a^0 \mod N = 1$).

2. **Create superposition.** Apply Hadamard gates to all counting qubits, creating:
   $$\frac{1}{\sqrt{2^{n_c}}} \sum_{x=0}^{2^{n_c}-1} |x\rangle |1\rangle$$

3. **Controlled modular exponentiation.** For each counting qubit $j$ (from 0 to $n_c - 1$), apply a controlled gate that multiplies the work register by $a^{2^j} \mod N$, controlled by the $j$-th counting qubit. The resulting state is:
   $$\frac{1}{\sqrt{2^{n_c}}} \sum_{x=0}^{2^{n_c}-1} |x\rangle |a^x \mod N\rangle$$

4. **Apply the inverse QFT** to the counting register. The QFT maps the periodic structure encoded in the amplitudes to peaks in the frequency domain at multiples of $2^{n_c}/r$.

5. **Measure** the counting register. The outcome is an integer $y$ close to some multiple of $2^{n_c}/r$, i.e., $y \approx s \cdot 2^{n_c}/r$ for some integer $s \in \{0, 1, \ldots, r-1\}$.

### 2.3.3 The Quantum Fourier Transform

The Quantum Fourier Transform (QFT) is the quantum analogue of the discrete Fourier transform (DFT). It maps a computational basis state $|j\rangle$ to:

$$\text{QFT}|j\rangle = \frac{1}{\sqrt{2^n}} \sum_{k=0}^{2^n - 1} e^{2\pi i \cdot jk / 2^n} |k\rangle$$

The QFT can be decomposed into a circuit of $O(n^2)$ gates, consisting of Hadamard gates and controlled phase rotation gates $CR_k$ where $R_k$ applies a phase of $e^{2\pi i / 2^k}$. This is an exponential improvement over the classical Fast Fourier Transform, which requires $O(n \cdot 2^n)$ operations. The circuit structure is:

1. Apply $H$ to qubit $n-1$.
2. For each qubit $j$ from $n-2$ down to $0$, apply a controlled-$R_{n-j}$ gate from qubit $j$ to qubit $n-1$.
3. Repeat steps 1--2 for qubit $n-2$ (with fewer controlled rotations), then $n-3$, and so on.
4. Swap the qubit ordering to produce the standard QFT output.

The inverse QFT ($\text{QFT}^\dagger$) is the conjugate transpose of the QFT circuit, obtained by reversing the gate order and negating all rotation angles. It is the inverse QFT that appears in Shor's algorithm, converting the periodic amplitude pattern into measurable peaks.

### 2.3.4 Classical Post-Processing

After measuring the counting register, the outcome $y$ is an integer satisfying $y/2^{n_c} \approx s/r$ for some unknown integer $s$. The continued fractions algorithm extracts $r$ from this rational approximation:

1. Compute the phase estimate $\phi = y / 2^{n_c}$.
2. Find the best rational approximation $s/r$ to $\phi$ with $r \leq N$, using the continued fractions expansion.
3. Check whether $a^r \equiv 1 \pmod{N}$. If so, $r$ is a valid candidate period.
4. Attempt to extract factors using $\gcd(a^{r/2} \pm 1, N)$.

Multiple measurements may be needed, as the algorithm can produce $y = 0$ (which yields no information) or values of $s$ that share a common factor with $r$ (yielding a divisor of $r$ rather than $r$ itself).

### 2.3.5 Complexity Analysis

The overall complexity of Shor's algorithm is dominated by the modular exponentiation circuit. For an $n$-bit number $N$, the circuit requires $O(n)$ logical qubits for the work register, $O(n)$ counting qubits, and $O(n^3)$ elementary gate operations for the modular exponentiation (or $O(n^2 \log n \log \log n)$ using optimized multiplication). The classical post-processing runs in polynomial time. The total algorithm runs in polynomial time, providing an exponential speedup over the best-known classical factoring algorithms.

## 2.4 Lattice-Based Cryptography

### 2.4.1 Lattices and Hard Problems

A **lattice** $\mathcal{L}$ in $\mathbb{R}^n$ is the set of all integer linear combinations of a set of linearly independent basis vectors $\mathbf{b}_1, \ldots, \mathbf{b}_m$:

$$\mathcal{L} = \left\{ \sum_{i=1}^m z_i \mathbf{b}_i : z_i \in \mathbb{Z} \right\}$$

Several computational problems on lattices are believed to be hard for both classical and quantum computers, making them attractive foundations for post-quantum cryptography. The principal hard lattice problems are:

- **Shortest Vector Problem (SVP)**: Given a lattice basis, find the shortest non-zero lattice vector. The best-known quantum algorithms for SVP still require exponential time.

- **Learning With Errors (LWE)** [Regev, 2005]: Given a matrix $\mathbf{A} \in \mathbb{Z}_q^{m \times n}$, a secret vector $\mathbf{s} \in \mathbb{Z}_q^n$, and an error vector $\mathbf{e}$ drawn from a discrete Gaussian distribution, distinguish $(\mathbf{A}, \mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e} \mod q)$ from $(\mathbf{A}, \mathbf{u})$ where $\mathbf{u}$ is uniformly random. Regev showed a quantum reduction from worst-case lattice problems (GapSVP and SIVP) to LWE, providing strong theoretical evidence for the hardness of LWE.

### 2.4.2 Module Learning With Errors (MLWE)

The **Module-LWE (MLWE)** problem is a structured variant of LWE that provides a balance between the unstructured LWE problem (which has large key sizes) and the Ring-LWE problem (which has very efficient operations but relies on the structure of a single polynomial ring).

In MLWE, the matrix $\mathbf{A}$ is drawn from the ring $R_q^{k \times k}$, where $R_q = \mathbb{Z}_q[X]/(X^n + 1)$ is a polynomial ring with $n$ a power of 2 and $q$ a prime. The secret and error vectors are elements of $R_q^k$. The MLWE problem is: given $(\mathbf{A}, \mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e})$ in $R_q^{k \times k} \times R_q^k$, distinguish this from uniformly random.

The parameter $k$ (the module rank) controls the security-efficiency trade-off:
- $k = 1$ recovers Ring-LWE (most efficient, strongest algebraic structure assumptions).
- $k = n$ recovers plain LWE (least efficient, weakest structural assumptions).
- Intermediate values of $k$ (2, 3, 4) provide practical efficiency with reduced dependence on ring structure.

The algebraic structure of $R_q$ enables the use of the **Number Theoretic Transform (NTT)**, the finite-field analogue of the FFT, for fast polynomial multiplication in $O(n \log n)$ instead of $O(n^2)$. This is critical for the practical efficiency of ML-KEM.

## 2.5 ML-KEM (FIPS 203)

### 2.5.1 Overview

ML-KEM (Module-Lattice-Based Key Encapsulation Mechanism) is the NIST standard for post-quantum key encapsulation, published as FIPS 203 in August 2024 [NIST, 2024]. It is derived from the CRYSTALS-Kyber algorithm, which was selected through NIST's multi-round post-quantum cryptography competition. ML-KEM is an IND-CCA2-secure KEM, meaning it is secure against adaptive chosen-ciphertext attacks, the strongest standard notion of security for public-key encryption/KEM schemes.

A KEM provides three operations:
- **KeyGen()**: Generate a public key $pk$ and a secret key $sk$.
- **Encaps($pk$)**: Using the public key, produce a shared secret $K$ and a ciphertext $ct$.
- **Decaps($sk$, $ct$)**: Using the secret key and ciphertext, recover the shared secret $K$.

The shared secret $K$ is then used as the key for a symmetric cipher (e.g., AES-256) to encrypt the actual data. This is the standard paradigm for hybrid encryption, and ML-KEM is a direct replacement for classical key exchange mechanisms such as ECDH.

### 2.5.2 Parameter Sets

ML-KEM defines three parameter sets targeting different security levels:

| Parameter | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|-----------|-----------|-----------|------------|
| Module rank $k$ | 2 | 3 | 4 |
| Polynomial degree $n$ | 256 | 256 | 256 |
| Modulus $q$ | 3329 | 3329 | 3329 |
| NIST security level | 1 (128-bit) | 3 (192-bit) | 5 (256-bit) |
| Public key size (bytes) | 800 | 1,184 | 1,568 |
| Ciphertext size (bytes) | 768 | 1,088 | 1,568 |
| Shared secret size (bytes) | 32 | 32 | 32 |

Table 1: ML-KEM parameter sets and sizes.

The NIST security levels correspond to the estimated computational effort required to break the scheme:
- **Level 1**: At least as hard to break as AES-128 (exhaustive key search).
- **Level 3**: At least as hard to break as AES-192.
- **Level 5**: At least as hard to break as AES-256.

ML-KEM-768 (Level 3) is the recommended parameter set for most applications, balancing security margin against performance and size overhead.

### 2.5.3 Internal Structure

The internal construction of ML-KEM follows the Fujisaki-Okamoto (FO) transform applied to a CPA-secure public-key encryption scheme based on MLWE. At a high level:

1. **KeyGen**: Sample a random matrix $\mathbf{A} \in R_q^{k \times k}$ (derived from a seed via an extendable output function), sample secret and error vectors $\mathbf{s}, \mathbf{e} \leftarrow \beta_\eta$, compute the public key $\mathbf{t} = \mathbf{A}\mathbf{s} + \mathbf{e}$. The public key is $(\mathbf{A}, \mathbf{t})$ (compressed); the secret key includes $\mathbf{s}$.

2. **Encaps**: Sample a random message $m$, derive randomness from $m$ and $pk$ via a hash, encrypt $m$ under the CPA-secure scheme (producing ciphertext $ct$), and derive the shared secret $K$ from $m$, $ct$, and a hash of $pk$.

3. **Decaps**: Decrypt $ct$ to recover $m'$, re-encrypt $m'$ to obtain $ct'$, and compare $ct'$ with $ct$. If they match, output $K = \text{KDF}(m', H(ct))$; otherwise, output a pseudorandom value derived from the secret key (implicit rejection). This re-encryption check is the core of the FO transform and provides CCA2 security.

### 2.5.4 Comparison with Classical Key Exchange

For context, the most widely used classical key exchange mechanism in modern TLS is X25519, an elliptic-curve Diffie-Hellman (ECDH) scheme on Curve25519 [Bernstein, 2006]. Table 2 compares ML-KEM-768 with X25519:

| Property | X25519 | ML-KEM-768 | Ratio |
|----------|--------|-----------|-------|
| Public key (bytes) | 32 | 1,184 | 37x |
| Ciphertext / DH share (bytes) | 32 | 1,088 | 34x |
| Shared secret (bytes) | 32 | 32 | 1x |
| NIST security level | ~128-bit classical | Level 3 (192-bit PQ) | --- |
| Quantum-safe | No | Yes | --- |

Table 2: Size comparison between X25519 and ML-KEM-768.

The key and ciphertext size increase is the primary practical concern for migration. In a TLS 1.3 handshake, the client sends a key share in the ClientHello message, and the server responds with a key share in the ServerHello. Replacing X25519 with ML-KEM-768 increases the handshake payload by approximately 2.2 KB, which may affect performance on bandwidth-constrained or latency-sensitive connections.

## 2.6 Current Quantum Hardware Landscape

### 2.6.1 Superconducting Qubits

The dominant quantum computing platform is superconducting transmon qubits, developed by IBM, Google, and others. Key milestones include:

- **IBM**: The Eagle processor (127 qubits, 2021), Osprey (433 qubits, 2022), Condor (1,121 qubits, 2023), and the Heron processor (133 qubits with improved connectivity and lower error rates, 2024). IBM's roadmap targets 100,000+ qubits by 2033 through modular architectures connecting multiple processors.

- **Google**: The Sycamore processor (53 qubits) demonstrated "quantum supremacy" in 2019 by performing a sampling task faster than any classical computer [Arute et al., 2019]. The Willow processor (105 qubits, 2024) demonstrated below-threshold quantum error correction, a milestone where adding more qubits to an error-correcting code reduces the logical error rate rather than increasing it.

- **Other platforms**: Trapped-ion systems (IonQ, Quantinuum), neutral-atom systems (QuEra, Pasqal), and photonic systems (PsiQuantum, Xanadu) represent alternative approaches, each with distinct advantages in connectivity, gate fidelity, and scalability.

### 2.6.2 The Gap to Cryptographic Relevance

Despite impressive progress, current quantum hardware is far from threatening real-world cryptography. The key metrics illustrate the gap:

- **Qubit count**: Current devices have $O(10^3)$ physical qubits. Breaking RSA-2048 requires approximately $2 \times 10^7$ physical qubits [Gidney and Ekera, 2021], a factor of $\sim 10^4$ beyond current capabilities.

- **Error rates**: Current two-qubit gate error rates are $\sim 10^{-3}$ to $10^{-2}$. Fault-tolerant Shor's algorithm using surface codes requires physical error rates below $\sim 10^{-3}$ (the surface code threshold) to function, and lower error rates reduce the overhead of error correction.

- **Circuit depth**: Shor's algorithm for RSA-2048 requires circuits with depths on the order of $10^8$ to $10^9$ gate layers. Current devices support circuit depths of $O(10^2)$ before noise overwhelms the computation.

- **Error correction overhead**: Each logical qubit in a surface code requires $O(d^2)$ physical qubits, where $d$ is the code distance. For the error rates and logical error rates needed, $d \approx 20$--30, meaning each logical qubit requires roughly 1,000 physical qubits. The 4,000+ logical qubits needed for Shor's algorithm thus translate to approximately 20 million physical qubits.

These estimates place a cryptographically relevant quantum computer (CRQC) at least a decade away under optimistic projections, and potentially several decades under conservative assumptions. Nevertheless, the HNDL threat model (Section 1.3) means that the transition to post-quantum cryptography should begin now, even if the full threat is not yet imminent.

### 2.6.3 IBM Quantum Access Model

For this project, we use IBM Quantum's cloud-accessible quantum hardware via the Qiskit SDK. IBM provides several tiers of access:

- **Simulators**: The Qiskit Aer simulator provides noise-free and configurable-noise simulation of quantum circuits on classical hardware. This allows testing circuit correctness and studying noise models without consuming hardware resources.

- **Real hardware**: IBM Quantum provides cloud access to real superconducting quantum processors. Jobs are submitted to a queue and executed asynchronously. For educational and research use, IBM offers free access to processors with up to 127 qubits via the IBM Quantum Platform.

The combination of simulator and hardware execution allows us to isolate the effect of quantum noise: a circuit that succeeds on the simulator but fails on hardware demonstrates the impact of real-world noise on algorithmic performance.
