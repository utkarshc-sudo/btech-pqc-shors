"""Statistical analysis utilities for PQC and Shor's benchmark data.

Contains:
- Loading and parsing benchmark CSV data
- Summary statistics (mean, median, std, percentiles)
- Speedup ratio computation between algorithms
- Shor's algorithm success-rate analysis
"""

import numpy as np
import pandas as pd
from pathlib import Path


def load_benchmark_data(filepath):
    """Load raw benchmark CSV data into a DataFrame.

    Expects columns: algorithm, operation, iteration, time_ns.

    Args:
        filepath: Path (str or Path) to the CSV file.

    Returns:
        pd.DataFrame with the raw benchmark rows.
    """
    filepath = Path(filepath)
    df = pd.read_csv(filepath)
    return df


def compute_summary_stats(df, group_cols=None):
    """Compute summary statistics from raw benchmark data.

    Groups by the specified columns and computes descriptive statistics
    on the time_ns column, converting nanoseconds to microseconds.

    Args:
        df: DataFrame with at least a 'time_ns' column and the grouping columns.
        group_cols: List of column names to group by.
            Defaults to ['algorithm', 'operation'].

    Returns:
        pd.DataFrame with columns:
            <group_cols>, mean_us, median_us, std_us, p95_us, p99_us, min_us, max_us
    """
    if group_cols is None:
        group_cols = ['algorithm', 'operation']

    ns_to_us = 1e-3  # nanoseconds -> microseconds

    grouped = df.groupby(group_cols)['time_ns']

    summary = grouped.agg(
        mean_us=('mean'),
        median_us=('median'),
        std_us=('std'),
        min_us=('min'),
        max_us=('max'),
    ).reset_index()

    # Convert from ns to us
    for col in ['mean_us', 'median_us', 'std_us', 'min_us', 'max_us']:
        summary[col] = summary[col] * ns_to_us

    # Percentiles require manual computation
    p95 = grouped.quantile(0.95).reset_index().rename(columns={'time_ns': 'p95_us'})
    p99 = grouped.quantile(0.99).reset_index().rename(columns={'time_ns': 'p99_us'})

    summary = summary.merge(p95, on=group_cols)
    summary = summary.merge(p99, on=group_cols)

    summary['p95_us'] = summary['p95_us'] * ns_to_us
    summary['p99_us'] = summary['p99_us'] * ns_to_us

    # Reorder columns for consistency
    stat_cols = ['mean_us', 'median_us', 'std_us', 'p95_us', 'p99_us', 'min_us', 'max_us']
    summary = summary[group_cols + stat_cols]

    return summary


def compute_speedup_ratio(baseline_df, comparison_df, operation):
    """Compute how much faster/slower the comparison is vs the baseline.

    Speedup > 1 means the comparison is faster (lower time).
    Speedup < 1 means the comparison is slower.

    Both DataFrames should have columns: algorithm, operation, mean_us
    (i.e. summary-stat format from compute_summary_stats or loaded from
    a _summary.csv).

    Args:
        baseline_df: Summary DataFrame for the baseline algorithm(s).
        comparison_df: Summary DataFrame for the comparison algorithm(s).
        operation: Operation name to compare (e.g. 'keygen', 'encapsulate').

    Returns:
        dict mapping comparison algorithm name to the speedup ratio
        (baseline_mean / comparison_mean).
    """
    baseline_rows = baseline_df[baseline_df['operation'] == operation]
    comparison_rows = comparison_df[comparison_df['operation'] == operation]

    if baseline_rows.empty or comparison_rows.empty:
        return {}

    # Use the first baseline algorithm's mean as the reference
    baseline_mean = baseline_rows.iloc[0]['mean_us']

    ratios = {}
    for _, row in comparison_rows.iterrows():
        algo = row['algorithm']
        comp_mean = row['mean_us']
        if comp_mean > 0:
            ratios[algo] = baseline_mean / comp_mean
        else:
            ratios[algo] = float('inf')

    return ratios


def load_shors_results(filepath):
    """Load Shor's algorithm measurement results from CSV.

    Expects columns: bitstring, count, measured_value, phase,
                     candidate_r, valid_period, factors.

    Args:
        filepath: Path (str or Path) to the CSV file.

    Returns:
        pd.DataFrame with the Shor's measurement data.
    """
    filepath = Path(filepath)
    df = pd.read_csv(filepath)
    return df


def compute_shors_success_rate(df):
    """Compute the fraction of total shots that produced valid factors.

    A shot is considered successful if the 'factors' column is not empty/NaN,
    meaning the measurement led to a non-trivial factorisation.

    Args:
        df: DataFrame with columns 'count' and 'factors'.

    Returns:
        float: success rate in [0, 1].
    """
    total_shots = df['count'].sum()
    if total_shots == 0:
        return 0.0

    # Rows where factors were found (non-null, non-empty string)
    has_factors = df['factors'].notna() & (df['factors'].astype(str).str.strip() != '')
    success_shots = df.loc[has_factors, 'count'].sum()

    return success_shots / total_shots
