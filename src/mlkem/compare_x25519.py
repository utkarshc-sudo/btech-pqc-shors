"""
X25519 Baseline Comparison
==========================
Benchmarks X25519 ECDH key exchange (keygen, ephemeral encapsulate-equivalent,
and shared-secret derivation) over 10,000 iterations for comparison with ML-KEM.

Run from repo root:
    python -m src.mlkem.compare_x25519
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

ALGORITHM = "X25519"
ITERATIONS = 10_000
RESULTS_DIR = Path("results/raw")


def benchmark_x25519(iterations: int) -> list[dict]:
    """Benchmark X25519 keygen, encapsulate-equivalent, and full exchange."""
    records = []

    # --- Key Generation ---
    print(f"  keygen ({iterations} iterations)...", end=" ", flush=True)
    for i in range(iterations):
        t0 = time.perf_counter_ns()
        private_key = X25519PrivateKey.generate()
        t1 = time.perf_counter_ns()
        records.append({
            "algorithm": ALGORITHM,
            "operation": "keygen",
            "iteration": i,
            "time_ns": t1 - t0,
        })
    print("done")

    # --- Encapsulate-equivalent (ephemeral keygen + ECDH) ---
    # In a KEM-like workflow: Alice has a static key, Bob generates an ephemeral
    # key and derives a shared secret. This mirrors the encapsulation step.
    static_private = X25519PrivateKey.generate()
    static_public = static_private.public_key()

    print(f"  encapsulate-equiv ({iterations} iterations)...", end=" ", flush=True)
    for i in range(iterations):
        t0 = time.perf_counter_ns()
        ephemeral_private = X25519PrivateKey.generate()
        shared_secret = ephemeral_private.exchange(static_public)
        t1 = time.perf_counter_ns()
        records.append({
            "algorithm": ALGORITHM,
            "operation": "encapsulate",
            "iteration": i,
            "time_ns": t1 - t0,
        })
        if i == 0:
            first_ephemeral_public = ephemeral_private.public_key()
    print("done")

    # --- Decapsulate-equivalent (ECDH with received ephemeral public key) ---
    # Alice uses her static private key to derive the same shared secret from
    # Bob's ephemeral public key. This mirrors the decapsulation step.
    print(f"  decapsulate-equiv ({iterations} iterations)...", end=" ", flush=True)
    for i in range(iterations):
        t0 = time.perf_counter_ns()
        shared_secret_dec = static_private.exchange(first_ephemeral_public)
        t1 = time.perf_counter_ns()
        records.append({
            "algorithm": ALGORITHM,
            "operation": "decapsulate",
            "iteration": i,
            "time_ns": t1 - t0,
        })
    print("done")

    return records


def measure_sizes() -> dict:
    """Measure X25519 key and 'ciphertext' (ephemeral public key) sizes."""
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PublicFormat,
        PrivateFormat,
        NoEncryption,
    )

    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()

    pk_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    sk_bytes = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

    # "Ciphertext" in X25519 ECDH is the ephemeral public key
    ephemeral = X25519PrivateKey.generate()
    ct_bytes = ephemeral.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    # Shared secret is always 32 bytes for X25519
    shared_secret = private_key.exchange(public_key)

    return {
        "algorithm": ALGORITHM,
        "public_key_bytes": len(pk_bytes),
        "secret_key_bytes": len(sk_bytes),
        "ciphertext_bytes": len(ct_bytes),
        "shared_secret_bytes": len(shared_secret),
    }


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary statistics (in microseconds) per algorithm and operation."""
    rows = []
    for (algo, op), group in df.groupby(["algorithm", "operation"]):
        times_us = group["time_ns"].values / 1_000.0
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


def load_mlkem_summary() -> pd.DataFrame | None:
    """Try to load ML-KEM summary for comparison."""
    path = RESULTS_DIR / "mlkem_summary.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


def print_comparison_table(x25519_summary: pd.DataFrame) -> None:
    """Print X25519 results and, if available, compare with ML-KEM."""
    mlkem_summary = load_mlkem_summary()

    print("\n" + "=" * 100)
    print("COMPARISON: X25519 vs ML-KEM")
    print("=" * 100)

    if mlkem_summary is not None:
        combined = pd.concat([x25519_summary, mlkem_summary], ignore_index=True)
    else:
        combined = x25519_summary
        print("(ML-KEM results not found -- run `python -m src.mlkem.benchmark` first)")
        print("(Showing X25519 results only)\n")

    print(f"\n{'Algorithm':<16} {'Operation':<14} {'Mean (us)':>10} {'Median (us)':>12} "
          f"{'Std (us)':>10} {'P95 (us)':>10} {'P99 (us)':>10}")
    print("-" * 100)
    for _, row in combined.iterrows():
        print(f"{row['algorithm']:<16} {row['operation']:<14} "
              f"{row['mean_us']:>10.2f} {row['median_us']:>12.2f} "
              f"{row['std_us']:>10.2f} {row['p95_us']:>10.2f} {row['p99_us']:>10.2f}")
    print("=" * 100)

    # Print slowdown ratios if ML-KEM data is available
    if mlkem_summary is not None:
        print("\nSlowdown ratios (ML-KEM median / X25519 median):")
        print("-" * 60)
        for op in ["keygen", "encapsulate", "decapsulate"]:
            x_row = x25519_summary[x25519_summary["operation"] == op]
            if x_row.empty:
                continue
            x_median = x_row["median_us"].values[0]
            for algo in ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]:
                m_row = mlkem_summary[
                    (mlkem_summary["algorithm"] == algo)
                    & (mlkem_summary["operation"] == op)
                ]
                if not m_row.empty:
                    m_median = m_row["median_us"].values[0]
                    ratio = m_median / x_median if x_median > 0 else float("inf")
                    print(f"  {algo:<16} {op:<14} {ratio:>6.2f}x")
        print()


def print_sizes_comparison(x25519_sizes: dict) -> None:
    """Print sizes and compare with ML-KEM if available."""
    mlkem_sizes_path = RESULTS_DIR / "mlkem_sizes.csv"

    print("\n" + "=" * 80)
    print("KEY / CIPHERTEXT SIZES (bytes)")
    print("=" * 80)
    print(f"{'Algorithm':<16} {'PK':>12} {'SK':>12} {'CT':>12} {'SS':>12}")
    print("-" * 80)
    print(f"{x25519_sizes['algorithm']:<16} {x25519_sizes['public_key_bytes']:>12} "
          f"{x25519_sizes['secret_key_bytes']:>12} {x25519_sizes['ciphertext_bytes']:>12} "
          f"{x25519_sizes['shared_secret_bytes']:>12}")

    if mlkem_sizes_path.exists():
        mlkem_sizes_df = pd.read_csv(mlkem_sizes_path)
        for _, row in mlkem_sizes_df.iterrows():
            print(f"{row['algorithm']:<16} {row['public_key_bytes']:>12} "
                  f"{row['secret_key_bytes']:>12} {row['ciphertext_bytes']:>12} "
                  f"{row['shared_secret_bytes']:>12}")
    print("=" * 80)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nBenchmarking {ALGORITHM}...")
    records = benchmark_x25519(ITERATIONS)

    # Raw timings
    raw_df = pd.DataFrame(records)
    raw_path = RESULTS_DIR / "x25519_benchmark.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"\nRaw results saved to {raw_path}")

    # Summary statistics
    summary_df = compute_summary(raw_df)
    summary_path = RESULTS_DIR / "x25519_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Summary saved to {summary_path}")

    # Sizes
    sizes = measure_sizes()
    sizes_df = pd.DataFrame([sizes])
    sizes_path = RESULTS_DIR / "x25519_sizes.csv"
    sizes_df.to_csv(sizes_path, index=False)
    print(f"Sizes saved to {sizes_path}")

    # Print comparison
    print_comparison_table(summary_df)
    print_sizes_comparison(sizes)

    print(f"\nTotal measurements: {len(raw_df):,}")


if __name__ == "__main__":
    main()
