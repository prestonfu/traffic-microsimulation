"""The aimsun_folder_utils file is meant to simplify file location throughout
the Aimsun project. With many files, it becomes a hassle to access them all
each time without a centralized system. This script takes those file locations
and makes them available through a single function, without the hassle of
rebuilding a path to each file every time.

These specific filepaths are separated from the preprocessing_folder_utils
since Aimsun has trouble importing certain python packages. As a result, those
packages are not imported in this file to solve that error. The diagram below
shows the structure of the Aimsun folder and describes what each directory
holds and how it can be accessed.
"""

from os import path
from pathlib import Path

from utils import metadata_settings


__SIMULATION_CONFIG_FILENAME = "config.pkl"
__SIMULATION_OUTPUT_DATABASE_FILENAME = "output_database.sqlite"


__SIMULATION_EPOCH = metadata_settings.get_simulation_epoch()
__DATA_FOLDER_PATH = metadata_settings.get_data_folder_path()
__YEAR_OF_SIMULATION = metadata_settings.get_simulation_year()


# Aimsun
__AIMSUN_FOLDER_PATH = path.join(__DATA_FOLDER_PATH, "aimsun")
# - Inputs
__AIMSUN_INPUT_DATA_PATH = path.join(__AIMSUN_FOLDER_PATH, "inputs")
# -- Demand
__AIMSUN_INPUT_DEMAND_DATA_PATH = path.join(__AIMSUN_INPUT_DATA_PATH, "demand")
# -- Network
__AIMSUN_INPUT_NETWORK_DATA_PATH = path.join(__AIMSUN_INPUT_DATA_PATH, "network")
# --- Centroid connections
__AIMSUN_INPUT_CENTROID_CONNECTIONS_DATA_PATH = path.join(
    __AIMSUN_INPUT_NETWORK_DATA_PATH, "centroid_connections"
)
# --- Speed limit and capacity
__AIMSUN_INPUT_SPEED_CAPACITY_DATA_PATH = path.join(
    __AIMSUN_INPUT_NETWORK_DATA_PATH, "speed_limits_and_capacities"
)
# --- Traffic signals
__AIMSUN_INPUT_MASTER_CONTROL_PLAN_DATA_PATH = path.join(
    __AIMSUN_INPUT_NETWORK_DATA_PATH, "traffic_signals"
)
# --- Management Strategies
__AIMSUN_INPUT_TRAFFIC_MANAGEMENT_PATH = path.join(
    __AIMSUN_INPUT_NETWORK_DATA_PATH, "management_strategies"
)
# -- Network
__AIMSUN_INPUT_TRAFFIC_DATA_PATH = path.join(__AIMSUN_INPUT_DATA_PATH, "traffic")
# - Outputs
__AIMSUN_OUTPUTS_PATH = path.join(__AIMSUN_FOLDER_PATH, "outputs")
# -- Macrosimulations
__MACROSIMULATION_OUTPUTS_PATH = path.join(__AIMSUN_OUTPUTS_PATH, "macrosimulations")
# -- Microsimulations
__MICROSIMULATION_OUTPUTS_PATH = path.join(__AIMSUN_OUTPUTS_PATH, "microsimulations")


def __filepath_with_epoch_directory(
    folder_path: str, epoch_name: str, filename: str
) -> str:
    """Returns the path to the given filename assigned under the given
    simulation epoch_name. Creates a folder for the epoch_name if it does not
    exist.
    Args:
        folder_path: Path to folder that houses all simulation related files.
        filename: The name of the file under the given simulation epoch name.
        epoch_name: The unique epoch name assigned to the simulation.
    Returns:
        epoch_filepath: Path to the given filepath under the given epoch_name.
    """
    if not epoch_name:
        raise ValueError("Please set epoch_name.")
    unique_path = path.join(folder_path, epoch_name)
    Path(unique_path).mkdir(parents=True, exist_ok=True)
    return path.join(unique_path, filename)


def aimsun_output_directory_path() -> str:
    """Return aimsun output directory path."""
    return __AIMSUN_OUTPUTS_PATH


def aimsun_macro_databases_file() -> str:
    """Creates a directory for the macrosimulation output database and returns
    the file location of the database.
    """
    return __filepath_with_epoch_directory(
        __MACROSIMULATION_OUTPUTS_PATH,
        __SIMULATION_EPOCH,
        __SIMULATION_OUTPUT_DATABASE_FILENAME,
    )


def aimsun_macro_simulation_config_input_file() -> str:
    """Creates a directory for the macrosimulation configuration and returns
    the file location of the configuration.
    """
    return __filepath_with_epoch_directory(
        __MACROSIMULATION_OUTPUTS_PATH, __SIMULATION_EPOCH, __SIMULATION_CONFIG_FILENAME
    )


def aimsun_micro_databases_file() -> str:
    """Creates a directory for the microsimulation output database and returns
    the file location of the database.
    """
    return __filepath_with_epoch_directory(
        __MICROSIMULATION_OUTPUTS_PATH,
        __SIMULATION_EPOCH,
        __SIMULATION_OUTPUT_DATABASE_FILENAME,
    )


def aimsun_micro_simulation_config_input_file() -> str:
    """Creates a directory for the microsimulation configuration and returns
    the file location of the configuration.
    """
    return __filepath_with_epoch_directory(
        __MICROSIMULATION_OUTPUTS_PATH, __SIMULATION_EPOCH, __SIMULATION_CONFIG_FILENAME
    )


def centroid_connections_aimsun_input_file() -> str:
    """Returns the centroid connections .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_CENTROID_CONNECTIONS_DATA_PATH,
        f"centroid_connections_{__YEAR_OF_SIMULATION}.pkl",
    )


def detector_flow_aimsun_input_file() -> str:
    """Returns the detector flow .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_TRAFFIC_DATA_PATH, f"detector_flow_{__YEAR_OF_SIMULATION}.pkl"
    )


def master_control_plan_aimsun_input_file() -> str:
    """Returns the master control plan .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_MASTER_CONTROL_PLAN_DATA_PATH,
        f"master_control_plan_{__YEAR_OF_SIMULATION}.pkl",
    )


def od_demand_aimsun_input_file() -> str:
    """Returns the od demand .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_DEMAND_DATA_PATH, f"od_demand_{__YEAR_OF_SIMULATION}.pkl"
    )


def speed_and_capacity_aimsun_input_file() -> str:
    """Returns the speed limit and capacity per section .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_SPEED_CAPACITY_DATA_PATH,
        f"speed_limit_and_capacity_section_{__YEAR_OF_SIMULATION}.pkl",
    )


def traffic_demand_aimsun_input_file() -> str:
    """Returns the traffic demand .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_DEMAND_DATA_PATH, f"traffic_demand_{__YEAR_OF_SIMULATION}.pkl"
    )


def traffic_management_aimsun_input_file() -> str:
    """Returns the traffic management .pkl file location."""
    return path.join(
        __AIMSUN_INPUT_TRAFFIC_MANAGEMENT_PATH,
        f"traffic_management_{__YEAR_OF_SIMULATION}.pkl",
    )
