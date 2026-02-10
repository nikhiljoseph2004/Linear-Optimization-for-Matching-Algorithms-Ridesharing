# Linear Optimization for Ridesharing Matching Algorithms

A research project implementing linear programming models for real-time rider-driver matching in ridesharing systems. This work optimizes matching decisions to minimize travel distance while maximizing the number of successful matches.

## 📋 Overview

This project replicates and extends research on **dynamic ridesharing optimization**, applying linear programming techniques to solve the rider-driver matching problem. The optimization model uses integer linear programming (ILP) with the Gurobi solver to find optimal matches that balance efficiency and service quality.

### Key Objectives
- Maximize the **Matching Rate (MR)**: Percentage of riders successfully matched with drivers
- Minimize **Additional Kilometers**: Reduce total detour distance through optimal matching
- Evaluate different matching strategies and weighting schemes

### Research Context

This implementation is based on the paper:
> *"Novel dynamic formulations for real-time ride-sharing systems"*

The project was completed as part of IEDA3010 coursework, demonstrating practical applications of optimization theory to transportation systems.

## 🎯 Problem Formulation

### Mathematical Model

**Decision Variables:**
- `x[i,j]` ∈ {0,1}: Binary variable indicating whether rider `i` is matched with driver `j`

**Objective Function:**
```
Maximize: Σ x[i,j] × weight[i,j]
```

Where weights can represent:
- Number of matches (unweighted)
- Distance savings
- Distance proximity index
- Adjusted proximity index

**Constraints:**
```
Σ x[i,j] ≤ 1  ∀ drivers i    (each driver serves at most one rider)
Σ x[i,j] ≤ 1  ∀ riders j     (each rider served by at most one driver)
```

### Performance Metrics

1. **Matching Rate (MR)**
   ```
   MR = (2 × Number of Matches) / (Total Drivers + Total Riders)
   ```

2. **Additional Kilometers Saved (AKS)**
   ```
   AKS = (Σ Distance Saved per Match) / Number of Matches
   ```
   where Distance Saved = (Driver Trip + Rider Trip) - Shared Route Distance

## 📁 Repository Structure

```
.
├── README.md                  # Main project documentation (this file)
├── SETUP.md                   # Installation and setup guide
├── requirements.txt           # Python dependencies
│
├── src/                       # Source code
│   └── ridesharing_optimization.py   # Main optimization implementation
│
├── notebooks/                 # Jupyter notebooks
│   └── StableMatching.ipynb   # Interactive analysis and experimentation
│
├── data/                      # Data files
│   ├── Ridesharing_S_1.csv    # Melbourne ridesharing dataset
│   └── DATA_README.md         # Data description and schema
│
├── docs/                      # Documentation and papers
│   ├── IEDA3010 Final Report.pdf
│   ├── Novel dynamic formulations for real-time ride-sharing systems.pdf
│   └── ALGORITHM.md           # Detailed algorithm explanation
│
└── presentations/             # Presentation materials
    └── Dynamic_Ridesharing.pptx
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gurobi Optimizer (requires free academic license)
- Basic understanding of linear programming

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nikhiljoseph2004/Linear-Optimization-for-Matching-Algorithms-Ridesharing.git
   cd Linear-Optimization-for-Matching-Algorithms-Ridesharing
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gurobi license**
   - Get a free academic license from [Gurobi](https://www.gurobi.com/academia/academic-program-and-licenses/)
   - Follow their installation instructions

### Running the Optimization

**Option 1: Using the Python script**
```bash
cd src
python ridesharing_optimization.py
```

**Option 2: Using the Jupyter notebook**
```bash
jupyter notebook notebooks/StableMatching.ipynb
```

## 📊 Dataset

The project uses real-world ridesharing data from **Melbourne, Australia** containing:
- 5000+ trip announcements
- Origin and destination coordinates
- Time windows for pickups and drop-offs
- Distance and time estimates

For detailed data schema and description, see [`data/DATA_README.md`](data/DATA_README.md).

## 🔍 Key Features

### 1. Flexible Weighting Schemes
- **Unweighted**: Maximize number of matches
- **Distance Savings**: Minimize total additional distance
- **Proximity Index**: Favor trips with similar distances
- **Adjusted Proximity**: Hybrid approach combining multiple factors

### 2. Real-Time Feasibility Checks
The model filters infeasible matches based on:
- Time window constraints
- Maximum detour limits
- Geographic feasibility

### 3. Performance Visualization
Generates charts showing:
- Match distribution
- Distance savings analysis
- Matching rate vs. fleet size

## 📈 Results

Our implementation demonstrates:
- **Matching Rate**: 60-80% (varies with fleet size and constraints)
- **Average Distance Saved**: 2-5 km per match
- **Computation Time**: < 1 minute for 500 drivers + 500 riders

*For detailed results and analysis, refer to the [Final Report](docs/IEDA3010%20Final%20Report.pdf).*

## 🛠️ Technical Stack

- **Python 3.8+**: Core programming language
- **Gurobi Optimizer**: Integer linear programming solver
- **pandas**: Data manipulation and analysis
- **geopy**: Geographic distance calculations
- **matplotlib**: Visualization
- **Jupyter**: Interactive development and presentation

## 📚 Documentation

- **[SETUP.md](SETUP.md)**: Detailed installation and configuration guide
- **[data/DATA_README.md](data/DATA_README.md)**: Dataset description and schema
- **[docs/ALGORITHM.md](docs/ALGORITHM.md)**: In-depth algorithm explanation
- **[Final Report](docs/IEDA3010%20Final%20Report.pdf)**: Complete research findings
- **[Original Paper](docs/Novel%20dynamic%20formulations%20for%20real-time%20ride-sharing%20systems.pdf)**: Theoretical foundation

## 🤝 Contributing

This is an academic research project. While contributions are welcome, please note:
- The main implementation reflects research objectives from IEDA3010 coursework
- Focus is on demonstrating optimization techniques, not production deployment
- Suggested improvements: additional weighting schemes, larger datasets, different solvers

## 📄 License

This project is an academic work created for educational purposes. The code is provided as-is for learning and research.

## 👥 Authors

**Course**: IEDA3010 - Optimization Methods  
**Institution**: [Your University Name]  
**Contributors**: [Names of team members]

## 🙏 Acknowledgments

- Original paper authors for the theoretical framework
- Course instructors for guidance and support
- Gurobi for providing academic licenses
- Melbourne transportation data providers

## 📞 Contact

For questions or discussions about this research:
- Open an issue on GitHub
- Contact: [Your contact information]

---

**Note**: This is a research/educational project demonstrating optimization techniques for ridesharing. It is not intended for production use without significant additional development and testing.
