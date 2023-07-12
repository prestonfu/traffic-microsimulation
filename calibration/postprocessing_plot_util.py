"""Helper functions for Aimsun Micro/Macrosimulation output analysis."""

from __future__ import annotations

import datetime
import os
import sys
from typing import Any, Dict, List, Iterable, Union

import numpy as np
from sklearn.linear_model import LinearRegression

from calibration.postprocessing_util import (
    AimsunMacroOutputDatabase,
    AimsunMicroOutputDatabase
)

sys.path.append(os.path.abspath(os.path.join('..', 'Utils')))

from utils.aimsun_input_utils import AimsunFlowRealDataSet, ExternalId, InternalId


def convert_flow_per_time_to_list(
    real_flow_per_time: Dict[datetime.time, Dict[ExternalId, float]],
    simulated_flow_per_time: Dict[datetime.time, Dict[ExternalId, float]],
    time_list: List[datetime.time], city_common_id: str = None
) -> Union[tuple(np.array, np.array),
           tuple(np.array, np.array, np.array, np.array)]:
    """Convert dictionaries with real and simulated flow per time into
    sklearn & matplotlib friendly structures.

    Args:
        real_flow_per_time: Real flow data grouped by time.
        simulated_flow_per_time: Simulated flow data grouped by time.
        time_list: List of times to extract the real and simulated flow from.
        city_common_id: Common string that is shared within the external IDs of
            city detectors. Set to the year of observed data in the Fremont
            study.
    Returns:
        If city_common_id was NOT passed in as an argument:
            all_real_flow_list: All real flow data for each time within
                time_list aggregated together.
            all_simulated_flow_list: All simulated flow data for each time
                within time_list aggregated together.
        If city_common_id was passed in as an argument:
            city_real_flow_list: All real flow data through city detectors for
                each time within time_list aggregated together.
            city_simulated_flow_list: All simulated flow data through city
                detectors for each time within time_list aggregated together.
            pems_real_flow_list: All real flow data through PeMS detectors for
                each time within time_list aggregated together.
            pems_simulated_flow_list: All simulated flow data through PeMS
                detectors for each time within time_list aggregated together.
    """
    assert all(isinstance(time, datetime.time) for time in time_list)
    if city_common_id is None:
        all_real_flow_list = []
        all_simulated_flow_list = []
        for time in time_list:
            real_flow_dict = real_flow_per_time[time]
            simulated_flow_dict = simulated_flow_per_time[time]
            for detector_external_id, real_flow_value in \
                    real_flow_dict.items():
                all_real_flow_list.append(real_flow_value)
                all_simulated_flow_list.append(
                    simulated_flow_dict[detector_external_id])
        assert len(all_real_flow_list) == len(all_simulated_flow_list)
        all_real_flow_list = np.array(all_real_flow_list).reshape(-1, 1)
        all_simulated_flow_list = np.array(
            all_simulated_flow_list).reshape(-1, 1)
        return all_real_flow_list, all_simulated_flow_list
    city_real_flow_list = []
    city_simulated_flow_list = []
    pems_real_flow_list = []
    pems_simulated_flow_list = []
    for time in time_list:
        real_flow_dict = real_flow_per_time[time]
        simulated_flow_dict = simulated_flow_per_time[time]
        for detector_external_id, real_flow_value in \
                real_flow_dict.items():
            if city_common_id in detector_external_id:
                city_real_flow_list.append(real_flow_value)
                city_simulated_flow_list.append(
                    simulated_flow_dict[detector_external_id])
            else:
                pems_real_flow_list.append(real_flow_value)
                pems_simulated_flow_list.append(
                    simulated_flow_dict[detector_external_id])
    assert len(city_real_flow_list) == len(city_simulated_flow_list)
    assert len(pems_real_flow_list) == len(pems_simulated_flow_list)
    city_real_flow_list = np.array(city_real_flow_list).reshape(-1, 1)
    city_simulated_flow_list = np.array(
        city_simulated_flow_list).reshape(-1, 1)
    pems_real_flow_list = np.array(pems_real_flow_list).reshape(-1, 1)
    pems_simulated_flow_list = np.array(
        pems_simulated_flow_list).reshape(-1, 1)
    return city_real_flow_list, city_simulated_flow_list, \
        pems_real_flow_list, pems_simulated_flow_list


def get_linear_regression(
    real_data_list: np.array, simulated_data_list: np.array,
    enforce_intercept: bool
) -> tuple(float, float, float, float, np.array):
    """Compute linear regression results between real and simulated flow data.

    Args:
        real_data_list: Real flow data to be used as x-axis data in the linear
            regression.
        simulated_data_list: Simulated flow data to be used as y-axis data in
            the linear regression.
        enforce_intercept: Whether the intercept should be set to 0. If True,
            the intercept is enforced to 0. If False, the incercept will be
            defined by the slope of the linear regression.
    Returns:
        slope: Slope of the line of best fit.
        intercept: Intercept of the line of best fit.
        r_sq: R-squared value of the line of best fit.
        max_val: Maximum x-axis value. Used for plotting lower and upper bound
            indicator lines within the notebook.
        yhat: Predicted y-axis values according to the line of best fit.
    """
    lin_reg_object = LinearRegression(fit_intercept=(not enforce_intercept))
    lin_reg_object.fit(real_data_list, simulated_data_list)
    slope = lin_reg_object.coef_
    intercept = abs(lin_reg_object.intercept_)
    r_sq = lin_reg_object.score(real_data_list, simulated_data_list)
    yhat = np.dot(real_data_list, slope) + intercept
    max_val = real_data_list.max()
    if not enforce_intercept:
        intercept_float = intercept[0]
    else:
        intercept_float = intercept
    return slope[0][0], intercept_float, r_sq, max_val, yhat


def process_real_flow_data(
    real_flow_dataset: AimsunFlowRealDataSet, time_list: Iterable[datetime.time]
) -> tuple(dict(datetime.time, dict(ExternalId, float)),
           dict(ExternalId, dict(datetime.time, float)),
           list(ExternalId)):
    """Helper function to extract real flow per time and real flow per detector
    from an AimsunFlowRealDataSet object.

    Args:
        real_flow_dataset: Object that contains the real flow data.
        time_list: List of start times for each time interval within the
            timeframe of study.
    Returns:
        real_flow_per_time: Real flow data grouped by time. Used for flow
            biplots.
        real_flow_per_detector: Real flow data grouped by detector. Used for
            flow profiles.
        detector_external_id_list: List of external IDs for the detectors used
            in the study.
    """
    # Initialize return paramaters.
    real_flow_per_time = {}
    real_flow_per_detector = {}
    detector_external_id_list = []

    # Group flow by time.
    for time in time_list:
        flow_per_time_dict = {}
        for flow_real_data in real_flow_dataset.flow_data_set:
            detector_external_id = f"flow_{flow_real_data.external_id}"
            if detector_external_id not in detector_external_id_list:
                detector_external_id_list.append(detector_external_id)
            time_in_timedelta = datetime.timedelta(
                hours=time.hour, minutes=time.minute) \
                + datetime.timedelta(minutes=15)  # This line is the scaler
            flow_per_time_dict[detector_external_id] = \
                flow_real_data.flow_data[time_in_timedelta] * 4
        real_flow_per_time[time] = flow_per_time_dict

    # Group flow by detectors.
    for detector_external_id in detector_external_id_list:
        flow_per_detector_dict = {}
        for flow_real_data in real_flow_dataset.flow_data_set:
            if f"flow_{flow_real_data.external_id}" == detector_external_id:
                for time_key, flow_val in flow_real_data.flow_data.items():
                    time = (datetime.datetime.min + time_key).time()
                    if min(time_list) <= time <= max(time_list):
                        flow_per_detector_dict[time] = flow_val * 4
        real_flow_per_detector[detector_external_id] = flow_per_detector_dict

    return real_flow_per_time, real_flow_per_detector, detector_external_id_list


def __revert_dict_of_dict(
    dict_to_return: dict(Any, dict(Any, Any))
) -> dict(Any, dict(Any, Any)):
    """Revert a dictionary of dictionary."""
    return {y: {x: dict_to_return[x][y] for x in dict_to_return}
            for y in list(dict_to_return.values())[0]}


def process_macro_simulated_flow_data(
    simulation_results_database: dict(datetime.time, AimsunMacroOutputDatabase),
    detector_external_id_list: list(ExternalId)
) -> tuple(dict(datetime.time, dict(ExternalId, float)),
           dict(ExternalId, dict(datetime.time, float))):
    """Helper function to extract simulated flow per time and simulated flow per
    detector from a dictionary of AimsunMacroOutputDatabase objects at each
    time.

    Args:
        simulation_results_database: Aimsun output object that contains the
            microsimulation details.
        detector_external_id_list: List of external IDs for the detectors used
            in the study.
    Returns:
        simulated_flow_per_time: Simulated flow data grouped by time. Used for
            flow biplots.
        simulated_flow_per_detector: Simulated flow data grouped by detector.
            Used for flow profiles.
    """
    # Group flow by time.
    simulated_flow_per_time = {
        time: {
            detector_external_id: simulation_results_database[
                time].get_detector_flow(detector_external_id)
            for detector_external_id in detector_external_id_list
        }
        for time in simulation_results_database
    }
    return simulated_flow_per_time, __revert_dict_of_dict(
        simulated_flow_per_time)


def process_micro_simulated_flow_data(
    simulation_results_database: AimsunMicroOutputDatabase,
    time_list: list(datetime.time),
    detector_external_id_list: list[ExternalId]
) -> tuple(dict(datetime.time, dict(ExternalId, float)),
           dict(ExternalId, dict(datetime.time, float))):
    """Helper function to extract simulated flow per time and simulated flow per
    detector from an AimsunMicroOutputDatabase object.

    Args:
        simulation_results_database: Aimsun output object that contains the
            microsimulation details.
        time_list: List of start times for each time interval within the
            timeframe of study.
        detector_external_id_list: List of external IDs for the detectors used
            in the study.
    Returns:
        simulated_flow_per_time: Simulated flow data grouped by time. Used for
            flow biplots.
        simulated_flow_per_detector: Simulated flow data grouped by detector.
            Used for flow profiles.
    """
    # Group flow by time.
    simulated_flow_per_time = {
        time: {
            detector_external_id: simulation_results_database.get_detector_flow(
                detector_external_id, time)
            for detector_external_id in detector_external_id_list
        }
        for time in time_list
    }
    return simulated_flow_per_time, __revert_dict_of_dict(
        simulated_flow_per_time)


def process_network_delay_time_data(
    simulation_results_database: AimsunMicroOutputDatabase,
    time_intervals: List[datetime.time]
) -> List[float]:
    delay_times = []
    for time in time_intervals:
        delay_times.append(
            simulation_results_database.get_total_delay_time(time))
    return delay_times


# Add more methods as needed.
