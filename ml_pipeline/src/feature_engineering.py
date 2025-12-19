"""
Feature Engineering Module (FR-9 to FR-13)
Computes target variable and engineered features
"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Handles feature engineering per SRS requirements"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize feature engineer with cleaned dataframe
        
        Args:
            df: Cleaned dataframe
        """
        self.df = df.copy()
    
    def compute_delay_duration(self) -> pd.DataFrame:
        """
        Compute delay duration in minutes as target variable (FR-9)
        
        Delay = actual_time - scheduled_time (in minutes)
        
        Returns:
            DataFrame with delay_minutes column
        """
        logger.info("Computing delay duration...")
        
        if 'scheduled_time' not in self.df.columns or 'actual_time' not in self.df.columns:
            logger.warning("Timestamp columns missing, cannot compute delay")
            return self.df
        
        # Convert to datetime
        self.df['scheduled_time'] = pd.to_datetime(self.df['scheduled_time'], errors='coerce')
        self.df['actual_time'] = pd.to_datetime(self.df['actual_time'], errors='coerce')
        
        # Calculate delay in minutes with overflow protection
        # Remove rows with invalid timestamps first
        valid_mask = (
            self.df['scheduled_time'].notna() & 
            self.df['actual_time'].notna()
        )
        
        # Initialize delay column
        self.df['delay_minutes'] = pd.NA
        
        # Calculate delay row by row to handle overflow
        for idx in self.df.index:
            if valid_mask.loc[idx]:
                try:
                    sched = self.df.loc[idx, 'scheduled_time']
                    actual = self.df.loc[idx, 'actual_time']
                    if pd.notna(sched) and pd.notna(actual):
                        # Use timestamp() method to avoid overflow
                        sched_ts = sched.timestamp()
                        actual_ts = actual.timestamp()
                        delay_sec = actual_ts - sched_ts
                        delay_min = delay_sec / 60.0
                        # Cap at reasonable values (±1 year = 525600 minutes)
                        if -525600 <= delay_min <= 525600:
                            self.df.loc[idx, 'delay_minutes'] = delay_min
                        else:
                            logger.warning(f"Extreme delay value {delay_min:.1f} minutes at index {idx}, setting to NaN")
                except (OverflowError, ValueError, OSError) as e:
                    logger.warning(f"Error calculating delay at index {idx}: {str(e)}")
                    continue
        
        # Handle negative delays (early arrivals) - set to 0
        self.df['delay_minutes'] = self.df['delay_minutes'].clip(lower=0)
        
        # Remove rows where delay cannot be computed
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['delay_minutes'])
        removed = initial_count - len(self.df)
        
        if removed > 0:
            logger.info(f"Removed {removed} rows where delay could not be computed")
        
        logger.info(f"Delay computed. Mean delay: {self.df['delay_minutes'].mean():.2f} minutes")
        
        return self.df
    
    def generate_time_features(self) -> pd.DataFrame:
        """
        Generate time-based features such as time of day (FR-10)
        
        Creates:
        - hour: Hour of day (0-23)
        - time_of_day: Categorical (0=Morning, 1=Afternoon, 2=Evening, 3=Night)
        
        Returns:
            DataFrame with time features
        """
        logger.info("Generating time-based features...")
        
        if 'scheduled_time' not in self.df.columns:
            logger.warning("scheduled_time missing, cannot generate time features")
            return self.df
        
        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['scheduled_time']):
            self.df['scheduled_time'] = pd.to_datetime(self.df['scheduled_time'], errors='coerce')
        
        # Extract hour
        self.df['hour'] = self.df['scheduled_time'].dt.hour
        
        # Categorize time of day
        def categorize_time(hour):
            if pd.isna(hour):
                return 1  # Default to afternoon
            hour = int(hour)
            if 6 <= hour < 12:
                return 0  # Morning
            elif 12 <= hour < 18:
                return 1  # Afternoon
            elif 18 <= hour < 24:
                return 2  # Evening
            else:  # 0-6
                return 3  # Night
        
        self.df['time_of_day'] = self.df['hour'].apply(categorize_time)
        
        logger.info("Time features generated")
        return self.df
    
    def identify_weekend(self) -> pd.DataFrame:
        """
        Identify whether trip occurred on weekend (FR-11)
        
        Returns:
            DataFrame with is_weekend column (0=weekday, 1=weekend)
        """
        logger.info("Identifying weekend trips...")
        
        if 'scheduled_time' not in self.df.columns:
            logger.warning("scheduled_time missing, cannot identify weekend")
            return self.df
        
        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['scheduled_time']):
            self.df['scheduled_time'] = pd.to_datetime(self.df['scheduled_time'], errors='coerce')
        
        # Day of week: 0=Monday, 6=Sunday
        self.df['day_of_week'] = self.df['scheduled_time'].dt.dayofweek
        
        # Weekend: Saturday (5) or Sunday (6)
        self.df['is_weekend'] = (self.df['day_of_week'] >= 5).astype(int)
        
        weekend_count = self.df['is_weekend'].sum()
        logger.info(f"Weekend identification complete. {weekend_count} weekend trips")
        
        return self.df
    
    def compute_weather_severity(self) -> pd.DataFrame:
        """
        Compute weather severity as numerical index (FR-12)
        
        Severity scale:
        - clear: 0 (no impact)
        - cloudy: 1 (mild impact)
        - rainy: 2 (moderate impact)
        - snowy: 3 (severe impact)
        
        Returns:
            DataFrame with weather_severity column
        """
        logger.info("Computing weather severity index...")
        
        if 'weather' not in self.df.columns:
            logger.warning("weather column missing")
            return self.df
        
        severity_map = {
            'clear': 0,
            'cloudy': 1,
            'rainy': 2,
            'snowy': 3
        }
        
        self.df['weather_severity'] = self.df['weather'].map(severity_map).fillna(0)
        
        logger.info("Weather severity computed")
        return self.df
    
    def calculate_route_frequency(self) -> pd.DataFrame:
        """
        Calculate route frequency as a feature (FR-13)
        
        Frequency = number of trips per route / total trips
        
        Returns:
            DataFrame with route_frequency column
        """
        logger.info("Calculating route frequency...")
        
        if 'route_id' not in self.df.columns:
            logger.warning("route_id missing, cannot calculate frequency")
            return self.df
        
        # Count trips per route
        route_counts = self.df['route_id'].value_counts()
        total_trips = len(self.df)
        
        # Frequency = count / total
        self.df['route_frequency'] = self.df['route_id'].map(
            route_counts / total_trips
        )
        
        logger.info("Route frequency calculated")
        return self.df
    
    def engineer_all_features(self) -> pd.DataFrame:
        """
        Execute all feature engineering steps
        
        Returns:
            DataFrame with all engineered features
        """
        logger.info("Starting comprehensive feature engineering...")
        
        self.df = self.compute_delay_duration()
        self.df = self.generate_time_features()
        self.df = self.identify_weekend()
        self.df = self.compute_weather_severity()
        self.df = self.calculate_route_frequency()
        
        logger.info("Feature engineering completed")
        return self.df
    
    def get_feature_columns(self) -> list[str]:
        """Get list of feature columns (excluding target)"""
        feature_cols = [
            'route_id', 'weather', 'passenger_count', 'time_of_day', 
            'is_weekend', 'weather_severity', 'route_frequency'
        ]
        return [col for col in feature_cols if col in self.df.columns]
    
    def get_target_column(self) -> str:
        """Get target column name"""
        return 'delay_minutes' if 'delay_minutes' in self.df.columns else None

