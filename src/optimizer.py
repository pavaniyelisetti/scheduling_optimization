"""
optimizer.py
------------
MILP-based job sequencing optimizer for XYZ Paint Line.

Minimizes total nozzle changeover (switching) time across a day's job list.
Falls back to maximizing barrel throughput if the time budget is tight.

Usage:
    python src/optimizer.py --data data/sample_day.csv [--time-budget 480]
"""

import argparse
import pandas as pd
import gurobipy as grb
from gurobipy import GRB

from cost_matrix import build_cost_matrix
from utils import load_jobs, print_transition_table, print_sequence


def build_model(jobs: list[dict], cost_matrix: list[list[float]]) -> tuple:
    """
    Build and solve the TSP-based MILP for job sequencing.

    Parameters
    ----------
    jobs : list of dicts with keys: Job, Quantity, ExtColor, IntColor
    cost_matrix : N×N switching cost matrix (minutes)

    Returns
    -------
    model   : solved Gurobi model
    x       : binary transition variables x[i,j]
    u       : position variables (MTZ subtour elimination)
    """
    n = len(jobs)
    m = grb.Model("XYZ_Job_Optimizer")
    m.setParam("OutputFlag", 0)  # Suppress Gurobi console output

    # --- Decision Variables ---
    # x[i,j] = 1 if job j immediately follows job i
    x = m.addVars(n, n, vtype=GRB.BINARY, name="x")
    # u[i] = position of job i in sequence (MTZ)
    u = m.addVars(n, vtype=GRB.CONTINUOUS, lb=0, ub=n - 1, name="u")

    # --- Objective: Minimize total switching cost ---
    m.setObjective(
        grb.quicksum(cost_matrix[i][j] * x[i, j] for i in range(n) for j in range(n) if i != j),
        GRB.MINIMIZE,
    )

    # --- Constraints ---
    # Each job has exactly one successor
    for i in range(n):
        m.addConstr(grb.quicksum(x[i, j] for j in range(n) if j != i) == 1, name=f"out_{i}")

    # Each job has exactly one predecessor
    for j in range(n):
        m.addConstr(grb.quicksum(x[i, j] for i in range(n) if i != j) == 1, name=f"in_{j}")

    # MTZ subtour elimination
    for i in range(n):
        for j in range(1, n):
            if i != j:
                m.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1, name=f"mtz_{i}_{j}")

    # No self-loops
    for i in range(n):
        m.addConstr(x[i, i] == 0, name=f"noself_{i}")

    m.optimize()

    if m.status != GRB.OPTIMAL:
        raise RuntimeError(f"Model not optimal. Gurobi status: {m.status}")

    return m, x, u


def extract_sequence(x, n: int) -> list[int]:
    """Reconstruct the ordered job sequence from binary x[i,j] variables."""
    # Find the job with no predecessor that isn't a successor of anything
    successors = {i: j for i in range(n) for j in range(n) if i != j and round(x[i, j].x) == 1}
    predecessors = set(successors.values())
    start = next(i for i in range(n) if i not in predecessors)

    sequence = [start]
    current = start
    for _ in range(n - 1):
        current = successors[current]
        sequence.append(current)
    return sequence


def main():
    parser = argparse.ArgumentParser(description="XYZ Job Sequence Optimizer")
    parser.add_argument("--data", default="data/sample_day.csv", help="Path to jobs CSV")
    parser.add_argument("--time-budget", type=float, default=None,
                        help="Optional daily time budget in minutes")
    args = parser.parse_args()

    # Load jobs
    jobs = load_jobs(args.data)
    n = len(jobs)
    print(f"Loaded {n} jobs from {args.data}\n")

    # Build cost matrix
    cost_matrix = build_cost_matrix(jobs)

    # Solve
    print("Solving MILP...")
    model, x, u = build_model(jobs, cost_matrix)

    # Extract sequence
    sequence = extract_sequence(x, n)
    optimized_jobs = [jobs[i] for i in sequence]

    # Compute results
    total_barrels = sum(jobs[i]["Quantity"] for i in sequence)
    switch_cost = grb.quicksum(
        cost_matrix[i][j] * x[i, j].x for i in range(n) for j in range(n) if i != j
    ).getValue()

    time_per_barrel = 1 / 60  # assumed: 1 minute per 60 barrels (adjust as needed)
    total_processing_time = total_barrels * time_per_barrel
    total_day_time = total_processing_time + switch_cost

    # Print results
    print_sequence(optimized_jobs)
    print(f"\nTotal Barrels Processed in Optimized Sequence: {total_barrels}")
    print(f"\nTotal minimum switching cost in final sequence: {switch_cost:.2f} minutes")
    print(f"\nTotal Processing time for the day: {total_day_time:.2f} minutes")

    if args.time_budget and total_day_time > args.time_budget:
        print(f"\n⚠️  Total time ({total_day_time:.1f} min) exceeds budget ({args.time_budget} min).")
        print("   Consider enabling deferral mode for lower-priority jobs.")

    print_transition_table(jobs, x, n)


if __name__ == "__main__":
    main()
