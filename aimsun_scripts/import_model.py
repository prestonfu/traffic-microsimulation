"""Imports data into Aimsun."""

import datetime
from typing import Any, NewType

import aimsun_config_utils
import aimsun_folder_utils
import aimsun_input_utils
import aimsun_utils_functions
import metadata_settings


AIMSUN_MODEL = model
AIMSUN_SYSTEM = GKSystem.getSystem()
GKModel = NewType('GKModel', Any)


GK_OBJECT_STATUS_MODIFIED = GKObject.eModified


def create_gk_point(lon: float, lat: float):
    """Return Aimsun GKPoint at given longitude and latitude."""
    return GKPoint(lon, lat)


def create_schedule_demand_item():
    """Return empty Aimsun GKScheduleDemandItem object."""
    return GKScheduleDemandItem()


def create_gk_time_duration(time_duration_in_seconds: int):
    """Return Aimsun GKTimeDuration with given time duration."""
    return GKTimeDuration(time_duration_in_seconds)


def get_duration(
    begin_time_interval: datetime.time,
    end_time_interval: datetime.time
):
    """Return Aimsun GKTimeDuration object for time between begin and end time
    intervals.
    """
    begin_time_seconds = (
        begin_time_interval.hour * 3600
        + begin_time_interval.minute * 60
        + begin_time_interval.second)
    end_time_seconds = (
        end_time_interval.hour * 3600
        + end_time_interval.minute * 60
        + end_time_interval.second)
    difference = end_time_seconds - begin_time_seconds
    hours = difference // 3600
    minutes = (difference % 3600) // 60
    seconds = (difference % 60)
    return GKTimeDuration(hours, minutes, seconds)


def get_from_time(begin_time_interval: datetime.time):
    """Return Aimsun QTime object from begin time interval."""
    return QTime.fromString(
        begin_time_interval.strftime('%H:%M'), "hh:mm")


def create_master_control_plan_item():
    """Return empty Aimsun GKScheduleMasterControlPlanItem object."""
    return GKScheduleMasterControlPlanItem()


def create_q_date(year: int, month: int, day: int):
    """Return Aimsun QDate object from given year, month, and day."""
    return QDate(year, month, day)


def create_trajectory_condition():
    """Return empty Aimsun GKTrajectoryCondition object."""
    return GKTrajectoryCondition()


# 1. Create demand data

# Load centroid configuration
centroid_connections_path = aimsun_folder_utils.centroid_connections_aimsun_input_file()
print(f'Loading centroid configuration from {centroid_connections_path}...')
centroid_connections = aimsun_input_utils.CentroidConfiguration(
    centroid_connections_path)
print('Creating the centroid connections in Aimsun...')
aimsun_utils_functions.create_centroids(
    centroid_connections, AIMSUN_MODEL, AIMSUN_SYSTEM, create_gk_point)
print('Done')
# Load OD demand matrices
od_demand_matrix_filepath = aimsun_folder_utils.od_demand_aimsun_input_file()
print(f'Loading OD demand matrices from {od_demand_matrix_filepath}...')
od_demand_matrix = aimsun_input_utils.OriginDestinationMatrices(
    od_demand_matrix_filepath)
print('Creating the OD demand matrices in Aimsun...')
aimsun_utils_functions.create_od_matrices(
    od_demand_matrix, AIMSUN_MODEL, AIMSUN_SYSTEM, get_duration, get_from_time)
print('Done')
# Load traffic demands
traffic_demands_filepath = aimsun_folder_utils.traffic_demand_aimsun_input_file()
print(f'Loading traffic demands from {traffic_demands_filepath}...')
traffic_demands = aimsun_config_utils.AimsunTrafficDemands(
    traffic_demands_filepath)
print('Creating the traffic demands in Aimsun...')
aimsun_utils_functions.create_traffic_demand(
    traffic_demands, model, GKSystem.getSystem(), create_schedule_demand_item,
    create_gk_time_duration)
print('Done')


# 2. Create network data

# Load speed limit and capacity
speed_and_capacity_filepath = aimsun_folder_utils.speed_and_capacity_aimsun_input_file()
print(f'Loading speed limits and capacities from {speed_and_capacity_filepath}.')
speed_and_capacity_data = aimsun_input_utils.SectionSpeedLimitsAndCapacities(
    speed_and_capacity_filepath)
print('Creating the speed limits and capacities in Aimsun...')
aimsun_utils_functions.update_speed_and_capacity(
    speed_and_capacity_data, AIMSUN_MODEL)
print('Done')
# Load traffic management strategies
traffic_management_filepath = aimsun_folder_utils.traffic_management_aimsun_input_file()
print(f'Loading traffic management strategies from {traffic_management_filepath}...')
traffic_management = aimsun_input_utils.TrafficManagementStrategy(
    traffic_management_filepath)
print('Creating the traffic management strategies in Aimsun...')
aimsun_utils_functions.import_scenarios(
    traffic_management, AIMSUN_MODEL, AIMSUN_SYSTEM)
print('Done')


# 3. Create flow detectors

# Load detector locations
real_data_set_path = aimsun_folder_utils.detector_flow_aimsun_input_file()
print(f'Loading flow detectors and real dataset from {real_data_set_path}...')
# TODO: Rename and split to detector locations file.
real_data_set_object = aimsun_input_utils.AimsunFlowRealDataSet(
    real_data_set_path)
flow_detectors = aimsun_input_utils.Detectors()
for flow_data_set in real_data_set_object.flow_data_set:
    det = aimsun_input_utils.Detector()
    det.external_id = flow_data_set.external_id
    det.aimsun_section_internal_id = flow_data_set.aimsun_section_internal_id
    flow_detectors.detector_list.append(det)
aimsun_utils_functions.create_detectors(
    flow_detectors, True, AIMSUN_MODEL, AIMSUN_SYSTEM)
print('Detectors have been created.')
