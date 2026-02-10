# Algorithm Documentation

## Overview

This document provides a detailed explanation of the optimization algorithm used in this ridesharing matching system. The approach uses **Integer Linear Programming (ILP)** to find optimal rider-driver matches.

## Problem Statement

### Input
- Set of **drivers** `D = {d₁, d₂, ..., dₙ}` with:
  - Origin and destination coordinates
  - Time windows `[eᵢ, lᵢ]` for pickup
  - Trip distance and duration
  
- Set of **riders** `R = {r₁, r₂, ..., rₘ}` with:
  - Origin and destination coordinates
  - Time windows `[eⱼ, lⱼ]` for pickup
  - Trip distance and duration

### Output
- Set of matches `M ⊆ D × R` where each match pairs one driver with one rider
- Each driver matched with at most one rider
- Each rider matched with at most one driver

### Objectives
1. **Maximize matching rate**: Pair as many riders and drivers as possible
2. **Minimize additional distance**: Reduce total detour distance
3. **Maximize efficiency**: Use various weighting schemes to balance objectives

## Mathematical Formulation

### Decision Variables

```
xᵢⱼ ∈ {0, 1}  for all i ∈ D, j ∈ R

where:
  xᵢⱼ = 1  if driver i is matched with rider j
  xᵢⱼ = 0  otherwise
```

### Objective Functions

#### 1. Unweighted Model (Maximize Matches)

```
maximize: Σᵢ∈D Σⱼ∈R xᵢⱼ
```

**Purpose**: Find the maximum number of matches possible

#### 2. Weighted Model (Minimize Distance or Maximize Efficiency)

```
maximize: Σᵢ∈D Σⱼ∈R wᵢⱼ · xᵢⱼ

where wᵢⱼ is the weight for matching driver i with rider j
```

**Weight Options**:

**a) Distance Savings Weight**
```
wᵢⱼ = (dᵢ + dⱼ) - (d(Oᵢ, Oⱼ) + d(Oⱼ, Dⱼ) + d(Dⱼ, Dᵢ))
```
where:
- `dᵢ` = driver i's trip distance
- `dⱼ` = rider j's trip distance  
- `d(A, B)` = geodesic distance between points A and B
- `Oᵢ, Dᵢ` = origin and destination of driver i
- `Oⱼ, Dⱼ` = origin and destination of rider j

**b) Distance Proximity Index**
```
wᵢⱼ = min(dᵢ/dⱼ, dⱼ/dᵢ)
```

**Purpose**: Favor matches where trip distances are similar

**c) Adjusted Proximity Index**
```
wᵢⱼ = (dᵢ / dₘₐₜcₕ) · min(dᵢ/dⱼ, dⱼ/dᵢ)

where dₘₐₜcₕ = d(Oᵢ, Oⱼ) + d(Oⱼ, Dⱼ) + d(Dⱼ, Dᵢ)
```

### Constraints

#### 1. Each Driver Serves At Most One Rider
```
Σⱼ∈R xᵢⱼ ≤ 1    ∀i ∈ D
```

#### 2. Each Rider Served by At Most One Driver
```
Σᵢ∈D xᵢⱼ ≤ 1    ∀j ∈ R
```

#### 3. Binary Constraints
```
xᵢⱼ ∈ {0, 1}    ∀i ∈ D, j ∈ R
```

## Feasibility Filtering

Before optimization, infeasible matches are filtered out based on time window constraints.

### Time Feasibility Check

For a match between driver `i` and rider `j` to be feasible:

```
Let k = min(
    lⱼ - tⱼ - d(Oᵢ, Oⱼ) / vᵢ,
    lᵢ - tᵢ - d(Oⱼ, Oᵢ) / vⱼ
)

where:
- tᵢ, tⱼ = trip durations for driver i and rider j
- lᵢ, lⱼ = latest start times
- eᵢ, eⱼ = earliest start times
- vᵢ, vⱼ = average speeds (calculated as distance/time)
```

**Feasibility Condition**:
```
(k - eᵢ ≥ 0) OR (k + d(Oᵢ, Oⱼ)/vᵢ - eⱼ ≥ 0)
```

If this condition is violated, the pair `(i, j)` is excluded from the model.

## Algorithm Workflow

### Phase 1: Data Preprocessing

```
1. Load ridesharing data from CSV
2. Split into driver set D and rider set R
   - D = {announcements with ID < 100000}
   - R = {announcements with ID ≥ 100000}
3. Sort both sets by announcement time
4. Limit to specified size (e.g., 500 drivers, 500 riders)
5. Rename columns to match paper notation:
   - t = announcement time
   - e = earliest time
   - l = latest time
6. Calculate derived variable q = l - trip_time
```

### Phase 2: Pair Generation

```
1. Create Cartesian product: P = D × R
2. For each pair (i, j) ∈ P:
   - Calculate geodesic distances
   - Check time window feasibility
   - Remove if infeasible
3. Result: Feasible pair set F ⊆ P
```

### Phase 3: Weight Calculation (Optional)

```
1. Choose weighting method (distance_savings, proximity, etc.)
2. For each (i, j) ∈ F:
   - Calculate weight wᵢⱼ using chosen method
   - Store in pair dataframe
```

### Phase 4: Model Construction

```
1. Initialize Gurobi model
2. Create binary variables xᵢⱼ for all (i, j) ∈ F
3. Set objective function:
   - Unweighted: maximize Σxᵢⱼ
   - Weighted: maximize Σ(wᵢⱼ · xᵢⱼ)
4. Add constraints:
   - Driver constraint: Σⱼ xᵢⱼ ≤ 1 for all i
   - Rider constraint: Σᵢ xᵢⱼ ≤ 1 for all j
```

### Phase 5: Optimization

```
1. Call Gurobi optimizer
2. Solver finds optimal solution using:
   - Branch-and-bound
   - Cutting planes
   - Presolve techniques
3. Return optimal matches
```

### Phase 6: Performance Evaluation

```
1. Calculate Matching Rate (MR):
   MR = (2 × |M|) / (|D| + |R|)
   
2. Calculate Additional Kilometers Saved (AKS):
   For each match (i, j) ∈ M:
     savings = (dᵢ + dⱼ) - dₘₐₜcₕ
   AKS = (Σ savings) / |M|
   
3. Generate visualizations and reports
```

## Pseudocode

```python
ALGORITHM RidesharingOptimization(data_path, num_drivers, num_riders, use_weights)
    # Phase 1: Load and preprocess
    df ← READ_CSV(data_path)
    D ← FILTER(df, Announcement < 100000).HEAD(num_drivers)
    R ← FILTER(df, Announcement ≥ 100000).HEAD(num_riders)
    D ← SORT_BY(D, Announcementtime)
    R ← SORT_BY(R, Announcementtime)
    
    # Phase 2: Generate pairs
    F ← {}
    FOR each d IN D:
        FOR each r IN R:
            IF TIME_FEASIBLE(d, r):
                F ← F ∪ {(d, r)}
    
    # Phase 3: Calculate weights (if needed)
    IF use_weights:
        FOR each (d, r) IN F:
            w[d,r] ← CALCULATE_WEIGHT(d, r, method)
    
    # Phase 4: Build model
    model ← NEW_GUROBI_MODEL()
    x ← model.ADD_BINARY_VARS(F)
    
    IF use_weights:
        model.SET_OBJECTIVE(MAXIMIZE Σ w[d,r] · x[d,r])
    ELSE:
        model.SET_OBJECTIVE(MAXIMIZE Σ x[d,r])
    
    FOR each d IN D:
        model.ADD_CONSTRAINT(Σ_r x[d,r] ≤ 1)
    
    FOR each r IN R:
        model.ADD_CONSTRAINT(Σ_d x[d,r] ≤ 1)
    
    # Phase 5: Optimize
    model.OPTIMIZE()
    
    # Phase 6: Extract and evaluate
    M ← {(d,r) | x[d,r] = 1}
    MR ← CALCULATE_MATCHING_RATE(M, D, R)
    AKS ← CALCULATE_AKS(M, D, R)
    
    RETURN M, MR, AKS
END ALGORITHM
```

## Complexity Analysis

### Time Complexity

**Without Feasibility Filtering**:
- Pair generation: O(|D| × |R|)
- Model construction: O(|D| × |R|)
- Optimization: O(2^(|D|×|R|)) worst case (ILP is NP-hard)
  - In practice: O(|D|×|R|) to O(|D|×|R|²) with modern solvers
- Total: Dominated by optimization phase

**With Feasibility Filtering**:
- If filtering removes k% of pairs, reduces to O((1-k)×|D|×|R|)

### Space Complexity

- Decision variables: O(|D| × |R|)
- Constraints: O(|D| + |R|)
- Data storage: O(|D| + |R|)
- Total: O(|D| × |R|)

### Scalability

For 500 drivers and 500 riders:
- Maximum possible pairs: 250,000
- After feasibility filtering: ~50,000 to 150,000 (typical)
- Optimization time: 10 seconds to 2 minutes (depends on hardware and Gurobi parameters)

## Implementation Notes

### Gurobi Configuration

**Recommended settings for faster convergence**:
```python
model.setParam('TimeLimit', 300)        # 5-minute time limit
model.setParam('MIPGap', 0.01)          # 1% optimality gap acceptable
model.setParam('Presolve', 2)           # Aggressive presolve
model.setParam('Threads', 4)            # Use 4 CPU threads
```

### Distance Calculation

Uses **geodesic distance** (great-circle) rather than Euclidean:
```python
from geopy.distance import geodesic
distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
```

This accounts for Earth's curvature, providing more accurate distance estimates.

## Performance Optimization Tips

1. **Reduce problem size**:
   - Use smaller subsets (e.g., 100 drivers + 100 riders)
   - Filter by time windows before pairing
   - Filter by geographic proximity

2. **Warm start**:
   - Provide initial feasible solution
   - Use greedy heuristic for initial matches

3. **Parallel processing**:
   - Enable Gurobi threading
   - Parallelize weight calculations

4. **Incremental solving**:
   - Solve smaller time windows sequentially
   - Fix variables for already-matched pairs

## References

1. **Original Paper**: "Novel dynamic formulations for real-time ride-sharing systems"
2. **Gurobi Documentation**: [Gurobi Optimization Guide](https://www.gurobi.com/documentation/)
3. **Integer Programming**: Wolsey, L.A. (1998). Integer Programming

## Related Documentation

- [Main README](../README.md): Project overview
- [Setup Guide](../SETUP.md): Installation instructions
- [Data Documentation](../data/DATA_README.md): Dataset description
- [Source Code](../src/ridesharing_optimization.py): Implementation

---

**Version**: 1.0  
**Last Updated**: February 2026
