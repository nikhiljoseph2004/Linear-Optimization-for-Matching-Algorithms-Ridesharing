# Dataset Documentation

## Overview

This directory contains the ridesharing dataset used for optimization experiments. The data represents real-world trip announcements from **Melbourne, Australia**, including both driver availability and rider requests.

## Dataset: Ridesharing_S_1.csv

### Description

The dataset contains trip announcement data used to simulate a ridesharing matching system. Each row represents a trip announcement with origin/destination coordinates, time windows, and distance/time estimates.

### Key Statistics

- **Total Records**: ~5,000+ trip announcements
- **Geographic Region**: Melbourne, Australia
- **Data Type**: Mixed (drivers and riders)
- **File Size**: ~3.2 MB
- **Format**: CSV (Comma-Separated Values)

### Identifying Drivers vs. Riders

The dataset combines both driver and rider announcements in a single file:

- **Drivers**: `Announcement < 100000`
- **Riders**: `Announcement >= 100000`

This convention allows easy filtering:
```python
drivers = df[df['Announcement'] < 100000]
riders = df[df['Announcement'] >= 100000]
```

## Data Schema

### Column Descriptions

| Column Name | Type | Description | Units |
|------------|------|-------------|-------|
| `Announcement` | Integer | Unique identifier for the trip announcement | - |
| `Origin` | Integer | Origin location ID | - |
| `Destination` | Integer | Destination location ID | - |
| `Distance_Car-Peak` | Float | Estimated distance during peak hours | Kilometers |
| `Time_Car-Peak` | Float | Estimated travel time during peak hours | Minutes |
| `Earliesttime` | Float | Earliest acceptable pickup/start time | Minutes from midnight |
| `Latesttime` | Float | Latest acceptable pickup/start time | Minutes from midnight |
| `Announcementtime` | Float | Time when trip was announced | Minutes from midnight |
| `Starttime` | Float | Actual/scheduled start time | Minutes from midnight |
| `Origin_Latitude` | Float | Latitude of origin location | Degrees |
| `Origin_Longitude` | Float | Longitude of origin location | Degrees |
| `Destination_Latitude` | Float | Latitude of destination location | Degrees |
| `Destination_Longitude` | Float | Longitude of destination location | Degrees |

### Time Representation

All time columns use **minutes from midnight** (0-1440):
- `0` = 00:00 (midnight)
- `600` = 10:00 AM
- `720` = 12:00 PM (noon)
- `1080` = 6:00 PM

**Example**: 
- `Announcementtime = 622.87` → Approximately 10:23 AM
- `Earliesttime = 626.89` → Approximately 10:27 AM
- `Latesttime = 656.66` → Approximately 10:57 AM

### Geographic Coordinates

The dataset uses the **WGS84 coordinate system**:
- Latitude range: Approximately -38.0° to -37.7° (Southern Hemisphere)
- Longitude range: Approximately 144.5° to 145.3° (Eastern Hemisphere)

These coordinates correspond to the **greater Melbourne metropolitan area**.

## Sample Data

```csv
Announcement,Origin,Destination,Distance_Car-Peak,Time_Car-Peak,Earliesttime,Latesttime,Announcementtime,Starttime,Origin_Latitude,Origin_Longitude,Destination_Latitude,Destination_Longitude
1,27264,27264,8.797,9.774,626.886,656.661,622.874,636.886,-37.946,144.690,-37.955,144.685
2,24412,24412,6.002,6.669,694.713,721.382,662.647,704.713,-37.821,145.203,-37.805,145.227
```

## Data Usage in Optimization

### Preprocessing Steps

1. **Split into driver and rider datasets**
   ```python
   driverdf = df[df['Announcement'] < 100000]
   riderdf = df[df['Announcement'] > 100000]
   ```

2. **Sort by announcement time**
   ```python
   driverdf = driverdf.sort_values(by='Announcementtime')
   riderdf = riderdf.sort_values(by='Announcementtime')
   ```

3. **Limit dataset size** (for computational efficiency)
   ```python
   driverdf = driverdf.head(500)
   riderdf = riderdf.head(500)
   ```

4. **Create derived variables** (as per research paper notation)
   ```python
   # Rename to match paper notation
   df = df.rename(columns={
       'Announcementtime': 't',
       'Earliesttime': 'e',
       'Latesttime': 'l'
   })
   
   # Calculate latest feasible start time
   df['q'] = df['l'] - df['Time_Car-Peak']
   ```

### Distance Calculations

The optimization uses **geodesic distance** (great-circle distance) for precise calculations:

```python
from geopy.distance import geodesic

origin = (latitude1, longitude1)
destination = (latitude2, longitude2)
distance_km = geodesic(origin, destination).kilometers
```

### Time Window Feasibility

A match between driver `i` and rider `j` is feasible only if:

```
k = min(
    l_j - time_j - distance(origin_i, origin_j),
    l_i - time_i - distance(origin_j, origin_i)
)

if (k - e_i >= 0) OR (k + distance(origin_i, origin_j) - e_j >= 0):
    # Match is feasible
```

## Data Quality Notes

### Assumptions
- All times are in the same timezone (Melbourne local time)
- Distance estimates are based on road network calculations
- Peak hour conditions are assumed throughout

### Limitations
- Some announcements may have identical origin and destination (same location ID)
- Time windows vary significantly in size
- Not all origin-destination pairs are feasible for matching

### Missing Data
This dataset is complete with no missing values. All required fields are populated for every record.

## Usage Examples

### Loading the Data

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('data/Ridesharing_S_1.csv')

# Basic exploration
print(f"Total records: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```

### Filtering by Time

```python
# Get announcements between 8 AM and 10 AM
morning_rush = df[
    (df['Announcementtime'] >= 480) &  # 8:00 AM
    (df['Announcementtime'] <= 600)    # 10:00 AM
]
```

### Geographic Filtering

```python
# Get trips within a specific region
city_center = df[
    (df['Origin_Latitude'] >= -37.85) &
    (df['Origin_Latitude'] <= -37.80) &
    (df['Origin_Longitude'] >= 144.95) &
    (df['Origin_Longitude'] <= 145.00)
]
```

### Statistics

```python
# Distance statistics
print(f"Average trip distance: {df['Distance_Car-Peak'].mean():.2f} km")
print(f"Average trip time: {df['Time_Car-Peak'].mean():.2f} minutes")

# Time window statistics
df['TimeWindow'] = df['Latesttime'] - df['Earliesttime']
print(f"Average time window: {df['TimeWindow'].mean():.2f} minutes")
```

## Data Source

This dataset is derived from real-world transportation data from Melbourne, Australia. It has been anonymized and processed for research purposes.

**Citation**: If you use this data in your research, please cite the original paper:
> "Novel dynamic formulations for real-time ride-sharing systems"

## Related Files

- **Original data documentation**: `data introduction.docx` (in root directory)
- **Optimization script**: `src/ridesharing_optimization.py`
- **Interactive analysis**: `notebooks/StableMatching.ipynb`

## Questions or Issues?

If you encounter any issues with the data or have questions about the schema:
1. Check the [main README](../README.md) for project context
2. Review the [algorithm documentation](../docs/ALGORITHM.md)
3. Open an issue on GitHub with specific questions

---

**Last Updated**: February 2026  
**Version**: 1.0
