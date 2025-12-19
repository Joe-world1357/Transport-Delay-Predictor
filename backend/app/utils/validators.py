"""
Custom validation functions
"""
from typing import Tuple


def validate_business_hours(time_of_day: int, is_weekend: int) -> Tuple[bool, str]:
    """
    Validate reasonable transport operating hours
    
    Args:
        time_of_day: Time period (0-3)
        is_weekend: Weekend flag (0 or 1)
        
    Returns:
        Tuple of (is_valid, message)
    """
    # For weekdays, unusual hours might be flagged
    if is_weekend == 0:
        # Night hours (3) are less common for weekday transport
        if time_of_day == 3:
            return True, "Night hours detected for weekday - prediction may be less accurate"
    
    return True, ""


def validate_route_operating_hours(route_id: int, time_of_day: int) -> Tuple[bool, str]:
    """
    Validate if route operates during specified time
    
    Args:
        route_id: Route identifier
        time_of_day: Time period (0-3)
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Some routes might not operate at night
    if time_of_day == 3 and route_id > 8:
        return True, "Route may have limited night service"
    
    return True, ""

