"""
Generate Sample Dirty Dataset
Creates a sample dataset with noise for testing the pipeline
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

def generate_dirty_dataset(n_records=300, output_path="data/dirty_transport_dataset.csv"):
    """
    Generate a sample dirty dataset with:
    - Missing values
    - Inconsistent formats
    - Outliers
    - Noisy categories
    """
    np.random.seed(42)
    random.seed(42)
    
    # Base data
    routes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    weathers = ['clear', 'cloudy', 'rainy', 'snowy']
    weather_variants = {
        'clear': ['clear', 'sunny', 'Sun', 'CLEAR'],
        'cloudy': ['cloudy', 'Cloudy', 'overcast', 'clouds'],
        'rainy': ['rainy', 'rain', 'Rain', 'drizzle'],
        'snowy': ['snowy', 'snow', 'Snow', 'sleet']
    }
    
    data = []
    base_time = datetime(2024, 1, 1, 6, 0, 0)
    
    for i in range(n_records):
        # Route ID - sometimes with text, sometimes numeric
        route = random.choice(routes)
        if random.random() < 0.3:  # 30% have text format
            route_id = f"Route {route}" if random.random() < 0.5 else f"R{route}"
        else:
            route_id = route
        
        # Scheduled time
        scheduled_time = base_time + timedelta(days=i//10, hours=i%24, minutes=random.randint(0, 59))
        scheduled_str = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Actual time - sometimes dirty format, sometimes missing
        if random.random() < 0.1:  # 10% missing
            actual_time = None
        else:
            delay = np.random.exponential(10)  # Exponential delay distribution
            actual_time = scheduled_time + timedelta(minutes=delay)
            if random.random() < 0.2:  # 20% dirty format
                actual_time = actual_time.strftime('%d/%m/%Y %H:%M')
            else:
                actual_time = actual_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Weather - sometimes noisy
        base_weather = random.choice(weathers)
        if random.random() < 0.3:  # 30% noisy
            weather = random.choice(weather_variants[base_weather])
        else:
            weather = base_weather
        
        # Passenger count - sometimes missing, sometimes outlier
        if random.random() < 0.15:  # 15% missing
            passenger_count = None
        elif random.random() < 0.1:  # 10% outliers
            passenger_count = random.choice([-50, 600, 1000, -10])
        else:
            passenger_count = random.randint(50, 200)
        
        # GPS coordinates - sometimes invalid, sometimes missing
        if random.random() < 0.1:  # 10% missing
            latitude = None
            longitude = None
        elif random.random() < 0.05:  # 5% invalid
            latitude = random.choice([91, -91, 200, -200])
            longitude = random.choice([181, -181, 300])
        else:
            latitude = random.uniform(40.0, 50.0)
            longitude = random.uniform(-80.0, -70.0)
        
        data.append({
            'route_id': route_id,
            'scheduled_time': scheduled_str,
            'actual_time': actual_time,
            'weather': weather,
            'passenger_count': passenger_count,
            'latitude': latitude,
            'longitude': longitude
        })
    
    df = pd.DataFrame(data)
    
    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} records")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    generate_dirty_dataset()

