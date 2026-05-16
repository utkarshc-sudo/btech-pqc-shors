"""Classical post-processing for Shor's algorithm.

Contains:
- GCD via Euclidean algorithm
- Continued fractions expansion
- Period extraction from QFT measurement
- Factor extraction from period
"""

from math import gcd, log2, ceil
from fractions import Fraction


def classical_order(a, N):
    """Find the multiplicative order of a modulo N by brute force.

    The order r is the smallest positive integer such that a^r ≡ 1 (mod N).

    This is the classical method — exponential time for large N.
    Shor's algorithm finds r in polynomial time on a quantum computer.

    Args:
        a: Base (must be coprime to N).
        N: Modulus.

    Returns:
        The order r, or None if a is not coprime to N.
    """
    if gcd(a, N) != 1:
        return None
    r = 1
    current = a % N
    while current != 1:
        current = (current * a) % N
        r += 1
        if r > N:
            return None  # safety: shouldn't happen if a is coprime to N
    return r


def measurement_to_phase(measured_value, n_count):
    """Convert a measurement outcome to an estimated phase.

    The QFT produces values that are multiples of 2^n_count / r,
    where r is the period. Dividing by 2^n_count gives the phase s/r.

    Args:
        measured_value: Integer measured from the counting register.
        n_count: Number of qubits in the counting register.

    Returns:
        Float phase estimate (measured_value / 2^n_count).
    """
    return measured_value / (2**n_count)


def phase_to_period(phase, N, max_denominator=None):
    """Extract the period r from a phase estimate using continued fractions.

    The phase should be approximately s/r for some integer s.
    We use Python's Fraction to find the best rational approximation
    with denominator ≤ N (since r < N).

    Args:
        phase: Float phase estimate from measurement_to_phase.
        N: The number being factored (used as max_denominator if not specified).
        max_denominator: Maximum allowed denominator. Defaults to N.

    Returns:
        Candidate period r (the denominator of the fraction).
    """
    if max_denominator is None:
        max_denominator = N
    if phase == 0:
        return 0
    frac = Fraction(phase).limit_denominator(max_denominator)
    return frac.denominator


def find_factors_from_period(a, r, N):
    """Attempt to find factors of N given the period r of a^x mod N.

    If r is even, we compute gcd(a^(r/2) ± 1, N).
    With probability ≥ 1/2, this gives non-trivial factors.

    Args:
        a: Base used in modular exponentiation.
        r: Period (order of a modulo N).
        N: Number to factor.

    Returns:
        Tuple (p, q) of factors, or None if this attempt fails.
    """
    if r == 0:
        return None
    if r % 2 != 0:
        return None  # r must be even

    x = pow(a, r // 2, N)
    if x == N - 1:
        return None  # trivial: a^(r/2) ≡ -1 (mod N)

    p = gcd(x + 1, N)
    q = gcd(x - 1, N)

    if p == 1 or p == N:
        p = None
    if q == 1 or q == N:
        q = None

    if p and q:
        return (min(p, q), max(p, q))
    elif p:
        return (p, N // p)
    elif q:
        return (q, N // q)
    return None


def process_shor_result(counts, n_count, a, N):
    """Process all measurement outcomes from Shor's circuit.

    For each measurement outcome:
    1. Convert to phase estimate
    2. Use continued fractions to find candidate period r
    3. Verify r by checking a^r ≡ 1 (mod N)
    4. Attempt to find factors from valid periods

    Args:
        counts: Dict of {bitstring: count} from quantum measurement.
        n_count: Number of counting qubits.
        a: Base used in modular exponentiation.
        N: Number to factor.

    Returns:
        Dict with keys:
            'measurements': list of {value, phase, candidate_r, valid, factors}
            'success_count': number of measurements that led to factors
            'total_shots': total number of shots
            'factors_found': set of factor pairs found
    """
    total_shots = sum(counts.values())
    measurements = []
    success_count = 0
    factors_found = set()

    for bitstring, count in sorted(counts.items()):
        measured_value = int(bitstring, 2)
        phase = measurement_to_phase(measured_value, n_count)
        candidate_r = phase_to_period(phase, N)

        # Verify: does a^r ≡ 1 (mod N)?
        valid = False
        if candidate_r > 0:
            valid = pow(a, candidate_r, N) == 1

        # Try to extract factors
        factors = None
        if valid:
            factors = find_factors_from_period(a, candidate_r, N)
            if factors:
                success_count += count
                factors_found.add(factors)

        measurements.append({
            'bitstring': bitstring,
            'value': measured_value,
            'count': count,
            'phase': phase,
            'candidate_r': candidate_r,
            'valid_period': valid,
            'factors': factors,
        })

    return {
        'measurements': measurements,
        'success_count': success_count,
        'total_shots': total_shots,
        'success_rate': success_count / total_shots if total_shots > 0 else 0,
        'factors_found': factors_found,
    }
