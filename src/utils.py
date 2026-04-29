"""
utils.py
--------
Helper functions: job loading, result printing.
"""

import pandas as pd


def load_jobs(filepath: str) -> list[dict]:
    """
    Load job data from a CSV file.

    Expected columns: Job, Quantity, ExtColor, IntColor
    Returns a list of dicts, one per job.
    """
    df = pd.read_csv(filepath)
    required = {"Job", "Quantity", "ExtColor", "IntColor"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    return df.to_dict(orient="records")


def print_sequence(jobs: list[dict]) -> None:
    """Print the optimized job sequence in a readable format."""
    print("\nOptimized Job Sequence:")
    print("-" * 50)
    for idx, job in enumerate(jobs, start=1):
        print(
            f"  {idx:>2}. Job {job['Job']:>3} | "
            f"Qty: {job['Quantity']:>4} barrels | "
            f"Ext: {job['ExtColor']:<10} | Int: {job['IntColor']}"
        )
    print("-" * 50)


def print_transition_table(jobs: list[dict], x, n: int) -> None:
    """Print the binary job transition table x[i,j]."""
    print("\nJob Transition Table (x[i, j]):\n")

    # Header row
    print(f"{'':10}", end="")
    for j in range(n):
        print(f"{jobs[j]['Job']:<10}", end="")
    print()

    # Data rows
    for i in range(n):
        print(f"{jobs[i]['Job']:<10}", end="")
        for j in range(n):
            print(f"{int(round(x[i, j].x))}".ljust(10), end="")
        print()
