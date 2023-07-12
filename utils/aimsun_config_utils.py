"""This module houses the classes and methods used to create, import, and
export configuration files for Aimsun Experiments. Enumerator classes are used
to map Aimsun parameters that are not primitive values. The classes utilize the
pickle module to save object data into .pkl files. These can be read later, and
their attributes are imported into Aimsun.

The main use of this module is to configure simulation parameters. For more
information relating to each parameter and enumeration, please read the routing
calibration document for a more in depth descriptions.
"""

import datetime
import enum
import pickle
from typing import List

from utils.aimsun_attribute_utils import (
    micro_dynamic_simulator_engine_attributes,
    micro_experiment_attributes
)
from utils import aimsun_input_utils
from utils.verification_utils import verify_filepath, verify_attributes


class AimsunScheduleDemandItem(aimsun_input_utils.AimsunObject):
    """The AimsunScheduleDemandItem class saves demand information to be
    imported and used by the Aimsun simulator. It saves some information in
    an OD Matrix object, which is referenced by External ID in this object.
    Python object modeling the Aimsun GKScheduleDemandItem.

    Attributes:
        demand_factor: The percentage of traffic demand that will be used based
            on the traffic demand information found in the OD Matrix.
        demand_external_id: The External ID referencing this object's
            associated OD Matrix object. Traffic demand data, vehicle type, and
            simulation start time are saved in this object.
    """
    demand_factor: str
    demand_external_id: aimsun_input_utils.ExternalId

    def __init__(
        self, begin_time: datetime.time,
        vehicle_type: aimsun_input_utils.VehicleTypeName,
        demand_factor: str = '100'
    ):
        self.demand_external_id = aimsun_input_utils.od_matrix_name_generation(
            begin_time, vehicle_type)
        self.demand_factor = demand_factor


class AimsunTrafficDemand(aimsun_input_utils.AimsunObject):
    """Aggregate class containing a list of AimsunScheduleDemandItem objects.

    The AimsunTrafficDemand class corresponds to the traffic demand of one
    simulation. It holds a list of AimsunScheduleDemandItems which each
    describe a part of the total AimsunTrafficDemand.
    Python object modeling the Aimsun GKTrafficDemand.

    Attributes:
        demand_items: A list of AimsunScheduleDemandItem objects.
        external_id: Inherited from AimsunObject. This is the GKTrafficDemand
            external id.
        name: Inherited from AimsunObject.
    """
    demand_items: List[AimsunScheduleDemandItem]

    def __init__(self, external_id: str):
        self.demand_items = []
        self.external_id = external_id
        self.name = external_id


class AimsunTrafficDemands:
    """Aggregate class containing a list of AimsunTrafficDemand objects.

    The AimsunTrafficDemand class stores a list of
    AimsunTrafficDemand objects, each of which correspond to the demand for
    one simulation. By utilizing the pickle module, we can save one object
    instead of a group of AimsunTrafficDemand objects.

    Attributes:
        traffic_demands: A list of AimsunTrafficDemand objects.
    """
    traffic_demands: List[AimsunTrafficDemand]

    def __init__(self, filepath: str = ''):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.traffic_demands = []

    def export_to_file(self, filepath: str):
        """Function to export AimsunTrafficDemands object using pickle.

        Args:
            filepath: Location where this object should be exported to. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        if not hasattr(self, 'traffic_demands'):
            raise ValueError("Traffic demands attribute does not exist.")
        if not isinstance(self.traffic_demands, List):
            raise TypeError("Traffic demands is not a list.")
        for i, traffic_demand in enumerate(self.traffic_demands):
            if not isinstance(traffic_demand, AimsunTrafficDemand):
                raise TypeError(
                    f"Object at index {i} in list traffic_demands is not an "
                    "AimsunTrafficDemand object.")
            if not hasattr(traffic_demand, 'demand_items'):
                raise ValueError(
                    f"Object at index {i} in list traffic_demands; attribute "
                    "demand_items does not exist.")
            for j, demand_item in enumerate(traffic_demand.demand_items):
                if not isinstance(demand_item, AimsunScheduleDemandItem):
                    raise TypeError(
                        f"Object at index {j} in list demand_items for object "
                        f"{traffic_demand} is not an AimsunScheduleDemandItem "
                        "object.")
                if not hasattr(demand_item, 'demand_factor'):
                    raise ValueError(
                        f"Object at index {j} in list demand_items for object "
                        f"{traffic_demand}; attribute demand_factor does not "
                        "exist.")
                if not hasattr(demand_item, 'demand_external_id'):
                    raise ValueError(
                        f"Object at index {j} in list demand_items for object "
                        f"{traffic_demand}; attribute demand_external_id does "
                        "not exist.")
                if not isinstance(demand_item.demand_external_id, str):
                    raise TypeError(
                        f"Object at index {j} in list demand_items for object "
                        f"{traffic_demand}; attribute demand_external_id is "
                        "not type ExternalId.")
        with open(filepath, 'wb') as file:
            pickle.dump(self.traffic_demands, file)

    def __import_from_file(self, filepath: str):
        """Function to import AimsunTrafficDemands object using pickle.

        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, 'rb') as file:
            imported_traffic_demands = pickle.load(file)
            if not isinstance(imported_traffic_demands, List):
                raise TypeError("imported_traffic_demands is not type List.")
            for i, traffic_demand in enumerate(imported_traffic_demands):
                if not isinstance(traffic_demand, AimsunTrafficDemand):
                    raise TypeError(
                        f"Object at index {i} in list imported_traffic_demands "
                        "is not an AimsunTrafficDemand object.")
            self.traffic_demands = imported_traffic_demands


class AimsunDataBaseInfo:
    """The AimsunDataBaseInfo class connects data storage from an external
    database to Aimsun by a driver reference and database path. The database
    can also be set to automatic for Aimsun to manage it without asking the
    user for a file.
    Python object modeling the Aimsun GKDataBaseInfo.

    Attributes:
        automatic: A boolean denoting whether Aimsun will manage this database
            automatically. This means Aimsun will automatically create a small
            database itself to store network data if a database doesn't already
            exist. It can either be an Access database or an SQLite database.
            Note: as the size of this database is small, it is recommended to
            have an external database and not this automatic database for large
            scale networks.
        automatically_created: A boolean denoting whether the linked database
            would be created automatically using the current given database
            name. This attribute is linked to the attribute 'automatic', and
            creates the small database with the aforementioned specifications.
        database_driver_name: A String denoting the type of database being
            used with this object. Possible values are QODBC3, QSQLITE, ACCESS,
            and any other database supported by the installed Qt sqldrivers.
        database_path: The filepath location of the associated database.
        use_project_db: A boolean denoting whether to use the linked database
            or the project database. If true, uses the project database. The
            project database is the database set within the 'Project Output
            Database' setting for each project, while the linked database could
            be a separate external database unrelated to the project's set
            database.
    """
    use_project_db: bool
    automatic: bool
    automatically_created: bool
    database_driver_name: str
    database_path: str

    def __init__(
        self, database_path: str, use_project_db: bool = False,
        automatic: bool = False,
        database_driver_name: str = aimsun_input_utils.DATABASE_DRIVER_NAME,
        automatically_created: bool = True
    ):
        self.use_project_db = use_project_db
        self.automatic = automatic
        self.database_driver_name = database_driver_name
        self.automatically_created = automatically_created
        self.database_path = database_path


class AimsunGenericExperiment(aimsun_input_utils.AimsunObject):
    """The AimsunGenericExperiment class acts as a placeholder for Aimsun
    structure. It has no functionality within itself, but Aimsun's experiment
    classes inherit from this class. Thus, it is copied over to preserve
    abstraction.
    Python object modeling the Aimsun GKGenericExperiment.
    """
    def hasattr(self, attribute: str):
        """This hasattr function is redefined for the mapping to work elsewhere
        in the scripts.
        """
        return hasattr(self, attribute)


AIMSUN_STATIC_ENGINE = 'FrankWolfe'


class DynamicUserEquilibriumAssignmentModel(enum.IntEnum):
    """This enumeration class is used to differentiate the different model
    types for a Dynamic User Equilibrium experiment.
        MSA: Shorthand for Method of Successive Averages, this model type is
            based on redistributing flows of traffic among different available
            paths in an iterative procedure that computes a new shortest path
            from the origin to destination at each iteration, updating path
            flows based on two sets of flow update procedures. These path
            updates are based on parameter alpha (the weighting coefficient).
        WEIGHTED_MSA: Weighted MSA modifies the MSA algorithm by modifying
            alpha, which accounts for variable step length, dependent on
            current path travel time. However, computational drawbacks from
            large networks require the user to also specify the maximum number
            of paths to keep for each origin-destination pair to reduce
            computational overload.
        GRADIENT_BASED: This model uses the gradient descent method to solve
            the minimization problem in the Dynamic User Equilibrium model. It
            is an iterative procedure that calculates a negative gradient
            search direction and determines the step length in that direction
            until it hits the stopping criterion r_gap (relative gap).
    """
    MSA = 0
    WEIGHTED_MSA = 1
    GRADIENT_BASED = 2


class CarFollowingVersionEnum(enum.IntEnum):
    """This enumeration class is used to differentiate the car-following
    code version. These versions correspond to different behavior for the car-
    following model.
    """
    VERSION_4_1 = 0
    VERSION_4_2 = 1


class DynamicSimulatorEngine(enum.IntEnum):
    """This enumeration class is used to describe the network loading type.
    Each enumeration tells Aimsun what kind of simulator should be used for
    the given experiment.
    Associated to the Aimsun GKExperiment.SimulatorEngine enumeration.
        MICROSIMULATION: Microsimulations are time-based simulations. At each
            time step, every vehicle considers its speed and lane choice. Using
            that information, the vehicle changes its distance along a road
            section.
        MESOSIMULATION: Mesosimulations are event-based simulations. Time is
            moved forward based on events where vehicles enter or leave a
            section or node. Only vehicles at the head of a queue are
            considered when updating events to reduce computational time to run
            a simulation.
        HYBRID_SIMULATION: A hybrid simulation combines both of the analysis
            procedures of the micro and meso simulations. Larger areas are
            covered with mesoscopic simulations, while more detailed
            microsimulations can be run on critical areas.
        DYNAMIC_MACROSIMULATION: Macrosimulations are flow-based simulations.
            As there are no individual vehicles, data is instead aggregated
            into flows, which are assigned to the network to balance load and
            minimize journey time.
    """
    MICROSIMULATION = 0
    MESOSIMULATION = 1
    HYBRID_SIMULATION = 2
    DYNAMIC_MACROSIMULATION = 3


class DynamicSimulationEngineMode(enum.IntEnum):
    """This enumeration class tells Aimsun what type of dynamic traffic
    assignment experiment will run. An Iterative Assignment
    (ITERATIVE_ASSIGNMENT) is based on dynamic user equilibrium (DUE) while the
    One Shot Assignment (ONE_SHOT_ASSIGNMENT) is based on stochastic route
    choice (SRC).
    Associated to the Aimsun GKExperiment.EngineMode enumeration.
    """
    ITERATIVE_ASSIGNMENT = 0
    ONE_SHOT_ASSIGNMENT = 1


class StochasticRouteChoiceModel(enum.IntEnum):
    """This enumeration class tells Aimsun the type of route choice model that
    is used in the associated experiment.

    FIXED_DISTANCE: Each route choice is made purely based on shortest distance.
        The full term for this model is the Fixed using Travel Time in Free
        Flow Conditions. In this model, the paths are calculated at the
        beginning of a simulation, taking the initial cost as the cost of each
        arc. Here, congestion is not taken into account, as the shortest paths
        are never recalculated after the start of the simulation.
    FIXED_TIME: Each route choice is made purely based on shortest time. The
        full term for this model is the Fixed using Travel Time during Warm-Up
        Period. The setup for this model is similar to FIXED_DISTANCE, but the
        shortest paths are calculated regularly instead of once; the first
        calculation happens at the start of the simulation, and the subsequent
        calculations happen at even time intervals after the predefined warm-up
        period, in which the simulation has already ran for some time. Due to
        the change in state, the subsequent calculations are able to factor in
        some congestion that has built up during the warm-up period.
        The parameter that is changed here is the time interval for shortest
        paths recalculation.
    BINOMIAL: The route choices have a binomial probability distribution for
        being selected.
        The parameter that is changed here is the probability.
    PROPORTIONAL: The route choices have a proportional probability distribution
        for being selected.
        The parameter that is changed here is the alpha factor.
    LOGIT: The route choices have a probability distribution for being selected
        based on the Logit function, the inverse of the standard logistic
        function.
        The parameter that is changed here is the scale factor. Scale factor is
        also defined as low variance factor.
    C_LOGIT: The route choices have a probability distribution for being
        selected based on the C-Logit function, a modified Logit function
        proposed by Cascetta. This function considers perceived utility and
        commonality factors (proportional to the degree of overlapping paths).
        The parameters that are changed here are the scale factor, beta, and
        gamma. Scale factor is also defined as low variance factor.
    USER_DEFINED: The route choice probability distribution is defined by the
        user instead of a function defined by Aimsun. In Aimsun, these models
        can be created using the Cost Function Editor, so changed parameters
        may be different based on the user's given cost function.
    """
    FIXED_DISTANCE = 0
    FIXED_TIME = 1
    BINOMIAL = 2
    PROPORTIONAL = 3
    LOGIT = 4
    C_LOGIT = 5
    USER_DEFINED = 6


class FrankWolfeMethod(enum.IntEnum):
    """This enumeration class is used with Macroexperiments to describe whether
    the normal or conjugate direction Frank-Wolfe Method is used in the
    associated experiment.
    Associated to the Aimsun CFrankWolfeParams.fwMethod enumeration.
    """
    NORMAL = 0
    CONJUGATE = 1


class ReactionTimeTypeEnum(enum.IntEnum):
    """This enumeration class is used to describe the type of reaction time
    type of a simulation. REACTION_TIME_EQUAL_TO_SIM_STEP denotes the same
    reaction times for every vehicle (that being the simulation step), while
    REACTION_TIME_PER_VEHICLE_TYPE denotes a reaction time set for each vehicle
    type instead.
    Associated to the Aimsun GKReationTimeType enumeration.
    """
    REACTION_TIME_EQUAL_TO_SIM_STEP = 0
    REACTION_TIME_PER_VEHICLE_TYPE = 1


class TwoLaneCarFollowingModel(enum.IntEnum):
    """This enumeration class is used to describe the type of model that two-
    lane car-following will follow for the simulation. The Absolute model is
    used to speed up vehicles to match the flow of traffic as it merges in
    from on ramps. The Relative model is used to slow down fast-moving vehicles
    to anticipate possible merging of slower-moving vehicles. The Adjacent
    Paths model is used to look at subpaths between adjacent lanes that may be
    in two different road sections. Because the sections are separated, this
    model is able to read past a single section in order to calculate possible
    merging.
    """
    ABSOLUTE = 0
    RELATIVE = 1
    ADJACENT_PATHS = 2


class FrankWolfeParameters:
    """The FrankWolfeParameters class is used to store parameters used in a
    Macroexperiment.
    Python object modeling the Aimsun CFrankWolfeParams.

    Attributes:
        max_iterations: The maximum number of gradient descent steps. Used as
            a stopping criterion for the experiment.
        max_relative_gap: The maximum relative gap. Used as a stopping
            criterion for the experiment. Relative gap shows the differences
            between path travel times or path costs for all OD pairs.
        method: The Frank Wolfe method that is used. Can be either Normal or
            Conjugate.
    """
    max_iterations: int
    max_relative_gap: float
    method: FrankWolfeMethod

    def __init__(self, max_iterations: int = 100,
                 method: FrankWolfeMethod = FrankWolfeMethod.CONJUGATE,
                 max_relative_gap: float = 0.001):
        self.max_iterations = max_iterations
        self.method = method
        self.max_relative_gap = max_relative_gap


class AimsunReplication(aimsun_input_utils.AimsunObject):
    """A class used to save replication data from Aimsun's GKReplication
    objects.

    Attributes:
        random_seed: the seed that is set within Aimsun to generate a pseudo-
            random simulation.
        results_to_generate: a boolean that denotes whether the simulation is
            going to be recorded.
    """
    random_seed: int
    results_to_generate: bool

    def __init__(self, random_seed: int, results_to_generate: bool):
        self.random_seed = random_seed
        self.results_to_generate = results_to_generate


class AimsunStaticMacroExperiment(AimsunGenericExperiment):
    """The AimsunStaticMacroExperiment class stores the data needed to run a
    static macroexperiment. This data will be accessed later when instantiating
    a new experiment within Aimsun.
    Python object associated with the Aimsun MacroExperiment.

    Attributes:
        engine: The internal name for the engine. Has a default value of
            AIMSUN_STATIC_ENGINE.
        parameters: The Frank-Wolfe Parameters associated with this
            macroexperiment. Has default values max_iteration = 100, conjugate
            Frank-Wolfe method, and max_relative_gap = 0.001.
    """
    engine: str
    parameters: FrankWolfeParameters

    def __init__(
        self, engine: str = AIMSUN_STATIC_ENGINE, max_iterations: int = 100,
        method: FrankWolfeMethod = FrankWolfeMethod.CONJUGATE,
        max_relative_gap: float = 0.001
    ):
        self.engine = engine
        self.parameters = FrankWolfeParameters(
            max_iterations=max_iterations,
            method=method,
            max_relative_gap=max_relative_gap)


class AimsunMicroExperiment(AimsunGenericExperiment):
    """This class holds all the needed parameters to run a dynamic
    microsimulation. The experiment can be a stochastic route choice (SRC) or a
    dynamic user-equilibrium (DUE) experiment.

    GKExperiment.
    Attributes:
    Scenario Data Attributes:
        dynamic_simulator_engine: DynamicSimulatorEngine
        engine_mode: DynamicSimulationEngineMode
        replications: A List of AimsunReplication objects.
    Stochastic Route Choice (SRC) Scenario Data Attributes:
        stochastic_route_choice_model: used with an SRC simulation. For
            route choice, this describes the type of route choice that could be
            chosen for a simulation. Check the StochasticRouteChoiceModel
            class for more information. On the Aimsun GUI, this can be set by
            the path Dynamic Traffic Assignment -> Stochastic Route Choice ->
            Model.
    Dynamic User-Equilibrium (DUE) Scenario Data Attributes:
        due_assignment_model: used with DUE experiments. The assignment model
            'aValue' should be 0 for MSA, 1 for Weighted MSA, and 2 for
            Gradient-based. On the GUI within Aimsun, this can be set by the
            path Dynamic Traffic Assignment -> Dynamic User Equilibrium ->
            Model.
        due_experienced_costs: used in DUE experiments. Describes whether this
            experiment uses experienced costs or instantaneous costs.
        stopping_criteria_iterations: the number of iterations needed to be
            carried out to stop.
        stopping_criteria_rgap: the relative gap criteria needed to stop.
    Scenario Parameter Attributes:
        apply_twopas_slope_model: a boolean that denotes whether this
            simulation should apply the TWOPAS slope model. The TWOPAS model
            calculates acceleration and speed of a vehicle based on the impacts
            of engine output,weight, air resistance, and slopes on the vehicle
            speed and acceleration.
        apply_two_lanes: considers whether this simulation should apply a
            two-lane car-following.
        capacity_weight: describes the route choice on capacity weights.
        car_following_consider_min_headway: considers if this simulation
            uses the minimum headway in car-following or not.
        car_following_version: the version of cars being used in this
            simulation.
        cycle_time: the amount of time each cycle lasts in seconds. On the
            GUI within Aimsun, this can be set by the path Dynamic Traffic
            Assignment -> Cycle.
        dynamic: describes whether the route choice model uses the dynamic cost
            function.
        intervals: the number of intervals used in this simulation. On the
            Aimsun GUI, this can be set by the path Dynamic Traffic Assignment
            -> Number of Intervals.
        max_assign_paths: describes the maximum number of shortest paths
            considered from the Path Assignment Plan files.
        max_distance: the maximum distance between a given vehicle and its
            surrounding vehicles that are taken into account when applying the
            Two-lane Car-Following model.
        micro_activate_external_behavioral_model: used with MICRO experiments.
            For the Aimsun Next Micro SDK, this sets whether the experiment uses
            an external model or not. On the Aimsun GUI, this can be set by the
            path Behavior -> Behavior Models.
        micro_max_speed_diff: used with MICRO experiments. The maximum speed
            difference when using tow-lane car-following, in kilometers per
            hour. On the Aimsun GUI, this can be set by the path Behavior ->
            Car Following -> Maximum Speed Difference.
        micro_max_speed_diff_ramp: used with MICRO experiments. The maximum
            speed difference on a ramp when using two-lane car-following, in
            kilometers per hour. On the Aimsun GUI, this can be set by the path
            Behavior -> Car Following -> Maximum Speed Difference.
        micro_num_of_threads: used with MICRO experiments. The number of threads
            used in a micro simulation. On the Aimsun GUI, this can be set by
            the path Main -> Performance Settings -> Simulation Threads.
        micro_num_of_vehicles: used with MICRO experiments. The minimum number
            of vehicles needed to consider whether Aimsun should use two-lane
            car-following. On the Aimsun GUI, this can be set by the path
            Behavior -> Car Following -> Maximum Distance.
        micro_queue_leaving_speed: used with MICRO experiments. Describes the
            queue exit speed in meters per second. On the Aimsun GUI, this can
            be set by the path Behavior -> Queue Speeds -> Queue Exit Speed.
        micro_queue_up_speed: used with a MICRO experiments. Describes the queue
            entry speed in meters per second. On the Aimsun GUI, this can be
            set by the path Behavior -> Queue Speeds -> Queue Entry Speed.
        micro_sim_step: used with a MICRO simulation. Describes the
            length of time per simulation step. On the GUI within Aimsun, this
            can be set by the path Reaction Time -> Simulation Step ->
            Simulation Step.
        meso_num_of_threads: used with MESO experiments. The number of threads
            used in a meso simulation. On the Aimsun GUI, this can be set by the
            path Main -> Performance Settings -> Simulation Threads.
        num_of_paths_threads: The number of threads used in a route choice
            simulation. On the Aimsun GUI, this can be set by the
            path Main -> Performance Settings -> Route Choice Threads.
        reaction_at_stop: the reaction time at stop. On the Aimsun GUI, this
            can be set by the path Reaction Time -> Reaction Time Settings.
        reaction_at_traffic_light: the reaction time at traffic light, applied
            to the first vehicle stopping at the traffic light.
        reaction_time: the reaction time for meso experiments. On the Aimsun
            GUI, this can be set by the path Reaction Time -> Reaction Time
            Settings.
        reaction_time_type: the type of reaction time the simulation will
            use. If this is set to 0, then the reaction time is the same for all
            vehicles, equaling the simulation step time. If this is set to 1,
            then the reaction time is set for each vehicle type. On the Aimsun
            GUI, this can be set by the path Reaction Time -> Reaction Time
            Settings.
        warmup_demand: determines whether this is uses a warmup-demand
            object.
    SRC General Parameters Attributes:
        initial_shortest_paths_trees: used in SRC experiments. Describes
            the route choice on initial K-SPs. On the Aimsun GUI, this can be
            set by the path Dynamic Traffic Assignment -> Stochastic Route
            Choice -> Basic -> K-SP.
        max_routes: describes the maximum number of different paths that are
            used in the decision process to pick the next route.
    SRC Binomial Parameters Attributes:
        probability: used in Binomial SRC experiments. Describes the route
        choice's probability for picking the most recently calculated shortest
        paths.
    SRC Proportional Parameters Attributes:
        alfa: used with SRC Proportional experiments. Describes the route
            choice on alpha factor. On the Aimsun GUI, this can be set by the
            pathDynamic Traffic Assignment -> User-Defined Cost Weight.
    SRC Logit Parameters Attributes:
        low_variance_factor: used with SRC experiments. Describes the route
            choice on scale factor. On the Aimsun GUI, this can be set by the
            path Dynamic Traffic Assignment -> Stochastic Route Choice ->
            Parameters -> Scale.
    SRC C-Logit Parameters Attributes:
        beta: used with SRC C-Logit experiments. Describes the route
            choice on beta factor. On the Aimsun GUI, this can be set by the
            path Dynamic Traffic Assignment -> Stochastic Route Choice ->
            Parameters -> Beta.
        c_logit_past_cost_replication: used with SRC experiments. Describes the
            route choice on link costs replication.
        gamma: used in SRC C-Logit experiments. Describes the route
            choice on gamma factor. On the Aimsun GUI, this can be set by the
            path Dynamic Traffic Assignment -> Stochastic Route Choice ->
            Parameters -> Gamma.
        low_variance_factor: used with SRC experiments. Describes the route
            choice on scale factor. On the Aimsun GUI, this can be set by the
            path Dynamic Traffic Assignment -> Stochastic Route Choice ->
            Parameters -> Scale.
    SRC User-Defined Parameters Attributes:
        user_defined_cost_weigth: describes the route choice for
            user-defined cost weights. On the Aimsun GUI, this can be set by
            the path Dynamic Traffic Assignment -> User-Defined Cost Weight.
        user_function: describes the route choice for user functions.
    Overtaking Model Parameters:
        apply_non_lane_based_movement: a boolean that denotes whether this
            simulation should consider lateral non-lane-based vehicle
            movements. This effectively takes the width of each lane a new
            parameter as well as the maximum lateral speed a vehicle has in
            order to more accurately model realistic traffic conditions.
        apply_two_way_overtaking_model: a boolean denoting whether this
            experiment will use two-way two-lane lane changing.
        delay_between_simultaneous_overtaking: the time delay between
            simultaneous overtaking operations, if multiple are queued.
        delay_time_threshold: the minimum delay time induced by waiting in a
            queue that a vehicle will consider before attempting to overtake
            the queue.
        number_of_simultaneous_overtaking_allowed: the number of overtaking
            operations that can concurrently run within the modeling
            environment.
        overtaking_speed_magnification: the scale factor applied to the
            vehicle's current speed for it to begin overtaking the queue.
        rank_threshold: the maximum rank of a vehicle for it to consider
            overtaking the queue. The rank of a vehicle is its place in a queue
            that has formed due to slowing traffic.
        remaining_travel_time_threshold: the minimum amount of time to
            guarantee a vehicle will overtake the queue
        sensitivity_factor_reduce_car_following: a parameter used to define
            the estimated deceleration of a vehicle leader in a queue. If this
            value is less than 1, the overtaking vehicle underestimates the
            deceleration of the leader vehicle, thus acting more aggressive in
            overtaking. If this value is greater than 1, the overtaking vehicle
            overestimates the deceleration of the leader vehicle, thus acting
            less aggressive in overtaking.
        speed_difference_max_threshold: the maximum speed difference a vehicle
            must have with the vehicle immediately in front of itself for the
            vehicle to consider overtaking.
        speed_difference_min_threshold: the minimum speed difference a vehicle
            must have with the vehicle immediately in front of itself for the
            vehicle to consider overtaking.
        speed_difference_overtaking_threshold: the minimum speed difference
            that must be achieved before a vehicle can engage in overtaking the
            queue.
        two_lane_car_following_model: the model that will be used to describe
            two-lane car-following behavior. If set to ABSOLUTE, vehicles will
            speed up to their surroundings. If set to RELATIVE, fast vehicles
            will slow down relative to how many other slow vehicles are around
            themselves. If set to ADJACENT_PATHS, vehicles in separate sections
            but still adjacent lanes are able to merge.
    """
    # Scenario Data
    stochastic_route_choice_model: StochasticRouteChoiceModel
    dynamic_simulator_engine: DynamicSimulatorEngine
    engine_mode: DynamicSimulationEngineMode
    stopping_criteria_iterations: int
    stopping_criteria_rgap: float
    replications: List[AimsunReplication]
    # Scenario Parameters
    apply_twopas_slope_model: bool
    apply_two_lanes: bool
    capacity_weight: float
    car_following_consider_min_headway: int
    cycle_time: int
    dynamic: bool
    gamma: float
    initial_shortest_paths_trees: int
    intervals: int
    low_variance_factor: float
    max_assign_paths: int
    max_distance: int
    max_routes: int
    micro_activate_external_behavior_model: bool
    micro_max_speed_diff: int
    micro_max_speed_diff_ramp: int
    micro_num_of_threads: int
    micro_num_of_vehicles: int
    micro_queue_leaving_speed: int
    micro_queue_up_speed: int
    micro_sim_step: float
    meso_num_of_threads: int
    num_of_paths_threads: int
    probability: float
    reaction_at_stop: float
    reaction_at_traffic_light: float
    reaction_time: float
    user_defined_cost_weigth: float
    user_function: int
    warmup_demand: bool
    # Overtaking Model Parameters
    apply_non_lane_based_movement: bool
    apply_two_way_overtaking_model: bool
    delay_between_simultaneous_overtaking: int
    delay_time_threshold: int
    number_of_simultaneous_overtaking_allowed: int
    overtaking_speed_magnification: float
    rank_threshold: int
    sensitivity_factor_reduce_car_following: float
    speed_difference_max_threshold: int
    speed_difference_min_threshold: int
    speed_difference_overtaking_threshold: int
    two_lane_car_following_model: TwoLaneCarFollowingModel
    # Enum-based Scenario Parameters
    car_following_version: CarFollowingVersionEnum
    due_assignment_model: DynamicUserEquilibriumAssignmentModel
    reaction_time_type: ReactionTimeTypeEnum
    # SRC Parameters
    alfa: float
    beta: float
    c_logit_past_cost_replication: float
    # DUE Parameters
    due_experienced_costs: int

    def __init__(self, capacity_weight=1.0, dynamic=True, max_assign_paths=1,
                 max_routes=5, probability=1.0, user_defined_cost_weigth=1,
                 warmup_demand=True):
        """Create a new Microexpierment. The predefined attributes are presets
        from the Routing Calibration Process readme.
        """
        self.capacity_weight = capacity_weight
        self.dynamic = dynamic
        self.max_assign_paths = max_assign_paths
        self.max_routes = max_routes
        self.probability = probability
        self.user_defined_cost_weigth = user_defined_cost_weigth
        self.warmup_demand = warmup_demand
        self.replications = []

    def assert_experiment_well_formatted(self):
        """Checks whether the experiment associated with this object has the
        correct attributes initiated in order for the specified experiment to
        run.
        """
        verify_attributes(self, micro_experiment_attributes())
        if self.dynamic_simulator_engine == \
                DynamicSimulatorEngine.MICROSIMULATION:
            verify_attributes(
                self, micro_dynamic_simulator_engine_attributes())
            if self.apply_two_lanes:
                verify_attributes(
                    self, micro_dynamic_simulator_engine_attributes(
                        engine_parameters='apply_two_lanes'))
            if self.apply_two_way_overtaking_model:
                verify_attributes(
                    self, micro_dynamic_simulator_engine_attributes(
                        engine_parameters='apply_two_way_overtaking_model'))
            assert self.replications
            for replication in self.replications:
                verify_attributes(
                    replication, ['random_seed', 'results_to_generate'])
        elif self.dynamic_simulator_engine == \
                DynamicSimulatorEngine.MESOSIMULATION:
            raise NotImplementedError("Not implemented")
        elif self.dynamic_simulator_engine == \
                DynamicSimulatorEngine.HYBRID_SIMULATION:
            raise NotImplementedError("Not implemented")
        elif self.dynamic_simulator_engine == \
                DynamicSimulatorEngine.DYNAMIC_MACROSIMULATION:
            raise NotImplementedError("Not implemented")
        else:
            raise ValueError('Wrong value for dynamic_simulator_engine.')

        if (self.engine_mode
                == DynamicSimulationEngineMode.ITERATIVE_ASSIGNMENT):
            verify_attributes(self, micro_dynamic_simulator_engine_attributes(
                engine_mode='iterative_assignment'))
        elif (self.engine_mode
                == DynamicSimulationEngineMode.ONE_SHOT_ASSIGNMENT):
            verify_attributes(
                self, micro_dynamic_simulator_engine_attributes(
                    engine_parameters='one_shot_assignment'))
            if (self.stochastic_route_choice_model
                    == StochasticRouteChoiceModel.BINOMIAL):
                verify_attributes(
                    self, micro_dynamic_simulator_engine_attributes(
                        engine_parameters='one_shot_assignment',
                        route_choice_model='binomial'),
                    message='The Binomial model must have a "success" '
                            + 'probability parameter.')
            if (self.stochastic_route_choice_model
                    == StochasticRouteChoiceModel.PROPORTIONAL):
                verify_attributes(
                    self, micro_dynamic_simulator_engine_attributes(
                        engine_parameters='one_shot_assignment',
                        route_choice_model='proportional'),
                    message='The Proportional model must have a probability of '
                            + 'switching to a lower-cost path.')
            if (self.stochastic_route_choice_model
                    == StochasticRouteChoiceModel.LOGIT):
                verify_attributes(
                    self, micro_dynamic_simulator_engine_attributes(
                        engine_parameters='one_shot_assignment',
                        route_choice_model='logit'),
                    message='The Logit model must have a parameter that scales '
                            + 'the importance of u_k, which are lower-cost '
                            + 'paths.')
            if (self.stochastic_route_choice_model
                    == StochasticRouteChoiceModel.C_LOGIT):
                verify_attributes(
                    self, micro_dynamic_simulator_engine_attributes(
                        engine_parameters='one_shot_assignment',
                        route_choice_model='c_logit'))
        else:
            raise ValueError('Wrong engine_mode.')


class AimsunGenericScenario(aimsun_input_utils.AimsunObject):
    """The AimsunGenericScenario class holds the data needed to create a
    GKGenericScenario within Aimsun.
    Python object associated with the Aimsun GKGenericScenario.

    Attributes:
        begin_date: The start date (date time) of the experiment.
        database_info: A Python AimsunDataBaseInfo object that holds the data
            needed to link this scenario to an external database.
        experiment: A Python AimsunGenericExperiment object that holds the data
            for creating an experiment within Aimsun.
        master_control_plan_external_id: The External ID of a
            GKMasterControlPlan Aimsun object.
        real_dataset_external_id: The External ID of a GKRealDataSet Aimsun
            object.
        traffic_demand_external_id: The External ID of a GKTrafficDemand Aimsun
            object.
        traffic_strategy_external_ids: A List of External IDs for GKStrategy
            Aimsun objects.
    """
    begin_date: datetime.date
    database_info: AimsunDataBaseInfo
    experiment: AimsunGenericExperiment
    master_control_plan_external_id: aimsun_input_utils.ExternalId
    real_dataset_external_id: aimsun_input_utils.ExternalId
    traffic_demand_external_id: aimsun_input_utils.ExternalId
    traffic_strategy_external_ids: List[aimsun_input_utils.ExternalId]

    def __init__(self):
        self.begin_date = aimsun_input_utils.SCENARIO_DATE
        self.master_control_plan_external_id =\
            aimsun_input_utils.MASTER_CONTROL_PLAN_EXTERNAL_ID
        self.real_dataset_external_id =\
            aimsun_input_utils.REAL_DATA_SET_EXTERNAL_ID
        self.traffic_strategy_external_ids = [
            aimsun_input_utils.TRAFFIC_STRATEGY_EXTERNAL_ID]


class AimsunTrajectoryCondition:
    """AimsunTrajectoryCondition correspond to GKTrajectoryCondition.

    Attributes:
        destination_centroid_external_id: The External ID of a GKCentroid
            Aimsun object corresponding to the destination of a trajectory.
        origin_centroid_external_id: The External ID of a GKCentroid
            Aimsun object corresponding to the origin of a trajectory.
        percentage: The percentage of vehicles traveling between the origin
            and destination centroids for this trajectory.
    """
    destination_centroid_external_id: aimsun_input_utils.ExternalId
    origin_centroid_external_id: aimsun_input_utils.ExternalId
    percentage: float


class AimsunScenarioInputData:
    """The AimsunScenarioInputData class holds all the scenario input data,
    such as traffic demand, control plans, statistics, and public transport
    plans. This data will be imported into Aimsun later by accessing its
    attributes and assigning them to the relevant attributes within Aimsun.
    Python object associated with the Aimsun GKScenarioInputData.

    Attributes:
        detection_interval: The time interval used to gather detection data.
        global_trajectories_statistics: A boolean denoting whether global
            trajectory statistics will be saved or not. Global trajectories
            store origin and destination centroids for each vehicle. For public
            transport vehicles, the trajectory stores the sections where the
            vehicle entered and exited the network. For all vehicles, it stores
            the entrance and exit times in the network, travel time, and delay
            time for the whole trip.
        section_trajectories_statistics: A boolean denoting whether section
            trajectory statistics will be saved or not. Section trajectories
            stores the ID of each section that a vehicle has traveled through,
            as well as the vehicle's exit time from each section and the
            vehicle's travel time and delay time through each section. If true,
            then the MISECT table will be created in the output database.
        statistical_interval: The length of the time interval used to gather
            statistic data.
        trajectories_statistics: A boolean denoting whether trajectory
            statistics will be saved or not. Used in Micro simulations,
            detailed trajectories save the ID of each vehicle's current section
            or node, lane index, coordinates of the vehicle's front midpoint,
            current speed, current acceleration, and distance traveled since
            the vehicle first entered the network.
        trajectory_condition_list: A list of Python AimsunTrajectoryCondition
            objects.
    """
    detection_interval: datetime.timedelta
    global_trajectories_statistics: bool
    section_trajectories_statistics: bool
    statistical_interval: datetime.timedelta
    trajectories_statistics: bool
    trajectory_condition_list: List[AimsunTrajectoryCondition]


class AimsunScenario(AimsunGenericScenario):
    """The AimsunScenario class holds all the needed parameters to run a
    dynamic simulation. This simulation is defined either as an SRC (stochastic
    route choice) or a DUE (dynamic user-equilibrium). By utilizing the pickle
    module, we can import and export this Python object to save scenario data
    for more general use.
    Python object associated with the Aimsun GKScenario.

    Attributes:
        scenario_input_data: A Python AimsunScenarioInputData object.
    """
    scenario_input_data: AimsunScenarioInputData

    def __init__(self, filepath: str = ''):
        super().__init__()
        if filepath:
            self.__import_from_file(filepath)

    def export_to_file(self, filepath: str):
        """Function to export AimsunScenario object using pickle.

        Args:
            filepath: Location where this object should be exported to. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        # Check existence and validity of general attributes.
        if not hasattr(self, 'name'):
            raise ValueError("Name attribute does not exist.")
        if not isinstance(self.name, str):
            raise TypeError("Name is not type string.")
        if not hasattr(self, 'external_id'):
            raise ValueError("External ID attribute does not exist.")
        if not isinstance(self.external_id, str):
            raise TypeError("External Id is not type ExternalId.")
        if not hasattr(self, 'begin_date'):
            raise ValueError("Begin date attribute does not exist.")
        if not isinstance(self.begin_date, datetime.date):
            raise TypeError("Begin Date is not type date.")
        # Check existence and validity of database_info and its attributes.
        if not hasattr(self, 'database_info'):
            raise ValueError("Database info attribute does not exist.")
        if not isinstance(self.database_info, AimsunDataBaseInfo):
            raise TypeError("Database info is not an AimsunDataBaseInfo"
                            "object.")
        if not hasattr(self.database_info, 'use_project_db'):
            raise ValueError("Use project database attribute in the database "
                             "info object does not exist.")
        if not isinstance(self.database_info.use_project_db, bool):
            raise TypeError("Use project database attribute in the database "
                            "info object is not type boolean.")
        if not hasattr(self.database_info, 'automatic'):
            raise ValueError("Automatic attribute in the database "
                             "info object does not exist.")
        if not isinstance(self.database_info.automatic, bool):
            raise TypeError("Automatic attribute in the database "
                            "info object is not type boolean.")
        if not hasattr(self.database_info, 'automatically_created'):
            raise ValueError("Automatically created attribute in the database "
                             "info object does not exist.")
        if not isinstance(self.database_info.automatically_created, bool):
            raise TypeError("Automatically created attribute in the database "
                            "info object is not type boolean.")
        if not hasattr(self.database_info, 'database_driver_name'):
            raise ValueError("Database driver name attribute in the database "
                             "info object does not exist.")
        if not isinstance(self.database_info.database_driver_name, str):
            raise TypeError("Database driver attribute in the database "
                            "info object is not type string.")
        if not hasattr(self.database_info, 'database_path'):
            raise ValueError("Database path attribute in the database "
                             "info object does not exist.")
        if not isinstance(self.database_info.database_path, str):
            raise TypeError("Database path attribute in the database "
                            "info object is not type string.")
        # Check existence and validity of experiment and its attributes.
        if not hasattr(self, 'experiment'):
            raise ValueError("Experiment attribute does not exist.")
        if not isinstance(self.experiment, AimsunMicroExperiment):
            raise TypeError("Experiment is not type AimsunMicroExperiment.")
        # Check existence and validity of External ID attributes.
        if not hasattr(self, 'master_control_plan_external_id'):
            raise ValueError("Master control plan External ID attribute does "
                             "not exist.")
        if not isinstance(self.master_control_plan_external_id, str):
            raise TypeError("Master control plan External ID is not type "
                            "External ID.")
        if not hasattr(self, 'real_dataset_external_id'):
            raise ValueError("Real dataset External ID attribute does not "
                             "exist.")
        if not isinstance(self.real_dataset_external_id, str):
            raise TypeError("Real dataset External ID is not type "
                            "External ID.")
        if not hasattr(self, 'traffic_demand_external_id'):
            raise ValueError("Traffic demand External ID attribute does not "
                             "exist.")
        if not isinstance(self.traffic_demand_external_id, str):
            raise TypeError("Traffic demand External ID is not type "
                            "External ID.")
        if not hasattr(self, 'traffic_strategy_external_ids'):
            raise ValueError("Traffic Strategy External ID attribute does not "
                             "exist.")
        if not isinstance(self.traffic_strategy_external_ids, List):
            raise TypeError("Traffic Strategy External IDs is not a list.")
        for i, external_id in enumerate(self.traffic_strategy_external_ids):
            if not isinstance(external_id, str):
                raise TypeError(
                    f"Traffic Strategy External ID at index {i} in list "
                    "traffic_strategy_external_ids is not type External ID.")
        # Check existence and validity of scenario_input_data.
        if not hasattr(self, 'scenario_input_data'):
            raise ValueError("Scenario input data attribute does not exist.")
        if not isinstance(self.scenario_input_data, AimsunScenarioInputData):
            raise TypeError("Scenario input data is not an "
                            "AimsunScenarioInputData object.")
        if not hasattr(self.scenario_input_data, 'detection_interval'):
            raise ValueError(
                "Detection_interval attribute does not exist.")
        if not isinstance(self.scenario_input_data.detection_interval,
                          datetime.timedelta):
            raise TypeError(
                "Detection_interval is not type timedelta.")
        if not hasattr(self.scenario_input_data,
                       'global_trajectories_statistics'):
            raise ValueError(
                "Global_trajectories_statistics attribute does not exist.")
        if not isinstance(self.scenario_input_data.
                          global_trajectories_statistics, bool):
            raise TypeError(
                "Global_trajectories_statistics attribute is not type boolean.")
        if not hasattr(self.scenario_input_data,
                       'section_trajectories_statistics'):
            raise ValueError(
                "Section_trajectories_statistics attribute does not exist.")
        if not isinstance(self.scenario_input_data.
                          section_trajectories_statistics, bool):
            raise TypeError(
                "Section_trajectories_statistics attribute is not type "
                "boolean.")
        if not hasattr(self.scenario_input_data, 'statistical_interval'):
            raise ValueError("Statistical_interval attribute does not exist.")
        if not isinstance(self.scenario_input_data.statistical_interval,
                          datetime.timedelta):
            raise TypeError(
                "Statistical_interval attribute is not type timedelta.")
        if not hasattr(self.scenario_input_data, 'trajectories_statistics'):
            raise ValueError(
                "Trajectories_statistics attribute does not exist.")
        if not isinstance(self.scenario_input_data.trajectories_statistics,
                          bool):
            raise TypeError(
                "Trajectories_statistics attribute is not type boolean.")
        if not hasattr(self.scenario_input_data, 'trajectory_condition_list'):
            raise ValueError(
                "Trajectory_condition_list attribute does not exist.")
        if not isinstance(self.scenario_input_data.trajectory_condition_list,
                          List):
            raise TypeError(
                "Trajectory_condition_list attribute is not a list.")
        for k, trajectory_condition in enumerate(
                self.scenario_input_data.trajectory_condition_list):
            if not isinstance(trajectory_condition, AimsunTrajectoryCondition):
                raise TypeError(
                    f"Object at index {k} in list trajectory_condition_list is "
                    "not an AimsunTrajectoryCondition object.")
            if not hasattr(trajectory_condition,
                           'destination_centroid_external_id'):
                raise ValueError(
                    f"Object at index {k} in list trajectory_condition_list; "
                    "attribute destination_centroid_external_id does not "
                    "exist.")
            if not isinstance(trajectory_condition.
                              destination_centroid_external_id, str):
                raise TypeError(
                    f"Object at index {k} in list "
                    "trajectory_condition_list for object "
                    f"{trajectory_condition}; attribute "
                    "destination_centroid_external_id is not type "
                    "External ID.")
            if not hasattr(trajectory_condition,
                           'origin_centroid_external_id'):
                raise ValueError(
                    f"Object at index {k} in list "
                    "trajectory_condition_list; attribute "
                    "origin_centroid_external_id does not exist.")
            if not isinstance(trajectory_condition.
                              origin_centroid_external_id, str):
                raise TypeError(
                    f"Object at index {k} in list "
                    "trajectory_condition_list for object "
                    f"{trajectory_condition}; attribute "
                    "origin_centroid_external_id is not type "
                    "External ID.")
            if not hasattr(trajectory_condition, 'percentage'):
                raise ValueError(
                    f"Object at index {k} in list "
                    "trajectory_condition_list; attribute "
                    "percentage does not exist.")
            if not isinstance(trajectory_condition.percentage, float):
                raise TypeError(
                    f"Object at index {k} in list "
                    "trajectory_condition_list for object "
                    f"{trajectory_condition}; attribute "
                    "percentage is not type float.")
        with open(filepath, 'wb') as file:
            pickle.dump([self.name, self.external_id, self.begin_date,
                         self.database_info, self.experiment,
                         self.master_control_plan_external_id,
                         self.real_dataset_external_id,
                         self.traffic_demand_external_id,
                         self.traffic_strategy_external_ids,
                         self.scenario_input_data], file)

    def __import_from_file(self, filepath: str):
        """Function to import AimsunScenario object using pickle.

        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, 'rb') as file:
            att_list = pickle.load(file)
            imported_name = att_list[0]
            imported_external_id = att_list[1]
            imported_begin_date = att_list[2]
            imported_database_info = att_list[3]
            imported_experiment = att_list[4]
            imported_master_control_plan_external_id = att_list[5]
            imported_real_dataset_external_id = att_list[6]
            imported_traffic_demand_external_id = att_list[7]
            imported_traffic_strategy_external_ids = att_list[8]
            imported_scenario_input_data = att_list[9]
        if not isinstance(imported_name, str):
            raise TypeError("Imported Name is not type string.")
        if not isinstance(imported_external_id, str):
            raise TypeError("Imported External Id is not type ExternalId.")
        if not isinstance(imported_begin_date, datetime.date):
            raise TypeError("Imported Begin Date is not type date.")
        if not isinstance(imported_database_info, AimsunDataBaseInfo):
            raise TypeError("Imported Database info is not an "
                            "AimsunDataBaseInfo object.")
        if not isinstance(imported_experiment, AimsunMicroExperiment):
            raise TypeError("Imported Experiment is not type "
                            "AimsunMicroExperiment.")
        if not isinstance(imported_master_control_plan_external_id, str):
            raise TypeError("Imported Master control plan External ID is not "
                            "type External ID.")
        if not isinstance(imported_real_dataset_external_id, str):
            raise TypeError("Imported Real dataset External ID is not type "
                            "External ID.")
        if not isinstance(imported_traffic_demand_external_id, str):
            raise TypeError("Imported Traffic demand External ID is not type "
                            "External ID.")
        if not isinstance(imported_traffic_strategy_external_ids, List):
            raise TypeError("Imported Traffic Strategy External IDs is not a "
                            "list.")
        for i, external_id in enumerate(imported_traffic_strategy_external_ids):
            if not isinstance(external_id, str):
                raise TypeError(
                    f"Imported Traffic Strategy External ID at index {i} in "
                    "list traffic_strategy_external_ids is not type External "
                    "ID.")
        if not isinstance(imported_scenario_input_data,
                          AimsunScenarioInputData):
            raise TypeError(
                "Imported Scenario Input Data is not an "
                "AimsunScenarioInputData object.")
        self.name = imported_name
        self.external_id = imported_external_id
        self.begin_date = imported_begin_date
        self.database_info = imported_database_info
        self.experiment = imported_experiment
        self.master_control_plan_external_id = (
            imported_master_control_plan_external_id)
        self.real_dataset_external_id = imported_real_dataset_external_id
        self.traffic_demand_external_id = (
            imported_traffic_demand_external_id)
        self.traffic_strategy_external_ids = (
            imported_traffic_strategy_external_ids)
        self.scenario_input_data = imported_scenario_input_data


class AimsunPathAssignment:
    """The AimsunPathAssignment class holds a filename and file directory
    location that can be accessed by an Aimsun object.
    Python object associated with the Aimsun GKPathAssignment.

    Attributes:
        disaggregate_super_node: A boolean denoting whether disaggregate super
            nodes will be used or not. Disaggregate super nodes are super nodes
            that are broken down into parts. A super node is a group of nodes
            gathered together to create a more complicated intersection. They
            are initialized by default to False.
        filename: The filename that this path assignment object is pointing to.
        folder_path: The directory path that needs to be taken to find the file
            with the saved filename.
    """
    disaggregate_super_node: bool
    filename: str
    folder_path: str


class AimsunMacroScenarioOutputData:
    """The AimsunMacroScenarioOutputData class holds all the parameters for
    statistic collection during an experiment. Using those parameters, the
    object saves statistic data for static assignment scenarios. The output
    data statistics can then be retrieved later.
    Python object associated with the Aimsun MacroScenarioOutputData.

    Attributes:
        activate_path_statistics: A boolean denoting whether the path
            statistics will be gathered or not. Path statistics are located
            within the Paths tab in the Outputs to Generate tab. Path
            statistics are data generated and calculated by the Dynamic Traffic
            Assignment algorithm.
        convergence_statistics: A boolean denoting whether the algorithm
            convergence data will be gathered or not. Convergence statistics
            are located within the Convergence tab in the Static Assignment
            Results tab. Convergence statistics are the achieved relative gap
            and lambda (step length) for each iteration.
        generate_skim: A boolean denoting whether the skim matrices that are
            generated during an experiment will be saved or not. Skim matrices
            contain the costs between each OD pair, these costs being the cost
            to choose one route over another. As these are outputs of an
            assignment experiment, they are updated over time with better
            estimates using the multiple iterations to refine the data.
        group_statistics: A boolean denoting whether the data related to groups
            will be calculated or not. Grouping statistics are statistics
            related to grouping objects. A grouping object is a set of objects
            of the same time used to automatically obtain the mean or sum of
            attributes in the group.
        store_statistics: A boolean denoting whether the data related to
            sections and turns (MASECT and MATURN) will be stored or not.
            Section statistics are the data generated in Aimsun when a vehicle
            leaves a section. This includes data for the count, delay time,
            density, flow, harmonic speed, input count, input flow, max queue,
            max virtual queue, mean queue, mean virtual queue, number of lane
            changes, number of stops, speed, stop time, total number of lane
            changes, total travel time, total distance traveled, travel time,
            V/C ratio, virtual queue, and waiting time in virtual queue.
            Turn statistics provide measurements of vehicles that have crossed
            over a turn. As road sections can have more than one downstream
            turn, not all of the statistics are available for each turn. The
            data that is generated includes count, delay time, flow, harmonic
            speed, input count, input flow, lost vehicles, max queue, mean
            queue, missed vehicles, number of lane changes, number of stops,
            speed, stop time, total number of lane changes, total travel time,
            total distance traveled, travel time, and waiting time in virtual
            queue.
    """
    activate_path_statistics: bool
    convergence_statistics: bool
    generate_skim: bool
    group_statistics: bool
    store_statistics: bool

    def __init__(self):
        self.store_statistics = True
        self.generate_skim = False
        self.group_statistics = False
        self.convergence_statistics = False
        self.activate_path_statistics = False


class AimsunStaticMacroScenario(AimsunGenericScenario):
    """The AimsunStaticMacroScenario class holds the data needed to create a
    MacroScenario object within Aimsun. It holds the output parameters of the
    scenario as well as a path to the input data.
    Python object associated with the Aimsun MacroScenario.

    Attributes:
        input_path_assignment: A Python AimsunPathAssignment object.
        output_data: A Python AimsunMacroScenarioOutputData object.
    """
    depature_time: datetime.time
    input_path_assignment: AimsunPathAssignment
    output_data: AimsunMacroScenarioOutputData


class AimsunStaticMacroScenarios:
    """Aggregate class containing a list of AimsunStaticMacroScenario objects.

    The AimsunStaticMacroScenarios class stores a list of
    AimsunStaticMacroScenario objects to simplify storage and access of
    AimsunStaticMacroScenario objects. By utilizing the pickle module, we can
    save one object instead of a group of AimsunStaticMacroScenario objects.

    Attributes:
        aimsun_static_macroscenarios: A list of Python
            AimsunStaticMacroScenario objects.
    """
    aimsun_static_macroscenarios: List[AimsunStaticMacroScenario]

    def __init__(self, filepath: str = ''):
        if filepath:
            self.__import_from_file(filepath)

    def export_to_file(self, filepath: str):
        """Function to import AimsunStaticMacroScenarios object using pickle.

        Args:
            filepath: Location where this object should be exported to. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(self.aimsun_static_macroscenarios, file)

    def __import_from_file(self, filepath: str):
        """Function to import AimsunStaticMacroScenarios object using pickle.

        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, 'rb') as file:
            self.aimsun_static_macroscenarios = pickle.load(file)
