# XYZ Job Optimization — Paint Line Changeover Scheduler

> **Course:** SEGR 4114 / EMGT 5114: Production Control Systems  
> **Team:** Isaac Oladipupo · Thomas Phillips · Pavani Yelisetti

---

## Overview

Company XYZ operates a barrel paint/lining production line and was losing **40–60% of daily work hours** to nozzle changeover between jobs. This project formulates and solves a Mixed-Integer Linear Program (MILP) to sequence daily jobs so that total changeover (switching) time is minimized and barrel throughput is maximized.

The model is inspired by the **Travelling Salesman Problem (TSP)** and draws on lean manufacturing principles (SMED) to deliver a practical, scalable scheduling tool for daily production planning.

---

## Problem Statement

| Symptom | Root Cause |
|---|---|
| Significant order backlog | Excessive nozzle changeover between jobs |
| 40–60% daily hours lost | Paint color switches require full nozzle cleaning |
| Inconsistent throughput | No optimized job sequence |

**Goal:** Find the job sequence that minimizes total switching cost while processing up to 1,367+ barrels per day.

---

## Model

### Decision Variables

- `x[i, j]` — Binary: 1 if job `j` directly follows job `i` in the sequence, 0 otherwise
- `u[i]` — Continuous: position of job `i` in sequence (Miller-Tucker-Zemlin subtour elimination)

### Objective

```
Minimize: Σ cost_matrix[i][j] · x[i, j]   ∀ i ≠ j
```

### Constraints

- Each job has exactly one successor and one predecessor
- Subtour elimination (MTZ formulation)
- Feasibility fallback: if minimization is infeasible, model pivots to **maximize barrel output** under a daily time budget
- Penalty calibration: jobs are deferred when penalty < job size; prioritized when penalty ≥ job size

### Cost Matrix

Switching costs are based on interior (lining) and exterior (body) color transitions:

| Transition | Cost (minutes) |
|---|---|
| Same color → same color | 0 |
| Color → unlined (or vice versa) | Low |
| Color → different color | High |

---

## Repository Structure

```
xyz-job-optimization/
├── README.md
├── requirements.txt
├── src/
│   ├── optimizer.py          # Core MILP model (Gurobi)
│   ├── cost_matrix.py        # Switching cost computation
│   └── utils.py              # Helpers: sequence printer, job loader
├── data/
│   └── sample_day.csv        # Sample 12-job day (1,367 barrels)
├── notebooks/
│   └── Carryover_Consideration.ipynb   # Full experiment notebook
└── docs/
    └── XYZ_Project_Slides.pdf          # Project presentation
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Gurobi license required.** Academic licenses are free at [gurobi.com](https://www.gurobi.com/academia/academic-program-and-licenses/).

### 2. Run the optimizer

```bash
python src/optimizer.py --data data/sample_day.csv
```

### 3. Expected output

```
Optimized Job Sequence: [1, 2, 3, 4, 5, ...]

Total Barrels Processed in Optimized Sequence: 1367
Total minimum switching cost in final sequence: XX minutes
Total Processing time for the day: XXX minutes

Job Transition Table (x[i, j]):
          Job1      Job2      Job3  ...
Job1      0         1         0    ...
Job2      0         0         1    ...
...
```

---

## Key Results

| Scenario | Avg Barrels/Day | Max Barrels/Day |
|---|---|---|
| Base Jobs | 1,192 | 1,367 |
| Dominant Job | 1,956 | 2,867 |
| Double Jobs | 1,872 | 2,734 |

**Penalty sensitivity:**
- Penalty `0.08` → avg **2,151** barrels (aggressive inclusion)
- Penalty `0.35` → avg **1,097** barrels (conservative, many deferrals)

---

## Literature Basis

| Source | Contribution |
|---|---|
| Shingo (1985) | SMED — separates internal/external setup tasks |
| Wang et al. (2023) | MILP integrating maintenance & production |
| Li (2020) | Steel scheduling via algorithmic changeover reduction |
| Sharma et al. (2017) | Simulation of food manufacturing setups |
| Borisovsky et al. (2014) | Reduced-constraint MIP for faster solve time |

---

## Further Extensions

- [ ] Replace static penalty with financial/job cost
- [ ] Non-linear deferral penalties
- [ ] End-of-day clean vs. final state constraint
- [ ] Multi-day processing & carryover logic
- [ ] Greater statistical analysis across long-run scenarios

---

## Requirements

See [`requirements.txt`](requirements.txt) for full list.

```
gurobipy
pandas
numpy
jupyter
```

---

## License

This project was developed for academic purposes under SEGR 4114 / EMGT 5114. All rights reserved by the authors.
