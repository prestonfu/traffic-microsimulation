"""Attributes for Aimsun-specific objects.

This file serves to reduce redundancies between attribute-checking assert
statements by defining common attribute between Aimsun objects.
"""

from typing import List


def micro_experiment_attributes() -> List[str]:
    """Get the required attributes for Aimsun Micro Experiment.

    Returns:
        attributes: Attributes for Aimsun Micro Experiment.
    """
    return ['name', 'external_id', 'dynamic_simulator_engine', 'engine_mode',
            'cycle_time', 'intervals', 'capacity_weight', 'dynamic',
            'max_assign_paths']


def micro_dynamic_simulator_engine_attributes(
    engine_parameters: str = '', engine_mode: str = '',
    route_choice_model: str = ''
) -> List[str]:
    """Get the required attributes for Aimsun Micro Dynamic Simulator Engine.

    Args:
        engine_parameters: Parameters for the Dynamic Simulator Engine. Can be
            either 'apply_two_lanes' or 'apply_two_way_overtaking_model'.
            Defaults to an empty string.
        engine_mode: Engine mode for the Dynamic Simulator Engine. Can be either
            'iterative_assignment' or 'one_shot_assignment'. Defaults to an
            empty string.
        route_choice_model: Route choice model for the Dynamic Simulator Engine
            when engine_mode is set to 'one_shot_assignment. Can be either
            'binomial', 'proportional', 'logit', or 'c_logit'.
    Returns:
        attributes: Attributes for Aimsun Micro Dynamic Simulator Engine.
    """
    attributes = micro_experiment_attributes()
    if not engine_parameters and not engine_mode:
        attributes += [
            'micro_sim_step', 'car_following_version',
            'car_following_consider_min_headway', 'apply_two_lanes',
            'apply_twopas_slope_model', 'apply_non_lane_based_movement',
            'apply_two_way_overtaking_model', 'micro_queue_up_speed',
            'micro_queue_leaving_speed',
            'micro_activate_external_behavior_model', 'reaction_time_type',
            'reaction_at_stop', 'reaction_at_traffic_light', 'replications']
        return attributes

    # Add required attributes according to engine parameters.
    if engine_parameters:
        if engine_parameters == 'apply_two_lanes':
            attributes += [
                'max_distance', 'two_lane_car_following_model',
                'micro_num_of_vehicles', 'micro_max_speed_diff',
                'micro_max_speed_diff_ramp']
        elif engine_parameters == 'apply_two_way_overtaking_model':
            attributes += [
                'delay_time_threshold', 'speed_difference_min_threshold',
                'speed_difference_max_threshold', 'rank_threshold',
                'remaining_travel_time_threshold',
                'number_of_simultaneous_overtaking_allowed',
                'delay_between_simultaneous_overtaking',
                'sensitivity_factor_reduce_car_following',
                'overtaking_speed_magnification',
                'speed_difference_overtaking_threshold']

    # Add required attributes according to engine mode.
    if engine_mode == 'iterative_assignment':
        attributes += [
            'stopping_criteria_iterations', 'stopping_criteria_rgap',
            'due_assignment_model', 'due_experienced_costs']
    elif engine_mode == 'one_shot_assignment':
        attributes += [
            'stochastic_route_choice_model', 'user_defined_cost_weigth',
            'initial_shortest_paths_trees', 'max_routes']
        if route_choice_model == 'binomial':
            attributes += ['probability']
        elif route_choice_model == 'proportional':
            attributes += ['alfa']
        elif route_choice_model == 'logit':
            attributes += ['low_variance_factor']
        elif route_choice_model == 'c_logit':
            attributes += [
                'beta', 'gamma', 'low_variance_factor',
                'c_logit_past_cost_replication']
    return attributes
