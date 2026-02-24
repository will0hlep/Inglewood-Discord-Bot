"""
This module implements a function for calculating the current time of
day in seconds.
"""

import datetime

from constants import TIME_ZONE


def get_timestamp() -> float:
    """
    Returns the current time of day in seconds.

    Returns:
        time : float
            time of day in seconds
    """
    now = datetime.datetime.now(TIME_ZONE)
    timedelta = now - now.replace(hour=0, minute=0, second=0, microsecond=0)
    time = timedelta.total_seconds()
    return time
