"""Run Shor's algorithm on IBM Quantum hardware.

Usage:
    python -m src.shors.run_hardware

Requires:
    - IBM Quantum token in .env file
    - Explicit user confirmation before submitting jobs
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


def get_ibm_service():
    """Initialize IBM Quantum service from .env token."""
    load_dotenv()
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token or token == "paste_your_token_here":
        raise RuntimeError(
            "IBM_QUANTUM_TOKEN not set. Update your .env file with a valid token "
            "from https://quantum.ibm.com/account"
        )
    service = QiskitRuntimeService(
        channel="ibm_quantum",
        token=token,
    )
    return service


def run_shors_hardware(N, a, shots=100, n_count=8):
    """Run Shor's algorithm on IBM Quantum hardware.

    Args:
        N: Number to factor (15 or 21).
        a: Base for modular exponentiation.
        shots: Number of measurement shots (default 100 to conserve quota).
        n_count: Number of counting qubits.

    Returns:
        Dict with measurement results and analysis.
    """
    print(f"\n{'='*60}")
    print(f"Shor's Algorithm on REAL HARDWARE: N={N}, a={a}")
    print(f"{'='*60}")

    # Classical verification
    r_classical = classical_order(a, N)
    print(f"Classical order of {a} mod {N}: r = {r_classical}")

    # Build circuit
    qc = shors_circuit(N, a, n_count=n_count)
    print(f"\nCircuit: {qc.num_qubits} qubits, depth={qc.depth()}")

    # Quota warning
    print(f"\n*** QUOTA WARNING ***")
    print(f"  Qubits: {qc.num_qubits}")
    print(f"  Shots: {shots}")
    print(f"  This will consume IBM Quantum quota.")

    confirm = input("  Submit to IBM Quantum hardware? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("  Cancelled by user.")
        return None, None

    # Connect to IBM Quantum
    print("\nConnecting to IBM Quantum...")
    service = get_ibm_service()

    # Get least busy backend
    backend = service.least_busy(
        simulator=False,
        min_num_qubits=qc.num_qubits,
        operational=True,
    )
    print(f"Selected backend: {backend.name}")
    print(f"Backend qubits: {backend.num_qubits}")

    # Transpile for the specific backend
    print("Transpiling circuit for hardware...")
    pm = generate_preset_pass_manager(
        backend=backend,
        optimization_level=3,
    )
    transpiled = pm.run(qc)
    print(f"Transpiled depth: {transpiled.depth()}")
    print(f"Transpiled gate count: {dict(transpiled.count_ops())}")

    # Run on hardware
    print(f"\nSubmitting job ({shots} shots)...")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([transpiled], shots=shots)
    print(f"Job ID: {job.job_id()}")
    print("Waiting for results (this may take several minutes)...")

    result = job.result()
    pub_result = result[0]

    # Extract counts from SamplerV2 result
    counts = pub_result.data.meas.get_counts()
    print(f"Received {sum(counts.values())} measurement results.")

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
    print(f"Backend: {backend.name}")
    if analysis['factors_found']:
        print(f"Factors found: {analysis['factors_found']}")
    else:
        print("No factors found — expected on noisy hardware for larger circuits.")

    # Add hardware metadata
    analysis['backend'] = backend.name
    analysis['job_id'] = job.job_id()
    analysis['transpiled_depth'] = transpiled.depth()

    return analysis, counts


def save_results(analysis, counts, filepath, backend_name=""):
    """Save hardware results to CSV."""
    with open(filepath, 'w', newline='') as f:
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
                'backend': backend_name,
            })


def main():
    """Run Shor's algorithm on IBM Quantum hardware."""
    print("Shor's Algorithm — IBM Quantum Hardware")
    print("="*60)
    print("\nThis script submits jobs to real quantum hardware.")
    print("Each job consumes your monthly IBM Quantum quota.\n")

    # N=15 on hardware
    analysis_15, counts_15 = run_shors_hardware(
        N=15, a=7, shots=100, n_count=8
    )
    if analysis_15:
        outpath = RESULTS_DIR / "shors_hardware_N15.csv"
        save_results(analysis_15, counts_15, outpath,
                     backend_name=analysis_15.get('backend', ''))
        print(f"\nResults saved to {outpath}")

    # Optionally try N=21
    print("\n" + "="*60)
    print("N=21 requires more qubits and will likely fail on hardware")
    print("due to noise. This is expected and documented in the report.")
    try_21 = input("Attempt N=21 on hardware? [y/N]: ").strip().lower()
    if try_21 == 'y':
        analysis_21, counts_21 = run_shors_hardware(
            N=21, a=2, shots=100, n_count=10
        )
        if analysis_21:
            outpath = RESULTS_DIR / "shors_hardware_N21.csv"
            save_results(analysis_21, counts_21, outpath,
                         backend_name=analysis_21.get('backend', ''))
            print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
