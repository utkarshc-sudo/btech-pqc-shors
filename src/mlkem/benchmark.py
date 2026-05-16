"""
ML-KEM Benchmark Harness
========================
Benchmarks ML-KEM-512, ML-KEM-768, and ML-KEM-1024 for keygen, encapsulate,
and decapsulate operations over 10,000 iterations each. Saves raw timings,
summary statistics, and key/ciphertext sizes to CSV.

Run from repo root:
    python -m src.mlkem.benchmark
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd
import oqs


ALGORITHMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
ITERATIONS = 10_000
RESULTS_DIR = Path("results/raw")


def benchmark_algorithm(algorithm: str, iterations: int) -> list[dict]:
    """Benchmark keygen, encaps, and decaps for a single ML-KEM parameter set."""
    records = []

    # --- Key Generation ---
    print(f"  keygen ({iterations} iterations)...", end=" ", flush=True)
    for i in range(iterations):
        kem = oqs.KeyEncapsulation(algorithm)
        t0 = time.perf_counter_ns()
        public_key = kem.generate_keypair()
        t1 = time.perf_counter_ns()
        records.append({
            "algorithm": algorithm,
            "operation": "keygen",
            "iteration": i,
            "time_ns": t1 - t0,
        })
        if i == 0:
            # Stash for encaps/decaps and size measurement
            first_kem = kem
            first_pk = public_key
    print("done")

    # --- Encapsulation ---
    print(f"  encapsulate ({iterations} iterations)...", end=" ", flush=True)
    for i in range(iterations):
        kem_enc = oqs.KeyEncapsulation(algorithm)
        t0 = time.perf_counter_ns()
        ciphertext, shared_secret_enc = kem_enc.encap_secret(first_pk)
        t1 = time.perf_counter_ns()
        records.append({
            "algorithm": algorithm,
            "operation": "encapsulate",
            "iteration": i,
            "time_ns": t1 - t0,
        })
        if i == 0:
            first_ct = ciphertext
            first_ss = shared_secret_enc
    print("done")

    # --- Decapsulation ---
    print(f"  decapsulate ({iterations} iterations)...", end=" ", flush=True)
    # Generate a fresh keypair and matching ciphertext for decaps benchmarking
    kem_dec = oqs.KeyEncapsulation(algorithm)
    pk_dec = kem_dec.generate_keypair()
    kem_enc_for_dec = oqs.KeyEncapsulation(algorithm)
    ct_dec, _ = kem_enc_for_dec.encap_secret(pk_dec)

    for i in range(iterations):
        # Re-create the KEM object with the same secret key each time
        kem_d = oqs.KeyEncapsulation(algorithm, secret_key=kem_dec.export_secret_key())
        t0 = time.perf_counter_ns()
        shared_secret_dec = kem_d.decap_secret(ct_dec)
        t1 = time.perf_counter_ns()
        records.append({
            "algorithm": algorithm,
            "operation": "decapsulate",
            "iteration": i,
            "time_ns": t1 - t0,
        })
    print("done")

    return records


def measure_sizes(algorithm: str) -> dict:
    """Measure public key, secret key, ciphertext, and shared secret sizes."""
    kem = oqs.KeyEncapsulation(algorithm)
    public_key = kem.generate_keypair()
    secret_key = kem.export_secret_key()

    kem_enc = oqs.KeyEncapsulation(algorithm)
    ciphertext, shared_secret = kem_enc.encap_secret(public_key)

    return {
        "algorithm": algorithm,
        "public_key_bytes": len(public_key),
        "secret_key_bytes": len(secret_key),
        "ciphertext_bytes": len(ciphertext),
        "shared_secret_bytes": len(shared_secret),
    }


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary statistics (in microseconds) per algorithm and operation."""
    rows = []
    for (algo, op), group in df.groupby(["algorithm", "operation"]):
        times_us = group["time_ns"].values / 1_000.0  # ns -> us
        rows.append({
            "algorithm": algo,
            "operation": op,
            "mean_us": np.mean(times_us),
            "median_us": np.median(times_us),
            "std_us": np.std(times_us),
            "p95_us": np.percentile(times_us, 95),
            "p99_us": np.percentile(times_us, 99),
            "min_us": np.min(times_us),
            "max_us": np.max(times_us),
        })
    return pd.DataFrame(rows)


def print_summary_table(summary_df: pd.DataFrame) -> None:
    """Pretty-print the summary table."""
    print("\n" + "=" * 90)
    print(f"{'Algorithm':<16} {'Operation':<14} {'Mean (us)':>10} {'Median (us)':>12} "
          f"{'Std (us)':>10} {'P95 (us)':>10} {'P99 (us)':>10}")
    print("-" * 90)
    for _, row in summary_df.iterrows():
        print(f"{row['algorithm']:<16} {row['operation']:<14} "
              f"{row['mean_us']:>10.2f} {row['median_us']:>12.2f} "
              f"{row['std_us']:>10.2f} {row['p95_us']:>10.2f} {row['p99_us']:>10.2f}")
    print("=" * 90)


def print_sizes_table(sizes_df: pd.DataFrame) -> None:
    """Pretty-print the sizes table."""
    print("\n" + "=" * 80)
    print(f"{'Algorithm':<16} {'PK (bytes)':>12} {'SK (bytes)':>12} "
          f"{'CT (bytes)':>12} {'SS (bytes)':>12}")
    print("-" * 80)
    for _, row in sizes_df.iterrows():
        print(f"{row['algorithm']:<16} {row['public_key_bytes']:>12} "
              f"{row['secret_key_bytes']:>12} {row['ciphertext_bytes']:>12} "
              f"{row['shared_secret_bytes']:>12}")
    print("=" * 80)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    all_sizes: list[dict] = []

    for algo in ALGORITHMS:
        print(f"\nBenchmarking {algo}...")
        records = benchmark_algorithm(algo, ITERATIONS)
        all_records.extend(records)

        sizes = measure_sizes(algo)
        all_sizes.append(sizes)

    # Raw timings
    raw_df = pd.DataFrame(all_records)
    raw_path = RESULTS_DIR / "mlkem_benchmark.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"\nRaw results saved to {raw_path}")

    # Summary statistics
    summary_df = compute_summary(raw_df)
    summary_path = RESULTS_DIR / "mlkem_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Summary saved to {summary_path}")

    # Key/ciphertext sizes
    sizes_df = pd.DataFrame(all_sizes)
    sizes_path = RESULTS_DIR / "mlkem_sizes.csv"
    sizes_df.to_csv(sizes_path, index=False)
    print(f"Sizes saved to {sizes_path}")

    # Print tables
    print_summary_table(summary_df)
    print_sizes_table(sizes_df)

    print(f"\nTotal measurements: {len(raw_df):,}")


if __name__ == "__main__":
    main()
