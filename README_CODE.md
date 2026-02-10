# Ridesharing Optimization Source Code

This repository now includes the complete source code that was previously only available as screenshots in the PowerPoint presentation.

## Source Code File

**`ridesharing_optimization.py`** - Main optimization program for ridesharing matching algorithms

## Description

This Python program implements a linear optimization model for matching riders with drivers in a ridesharing system. The model uses Gurobi optimizer to find optimal matches that minimize total detour distance while maximizing the matching rate.

### Key Features:

- **Linear Optimization Model**: Uses Gurobi to solve the rider-driver matching problem
- **Performance Metrics**:
  - **Matching Rate (MR)**: Percentage of riders successfully matched with drivers
  - **Additional Kilometers Saved (AKS)**: Distance saved through ridesharing
- **Visualization**: Generates charts showing matching results and distance analysis

## Requirements

To run this code, you need to install the following Python packages:

```bash
pip install pandas numpy matplotlib gurobipy
```

**Note**: Gurobi requires a license. You can get a free academic license from [Gurobi's website](https://www.gurobi.com/academia/academic-program-and-licenses/).

## Usage

1. Ensure the `Ridesharing_S_1.csv` data file is in the same directory
2. Run the optimization:

```bash
python ridesharing_optimization.py
```

3. The program will output:
   - Number of matches found
   - Matching rate (MR)
   - Additional kilometers saved (AKS)
   - A visualization saved as `ridesharing_results.png`

## Input Data Format

The program expects a CSV file (`Ridesharing_S_1.csv`) with the following columns:
- `Announcement`: Unique ID for each trip announcement
- `Origin`: Origin location ID
- `Destination`: Destination location ID
- `Origin_Latitude`: Latitude of origin
- `Origin_Longitude`: Longitude of origin
- `Destination_Latitude`: Latitude of destination
- `Destination_Longitude`: Longitude of destination
- `Distance_Car-Peak`: Distance in peak hours
- Other columns for timing information

## Algorithm

The optimization model:
1. Splits trip announcements into riders and drivers
2. Creates binary decision variables for each possible rider-driver match
3. Minimizes total detour distance using Manhattan distance calculation
4. Ensures each rider is matched with at most one driver and vice versa
5. Calculates performance metrics (MR and AKS)

## Source

This code was extracted from slides 14-15 of the `Dynamic_Ridesharing.pptx` presentation file in this repository.
