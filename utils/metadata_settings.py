"""Initializes global variables throughout the simulation process."""

import datetime
from typing import List

# Set path to data folder. Default set for fremont example.
__DATA_FOLDER_PATH = 'C:\\Users\\prest\\Documents\\Github\\traffic-microsimulation\\fremont-public-data'

# Set name of simulation epoch. Default set for fremont example.
__SIMULATION_EPOCH = 'fremont_example'

# Set year of simulation. Default set for fremont example.
__YEAR_OF_SIMULATION = 2019

# Set details for time steps used in simulation. Default set for fremont example.
__START_HOUR = 14
__END_HOUR = 20
__TIMESTEP_MINUTES = 15


def get_data_folder_path() -> str:
    """Return the path to data folder for the study."""
    return __DATA_FOLDER_PATH


def get_simulation_epoch() -> str:
    """Return the name of the simulation epoch for the study."""
    return __SIMULATION_EPOCH


def get_simulation_year() -> int:
    """Return year the study is conducted on."""
    return __YEAR_OF_SIMULATION


def get_time_intervals() -> List[datetime.time]:
    """Return time intervals used within the study."""
    time_intervals = []
    for hour in range(__START_HOUR, __END_HOUR):
        for minute in range(0, 60, __TIMESTEP_MINUTES):
            time_intervals.append(datetime.time(hour, minute))
    return time_intervals
