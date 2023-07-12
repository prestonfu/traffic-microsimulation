"""Helper functions to automatically generate simulation configuration file."""

import datetime
import os
import sys
from typing import Dict, Tuple, Union

module_path = os.path.abspath(os.path.join('..', 'Utils'))
if module_path not in sys.path:
    sys.path.append(module_path)

from calibration import aimsun_config_utils
from calibration import aimsun_folder_utils
from calibration import aimsun_input_utils


CONFIG_DEFAULT_VALUES: Dict[str, Union[float, int, bool]] = {
    'apply_two_lanes': True,
    'two_lanes_car_following': True,
    'micro_num_of_vehicles': 4,
    'max_distance': 100.0,
    'micro_max_speed_diff': 50.0,
    'micro_max_speed_diff_ramp': 70.0,
    'apply_twopas_slope_model': False,
    'apply_non_lane_based_movement': True,
    'apply_two_way_overtaking_model': True,
    'delay_time_threshold': 60.0,
    'speed_difference_min_threshold': 10.0,
    'speed_difference_max_threshold': 35.0,
    'rank_threshold': 2,
    'remaining_travel_time_threshold': 0.1,
    'number_of_simultaneous_overtaking_allowed': 1,
    'delay_between_simultaneous_overtaking': 10.0,
    'sensitivity_factor_reduce_car_following': 0.65,
    'overtaking_speed_magnification': 1.1,
    'speed_difference_overtaking_threshold': 15.0,
    'micro_queue_up_speed': 1.0,
    'micro_queue_leaving_speed': 4.0,
    'external_behavioral_model': False,
    'micro_sim_step': 0.8,
    'reaction_at_stop': 1.2,
    'reaction_at_traffic_light': 1.6,
    'intervals': 2,
    'cycle_time': 600.0,
    'capacity_weight': 1,
    'user_defined_cost_weight': 1,
    'initial_shortest_paths_trees': 5,
    'max_assign_path': 5,
    'max_routes': 5,
    'low_variance_factor': 1.0,
    'beta': 0.3,
    'gamma': 1.0,
    'dynamic': 1,
    'random_seed': 50000
}


PARAMETERS_RANGE: Dict[str, Union[Tuple[float, float], Tuple[int, int]]] = {
    'micro_num_of_vehicles': (0, 10),
    'max_distance': 100.0,
    'micro_max_speed_diff': (30.0, 70.0),
    'micro_max_speed_diff_ramp': (42.0, 98.0),
    'delay_time_threshold': (36.0, 84.0),
    'speed_difference_min_threshold': (5.0, 15.0),
    'speed_difference_max_threshold': (30.0, 40.0),
    'rank_threshold': (0, 10),
    'remaining_travel_time_threshold': (0.0, 10.0),
    'number_of_simultaneous_overtaking_allowed': (0, 6),
    'delay_between_simultaneous_overtaking': (5.0, 15.0),
    'sensitivity_factor_reduce_car_following': (0.5, 1.0),
    'overtaking_speed_magnification': (1.0, 1.25),
    'speed_difference_overtaking_threshold': (5.0, 20.0),
    'micro_queue_up_speed': (0.5, 1.5),
    'micro_queue_leaving_speed': (2.5, 5.5),
    'micro_sim_step': (0.5, 1.1),
    'reaction_at_stop': (0.5, 1.5),
    'reaction_at_traffic_light': (0.8, 2.0),
    'intervals': (1, 7),
    'cycle_time': (350.0, 750.0),
    'capacity_weight': 1,
    'user_defined_cost_weight': 1,
    'initial_shortest_paths_trees': (2, 6),
    'max_assign_path': (2, 6),
    'max_routes': (2, 6),
    'low_variance_factor': (0.0, 2.0),
    'beta': (0.3, 1.5),
    'gamma': (0.5, 1.5),
    'dynamic': 1,
    'random_seed': (0, 100000)
}


def __create_experiment_config(
    experiment_name: str = "Micro_experiment",
    experiment_external_id: aimsun_input_utils.ExternalId = "Micro_experiment",
    dynamic_simulator_engine: aimsun_config_utils.DynamicSimulatorEngine = \
    aimsun_config_utils.DynamicSimulatorEngine.MICROSIMULATION,
    engine_mode: aimsun_config_utils.DynamicSimulationEngineMode = \
    aimsun_config_utils.DynamicSimulationEngineMode.ONE_SHOT_ASSIGNMENT,
    stochastic_route_choice_model: aimsun_config_utils.\
    StochasticRouteChoiceModel = aimsun_config_utils.\
    StochasticRouteChoiceModel.C_LOGIT,
    apply_two_lanes: bool = bool(CONFIG_DEFAULT_VALUES['apply_two_lanes']),
    two_lanes_car_following: bool = \
    bool(CONFIG_DEFAULT_VALUES['two_lanes_car_following']),
    micro_num_of_vehicles: int = \
    int(CONFIG_DEFAULT_VALUES['micro_num_of_vehicles']),
    max_distance: float = CONFIG_DEFAULT_VALUES['max_distance'],
    micro_max_speed_diff: float = CONFIG_DEFAULT_VALUES['micro_max_speed_diff'],
    micro_max_speed_diff_ramp: float = \
    CONFIG_DEFAULT_VALUES['micro_max_speed_diff_ramp'],
    apply_twopas_slope_model: bool = \
    bool(CONFIG_DEFAULT_VALUES['apply_twopas_slope_model']),
    apply_non_lane_based_movement: bool = \
    bool(CONFIG_DEFAULT_VALUES['apply_non_lane_based_movement']),
    apply_two_way_overtaking_model: bool = \
    bool(CONFIG_DEFAULT_VALUES['apply_two_way_overtaking_model']),
    delay_time_threshold: float = CONFIG_DEFAULT_VALUES['delay_time_threshold'],
    speed_difference_min_threshold: float = \
    CONFIG_DEFAULT_VALUES['speed_difference_min_threshold'],
    speed_difference_max_threshold: float = \
    CONFIG_DEFAULT_VALUES['speed_difference_max_threshold'],
    rank_threshold: int = int(CONFIG_DEFAULT_VALUES['rank_threshold']),
    remaining_travel_time_threshold: float = \
    CONFIG_DEFAULT_VALUES['remaining_travel_time_threshold'],
    number_of_simultaneous_overtaking_allowed: int = \
    int(CONFIG_DEFAULT_VALUES['number_of_simultaneous_overtaking_allowed']),
    delay_between_simultaneous_overtaking: float = \
    CONFIG_DEFAULT_VALUES['delay_between_simultaneous_overtaking'],
    sensitivity_factor_reduce_car_following: float = \
    CONFIG_DEFAULT_VALUES['sensitivity_factor_reduce_car_following'],
    overtaking_speed_magnification: float = \
    CONFIG_DEFAULT_VALUES['overtaking_speed_magnification'],
    speed_difference_overtaking_threshold: float = \
    CONFIG_DEFAULT_VALUES['speed_difference_overtaking_threshold'],
    micro_queue_up_speed: float = CONFIG_DEFAULT_VALUES['micro_queue_up_speed'],
    micro_queue_leaving_speed: float = \
    CONFIG_DEFAULT_VALUES['micro_queue_leaving_speed'],
    external_behavioral_model: bool = \
    bool(CONFIG_DEFAULT_VALUES['external_behavioral_model']),
    micro_sim_step: float = CONFIG_DEFAULT_VALUES['micro_sim_step'],
    reaction_at_stop: float = CONFIG_DEFAULT_VALUES['reaction_at_stop'],
    reaction_at_traffic_light: float = \
    CONFIG_DEFAULT_VALUES['reaction_at_traffic_light'],
    intervals: int = int(CONFIG_DEFAULT_VALUES['intervals']),
    cycle_time: float = CONFIG_DEFAULT_VALUES['cycle_time'],
    capacity_weight: int = int(CONFIG_DEFAULT_VALUES['capacity_weight']),
    user_defined_cost_weight: int = \
    int(CONFIG_DEFAULT_VALUES['user_defined_cost_weight']),
    initial_shortest_paths_trees: int = \
    int(CONFIG_DEFAULT_VALUES['initial_shortest_paths_trees']),
    max_assign_path: int = int(CONFIG_DEFAULT_VALUES['max_assign_path']),
    max_routes: int = int(CONFIG_DEFAULT_VALUES['max_routes']),
    low_variance_factor: float = CONFIG_DEFAULT_VALUES['low_variance_factor'],
    beta: float = CONFIG_DEFAULT_VALUES['beta'],
    gamma: float = CONFIG_DEFAULT_VALUES['gamma'],
    dynamic: bool = bool(CONFIG_DEFAULT_VALUES['dynamic']),
    past_cost_replication: int = 0,
    results_to_generate: bool = False,
    random_seed: int = int(CONFIG_DEFAULT_VALUES['random_seed']),
    probability: float = 1.0
) -> aimsun_config_utils.AimsunMicroExperiment:
    """
    Args:
        experiment_name: Define the name of the experiment.
        experiment_external_id: Define the external id for the experiment.
        dynamic_simulator_engine: see AimsunMicroExperiment docstring.
        engine_mode: see AimsunMicroExperiment docstring.
        stochastic_route_choice_model: see AimsunMicroExperiment docstring.
        apply_two_lanes: see AimsunMicroExperiment docstring.
        two_lanes_car_following: see AimsunMicroExperiment docstring.
        micro_num_of_vehicles: see AimsunMicroExperiment docstring.
        max_distance: see AimsunMicroExperiment docstring.
        micro_max_speed_diff:  see AimsunMicroExperiment docstring.
        micro_max_speed_diff_ramp: see AimsunMicroExperiment docstring.
        apply_twopas_slope_model: see AimsunMicroExperiment docstring.
        apply_non_lane_based_movement: see AimsunMicroExperiment docstring.
        apply_two_way_overtaking_model: see AimsunMicroExperiment docstring.
        delay_time_threshold: see AimsunMicroExperiment docstring.
        speed_difference_min_threshold: see AimsunMicroExperiment docstring.
        speed_difference_max_threshold: see AimsunMicroExperiment docstring.
        rank_threshold: see AimsunMicroExperiment docstring.
        remaining_travel_time_threshold: see AimsunMicroExperiment docstring.
        number_of_simultaneous_overtaking_allowed:
            see AimsunMicroExperiment docstring.
        delay_between_simultaneous_overtaking:
            see AimsunMicroExperiment docstring.
        sensitivity_factor_reduce_car_following:
            see AimsunMicroExperiment docstring.
        overtaking_speed_magnification: see AimsunMicroExperiment docstring.
        speed_difference_overtaking_threshold:
            see AimsunMicroExperiment docstring.
        micro_queue_up_speed: see AimsunMicroExperiment docstring.
        micro_queue_leaving_speed: see AimsunMicroExperiment docstring.
        external_behavioral_model: see AimsunMicroExperiment docstring.
        micro_sim_step: see AimsunMicroExperiment docstring.
        reaction_at_stop: see AimsunMicroExperiment docstring.
        reaction_at_traffic_light: see AimsunMicroExperiment docstring.
        intervals: see AimsunMicroExperiment docstring.
        cycle_time: see AimsunMicroExperiment docstring.
        capacity_weight: see AimsunMicroExperiment docstring.
        user_defined_cost_weight: see AimsunMicroExperiment docstring.
        initial_shortest_paths_trees: see AimsunMicroExperiment docstring.
        max_assign_path: see AimsunMicroExperiment docstring.
        max_routes: see AimsunMicroExperiment docstring.
        low_variance_factor: see AimsunMicroExperiment docstring.
        beta: see AimsunMicroExperiment docstring.
        gamma: see AimsunMicroExperiment docstring.
        dynamic: see AimsunMicroExperiment docstring.
        past_cost_replication: see AimsunMicroExperiment docstring.
        results_to_generate: see AimsunMicroExperiment docstring.
        random_seed: see AimsunMicroExperiment docstring.
        probability: see AimsunMicroExperiment docstring.
    Returns:
        Creates a aimsun_config_utils.AimsunMicroExperiment.
    """
    experiment = aimsun_config_utils.AimsunMicroExperiment()
    experiment.name = experiment_name
    experiment.external_id = experiment_external_id

    experiment.dynamic_simulator_engine = dynamic_simulator_engine
    experiment.engine_mode = engine_mode

    # General parameters
    experiment.cycle_time = cycle_time
    experiment.intervals = intervals
    experiment.capacity_weight = capacity_weight
    experiment.dynamic = dynamic
    experiment.max_assign_paths = max_assign_path

    if experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.MICROSIMULATION:
        # Microsimulation
        experiment.micro_sim_step = micro_sim_step
        experiment.car_following_version = \
            aimsun_config_utils.CarFollowingVersionEnum.VERSION_4_1
        experiment.car_following_consider_min_headway = two_lanes_car_following
        experiment.apply_two_lanes = apply_two_lanes

        if experiment.apply_two_lanes:
            # The following attribute has no set default in the routing
            # calibration md file.
            experiment.max_distance = max_distance
            experiment.two_lane_car_following_model = \
                aimsun_config_utils.TwoLaneCarFollowingModel.ABSOLUTE
            experiment.micro_num_of_vehicles = micro_num_of_vehicles
            experiment.micro_max_speed_diff = micro_max_speed_diff
            experiment.micro_max_speed_diff_ramp = micro_max_speed_diff_ramp

        # The next three parameters have no defaults in the routing calibration
        # md file.
        experiment.apply_twopas_slope_model = apply_twopas_slope_model
        experiment.apply_non_lane_based_movement = apply_non_lane_based_movement
        experiment.apply_two_way_overtaking_model = \
            apply_two_way_overtaking_model

        # This block of parameters may not have related columns within Aimsun
        if experiment.apply_two_way_overtaking_model:
            experiment.delay_time_threshold = delay_time_threshold
            experiment.speed_difference_min_threshold = \
                speed_difference_min_threshold
            experiment.speed_difference_max_threshold = \
                speed_difference_max_threshold
            experiment.rank_threshold = rank_threshold
            experiment.remaining_travel_time_threshold = \
                remaining_travel_time_threshold
            experiment.number_of_simultaneous_overtaking_allowed = \
                number_of_simultaneous_overtaking_allowed
            experiment.delay_between_simultaneous_overtaking = \
                delay_between_simultaneous_overtaking
            experiment.sensitivity_factor_reduce_car_following = \
                sensitivity_factor_reduce_car_following
            experiment.overtaking_speed_magnification = \
                overtaking_speed_magnification
            experiment.speed_difference_overtaking_threshold = \
                speed_difference_overtaking_threshold

        experiment.micro_queue_up_speed = micro_queue_up_speed
        experiment.micro_queue_leaving_speed = micro_queue_leaving_speed
        experiment.micro_activate_external_behavior_model = \
            external_behavioral_model

        experiment.reaction_time_type = (
            aimsun_config_utils.ReactionTimeTypeEnum.
            REACTION_TIME_EQUAL_TO_SIM_STEP)
        experiment.reaction_at_stop = reaction_at_stop
        experiment.reaction_at_traffic_light = reaction_at_traffic_light
        experiment.replications.append(
            aimsun_config_utils.AimsunReplication(
                random_seed, results_to_generate))
    elif experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.MESOSIMULATION:
        raise NotImplementedError("Not implemented")
    elif experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.HYBRID_SIMULATION:
        raise NotImplementedError("Not implemented")
    elif experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.DYNAMIC_MACROSIMULATION:
        raise NotImplementedError("Not implemented")
    else:
        raise ValueError('Wrong value for dynamic_simulator_engine.')

    if experiment.engine_mode == \
            aimsun_config_utils.DynamicSimulationEngineMode.ONE_SHOT_ASSIGNMENT:

        experiment.stochastic_route_choice_model = stochastic_route_choice_model
        experiment.user_defined_cost_weight = user_defined_cost_weight
        experiment.initial_shortest_paths_trees = initial_shortest_paths_trees
        experiment.max_routes = max_routes

        if experiment.stochastic_route_choice_model == \
                aimsun_config_utils.StochasticRouteChoiceModel.BINOMIAL:
            experiment.probability = probability
        elif experiment.stochastic_route_choice_model == \
                aimsun_config_utils.StochasticRouteChoiceModel.PROPORTIONAL:
            raise NotImplementedError('Not implemented')
        elif experiment.stochastic_route_choice_model == \
                aimsun_config_utils.StochasticRouteChoiceModel.LOGIT:
            experiment.low_variance_factor = low_variance_factor
        elif experiment.stochastic_route_choice_model == \
                aimsun_config_utils.StochasticRouteChoiceModel.C_LOGIT:
            experiment.beta = beta
            experiment.gamma = gamma
            experiment.low_variance_factor = low_variance_factor
            experiment.c_logit_past_cost_replication = past_cost_replication
        else:
            raise ValueError('Incorrect stochastic_route_choice_model.')
    elif experiment.engine_mode == (
            aimsun_config_utils.DynamicSimulationEngineMode.
            ITERATIVE_ASSIGNMENT):
        raise NotImplementedError('Not implemented')
    else:
        raise ValueError('engine_mode is not correct.')

    experiment.assert_experiment_well_formatted()
    return experiment


def create_traffic_demand(
    traffic_demand_external_id: str = "traffic_demand_afternoon"
) -> aimsun_config_utils.AimsunTrafficDemands:
    """Create traffic demand file for traffic microsimulation."""
    aimsun_traffic_demands = aimsun_config_utils.AimsunTrafficDemands()
    aimsun_traffic_demand = aimsun_config_utils.AimsunTrafficDemand(
        traffic_demand_external_id)
    for vehicle_type in [aimsun_input_utils.VehicleTypeName.RESIDENT,
                         aimsun_input_utils.VehicleTypeName.TRAVELER]:
        for hour in range(14, 20, 1):
            for minutes in range(0, 60, 15):
                aimsun_traffic_demand.demand_items.append(
                    aimsun_config_utils.AimsunScheduleDemandItem(
                        datetime.time(hour=hour, minute=minutes), vehicle_type))
    aimsun_traffic_demands.traffic_demands.append(aimsun_traffic_demand)
    return aimsun_traffic_demands


def create_microsimulation_config(
    unique_name: str,
    traffic_demand_external_id: str,
    create_simulation_config_kwargs: Dict[str, Union[float, int, bool]] = None
):
    """Create configuration file for traffic microsimulation."""
    microscenario = aimsun_config_utils.AimsunScenario()
    db_path = aimsun_folder_utils.aimsun_micro_databases_file()
    microscenario.name = f"Microscenario_{unique_name}"
    microscenario.external_id = f"Microscenario_{unique_name}"
    microscenario.master_control_plan_external_id = (
        aimsun_input_utils.MASTER_CONTROL_PLAN_EXTERNAL_ID)
    microscenario.real_dataset_external_id = (
        aimsun_input_utils.REAL_DATA_SET_EXTERNAL_ID)
    microscenario.traffic_strategy_external_ids = [
        aimsun_input_utils.TRAFFIC_STRATEGY_EXTERNAL_ID]
    microscenario.traffic_demand_external_id = traffic_demand_external_id

    scenario_input_data = aimsun_config_utils.AimsunScenarioInputData()
    scenario_input_data.detection_interval = datetime.timedelta(seconds=900.0)
    scenario_input_data.global_trajectories_statistics = True
    scenario_input_data.section_trajectories_statistics = True
    scenario_input_data.statistical_interval = datetime.timedelta(seconds=900.0)
    scenario_input_data.trajectories_statistics = True
    scenario_input_data.trajectory_condition_list = []

    if not create_simulation_config_kwargs:
        create_simulation_config_kwargs = {}
    microscenario.experiment = __create_experiment_config(
        experiment_name=unique_name,
        experiment_external_id=unique_name,
        **create_simulation_config_kwargs)
    microscenario.database_info = aimsun_config_utils.AimsunDataBaseInfo(
        db_path)
    microscenario.scenario_input_data = scenario_input_data
    microscenario.export_to_file(
        aimsun_folder_utils.aimsun_micro_simulation_config_input_file())
