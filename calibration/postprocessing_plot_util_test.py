"""Tests for postprocessing_plot_util."""

import datetime
import os
import sys
import unittest
from unittest import mock

import numpy as np

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'Utils')))

from aimsun_input_utils import FlowRealData, AimsunFlowRealDataSet

from postprocessing_plot_util import (
    convert_flow_per_time_to_list,
    get_linear_regression,
    process_real_flow_data
)

TIME_LIST = [datetime.time(1, 1), datetime.time(17, 49), datetime.time(19, 45)]
REAL_DETECTOR_EXTERNAL_ID_LIST = [
    'detector_201901', 'detector_201902', 'detector_403829', 'detector_403928']
AIMSUN_DETECTOR_EXTERNAL_ID_LIST = [
    'flow_detector_201901', 'flow_detector_201902',
    'flow_detector_403829', 'flow_detector_403928']


class TestAllMethods(unittest.TestCase):
    """Test class to test all methods inside postprocessing_plot_util."""

    def test_convert_flow_per_time_to_list(self):
        """Verify correctness of the function convert_flow_per_time_to_list().

        This test case creates a dummy real_flow_per_time and
        simulated_flow_per_time object manually to verify that the outputs are
        contain correct data within their respective grouped flow lists.
        """
        real_flow_per_time, simulated_flow_per_time = {}, {}
        count = 0
        for time in TIME_LIST:
            real_flow_dict, simulated_flow_dict = {}, {}
            for detector_external_id in REAL_DETECTOR_EXTERNAL_ID_LIST:
                real_flow_dict[detector_external_id] = count
                simulated_flow_dict[detector_external_id] = count
                count += 1
            real_flow_per_time[time] = real_flow_dict
            simulated_flow_per_time[time] = simulated_flow_dict
        real_flow_list, simulated_flow_list = convert_flow_per_time_to_list(
            real_flow_per_time, simulated_flow_per_time, TIME_LIST)
        self.assertTrue(all(real_flow_list == simulated_flow_list))
        self.assertTrue(
            all(real_flow_list == np.arange(count).reshape(-1, 1)))
        city_real_flow_list, city_simulated_flow_list, pems_real_flow_list, \
            pems_simulated_flow_list = convert_flow_per_time_to_list(
                real_flow_per_time, simulated_flow_per_time, TIME_LIST, '2019')
        self.assertTrue(all(city_real_flow_list == city_simulated_flow_list))
        self.assertTrue(all(pems_real_flow_list == pems_simulated_flow_list))
        self.assertFalse(any(city_real_flow_list == pems_real_flow_list))
        self.assertTrue(int(np.average(city_real_flow_list)
                        + np.average(pems_real_flow_list)) == count - 1)

    def test_get_linear_regression(self):
        """Verify correctness of the function get_linear_regression().

        This test case generates manually created X and Y data of scatterplots
        and checks if the linear regression coefficients are equal to the
        manually calculated regression coefficients. Note that this test case
        allows errors within 0.00001 to account for 32-bit rounding errors.
        """
        sample_size = 30
        decimal_error_bound = 5

        arr_1 = np.arange(sample_size).reshape(-1, 1)
        arr_2 = arr_1
        temp_slope, temp_intercept, temp_r_sq, max_val_1, _ = \
            get_linear_regression(arr_1, arr_2, False)
        slope_1 = int(round(temp_slope, decimal_error_bound))
        intercept_1 = int(round(temp_intercept, decimal_error_bound))
        r_sq_1 = round(temp_r_sq, decimal_error_bound)
        self.assertTrue((slope_1, intercept_1, r_sq_1, max_val_1)
                        == (1, 0, 1.0, sample_size - 1))

        expected_intercept = 3
        expected_slope = 2
        arr_3 = np.array([expected_slope * x + expected_intercept for x in
                          range(sample_size)]).reshape(-1, 1)
        temp_slope, temp_intercept, temp_r_sq, max_val_2, yhat_2 = \
            get_linear_regression(arr_1, arr_3, False)
        slope_2 = int(round(temp_slope, decimal_error_bound))
        intercept_2 = int(round(temp_intercept, decimal_error_bound))
        r_sq_2 = round(temp_r_sq, decimal_error_bound)
        self.assertTrue((slope_2, intercept_2, r_sq_2, max_val_2)
                        == (expected_slope, expected_intercept, 1.0,
                            sample_size - 1))
        for i, y_val in enumerate(yhat_2):
            self.assertTrue(
                int(round(y_val[0], decimal_error_bound)), arr_3[i][0])

        temp_slope, temp_intercept, temp_r_sq, max_val_3, _ = \
            get_linear_regression(arr_1, arr_3, True)
        slope_3 = int(round(temp_slope, decimal_error_bound))
        intercept_3 = int(round(temp_intercept, decimal_error_bound))
        r_sq_3 = round(temp_r_sq, decimal_error_bound)
        self.assertTrue((slope_3, intercept_3, max_val_3)
                        == (expected_slope, 0, sample_size - 1))
        self.assertTrue(r_sq_3 > 0.9)
        self.assertTrue(r_sq_3 < 1.0)

    def test_process_real_flow_data(self):
        """Verify correctness of the function process_real_flow_data().

        This test case manually creates a AimsunRealFlowDataSet object and
        inputs it into process_real_flow_data to check that the output data
        contains the same timesteps & detector external IDs as the input.
        """
        flow_real_data_list = []
        count = 0
        for _, detector_external_id in enumerate(
                REAL_DETECTOR_EXTERNAL_ID_LIST):
            flow_real_data_obj = FlowRealData()
            flow_real_data_obj.external_id = detector_external_id
            flow_data_dict = {}
            for time in TIME_LIST:
                flow_data_dict[datetime.timedelta(
                    hours=time.hour, minutes=(time.minute + 15))] = count
                count += 1
            flow_real_data_obj.flow_data = flow_data_dict
            flow_real_data_list.append(flow_real_data_obj)
        flow_real_dataset = AimsunFlowRealDataSet()
        flow_real_dataset.flow_data_set = flow_real_data_list

        real_flow_per_time, real_flow_per_detector, detector_external_id_list \
            = process_real_flow_data(flow_real_dataset, TIME_LIST)

        self.assertTrue(
            detector_external_id_list == AIMSUN_DETECTOR_EXTERNAL_ID_LIST)
        self.assertTrue(list(real_flow_per_time.keys()) == TIME_LIST)
        self.assertTrue(list(real_flow_per_time[TIME_LIST[0]].keys())
                        == AIMSUN_DETECTOR_EXTERNAL_ID_LIST)
        self.assertTrue(list(real_flow_per_detector.keys())
                        == AIMSUN_DETECTOR_EXTERNAL_ID_LIST)


if __name__ == '__main__':
    unittest.main()
