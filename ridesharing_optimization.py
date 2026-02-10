import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import *

# Configuration constants
ESTIMATED_SAVINGS_RATE = 0.3  # Estimated 30% distance savings per rideshare match

# Read data
data = pd.read_csv('Ridesharing_S_1.csv')

# For simplicity, assume first half are riders and second half are drivers
# In a real scenario, you would have separate rider/driver identification
n = len(data)
split_point = n // 2

riders = data.iloc[:split_point]
drivers = data.iloc[split_point:]

num_riders = len(riders)
num_drivers = len(drivers)

print(f"Number of riders: {num_riders}")
print(f"Number of drivers: {num_drivers}")

# Create model
model = Model('Ridesharing')
model.setParam('OutputFlag', 0)  # Suppress Gurobi output

# Decision variables
x = {}
for i in range(num_riders):
    for j in range(num_drivers):
        x[i, j] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}')

# Update model to integrate new variables
model.update()

# Calculate distance function using coordinates
def calculate_distance(rider_idx, driver_idx):
    rider_orig_lat = riders.iloc[rider_idx]['Origin_Latitude']
    rider_orig_lon = riders.iloc[rider_idx]['Origin_Longitude']
    rider_dest_lat = riders.iloc[rider_idx]['Destination_Latitude']
    rider_dest_lon = riders.iloc[rider_idx]['Destination_Longitude']
    
    driver_orig_lat = drivers.iloc[driver_idx]['Origin_Latitude']
    driver_orig_lon = drivers.iloc[driver_idx]['Origin_Longitude']
    driver_dest_lat = drivers.iloc[driver_idx]['Destination_Latitude']
    driver_dest_lon = drivers.iloc[driver_idx]['Destination_Longitude']
    
    # Calculate sum of Manhattan distances between origins and destinations
    # This represents the detour needed for the driver to pick up and drop off the rider
    detour = (abs(rider_orig_lat - driver_orig_lat) + 
              abs(rider_orig_lon - driver_orig_lon) +
              abs(rider_dest_lat - driver_dest_lat) + 
              abs(rider_dest_lon - driver_dest_lon))
    
    return detour

# Objective function - minimize total detour distance
model.setObjective(
    quicksum(
        x[i, j] * calculate_distance(i, j)
        for i in range(num_riders)
        for j in range(num_drivers)
    ),
    GRB.MINIMIZE
)

# Constraints
# Each rider assigned to at most one driver
for i in range(num_riders):
    model.addConstr(quicksum(x[i, j] for j in range(num_drivers)) <= 1)

# Each driver assigned to at most one rider
for j in range(num_drivers):
    model.addConstr(quicksum(x[i, j] for i in range(num_riders)) <= 1)

# Solve model
print("\nOptimizing ridesharing matches...")
model.optimize()

# Extract solution
matches = []
if model.status == GRB.OPTIMAL:
    for i in range(num_riders):
        for j in range(num_drivers):
            if x[i, j].X > 0.5:
                rider_id = riders.iloc[i]['Announcement']
                driver_id = drivers.iloc[j]['Announcement']
                matches.append((rider_id, driver_id))
    
    print(f'\n=== RESULTS ===')
    print(f'Optimal solution found!')
    print(f'Number of matches: {len(matches)}')
    print(f'Total detour distance: {model.objVal:.2f}')
    print('\nSample matches (first 10):')
    for idx, (rider, driver) in enumerate(matches[:10]):
        print(f'  Rider {rider} matched with Driver {driver}')
    if len(matches) > 10:
        print(f'  ... and {len(matches) - 10} more matches')
else:
    print('No optimal solution found')

# Calculate matching rate (MR)
matching_rate = (len(matches) / num_riders) * 100
print(f'\n=== PERFORMANCE METRICS ===')
print(f'Matching Rate (MR): {matching_rate:.2f}%')

# Calculate additional kilometers saved (AKS)
# Original distance = sum of all rider distances
total_original_distance = riders['Distance_Car-Peak'].sum()

# With ridesharing, calculate saved distance
if model.status == GRB.OPTIMAL and len(matches) > 0:
    # Approximate distance saved per match
    avg_distance_per_rider = riders['Distance_Car-Peak'].mean()
    distance_saved = len(matches) * avg_distance_per_rider * ESTIMATED_SAVINGS_RATE
    print(f'Additional Kilometers Saved (AKS): {distance_saved:.2f} km')
    print(f'Total original distance: {total_original_distance:.2f} km')
    print(f'Savings percentage: {(distance_saved/total_original_distance)*100:.2f}%')
else:
    print(f'Additional Kilometers Saved (AKS): 0.00 km')

# Visualization
if len(matches) > 0:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Matching Rate
    categories = ['Matched', 'Unmatched']
    values = [len(matches), num_riders - len(matches)]
    colors = ['#2ecc71', '#e74c3c']
    ax1.bar(categories, values, color=colors)
    ax1.set_ylabel('Number of Riders')
    ax1.set_title(f'Matching Results (MR: {matching_rate:.2f}%)')
    ax1.set_ylim([0, num_riders * 1.1])
    
    # Add value labels on bars
    for i, v in enumerate(values):
        ax1.text(i, v + num_riders * 0.02, str(v), ha='center', va='bottom')
    
    # Plot 2: Distance Analysis
    categories2 = ['Original\nDistance', 'Distance\nSaved']
    values2 = [total_original_distance, distance_saved if model.status == GRB.OPTIMAL else 0]
    colors2 = ['#3498db', '#27ae60']
    ax2.bar(categories2, values2, color=colors2)
    ax2.set_ylabel('Distance (km)')
    ax2.set_title('Distance Analysis')
    
    # Add value labels on bars
    for i, v in enumerate(values2):
        ax2.text(i, v + max(values2) * 0.02, f'{v:.1f} km', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('ridesharing_results.png', dpi=300, bbox_inches='tight')
    print(f'\nVisualization saved as ridesharing_results.png')
    
print('\n=== OPTIMIZATION COMPLETE ===')
