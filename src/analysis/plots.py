"""Visualisation routines for PQC and Shor's benchmark results.

All plot functions save figures to results/figures/ as PNG at 150 DPI.
Uses seaborn 'whitegrid' style with a consistent colour palette.

Runnable as:
    python -m src.analysis.plots
from the repository root.  Missing CSV files are silently skipped.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

from src.analysis.stats import (
    load_benchmark_data,
    compute_summary_stats,
    load_shors_results,
    compute_shors_success_rate,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = REPO_ROOT / "results" / "raw"
FIG_DIR = REPO_ROOT / "results" / "figures"

DPI = 150
STYLE = "whitegrid"
PALETTE = sns.color_palette("muted")

# Named colours for consistent use across plots
COLORS = {
    "ML-KEM-512": PALETTE[0],
    "ML-KEM-768": PALETTE[1],
    "ML-KEM-1024": PALETTE[2],
    "X25519": PALETTE[3],
    "Simulator": PALETTE[4],
    "Hardware": PALETTE[5],
}


def _ensure_fig_dir():
    """Create the figures output directory if it does not exist."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def _savefig(fig, name):
    """Save a figure and close it."""
    _ensure_fig_dir()
    fig.savefig(FIG_DIR / name, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {FIG_DIR / name}")


def _load_summary(csv_name):
    """Load a summary CSV if it exists, else return None."""
    path = RAW_DIR / csv_name
    if path.exists():
        return pd.read_csv(path)
    return None


def _load_sizes(csv_name):
    """Load a sizes CSV if it exists, else return None."""
    path = RAW_DIR / csv_name
    if path.exists():
        return pd.read_csv(path)
    return None


# ---------------------------------------------------------------------------
# Plot functions
# ---------------------------------------------------------------------------

def plot_mlkem_timing_comparison():
    """Grouped bar chart comparing ML-KEM-512/768/1024 keygen/encap/decap times.

    Uses the summary CSV (mean_us) for each algorithm-operation pair.
    """
    df = _load_summary("mlkem_summary.csv")
    if df is None:
        print("  Skipping ML-KEM timing comparison (mlkem_summary.csv not found)")
        return

    sns.set_style(STYLE)

    operations = ["keygen", "encapsulate", "decapsulate"]
    algorithms = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]

    # Filter to the algorithms and operations of interest
    df = df[df["algorithm"].isin(algorithms) & df["operation"].isin(operations)].copy()
    if df.empty:
        print("  Skipping ML-KEM timing comparison (no matching data)")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(operations))
    width = 0.25

    for i, algo in enumerate(algorithms):
        algo_data = df[df["algorithm"] == algo]
        means = []
        for op in operations:
            row = algo_data[algo_data["operation"] == op]
            means.append(row["mean_us"].values[0] if not row.empty else 0)
        bars = ax.bar(
            x + i * width, means, width,
            label=algo, color=COLORS.get(algo, PALETTE[i]),
        )
        # Add value labels on bars
        for bar, val in zip(bars, means):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{val:.1f}", ha="center", va="bottom", fontsize=8,
            )

    ax.set_xlabel("Operation")
    ax.set_ylabel("Mean time (\u00b5s)")
    ax.set_title("ML-KEM Timing Comparison")
    ax.set_xticks(x + width)
    ax.set_xticklabels([op.capitalize() for op in operations])
    ax.legend()
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    _savefig(fig, "mlkem_timing_comparison.png")


def plot_mlkem_vs_x25519():
    """Bar chart comparing ML-KEM-768 vs X25519 for each operation.

    Operations are mapped to a common set of labels:
        keygen, encapsulate/derive, decapsulate/derive.
    """
    mlkem = _load_summary("mlkem_summary.csv")
    x25519 = _load_summary("x25519_summary.csv")
    if mlkem is None or x25519 is None:
        print("  Skipping ML-KEM vs X25519 (summary CSV(s) not found)")
        return

    sns.set_style(STYLE)

    # Normalise operation names so they can be compared side-by-side
    mlkem = mlkem[mlkem["algorithm"] == "ML-KEM-768"].copy()
    x25519 = x25519.copy()

    # Build a combined frame with a common operation label
    rows = []
    op_map_mlkem = {"keygen": "Key Generation", "encapsulate": "Encap / DH",
                    "decapsulate": "Decap / DH"}
    op_map_x25519 = {"keygen": "Key Generation", "encapsulate": "Encap / DH",
                     "decapsulate": "Decap / DH", "derive": "Encap / DH"}

    for _, r in mlkem.iterrows():
        label = op_map_mlkem.get(r["operation"])
        if label:
            rows.append({"Algorithm": "ML-KEM-768", "Operation": label,
                         "mean_us": r["mean_us"]})
    for _, r in x25519.iterrows():
        label = op_map_x25519.get(r["operation"])
        if label:
            rows.append({"Algorithm": "X25519", "Operation": label,
                         "mean_us": r["mean_us"]})

    if not rows:
        print("  Skipping ML-KEM vs X25519 (no matching operations)")
        return

    cdf = pd.DataFrame(rows)
    operations = cdf["Operation"].unique()

    fig, ax = plt.subplots(figsize=(9, 6))

    x = np.arange(len(operations))
    width = 0.35

    for i, algo in enumerate(["ML-KEM-768", "X25519"]):
        sub = cdf[cdf["Algorithm"] == algo]
        means = [sub[sub["Operation"] == op]["mean_us"].values[0]
                 if not sub[sub["Operation"] == op].empty else 0
                 for op in operations]
        bars = ax.bar(
            x + i * width, means, width,
            label=algo, color=COLORS.get(algo, PALETTE[i]),
        )
        for bar, val in zip(bars, means):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{val:.1f}", ha="center", va="bottom", fontsize=8,
            )

    ax.set_xlabel("Operation")
    ax.set_ylabel("Mean time (\u00b5s)")
    ax.set_title("ML-KEM-768 vs X25519 Performance")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(operations)
    ax.legend()

    _savefig(fig, "mlkem_vs_x25519.png")


def plot_timing_distributions():
    """Violin plots showing the distribution of raw timings for ML-KEM.

    Falls back to box plots if the dataset is very small.
    """
    path = RAW_DIR / "mlkem_benchmark.csv"
    if not path.exists():
        print("  Skipping timing distributions (mlkem_benchmark.csv not found)")
        return

    sns.set_style(STYLE)
    df = load_benchmark_data(path)
    df["time_us"] = df["time_ns"] / 1e3

    fig, ax = plt.subplots(figsize=(12, 6))

    try:
        sns.violinplot(
            data=df, x="operation", y="time_us", hue="algorithm",
            palette=PALETTE, inner="quartile", ax=ax, cut=0,
        )
    except Exception:
        # Fall back to box plots for very small sample sizes
        sns.boxplot(
            data=df, x="operation", y="time_us", hue="algorithm",
            palette=PALETTE, ax=ax,
        )

    ax.set_xlabel("Operation")
    ax.set_ylabel("Time (\u00b5s)")
    ax.set_title("Timing Distributions for ML-KEM Variants")
    ax.legend(title="Algorithm")

    _savefig(fig, "timing_distributions.png")


def plot_size_comparison():
    """Bar chart comparing key and ciphertext sizes across algorithms.

    Combines ML-KEM and X25519 size data.
    """
    mlkem_sizes = _load_sizes("mlkem_sizes.csv")
    x25519_sizes = _load_sizes("x25519_sizes.csv")

    frames = [f for f in [mlkem_sizes, x25519_sizes] if f is not None]
    if not frames:
        print("  Skipping size comparison (no size CSVs found)")
        return

    sns.set_style(STYLE)
    df = pd.concat(frames, ignore_index=True)

    size_cols = ["public_key_bytes", "secret_key_bytes", "ciphertext_bytes"]
    present_cols = [c for c in size_cols if c in df.columns]
    if not present_cols:
        print("  Skipping size comparison (expected columns missing)")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(df))
    n_bars = len(present_cols)
    width = 0.8 / n_bars

    labels_map = {
        "public_key_bytes": "Public Key",
        "secret_key_bytes": "Secret Key",
        "ciphertext_bytes": "Ciphertext",
    }

    for i, col in enumerate(present_cols):
        values = df[col].values
        bars = ax.bar(
            x + i * width, values, width,
            label=labels_map.get(col, col), color=PALETTE[i],
        )
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    str(int(val)), ha="center", va="bottom", fontsize=7,
                )

    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Size (bytes)")
    ax.set_title("Key and Ciphertext Sizes")
    ax.set_xticks(x + width * (n_bars - 1) / 2)
    ax.set_xticklabels(df["algorithm"].values, rotation=15, ha="right")
    ax.legend()

    _savefig(fig, "size_comparison.png")


def plot_shors_histogram(filepath, N, title=None):
    """Histogram of Shor's measurement outcomes.

    Each bar represents a distinct measured bitstring, coloured by whether
    the outcome led to valid factors.

    Args:
        filepath: Path to the Shor's CSV.
        N: The number being factored (used in default title).
        title: Optional custom title.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"  Skipping Shor's histogram for N={N} ({filepath.name} not found)")
        return

    sns.set_style(STYLE)
    df = load_shors_results(filepath)

    has_factors = df["factors"].notna() & (df["factors"].astype(str).str.strip() != "")

    fig, ax = plt.subplots(figsize=(12, 5))

    colors = [COLORS["Simulator"] if f else "#cccccc" for f in has_factors]
    ax.bar(range(len(df)), df["count"], color=colors)

    ax.set_xlabel("Measurement Outcome")
    ax.set_ylabel("Counts")
    ax.set_title(title or f"Shor's Algorithm Measurement Outcomes (N = {N})")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["bitstring"], rotation=90, fontsize=6)

    # Legend
    from matplotlib.patches import Patch
    legend_items = [
        Patch(facecolor=COLORS["Simulator"], label="Valid factors"),
        Patch(facecolor="#cccccc", label="No factors"),
    ]
    ax.legend(handles=legend_items)

    _savefig(fig, f"shors_histogram_N{N}.png")


def plot_shors_success_comparison():
    """Bar chart comparing simulator vs hardware success rates for N=15.

    Reads shors_simulator_N15.csv and shors_hardware_N15.csv.
    """
    sim_path = RAW_DIR / "shors_simulator_N15.csv"
    hw_path = RAW_DIR / "shors_hardware_N15.csv"

    rates = {}
    if sim_path.exists():
        sim_df = load_shors_results(sim_path)
        rates["Simulator"] = compute_shors_success_rate(sim_df)
    if hw_path.exists():
        hw_df = load_shors_results(hw_path)
        rates["Hardware"] = compute_shors_success_rate(hw_df)

    if not rates:
        print("  Skipping Shor's success comparison (no Shor's CSVs found)")
        return

    sns.set_style(STYLE)
    fig, ax = plt.subplots(figsize=(7, 5))

    labels = list(rates.keys())
    values = [rates[k] * 100 for k in labels]
    bar_colors = [COLORS.get(k, PALETTE[i]) for i, k in enumerate(labels)]

    bars = ax.bar(labels, values, color=bar_colors, width=0.5)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height(),
            f"{val:.1f}%", ha="center", va="bottom", fontsize=10,
        )

    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Shor's Algorithm: Simulator vs Hardware (N = 15)")
    ax.set_ylim(0, 105)

    _savefig(fig, "shors_success_comparison.png")


def plot_resource_extrapolation():
    """Chart showing estimated qubit requirements for factoring RSA key sizes.

    Reference data points from Gidney & Ekera (2021):
        RSA-2048 ~ 20 million noisy (physical) qubits
    Extrapolated to other RSA key sizes using the roughly linear scaling
    of the surface-code estimate (qubits ~ O(n * log(n)^2) for n-bit RSA).
    """
    sns.set_style(STYLE)

    # RSA key sizes (bits)
    rsa_bits = np.array([512, 1024, 2048, 3072, 4096])

    # Gidney & Ekera anchor: RSA-2048 needs ~20M noisy qubits.
    # Physical qubit count scales roughly as n * log2(n)^2 for n-bit modulus.
    def _qubit_estimate(n, anchor_n=2048, anchor_q=20e6):
        scale = (n * np.log2(n) ** 2) / (anchor_n * np.log2(anchor_n) ** 2)
        return anchor_q * scale

    qubits = _qubit_estimate(rsa_bits)

    # Current largest quantum computers (for context line)
    current_max_qubits = 1_180  # IBM Condor, as of 2024

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.semilogy(rsa_bits, qubits, "o-", color=PALETTE[2], linewidth=2,
                markersize=8, label="Estimated physical qubits (Gidney & Ekera)")

    # Annotate the anchor point
    idx_2048 = np.where(rsa_bits == 2048)[0][0]
    ax.annotate(
        f"~{qubits[idx_2048]/1e6:.0f}M qubits",
        xy=(rsa_bits[idx_2048], qubits[idx_2048]),
        xytext=(rsa_bits[idx_2048] + 300, qubits[idx_2048] * 2),
        arrowprops=dict(arrowstyle="->", color="grey"),
        fontsize=9,
    )

    # Current hardware reference line
    ax.axhline(current_max_qubits, color=PALETTE[3], linestyle="--",
               linewidth=1.5, label=f"Current max (~{current_max_qubits} qubits)")

    ax.set_xlabel("RSA Key Size (bits)")
    ax.set_ylabel("Estimated Physical Qubits (log scale)")
    ax.set_title("Qubit Requirements for Factoring RSA Keys\n"
                 "(Gidney & Ekera 2021 extrapolation)")
    ax.set_xticks(rsa_bits)
    ax.set_xticklabels([str(b) for b in rsa_bits])
    ax.legend()
    ax.grid(True, which="both", axis="y", alpha=0.3)

    _savefig(fig, "resource_extrapolation.png")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    """Generate all available plots from raw benchmark data."""
    _ensure_fig_dir()

    print("Generating plots...")

    print("[1/7] ML-KEM timing comparison")
    plot_mlkem_timing_comparison()

    print("[2/7] ML-KEM vs X25519")
    plot_mlkem_vs_x25519()

    print("[3/7] Timing distributions")
    plot_timing_distributions()

    print("[4/7] Size comparison")
    plot_size_comparison()

    print("[5/7] Shor's histograms")
    plot_shors_histogram(RAW_DIR / "shors_simulator_N15.csv", N=15,
                         title="Shor's Algorithm - Simulator (N = 15)")
    plot_shors_histogram(RAW_DIR / "shors_simulator_N21.csv", N=21,
                         title="Shor's Algorithm - Simulator (N = 21)")
    plot_shors_histogram(RAW_DIR / "shors_hardware_N15.csv", N=15,
                         title="Shor's Algorithm - IBM Hardware (N = 15)")

    print("[6/7] Shor's success comparison")
    plot_shors_success_comparison()

    print("[7/7] Resource extrapolation")
    plot_resource_extrapolation()

    print("Done.")


if __name__ == "__main__":
    main()
