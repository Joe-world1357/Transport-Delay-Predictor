"""
Data Cleaning and Preprocessing Module (FR-3 to FR-8)
Handles missing values, timestamp standardization, normalization, and outlier treatment
"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class DataCleaner:
    """Handles all data cleaning operations per SRS requirements"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize cleaner with dataframe
        
        Args:
            df: Raw dataframe to clean
        """
        self.df = df.copy()
        self.cleaning_log = []
    
    def handle_missing_values(self) -> pd.DataFrame:
        """
        Detect and handle missing values in all columns (FR-3)
        
        Strategy:
        - route_id: Forward fill (assume same route continues)
        - scheduled_time/actual_time: Cannot impute, will handle in timestamp cleaning
        - weather: Mode imputation (most common weather)
        - passenger_count: Median imputation (robust to outliers)
        - latitude/longitude: Drop rows with missing GPS (cannot reliably impute)
        
        Returns:
            DataFrame with missing values handled
        """
        logger.info("Handling missing values...")
        
        initial_missing = self.df.isnull().sum()
        self.cleaning_log.append(f"Initial missing values:\n{initial_missing[initial_missing > 0]}")
        
        # route_id: Forward fill
        if 'route_id' in self.df.columns:
            self.df['route_id'] = self.df['route_id'].ffill()
            self.cleaning_log.append("route_id: Forward filled missing values")
        
        # weather: Mode imputation
        if 'weather' in self.df.columns:
            mode_weather = self.df['weather'].mode()[0] if not self.df['weather'].mode().empty else 'clear'
            self.df['weather'] = self.df['weather'].fillna(mode_weather)
            self.cleaning_log.append(f"weather: Filled with mode ({mode_weather})")
        
        # passenger_count: Median imputation
        if 'passenger_count' in self.df.columns:
            median_passengers = self.df['passenger_count'].median()
            self.df['passenger_count'] = self.df['passenger_count'].fillna(median_passengers)
            self.cleaning_log.append(f"passenger_count: Filled with median ({median_passengers:.0f})")
        
        # GPS coordinates: Drop rows with missing (cannot reliably impute location)
        if 'latitude' in self.df.columns and 'longitude' in self.df.columns:
            gps_missing = self.df[['latitude', 'longitude']].isnull().any(axis=1).sum()
            if gps_missing > 0:
                self.df = self.df.dropna(subset=['latitude', 'longitude'])
                self.cleaning_log.append(f"Dropped {gps_missing} rows with missing GPS coordinates")
        
        final_missing = self.df.isnull().sum()
        remaining = final_missing[final_missing > 0]
        if len(remaining) > 0:
            logger.warning(f"Remaining missing values after cleaning:\n{remaining}")
        else:
            logger.info("All missing values handled")
        
        return self.df
    
    def standardize_timestamps(self) -> pd.DataFrame:
        """
        Standardize all timestamps into ISO format YYYY-MM-DD HH:MM:SS (FR-4)
        
        Handles various formats:
        - ISO format already
        - Unix timestamps
        - Various date formats
        - Dirty formats with extra text
        
        Returns:
            DataFrame with standardized timestamps
        """
        logger.info("Standardizing timestamps...")
        
        timestamp_columns = ['scheduled_time', 'actual_time']
        
        for col in timestamp_columns:
            if col not in self.df.columns:
                continue
            
            self.df[col] = self.df[col].apply(self._parse_timestamp)
            self.cleaning_log.append(f"{col}: Standardized to ISO format")
        
        return self.df
    
    def _parse_timestamp(self, value) -> str:
        """Parse various timestamp formats to ISO format"""
        if pd.isna(value):
            return None
        
        value_str = str(value).strip()
        
        # Try parsing as ISO format first
        try:
            dt = pd.to_datetime(value_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        # Try Unix timestamp
        try:
            if value_str.replace('.', '').replace('-', '').isdigit():
                dt = pd.to_datetime(float(value_str), unit='s')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        # Try various date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(value_str, fmt)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                continue
        
        # Extract date-like patterns
        date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        match = re.search(date_pattern, value_str)
        if match:
            try:
                dt = pd.to_datetime(match.group(1))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        logger.warning(f"Could not parse timestamp: {value_str}")
        return None
    
    def normalize_weather(self) -> pd.DataFrame:
        """
        Normalize categorical weather values (FR-5)
        
        Standardizes to: clear, cloudy, rainy, snowy
        
        Returns:
            DataFrame with normalized weather
        """
        logger.info("Normalizing weather categories...")
        
        if 'weather' not in self.df.columns:
            return self.df
        
        # Normalization mapping
        weather_mapping = {
            'clear': ['clear', 'sunny', 'sun', 'fair'],
            'cloudy': ['cloudy', 'clouds', 'overcast', 'cloud'],
            'rainy': ['rainy', 'rain', 'raining', 'drizzle', 'drizzling'],
            'snowy': ['snowy', 'snow', 'snowing', 'sleet']
        }
        
        def normalize_weather_value(value):
            if pd.isna(value):
                return 'clear'  # Default
            
            value_lower = str(value).lower().strip()
            
            for standard, variants in weather_mapping.items():
                if value_lower in variants or any(v in value_lower for v in variants):
                    return standard
            
            # Default to clear if no match
            return 'clear'
        
        self.df['weather'] = self.df['weather'].apply(normalize_weather_value)
        
        unique_weather = self.df['weather'].unique()
        self.cleaning_log.append(f"weather: Normalized to {unique_weather}")
        
        return self.df
    
    def unify_route_identifiers(self) -> pd.DataFrame:
        """
        Unify mixed route identifier formats (FR-6)
        
        Handles:
        - Numeric: 1, 2, 3
        - String with numbers: "Route 3", "R3", "3A"
        - Extracts numeric part
        
        Returns:
            DataFrame with unified route_id (numeric)
        """
        logger.info("Unifying route identifiers...")
        
        if 'route_id' not in self.df.columns:
            return self.df
        
        def extract_route_number(value):
            if pd.isna(value):
                return 1  # Default route
            
            value_str = str(value)
            
            # Extract first number found
            numbers = re.findall(r'\d+', value_str)
            if numbers:
                route_num = int(numbers[0])
                # Constrain to reasonable range (1-10 as per frontend)
                return min(max(route_num, 1), 10)
            
            # If no number found, try to map common patterns
            value_lower = value_str.lower()
            if 'one' in value_lower or '1' in value_lower:
                return 1
            elif 'two' in value_lower or '2' in value_lower:
                return 2
            # ... add more if needed
            
            return 1  # Default
        
        self.df['route_id'] = self.df['route_id'].apply(extract_route_number)
        
        unique_routes = sorted(self.df['route_id'].unique())
        self.cleaning_log.append(f"route_id: Unified to numeric values {unique_routes}")
        
        return self.df
    
    def treat_outliers(self) -> pd.DataFrame:
        """
        Identify and treat outliers in passenger_count using IQR (FR-7)
        
        Strategy:
        - Calculate IQR
        - Cap outliers at Q1 - 1.5*IQR (lower) and Q3 + 1.5*IQR (upper)
        - Ensure values are within reasonable range (0-500)
        
        Returns:
            DataFrame with outliers treated
        """
        logger.info("Treating outliers in passenger_count...")
        
        if 'passenger_count' not in self.df.columns:
            return self.df
        
        Q1 = self.df['passenger_count'].quantile(0.25)
        Q3 = self.df['passenger_count'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = max(0, Q1 - 1.5 * IQR)
        upper_bound = min(500, Q3 + 1.5 * IQR)
        
        outliers_before = ((self.df['passenger_count'] < lower_bound) | 
                          (self.df['passenger_count'] > upper_bound)).sum()
        
        # Cap outliers
        self.df['passenger_count'] = self.df['passenger_count'].clip(
            lower=lower_bound,
            upper=upper_bound
        )
        
        # Also ensure within absolute bounds (0-500)
        self.df['passenger_count'] = self.df['passenger_count'].clip(lower=0, upper=500)
        
        self.cleaning_log.append(
            f"passenger_count: Treated {outliers_before} outliers "
            f"(bounds: {lower_bound:.0f}-{upper_bound:.0f})"
        )
        
        return self.df
    
    def handle_gps_coordinates(self) -> pd.DataFrame:
        """
        Detect and correct/remove invalid GPS coordinates (FR-8)
        
        Valid ranges:
        - Latitude: -90 to 90
        - Longitude: -180 to 180
        
        Returns:
            DataFrame with valid GPS coordinates
        """
        logger.info("Handling GPS coordinates...")
        
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            return self.df
        
        # Remove invalid coordinates
        invalid_lat = ((self.df['latitude'] < -90) | (self.df['latitude'] > 90))
        invalid_lon = ((self.df['longitude'] < -180) | (self.df['longitude'] > 180))
        
        invalid_count = (invalid_lat | invalid_lon).sum()
        
        if invalid_count > 0:
            self.df = self.df[~invalid_lat & ~invalid_lon]
            self.cleaning_log.append(f"Removed {invalid_count} rows with invalid GPS coordinates")
        
        return self.df
    
    def clean_all(self) -> pd.DataFrame:
        """
        Execute all cleaning steps in order
        
        Returns:
            Fully cleaned DataFrame
        """
        logger.info("Starting comprehensive data cleaning...")
        
        self.df = self.handle_missing_values()
        self.df = self.standardize_timestamps()
        self.df = self.normalize_weather()
        self.df = self.unify_route_identifiers()
        self.df = self.treat_outliers()
        self.df = self.handle_gps_coordinates()
        
        logger.info("Data cleaning completed")
        return self.df
    
    def get_cleaning_log(self) -> list[str]:
        """Get log of all cleaning operations"""
        return self.cleaning_log
    
    def save_cleaned_data(self, output_path: str):
        """Save cleaned dataset to CSV"""
        self.df.to_csv(output_path, index=False)
        logger.info(f"Cleaned dataset saved to {output_path}")

