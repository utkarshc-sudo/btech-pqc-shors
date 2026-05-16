"""Direct hardware submission for Shor's algorithm (no interactive prompts).

Usage:
    python -m src.shors.submit_hardware
"""

import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

from src.shors.circuit import shors_circuit
from src.shors.classical import process_shor_result, classical_order


RESULTS_DIR = Path("results/raw")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    load_dotenv()
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token or token == "paste_your_token_here":
        raise RuntimeError("IBM_QUANTUM_TOKEN not set in .env")

    # Initialize service
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)

    # Build Shor's circuit for N=15, a=7
    N, a, n_count = 15, 7, 8
    shots = 100
    print(f"\nBuilding Shor's circuit: N={N}, a={a}, n_count={n_count}")
    qc = shors_circuit(N, a, n_count=n_count)
    print(f"Circuit: {qc.num_qubits} qubits, depth={qc.depth()}")

    # Get backend
    print("\nFinding least busy backend...")
    backend = service.least_busy(
        simulator=False,
        min_num_qubits=qc.num_qubits,
        operational=True,
    )
    print(f"Selected: {backend.name} ({backend.num_qubits} qubits)")

    # Transpile
    print("Transpiling...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    qc_t = pm.run(qc)
    print(f"Transpiled depth: {qc_t.depth()}, gates: {sum(qc_t.count_ops().values())}")

    # Submit
    print(f"\nSubmitting {shots} shots to {backend.name}...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([qc_t], shots=shots)
    print(f"Job ID: {job.job_id()}")
    print("Waiting for results...")

    result = job.result()
    pub_result = result[0]
    counts = pub_result.data.meas.get_counts()
    print(f"Received {sum(counts.values())} results from hardware.")

    # Process
    analysis = process_shor_result(counts, n_count, a, N)

    print(f"\nHardware Results ({backend.name}):")
    print(f"{'Bitstring':>12} {'Value':>6} {'Count':>6} {'Phase':>8} "
          f"{'r_cand':>7} {'Valid':>6} {'Factors'}")
    print("-" * 70)
    for m in sorted(analysis['measurements'], key=lambda x: -x['count']):
        factors_str = str(m['factors']) if m['factors'] else '-'
        print(f"{m['bitstring']:>12} {m['value']:>6} {m['count']:>6} "
              f"{m['phase']:>8.4f} {m['candidate_r']:>7} "
              f"{'Y' if m['valid_period'] else 'N':>6} {factors_str}")

    print(f"\nSuccess rate: {analysis['success_rate']:.1%} "
          f"({analysis['success_count']}/{analysis['total_shots']})")
    print(f"Factors found: {analysis['factors_found']}")

    # Save
    outpath = RESULTS_DIR / "shors_hardware_N15.csv"
    with open(outpath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'bitstring', 'value', 'count', 'phase',
            'candidate_r', 'valid_period', 'factors', 'backend'
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
                'backend': backend.name,
            })
    print(f"\nSaved to {outpath}")


if __name__ == "__main__":
    main()
