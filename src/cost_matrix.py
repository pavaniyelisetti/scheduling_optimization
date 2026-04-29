"""
cost_matrix.py
--------------
Builds the N×N switching cost matrix from job color attributes.

Cost logic (minutes):
  - Same ext + same int    →  0   (no changeover needed)
  - Same ext, diff int     →  2   (interior nozzle flush only)
  - Diff ext, same int     →  7   (exterior nozzle swap)
  - Diff ext, diff int     → 13   (full double nozzle swap)
  - To/from UNLINED        →  special cases (see below)

These values should be calibrated against actual shop floor timing data.
"""

# --------------------------------------------------------------------------- #
# Switching cost table (minutes).  Rows = "from" state, Cols = "to" state.
# Adjust COST_TABLE to match real measured changeover times.
# --------------------------------------------------------------------------- #

SAME_SAME = 0        # no change
EXT_ONLY  = 7        # exterior nozzle swap only
INT_ONLY  = 2        # interior nozzle flush only
BOTH      = 13       # full double swap
UNLINED_PENALTY = 3  # extra cost when transitioning to/from UNLINED interior


def switching_cost(from_job: dict, to_job: dict) -> float:
    """
    Compute the switching cost in minutes between two consecutive jobs.

    Parameters
    ----------
    from_job : dict with 'ExtColor' and 'IntColor'
    to_job   : dict with 'ExtColor' and 'IntColor'

    Returns
    -------
    float: switching cost in minutes
    """
    ext_change = from_job["ExtColor"].strip().upper() != to_job["ExtColor"].strip().upper()
    int_change = from_job["IntColor"].strip().upper() != to_job["IntColor"].strip().upper()

    to_unlined   = to_job["IntColor"].strip().upper() == "UNLINED"
    from_unlined = from_job["IntColor"].strip().upper() == "UNLINED"

    if not ext_change and not int_change:
        return SAME_SAME

    cost = 0.0
    if ext_change:
        cost += EXT_ONLY
    if int_change:
        cost += INT_ONLY
    if to_unlined or from_unlined:
        cost += UNLINED_PENALTY

    return cost


def build_cost_matrix(jobs: list[dict]) -> list[list[float]]:
    """
    Build an N×N cost matrix where cost_matrix[i][j] is the switching cost
    from job i directly to job j.

    Diagonal entries (i == j) are set to a large penalty to prevent self-loops.
    """
    n = len(jobs)
    BIG_M = 9999.0  # penalty to prevent self-assignment in the MILP

    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = BIG_M
            else:
                matrix[i][j] = switching_cost(jobs[i], jobs[j])

    return matrix
