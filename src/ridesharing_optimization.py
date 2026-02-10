"""
Ridesharing Optimization using Linear Programming

This module implements a linear optimization model for matching riders with drivers
in a ridesharing system. The model uses Gurobi optimizer to find optimal matches
that minimize total detour distance while maximizing the matching rate.

Key Metrics:
- Matching Rate (MR): Percentage of riders successfully matched with drivers
- Additional Kilometers Saved (AKS): Distance saved through ridesharing
"""

import pandas as pd
import os
from geopy.distance import geodesic
from gurobipy import Model, GRB
import warnings

warnings.filterwarnings('ignore')


class RidesharingOptimizer:
    """
    A class for optimizing rider-driver matches in a ridesharing system.
    """
    
    def __init__(self, data_path, num_drivers=500, num_riders=500):
        """
        Initialize the optimizer with data.
        
        Args:
            data_path: Path to the CSV file containing ridesharing data
            num_drivers: Number of drivers to consider (default: 500)
            num_riders: Number of riders to consider (default: 500)
        """
        self.data_path = data_path
        self.num_drivers = num_drivers
        self.num_riders = num_riders
        self.df = None
        self.driverdf = None
        self.riderdf = None
        self.processdf = None
        self.model = None
        self.x = None
        
    def load_data(self):
        """Load and preprocess the ridesharing data."""
        print("Loading data...")
        self.df = pd.read_csv(self.data_path)
        
        # Split into drivers (Announcement < 100000) and riders (Announcement > 100000)
        self.driverdf = self.df[self.df['Announcement'] < 100000]
        self.riderdf = self.df[self.df['Announcement'] > 100000]
        
        # Sort by announcement time and limit size
        self.driverdf = self.driverdf.sort_values(by='Announcementtime').head(self.num_drivers)
        self.riderdf = self.riderdf.sort_values(by='Announcementtime').head(self.num_riders)
        
        print(f"Loaded {len(self.driverdf)} drivers and {len(self.riderdf)} riders")
        
    def preprocess_data(self):
        """Preprocess data by renaming columns and creating variable columns."""
        print("Preprocessing data...")
        
        # Rename columns as per research paper notation
        self.driverdf = self.driverdf.rename(columns={
            'Announcementtime': 't',
            'Earliesttime': 'e',
            'Latesttime': 'l'
        })
        self.driverdf['q'] = self.driverdf['l'] - self.driverdf['Time_Car-Peak']
        
        self.riderdf = self.riderdf.rename(columns={
            'Announcementtime': 't',
            'Earliesttime': 'e',
            'Latesttime': 'l'
        })
        self.riderdf['q'] = self.riderdf['l'] - self.riderdf['Time_Car-Peak']
        
    def create_pairs(self):
        """Create Cartesian product of all driver-rider pairs."""
        print("Creating driver-rider pairs...")
        
        # Perform Cartesian product
        self.driverdf['key'] = 1
        self.riderdf['key'] = 1
        pairdf = pd.merge(self.driverdf, self.riderdf, on='key').drop('key', axis=1)
        
        # Create combined announcement ID
        pairdf['Combined_Announcement'] = (
            pairdf['Announcement_x'].astype(str) + pairdf['Announcement_y'].astype(str)
        )
        pairdf = pairdf.drop(columns=['Announcement_x', 'Announcement_y'])
        
        # Reorder columns
        columns = pairdf.columns.tolist()
        new_order = [columns[-1]] + columns[:-1]
        self.processdf = pairdf[new_order]
        
        print(f"Created {len(self.processdf)} possible pairs")
        
    def calculate_weights(self, method='distance_savings'):
        """
        Calculate weights for each pair based on the specified method.
        
        Args:
            method: Weight calculation method
                - 'distance_savings': Net distance savings from matching
                - 'distance_proximity': Distance proximity index
                - 'adjusted_proximity': Adjusted distance proximity index
        """
        print(f"Calculating weights using method: {method}")
        self.processdf['weight'] = 0
        
        for index, row in self.processdf.iterrows():
            driver_origin = (row['Origin_Latitude_x'], row['Origin_Longitude_x'])
            driver_endpoint = (row['Destination_Latitude_x'], row['Destination_Longitude_x'])
            rider_origin = (row['Origin_Latitude_y'], row['Origin_Longitude_y'])
            rider_endpoint = (row['Destination_Latitude_y'], row['Destination_Longitude_y'])
            
            driver_trip_length = row['Distance_Car-Peak_x']
            rider_trip_length = row['Distance_Car-Peak_y']
            
            if method == 'distance_savings':
                # Net distance savings
                no_match_length = driver_trip_length + rider_trip_length
                with_match_length = (
                    geodesic(driver_origin, rider_origin).kilometers +
                    geodesic(rider_origin, rider_endpoint).kilometers +
                    geodesic(rider_endpoint, driver_endpoint).kilometers
                )
                weight = no_match_length - with_match_length
                
            elif method == 'distance_proximity':
                # Distance proximity index
                weight = min(
                    driver_trip_length / rider_trip_length,
                    rider_trip_length / driver_trip_length
                )
                
            elif method == 'adjusted_proximity':
                # Adjusted distance proximity index
                with_match_length = (
                    geodesic(driver_origin, rider_origin).kilometers +
                    geodesic(rider_origin, rider_endpoint).kilometers +
                    geodesic(rider_endpoint, driver_endpoint).kilometers
                )
                weight = (driver_trip_length / with_match_length) * min(
                    driver_trip_length / rider_trip_length,
                    rider_trip_length / driver_trip_length
                )
                
            self.processdf.at[index, 'weight'] = weight
            
    def build_model(self, use_weights=False):
        """
        Build the optimization model.
        
        Args:
            use_weights: If True, use weighted objective; if False, maximize number of matches
        """
        print("Building optimization model...")
        
        drivers = self.driverdf['Announcement'].unique()
        riders = self.riderdf['Announcement'].unique()
        
        self.model = Model('ridesharing_maximizer')
        
        if use_weights:
            possible_matches = set(zip(
                self.processdf['Announcement_x'],
                self.processdf['Announcement_y'],
                self.processdf['weight']
            ))
            self.x = self.model.addVars(
                [(d, r, w) for d, r, w in possible_matches],
                vtype=GRB.BINARY,
                name="x"
            )
            # Maximize weighted matches
            self.model.setObjective(
                sum(self.x[d, r, w] * w for d, r, w in possible_matches),
                GRB.MAXIMIZE
            )
            
            # Constraints: each driver/rider matched at most once
            for d in drivers:
                self.model.addConstr(
                    sum(self.x[d, r, w] for dm, r, w in possible_matches if dm == d) <= 1
                )
            for r in riders:
                self.model.addConstr(
                    sum(self.x[d, r, w] for d, rm, w in possible_matches if rm == r) <= 1
                )
        else:
            possible_matches = set(zip(
                self.processdf['Announcement_x'],
                self.processdf['Announcement_y']
            ))
            self.x = self.model.addVars(possible_matches, vtype=GRB.BINARY, name="x")
            
            # Maximize number of matches
            self.model.setObjective(self.x.sum(), GRB.MAXIMIZE)
            
            # Constraints: each driver/rider matched at most once
            for d in drivers:
                self.model.addConstr(
                    sum(self.x[d, r] for r in riders if (d, r) in self.x) <= 1
                )
            for r in riders:
                self.model.addConstr(
                    sum(self.x[d, r] for d in drivers if (d, r) in self.x) <= 1
                )
                
    def optimize(self):
        """Run the optimization."""
        print("\nOptimizing...")
        self.model.optimize()
        
        if self.model.status == GRB.OPTIMAL:
            print("Optimal solution found!")
        else:
            print(f"Optimization status: {self.model.status}")
            
    def calculate_metrics(self):
        """Calculate performance metrics (Matching Rate and AKS)."""
        print("\nCalculating performance metrics...")
        
        drivers = self.driverdf['Announcement'].unique()
        riders = self.riderdf['Announcement'].unique()
        
        # Get all possible matches from decision variables
        if isinstance(list(self.x.keys())[0], tuple) and len(list(self.x.keys())[0]) == 3:
            # Weighted model
            possible_matches = [(d, r) for d, r, w in self.x.keys()]
            x_dict = {(d, r): self.x[d, r, w] for d, r, w in self.x.keys()}
        else:
            # Unweighted model
            possible_matches = list(self.x.keys())
            x_dict = self.x
        
        # Calculate matching rate
        matched = sum(1 for dr in possible_matches if x_dict[dr].x > 0.5)
        match_rate = matched * 2 / (len(drivers) + len(riders))
        
        # Calculate Additional Kilometers Saved (AKS)
        k_total = 0
        matched_count = 0
        
        for dr in possible_matches:
            if x_dict[dr].x > 0.5:
                driver_trip = self.driverdf[self.driverdf['Announcement'] == dr[0]]['Distance_Car-Peak']
                driver_trip_length = float(driver_trip.iloc[0])
                
                rider_trip = self.riderdf[self.riderdf['Announcement'] == dr[1]]['Distance_Car-Peak']
                rider_trip_length = float(rider_trip.iloc[0])
                
                no_match_length = driver_trip_length + rider_trip_length
                
                driver_row = self.driverdf[self.driverdf['Announcement'] == dr[0]]
                driver_origin = (
                    float(driver_row['Origin_Latitude'].iloc[0]),
                    float(driver_row['Origin_Longitude'].iloc[0])
                )
                driver_endpoint = (
                    float(driver_row['Destination_Latitude'].iloc[0]),
                    float(driver_row['Destination_Longitude'].iloc[0])
                )
                
                rider_row = self.riderdf[self.riderdf['Announcement'] == dr[1]]
                rider_origin = (
                    float(rider_row['Origin_Latitude'].iloc[0]),
                    float(rider_row['Origin_Longitude'].iloc[0])
                )
                rider_endpoint = (
                    float(rider_row['Destination_Latitude'].iloc[0]),
                    float(rider_row['Destination_Longitude'].iloc[0])
                )
                
                with_match_length = (
                    geodesic(driver_origin, rider_origin).kilometers +
                    geodesic(rider_origin, rider_endpoint).kilometers +
                    geodesic(rider_endpoint, driver_endpoint).kilometers
                )
                
                matched_count += 1
                k_total += no_match_length - with_match_length
                
        aks = k_total / matched_count if matched_count > 0 else 0
        
        print(f"\n{'='*50}")
        print(f"Performance Metrics:")
        print(f"{'='*50}")
        print(f"Total Matches: {matched}")
        print(f"Matching Rate (MR): {match_rate:.2%}")
        print(f"Additional Kilometers Saved (AKS): {aks:.2f} km")
        print(f"{'='*50}\n")
        
        return {
            'matches': matched,
            'match_rate': match_rate,
            'aks': aks
        }
        
    def run_optimization(self, use_weights=False, weight_method='distance_savings'):
        """
        Run the complete optimization pipeline.
        
        Args:
            use_weights: Whether to use weighted objective function
            weight_method: Method for calculating weights (if use_weights=True)
        """
        self.load_data()
        self.preprocess_data()
        self.create_pairs()
        
        if use_weights:
            self.calculate_weights(method=weight_method)
            
        self.build_model(use_weights=use_weights)
        self.optimize()
        metrics = self.calculate_metrics()
        
        return metrics


def main():
    """Main execution function."""
    # Set up data path
    data_path = '../data/Ridesharing_S_1.csv'
    
    print("\n" + "="*70)
    print("RIDESHARING OPTIMIZATION - Linear Programming Model")
    print("="*70 + "\n")
    
    # Initialize optimizer
    optimizer = RidesharingOptimizer(
        data_path=data_path,
        num_drivers=500,
        num_riders=500
    )
    
    # Run optimization (unweighted model)
    print("Running unweighted optimization (maximize number of matches)...\n")
    metrics = optimizer.run_optimization(use_weights=False)
    
    print("\nOptimization complete!")


if __name__ == "__main__":
    main()
