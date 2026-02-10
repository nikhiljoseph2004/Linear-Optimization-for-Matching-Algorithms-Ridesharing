# Setup Guide

This guide will help you set up the development environment for the Ridesharing Optimization project.

## Prerequisites

### Required Software
- **Python 3.8 or higher**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **Gurobi Optimizer**: Free academic license required (see below)

### System Requirements
- Operating System: Windows, macOS, or Linux
- RAM: Minimum 4GB (8GB recommended)
- Disk Space: ~500MB for dependencies and data

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nikhiljoseph2004/Linear-Optimization-for-Matching-Algorithms-Ridesharing.git
cd Linear-Optimization-for-Matching-Algorithms-Ridesharing
```

### 2. Set Up Python Environment

We recommend using a virtual environment to avoid dependency conflicts.

#### Option A: Using venv (built-in)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Option B: Using conda

```bash
# Create conda environment
conda create -n ridesharing python=3.9
conda activate ridesharing
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `matplotlib`: Visualization
- `gurobipy`: Optimization solver
- `geopy`: Geographic calculations
- `jupyter`: Interactive notebooks

### 4. Set Up Gurobi License

Gurobi is a commercial optimization solver that offers **free academic licenses**.

#### Step 4.1: Register for Academic License

1. Visit [Gurobi Academic Program](https://www.gurobi.com/academia/academic-program-and-licenses/)
2. Register with your academic email address (.edu)
3. Request a free academic license

#### Step 4.2: Install Gurobi License

After receiving your license:

```bash
# Download license file from Gurobi website
# Follow the instructions to get grbgetkey command

grbgetkey [YOUR-LICENSE-KEY]
```

The license file will be saved to:
- **Windows**: `C:\gurobi\gurobi.lic`
- **macOS/Linux**: `~/gurobi.lic`

#### Step 4.3: Verify Gurobi Installation

```bash
python -c "import gurobipy; print(gurobipy.gurobi.version())"
```

If successful, you should see the Gurobi version number.

## Verification

### Test Your Setup

Run a quick test to ensure everything is working:

```bash
cd src
python -c "from ridesharing_optimization import RidesharingOptimizer; print('Setup successful!')"
```

### Run the Optimization

```bash
cd src
python ridesharing_optimization.py
```

Expected output:
```
==============================================================
RIDESHARING OPTIMIZATION - Linear Programming Model
==============================================================

Loading data...
Loaded 500 drivers and 500 riders
Preprocessing data...
Creating driver-rider pairs...
Created 250000 possible pairs
Building optimization model...

Optimizing...
Gurobi Optimizer...
[optimization progress]
Optimal solution found!

Calculating performance metrics...

==================================================
Performance Metrics:
==================================================
Total Matches: 400
Matching Rate (MR): 80.00%
Additional Kilometers Saved (AKS): 3.45 km
==================================================
```

## Using Jupyter Notebooks

### Start Jupyter

```bash
jupyter notebook
```

This will open Jupyter in your browser. Navigate to `notebooks/StableMatching.ipynb`.

### Running the Notebook

1. Open `StableMatching.ipynb`
2. Run cells sequentially using `Shift+Enter`
3. Modify parameters as needed for experimentation

## Troubleshooting

### Problem: Gurobi license error

**Error**: `GRB_ERROR_NO_LICENSE`

**Solution**:
1. Verify license file location
2. Set environment variable:
   ```bash
   # Windows
   set GRB_LICENSE_FILE=C:\gurobi\gurobi.lic
   
   # macOS/Linux
   export GRB_LICENSE_FILE=~/gurobi.lic
   ```

### Problem: Module not found errors

**Error**: `ModuleNotFoundError: No module named 'gurobipy'`

**Solution**:
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Problem: Data file not found

**Error**: `FileNotFoundError: Ridesharing_S_1.csv`

**Solution**:
- Ensure you're running the script from the correct directory
- Verify the data file exists in `data/Ridesharing_S_1.csv`
- Check the path in the script: `data_path = '../data/Ridesharing_S_1.csv'`

### Problem: Memory errors with large datasets

**Error**: `MemoryError`

**Solution**:
- Reduce the number of drivers/riders in the script:
  ```python
  optimizer = RidesharingOptimizer(
      data_path=data_path,
      num_drivers=100,  # Reduce from 500
      num_riders=100    # Reduce from 500
  )
  ```

### Problem: Slow optimization

**Issue**: Optimization takes very long

**Solution**:
- Reduce problem size (fewer drivers/riders)
- Add time limit to Gurobi:
  ```python
  model.setParam('TimeLimit', 300)  # 5 minutes
  ```
- Enable presolve:
  ```python
  model.setParam('Presolve', 2)
  ```

## Alternative: Using Docker (Optional)

If you prefer containerization:

```dockerfile
# Dockerfile (create this file)
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/ridesharing_optimization.py"]
```

Build and run:
```bash
docker build -t ridesharing-opt .
docker run -v $(pwd)/data:/app/data ridesharing-opt
```

**Note**: Gurobi license setup in Docker requires additional configuration.

## Development Tips

### Enable Verbose Output

For debugging, enable detailed Gurobi output:
```python
model.setParam('OutputFlag', 1)  # Enable console output
model.setParam('LogFile', 'gurobi.log')  # Save to log file
```

### Use Smaller Datasets for Testing

Modify the script to use fewer samples:
```python
optimizer = RidesharingOptimizer(
    data_path=data_path,
    num_drivers=50,   # Smaller for quick tests
    num_riders=50
)
```

### Profile Performance

To measure performance:
```python
import time

start = time.time()
metrics = optimizer.run_optimization()
print(f"Time taken: {time.time() - start:.2f} seconds")
```

## Next Steps

After successful setup:
1. Review the main [README.md](README.md) for project overview
2. Explore the [algorithm documentation](docs/ALGORITHM.md)
3. Read the [data description](data/DATA_README.md)
4. Experiment with the Jupyter notebook
5. Try different optimization parameters

## Getting Help

If you encounter issues not covered here:
1. Check [GitHub Issues](https://github.com/nikhiljoseph2004/Linear-Optimization-for-Matching-Algorithms-Ridesharing/issues)
2. Review [Gurobi Documentation](https://www.gurobi.com/documentation/)
3. Open a new issue with:
   - Your operating system
   - Python version
   - Error message and full stack trace
   - Steps to reproduce

## Additional Resources

- [Gurobi Python API](https://www.gurobi.com/documentation/current/refman/py_python_api_overview.html)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [geopy Documentation](https://geopy.readthedocs.io/)
- [Jupyter Notebook Guide](https://jupyter-notebook.readthedocs.io/)
