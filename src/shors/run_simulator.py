"""Run Shor's algorithm on the Qiskit Aer simulator.

Usage:
    python -m src.shors.run_simulator
"""

import csv
from pathlib import Path

import numpy as np
from qiskit_aer import AerSimulator

from src.shors.circuit import shors_circuit
from src.shors.classical import process_shor_result, classical_order


RESULTS_DIR = Path("results/raw")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_shors_simulator(N, a, shots=4096, n_count=None):
    """Run Shor's algorithm on the Aer simulator.

    Args:
        N: Number to factor.
        a: Base for modular exponentiation.
        shots: Number of measurement shots.
        n_count: Number of counting qubits (default: 2*ceil(log2(N))).

    Returns:
        Dict with measurement results and analysis.
    """
    print(f"\n{'='*60}")
    print(f"Shor's Algorithm: N={N}, a={a}")
    print(f"{'='*60}")

    # Classical verification
    r_classical = classical_order(a, N)
    print(f"Classical order of {a} mod {N}: r = {r_classical}")

    # Build circuit
    n_work = 4 if N == 15 else 5 if N == 21 else int(np.ceil(np.log2(N)))
    if n_count is None:
        n_count = 2 * n_work
    qc = shors_circuit(N, a, n_count=n_count)
    print(f"Circuit: {n_count} counting qubits + {n_work} work qubits "
          f"= {qc.num_qubits} total")
    print(f"Circuit depth: {qc.depth()}")
    print(f"Running {shots} shots on Aer simulator...")

    # Decompose custom gates so Aer can simulate them
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    sim = AerSimulator()
    pm = generate_preset_pass_manager(backend=sim, optimization_level=1)
    qc_transpiled = pm.run(qc)

    result = sim.run(qc_transpiled, shots=shots).result()
    counts = result.get_counts()

    # Process results
    analysis = process_shor_result(counts, n_count, a, N)

    # Print results
    print(f"\nMeasurement outcomes:")
    print(f"{'Bitstring':>12} {'Value':>6} {'Count':>6} {'Phase':>8} "
          f"{'r_cand':>7} {'Valid':>6} {'Factors'}")
    print(f"{'-'*70}")
    for m in sorted(analysis['measurements'], key=lambda x: -x['count']):
        factors_str = str(m['factors']) if m['factors'] else '-'
        print(f"{m['bitstring']:>12} {m['value']:>6} {m['count']:>6} "
              f"{m['phase']:>8.4f} {m['candidate_r']:>7} "
              f"{'✓' if m['valid_period'] else '✗':>6} {factors_str}")

    print(f"\nSuccess rate: {analysis['success_rate']:.1%} "
          f"({analysis['success_count']}/{analysis['total_shots']})")
    if analysis['factors_found']:
        print(f"Factors found: {analysis['factors_found']}")
    else:
        print("No factors found in this run.")

    return analysis, counts


def save_results(analysis, filepath):
    """Save measurement results to CSV."""
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'bitstring', 'value', 'count', 'phase',
            'candidate_r', 'valid_period', 'factors'
        ])
        writer.writeheader()
        for m in analysis['measurements']:
            writer.writerow({
                'bitstring': m['bitstring'],
                'value': m['value'],
                'count': m['count'],
                'phase': f"{m['phase']:.6f}",
                'candidate_r': m['candidate_r'],
                'valid_period': m['valid_period'],
                'factors': str(m['factors']) if m['factors'] else '',
            })


def main():
    """Run Shor's algorithm for N=15 and N=21 on simulator."""
    # N=15, a=7: expected period r=4, factors 3×5
    analysis_15, counts_15 = run_shors_simulator(N=15, a=7, shots=4096)
    save_results(analysis_15, RESULTS_DIR / "shors_simulator_N15.csv")
    print(f"\nResults saved to {RESULTS_DIR / 'shors_simulator_N15.csv'}")

    # N=15, a=11: expected period r=2, factors 3×5
    analysis_15b, _ = run_shors_simulator(N=15, a=11, shots=4096)
    save_results(analysis_15b, RESULTS_DIR / "shors_simulator_N15_a11.csv")

    # N=21, a=2: expected period r=6, factors 3×7
    print("\n\n" + "="*60)
    print("Attempting N=21 (larger, more complex circuit)")
    print("="*60)
    analysis_21, counts_21 = run_shors_simulator(N=21, a=2, shots=4096)
    save_results(analysis_21, RESULTS_DIR / "shors_simulator_N21.csv")
    print(f"\nResults saved to {RESULTS_DIR / 'shors_simulator_N21.csv'}")

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"N=15 (a=7):  success rate = {analysis_15['success_rate']:.1%}, "
          f"factors = {analysis_15['factors_found']}")
    print(f"N=15 (a=11): success rate = {analysis_15b['success_rate']:.1%}, "
          f"factors = {analysis_15b['factors_found']}")
    print(f"N=21 (a=2):  success rate = {analysis_21['success_rate']:.1%}, "
          f"factors = {analysis_21['factors_found']}")


if __name__ == "__main__":
    main()
