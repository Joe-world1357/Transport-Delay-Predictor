"""
Data Loading Module (FR-1, FR-2)
Loads and validates the dirty transport dataset
"""
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles dataset loading and validation"""
    
    REQUIRED_COLUMNS = [
        'route_id',
        'scheduled_time',
        'actual_time',
        'weather',
        'passenger_count',
        'latitude',
        'longitude'
    ]
    
    def __init__(self, data_path: str = None):
        """
        Initialize data loader
        
        Args:
            data_path: Path to CSV file. If None, looks for dirty_transport_dataset.csv
        """
        if data_path is None:
            # Look for dataset in common locations
            base_path = Path(__file__).parent.parent
            possible_paths = [
                base_path / "data" / "dirty_transport_dataset.csv",
                base_path.parent / "data" / "dirty_transport_dataset.csv",
                Path("dirty_transport_dataset.csv")
            ]
            
            for path in possible_paths:
                if path.exists():
                    data_path = str(path)
                    break
            
            if data_path is None:
                raise FileNotFoundError(
                    "Dataset not found. Please provide path to dirty_transport_dataset.csv"
                )
        
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {data_path}")
    
    def load(self) -> pd.DataFrame:
        """
        Load dataset from CSV file (FR-1)
        
        Returns:
            DataFrame with raw data
        """
        logger.info(f"Loading dataset from {self.data_path}")
        
        try:
            df = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def validate(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """
        Validate column existence and data types (FR-2)
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns exist
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check data types
        if 'route_id' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['route_id']) and \
               not pd.api.types.is_object_dtype(df['route_id']):
                errors.append("route_id has unexpected data type")
        
        if 'passenger_count' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['passenger_count']):
                errors.append("passenger_count should be numeric")
        
        if 'weather' in df.columns:
            if not pd.api.types.is_object_dtype(df['weather']):
                errors.append("weather should be categorical/string")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Dataset validation passed")
        else:
            logger.warning(f"Dataset validation found issues: {errors}")
        
        return is_valid, errors
    
    def load_and_validate(self) -> pd.DataFrame:
        """
        Load and validate dataset in one step
        
        Returns:
            Validated DataFrame
        """
        df = self.load()
        is_valid, errors = self.validate(df)
        
        if not is_valid:
            logger.warning("Dataset has validation issues but will proceed")
            for error in errors:
                logger.warning(f"  - {error}")
        
        return df

