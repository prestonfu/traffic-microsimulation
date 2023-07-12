"""All classes that are used as Aimsun input.

This utils file sets up classes for different types of objects Aimsun will use.
Aggregate classes such as CentroidConfiguration or OriginDestinationMatrices
have import/export methods that utilize the pickle module to save objects to
files. Each import/export method includes rigorous type-checking; export methods
make sure each attribute is the correct type before saving the object. Since the
export method would check every subpart of an object for rigor, we can import
the correct object by checking only the object aggregate type, as well as the
object type that is listed within the aggregation data structure.

Testing is done through the use of __eq__ methods added to each object. By
instantiating a few instances of each class, we can compare their outputs to
check whether object creation, import/export, and equality methods themselves
work to our understanding. These tests are outlined within the file
aimsun_input_utils_test.py.

Global variables:
    CENTROID_CONFIG_EXTERNAL_ID: External ID of the centroid configuration.
    CSV_SEPARATOR: Character that seperates data in a csv file.
    DATABASE_DRIVER_NAME: Name of the Aimsun simulation database driver.
    MASTER_CONTROL_PLAN_EXTERNAL_ID: External ID of the master control plan.
    NETWORK_LAYER_NAME: Name of the Aimsun road section network layer.
    OSM_LAYER_NAME: Name of the OpenStreetMap layer.
    REAL_DATA_SET_EXTERNAL_ID: External ID of the real data set.
    SCENARIO_DATE: Default date for the Aimsun micro/macrosimulation scenario.
    TRAFFIC_STRATEGY_EXTERNAL_ID: External ID of the traffic strategy.

Enum classes:
    CentroidType: Type of centroid. Classified INTERNAL if centroid is in the
        area of study. Else, classified EXTERNAL.
    MeteringType: Type of metering.
    ScenarioChangeType: Type of Aimsun micro/macrosimulation scenario change.
    VehicleTypeName: Type of vehicle. Classified RESIDENT if the origin and
        destination of the vehicle is in the area of study. Else, TRAVELER.
    ControlJunctionType: Type of control junction.
    ControlMeteringType: Type of control metering.
    VehicleTypeInternalId: Internal ID used within Aimsun for vehicle types.
    ControlPhaseRecall: Type of control phase recall.
    FlashingType: Type of flashing.

Classes:
    AimsunObject: Parent class for common attributes among all Aimsun objects.
    CentroidConnection: Data class containing details about a single centroid
        such as connected road IDs, location, and type.
    CentroidConfiguration: Aggregate class containing a list of
        CentroidConnection objects.
    OriginDestinationTripsCount: Data class that contains traffic demand between
        an origin centroid and destination centroid.
    OriginDestinationMatrix: Aggregate class in matrix-form containing
        OriginDestinationTripsCount objects for all origin-destination centroid
        pairs.
    OriginDestinationMatrices: Aggregate class containing a list of
        OriginDestinationMatrix objects for each time interval.
    SectionSpeedLimitAndCapacity: Data class containing details about a single
        road section such as speed limit, internal ID, and vehicle capacity.
    SectionSpeedLimitsAndCapacities: Aggregate class containing a list of
        SectionSpeedLimitAndCapacity objects for all roads in the area of study.
    AimsunGeoObject: Data class corresponding to Aimsun geometry object.
    AimsunSectionObject: Data class corresponding to Aimsun GKSectionObject.
    Detector: Data class corresponding to Aimsun GKDetector.
    Metering: Data class corresponding to Aimsun GKMetering.
    Detectors: Aggregate class containing a list of all Detector objects for the
        area of study.
    FlowRealData: Data class for output flow data from one detector.
    AimsunFlowRealDataSet: Aggregate class for FlowRealData from multiple
        detectors in the area of study.
    ControlDetector: Data class corresponding to Aimsun GKControlDetector.
    ControlMetering: Data class corresponding to Aimsun GKControlMetering.
    ControlPhaseSignal: Data class corresponding to Aimsun GKControlPhaseSignal.
    ControlPhase: Parent class containing common attributes for Aimsun
        GKControlPhase.
    NonActuatedControlPhase: Data class for attributes specific to non-actuated
        Aimsun GKControlPhase objects.
    ActuatedControlPhase: Data class for attributes specific to actuated Aimsun
        GKControlPhase objects.
    ControlJunction: Parent class containing common attributes for Aimsun
        GKControlJunction.
    NonActuatedControlJunction: Data class for attributes specific to
        non-actuated Aimsun GKControlJunction objects.
    ActuatedControlJunction: Data class for attributes specific to actuated
        Aimsun GKControlJunction objects.
    ControlPlan: Data class corresponding to Aimsun GKControlPlan.
    MasterControlPlanItem: Data class corresponding to Aimsun
        GKScheduleMasterControlPlanItem.
    MasterControlPlan: Data class corresponding to Aimsun GKMasterControlPlan.
    TurningClosingChange: Data class corresponding to Aimsun
        GKTurningClosingChange.
    TrafficPolicy: Data class corresponding to Aimsun GKPolicy.
    TrafficManagementStrategy: Data class corresponding to Aimsun GKStrategy.
"""

from __future__ import annotations

import csv
import datetime
import enum
from os import path
import pickle
from typing import NewType
import warnings

from utils.verification_utils import verify_filepath

ExternalId = NewType('ExternalId', str)
InternalId = NewType('InternalId', int)


CENTROID_CONFIG_EXTERNAL_ID = "centroid_configuration"
CSV_SEPARATOR = ','
DATABASE_DRIVER_NAME = "QSQLITE"
MASTER_CONTROL_PLAN_EXTERNAL_ID = "master_control_plan"
NETWORK_LAYER_NAME = "Network"
OSM_LAYER_NAME = "OpenStreetMap"
REAL_DATA_SET_EXTERNAL_ID = "real_dataset"
SCENARIO_DATE = datetime.date(2019, 1, 1)
TRAFFIC_STRATEGY_EXTERNAL_ID = "Current Fremont Traffic Calming Strategy"


class CentroidType(enum.Enum):
    """Enumeration class to differentiate centroid types.

    The CentroidType class is implemented in order to make further scripts
    smoother in terms of juggling data types. Here, the CentroidType is defined
    as a child class of Enum, which makes it more intuitive to see what an
    attribute is referencing.

    INTERNAL: A centroid that corresponds to an interior section of the city
        that is being examined. Currently, that city is Fremont.
    EXTERNAL: A centroid that corresponds to surrounding regions around the city
        that is being examined.

    Example with CentroidType:
        c_con = CentroidConnection()
        c_con.centroid_type = CentroidType.INTERNAL # clear, with its own type.
    Example without CentroidType:
        c_con = CentroidConnection()
        c_con.centroid_type = 'Internal' # more vague, and is type str.
    """
    INTERNAL = 'Internal'
    EXTERNAL = 'External'


class MeteringType(enum.IntEnum):
    """Enumeration class to differentiate metering types.

    The MeteringType class is implemented in order to make further scripts
    smoother in terms of juggling data types. Here, the MeteringType is defined
    as a child class of Enum, which makes it more intuitive to see what an
    attribute is referencing. Each enumeration determines the current state of
    a meter.

    GREEN_TIME: Each cycle of the meter turns on green for a set amount of time.
    FLOW: Each cycle of the meter lets in a set number of vehicles.
    DELAY: Each cycle of the meter has a yellow light signaling a delay between
        cycles.
    FLOW_ALINEA: Similar to FLOW, but with an implementation of the ALINEA
        ramp control algorithm.
    GREEN_TIME_BY_LANE: Similar to GREEN_TIME, but multiple lanes are in the
        ramp. Thus, multiple GREEN_TIME meters run on the same ramp, straddling
        which lanes allow cars to pass.
    """
    GREEN_TIME = 0
    FLOW = 1
    DELAY = 2
    FLOW_ALINEA = 3
    GREEN_TIME_BY_LANE = 4


class ScenarioChangeType(enum.IntEnum):
    """Enumeration class to differentiate the types of changes to an
    intersection.
    """
    LANE_CLOSING = 0
    SPEED_CHANGE = 1
    FORCE_TURNING = 2
    DESTINATION_CHANGE = 3
    INCIDENT = 4
    DEMAND_MODIFICATION = 5
    TURNING_RESTRICTION = 6
    CONTROL_PLAN_CHANGE = 7
    PERIODIC_INCIDENT = 8
    SECTION_BEHAVIOR_PARAM_CHANGE = 9
    TURNING_BEHAVIOR_PARAM_CHANGE = 10
    DISABLE_RESERVED = 11
    ROAD_PRICING = 12
    ROAD_PRICING_CHANGE = 13
    METERING_ON_RAMP_CHANGE = 14
    INTERSECTION_PLAN_CHANGE = 15
    FORCE_ENROUTE_ASSIGNMENT = 16
    TURNING_COOPERATION = 17
    PARK_AND_RIDE_CHAGE = 18
    NONE = 19


class VehicleTypeName(str, enum.Enum):
    """Enumeration class to differentiate vehicle types.

    The VehicleTypeName class is implemented in order to make further scripts
    smoother in terms of juggling data types. Here, the VehicleTypeName is
    defined as a child class of Enum, which makes it more intuitive to see what
    an attribute is referencing.

    RESIDENT: An object with the RESIDENT VehicleTypeName is a set of data that
        corresponds to traffic data from local residents of the city that is
        examined.
    TRAVELER: An object with TRAVELER VehicleTypeName is a set of data that
        corresponds to traffic data from commuters traveling through a city that
        is examined.

    Example with VehicleTypeName:
        odm = OriginDestinationMatrices()
        odm.vehicle_type = VehicleTypeName.RESIDENT # clear, with its own type.
    Example without VehicleTypeName:
        odm = OriginDestinationMatrices()
        odm.vehicle_type = 'Resident' # more vague, and is type str.
    """
    RESIDENT = 'Resident'
    TRAVELER = 'Traveler'


class ControlJunctionType(enum.IntEnum):
    """Enumeration class to specify control junction type."""
    UNSPECIFIED = 0
    UNCONTROLLED = 1
    FIXED_CONTROL = 2
    EXTERNAL = 3
    ACTUATED = 4


class ControlMeteringType(enum.IntEnum):
    """Enumeration class to specify control metering type."""
    UNSPECIFIED = 0
    UNCONTROLLED = 1
    FIXED_CONTROL = 2
    EXTERNAL = 3


class VehicleTypeInternalId(enum.IntEnum):
    """Enumeration class to specify vehicle type IDs."""
    # This may have to be changed in the future.
    RESIDENT_TYPE_INTERNAL_ID = 151590241
    TRAVELLER_TYPE_INTERNAL_ID = 151590242


class ControlPhaseRecall(enum.IntEnum):
    """Enumeration class to specify control phase recall."""
    NO = 0
    MIN = 1
    MAX = 2
    COORD = 3


class FlashingType(enum.IntEnum):
    """Enumeration class to specify flashing type."""
    NO = 0
    FLASHING_GREEN = 1
    FLASHING_YELLOW = 2
    FLASHING_RED = 3


def od_matrix_name_generation(
    time: datetime.time, vehicle_type: VehicleTypeName
) -> ExternalId:
    """Generates name for origin-destination matrix.

    Args:
        time: Time when the origin-destination flow was collected.
        vehicle_type: Type of vehicle. Can be INTERNAL or EXTERNAL.
    Returns:
        od_matrix_name: Name of the origin-destination matrix defined by the
            input parameters.
    """
    return f"{vehicle_type}_{time.strftime('%H_%M')}"


class AimsunObject:
    """The main class that is called whenever an Aimsun object is created. It
    stores a name, Internal ID, and External ID to distinguish every object
    created from other objects. Internal IDs are unique, while External IDs are
    not. However, both External IDs and the name are user-generated, which can
    be helpful when looking for context-specific objects.

    This class corresponds to the GKObject object in Aimsun.

    Attributes:
        name: A user-generated name for the object.
        external_id: A user-generated ID for the object.
        internal_id: The Internal ID assigned by Aimsun.
    """
    name: str
    external_id: ExternalId
    internal_id: InternalId

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "{Aimsun Object: "
        if hasattr(self, 'name'):
            string += f"Name: {self.name}, "
        if hasattr(self, 'external_id'):
            string += f"External ID: {self.external_id}, "
        if hasattr(self, 'internal_id'):
            string += f"Internal ID: {self.internal_id}, "
        return string[:-2] + "}"

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'name'):
            if not isinstance(self.name, str):
                return False
        if hasattr(self, 'external_id'):
            if not isinstance(self.external_id, str):
                return False
        if hasattr(self, 'internal_id'):
            if not isinstance(self.internal_id, int):
                return False
        return True


class CentroidConnection(AimsunObject):
    """CentroidConnection class to create centroid objects.

    The CentroidConnection class incorporates the data similar to a GKCentroid
    object listed in the Aimsun documentation.

    Attributes:
        center_latitude_epsg_32610: Stores the latitude value of the centroid.
        center_longitude_epsg_32610: Stored the longitude value of the centroid.
        centroid_type: Stores whether the centroid is an internal or external
            centroid.
        from_section_internal_ids: List of other InternalIds that have a
            connection leading to this centroid.
        to_section_internal_ids: List of other InternalIds that have a
            connection leading away from this centroid.
    """
    center_latitude_epsg_32610: float
    center_longitude_epsg_32610: float
    centroid_type: CentroidType
    from_section_internal_ids: list[InternalId]
    to_section_internal_ids: list[InternalId]

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        return (
            f"{super().__str__()}, ({self.center_longitude_epsg_32610},"
            f" {self.center_latitude_epsg_32610}), From: ["
            ",".join(map(str, self.from_section_internal_ids)) + "], To: ["
            ",".join(map(str, self.to_section_internal_ids)) + "], "
            f"CentroidType: {self.centroid_type}")


class CentroidConfiguration(AimsunObject):
    """Aggregate class containing a list of CentroidConnection objects.

    The CentroidConfiguration class stores a list of CentroidConnection objects
    to simplify storage and access of CentroidConnection objects. By utilizing
    the pickle module, we can save one object instead of a group of
    CentroidConnection objects. This will make file storage simpler and data
    access more general in use.

    Attributes:
        centroid_connection_list: A list of CentroidConnection objects.
        external_id: inherited from AimsunObject. Default value is
            CENTROID_CONFIG_EXTERNAL_ID. External id is used to get this
            configuration when creating OD demand matrices.
    """
    centroid_connection_list: list[CentroidConnection]

    def __init__(self, filepath: str = '',
                 external_id: ExternalId = CENTROID_CONFIG_EXTERNAL_ID):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.external_id = external_id

    def export_to_file(self, filepath: str):
        """Function to export CentroidConfiguration object using pickle.

        Each if not/raise block is used to ensure the file we export using this
        function is a stable and complete CentroidConfiguration object. The
        blocks check each attribute of every object within the class. For
        this class, it checks for a valid name and for all attributes for
        each CentroidConnection have been filled out.

        Args:
            filepath: Location where this object should be exported to. The path
                must point to a '.pkl' file, otherwise the code will throw an
                error.
        """
        verify_filepath(filepath, 'pkl')
        if not isinstance(self.external_id, str):
            raise TypeError(
                "Attribute external_id is not type "
                "ExternalId.")
        if not hasattr(self, 'external_id'):
            raise ValueError("External_id does not exist.")
        if not self.external_id:
            raise ValueError("External_id does not exist.")
        if not isinstance(self.centroid_connection_list, list):
            raise TypeError(
                "Attribute centroid_connection_list is not type List.")
        for i, c_con in enumerate(self.centroid_connection_list):
            if not isinstance(c_con, CentroidConnection):
                raise TypeError(
                    f"Object at index {i} in list centroid_connection_list is "
                    "not a CentroidConnection object.")
            if not hasattr(c_con, 'external_id'):
                raise TypeError(
                    f"Object at index {i} in list centroid_connection_list; "
                    "attribute external_id does not exist.")
            if not isinstance(c_con.external_id, str):
                raise TypeError(
                    f"Object at index {i} in list centroid_connection_list; "
                    "attribute external_id is not type ExternalId.")
            if not isinstance(c_con.centroid_type, CentroidType):
                raise TypeError(
                    f"Object at index {i} in list centroid_connection_list; "
                    "attribute centroid_type is not type CentroidType")
            if not isinstance(c_con.center_latitude_epsg_32610, float):
                raise TypeError(
                    f"Object at index {i} in list centroid_connection_list; "
                    "attribute center_latitude_epsg_32610 is not type float.")
            if not isinstance(c_con.center_longitude_epsg_32610, float):
                raise TypeError(
                    f"Object at index {i} in list centroid_connection_list; "
                    "attribute center_longitude_epsg_32610 is not type float.")
            if not isinstance(c_con.from_section_internal_ids, list):
                raise TypeError(
                    "Attribute from_section_internal_ids is not type List.")
            for j, fsii in enumerate(c_con.from_section_internal_ids):
                if not isinstance(fsii, int):
                    raise TypeError(
                        f"Item at index {j} in list from_section_internal_ids "
                        "is not type InternalId.")
            if not isinstance(c_con.to_section_internal_ids, list):
                raise TypeError("to_section_internal_ids is not type List.")
            for k, tsii in enumerate(c_con.to_section_internal_ids):
                if not isinstance(tsii, int):
                    raise TypeError(
                        f"Item at index {k} in list from_section_internal_ids "
                        "is not type InternalId.")
        with open(filepath, 'wb') as file:
            pickle.dump(self.external_id, file)
            pickle.dump(self.centroid_connection_list, file)

    def __import_from_file(self, filepath: str):
        """Function to import CentroidConfiguration object using pickle.

        As objects should only be created and exported through this script, we
        only need to type check the basics of each imported file: valid
        filepath, file extension, and correct attribute types.
        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, "rb") as file:
            imported_ext_id = pickle.load(file)
            imported_connection_list = pickle.load(file)
            if not isinstance(imported_ext_id, str):
                raise TypeError("imported_ext_id is not type ExternalId.")
            if not isinstance(imported_connection_list, list):
                raise TypeError("imported_connection_list is not type List.")
            for i, centroid in enumerate(imported_connection_list):
                if not isinstance(centroid, CentroidConnection):
                    raise TypeError(
                        f"Object at index {i} in list imported_connection_list "
                        "is not a CentroidConnection object.")
            self.external_id = imported_ext_id
            self.centroid_connection_list = imported_connection_list

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Centroid Connections:\n"
        if hasattr(self, 'external_id'):
            string += f"External id: {self.external_id}\n"
        if hasattr(self, 'centroid_connection_list'):
            string += 'Connections:\n'.join(
                map(str, self.centroid_connection_list))
        return string


class OriginDestinationTripsCount:
    """Data class to contain matrices that detail the Origin/Destination
    Centroid ID pairs and the number of trips within a certain time interval,
    which is defined in the OriginDestinationMatrix class as begin_time_interval
    and end_time_interval.

    Attributes:
        destination_centroid_external_id: Destination centroid marked by
                                          External ID.
        num_trips: Number of measured counts within the given time frame.
        origin_centroid_id: Origin centroid marked by External ID.
    """
    destination_centroid_external_id: ExternalId
    num_trips: float
    origin_centroid_external_id: ExternalId


class OriginDestinationMatrix(AimsunObject):
    """Data class to relate time intervals, locations, and demand together in
    one object. This models origin and destination centroids as well as time
    frames between them and the number of trips that were measured. This OD pair
    is denoted by a lowercase i through the Unified Notation document, and
    corresponds to GKODMatrix within Aimsun.

    The data packaged within this class will be unpacked in the script 'D2 -
    Create OD demand.py' where it is added to the Aimsun model.

    Attributes:
        begin_time_interval: Start time for measuring demand.
        od_trips_count: List of matrices that detail the Origin/Destination
                        Centroid ID pairs and the number of trips within the
                        given time interval between begin_time_interval and
                        end_time_interval.
        end_time_interval: End time for measuring demand.
        vehicle_type: Stores whether the data relates to residential or
            traveling vehicles.
    """
    begin_time_interval: datetime.time
    end_time_interval: datetime.time
    od_trips_count: list[OriginDestinationTripsCount]
    vehicle_type: VehicleTypeName


class OriginDestinationMatrices:
    """Aggregate class containing a list of OriginDestinationMatrix objects.

    The OriginDestinationMatrices class stores a list of
    OriginDestinationMatrix objects to simplify storage and access of
    OriginDestinationMatrix objects. By utilizing the pickle module, we can save
    one object instead of a group of OriginDestinationMatrix objects. This will
    make file storage simpler and data access more general in use.

    Attributes:
        centroid_configuration_external_id: external id of the centroid
            configuration corresponding the OriginDestinationMatrices.
        od_matrices: A list of OriginDestinationMatrix objects.
    """
    centroid_configuration_external_id: ExternalId
    od_matrices: list[OriginDestinationMatrix]

    def __init__(
        self, filepath: str = '', external_id: str = CENTROID_CONFIG_EXTERNAL_ID
    ):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.centroid_configuration_external_id = external_id

    def export_to_file(self, filepath: str):
        """Function to export OriginDestinationMatricies object using pickle.

        Each if not/raise block is used to ensure the file we export using this
        function is a stable and complete OriginDestinationMatricies object. The
        blocks check each attribute of every object within the class. For
        this class, it checks for all attributes in each OriginDestinationMatrix
        object have been filled correctly and for a valid vehicle_type.

        Args:
            filepath: Location where this object should be exported to. The path
                must point to a '.pkl' file, otherwise the code will throw an
                error.
        """
        verify_filepath(filepath, 'pkl')
        if not isinstance(self.centroid_configuration_external_id, str):
            raise TypeError("Attribute centroid_configuration_external_id is "
                            + "not type ExternalId.")
        if not isinstance(self.od_matrices, list):
            raise TypeError("Attribute od_matrices is not type List.")
        for i, odd in enumerate(self.od_matrices):
            if not isinstance(odd, OriginDestinationMatrix):
                raise TypeError(
                    f"Object at index {i} in list od_matrices is not "
                    "an OriginDestinationMatrix object.")
            if not isinstance(odd.begin_time_interval, datetime.time):
                raise TypeError(
                    f"Object at index {i} in list od_matrices; "
                    "attribute begin_time_interval is not type datetime.time.")
            if not isinstance(odd.end_time_interval, datetime.time):
                raise TypeError(
                    f"Object at index {i} in list od_matrices; "
                    "attribute end_time_interval is not type datetime.time.")
            if not isinstance(odd.od_trips_count, list):
                raise TypeError(
                    f"Object at index {i} in list od_matrices; "
                    "od_trips_count is not attribute type list.")
            for j, od_trip in enumerate(odd.od_trips_count):
                if not isinstance(od_trip, OriginDestinationTripsCount):
                    raise TypeError(
                        f"Object at index {i} in list od_trips_count; "
                        f"od_trips_count at index {j} is not attribute type "
                        "OriginDestinationTripsCount.")
            if not isinstance(odd.vehicle_type, str):
                raise TypeError(
                    f"Object at index {i} in list od_matrices; "
                    "attribute vehicle_type is not type VehicleTypeName.")
        with open(filepath, 'wb') as file:
            pickle.dump(self.od_matrices, file)
            pickle.dump(self.centroid_configuration_external_id, file)

    def __import_from_file(self, filepath: str):
        """Function to import OriginDestinationMatricies object using pickle.

        As objects should only be created and exported through this script, we
        only need to type check the basics of each imported file: valid
        filepath, file extension, and correct attribute types.

        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, "rb") as file:
            imported_od_matrices = pickle.load(file)
            imported_external_id = pickle.load(file)
            if not isinstance(imported_od_matrices, list):
                raise TypeError("imported_od_matrices is not type List.")
            for i, od_demand_obj in enumerate(imported_od_matrices):
                if not isinstance(od_demand_obj, OriginDestinationMatrix):
                    raise TypeError(
                        f"Object at index {i} in list imported_od_matrices is "
                        "not an OriginDestinationMatrix object.")
            if not isinstance(imported_external_id, str):
                raise TypeError("imported_external_id is not type List.")
            if not imported_external_id:
                raise ValueError("imported_external_id is an empty string.")
            self.od_matrices = imported_od_matrices
            self.centroid_configuration_external_id = imported_external_id

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Origin Destination Matrices:\n"
        if hasattr(self, 'od_matrices'):
            for i, od_matrix in enumerate(self.od_matrices):
                string += 'Origin Destination Matrix ' + str(i) + ':\n'
                string += ('  Begin Time:' + str(od_matrix.begin_time_interval)
                           + '\n')
                string += ('  End Time:' + str(od_matrix.end_time_interval)
                           + '\n')
                string += ('  Vehicle Type:' + str(od_matrix.vehicle_type)
                           + '\n')
                string += '  OD Trips:' + '\n'
                for j, od_trip in enumerate(od_matrix.od_trips_count):
                    string += ('    Trip #' + str(j)
                               + 'OriginId: '
                               + od_trip.origin_centroid_external_id
                               + ', DestinationId: '
                               + od_trip.destination_centroid_external_id
                               + ', Trip Count: '
                               + str(od_trip.num_trips)
                               + '\n')
        return string


class SectionSpeedLimitAndCapacity:
    """A SectionSpeedLimitAndCapacity object corresponds to a Section, which is
    a part of a road upon which vehicles can travel. It is also given data for
    speed limit and vehicle capacity to better model actual road conditions.

    Attributes:
        section_internal_id: The Internal ID assigned by Aimsun.
        speed_limit_in_km_per_hour: The speed limit of this section.
        capacity_in_vehicles_per_hour: The maximum capacity of vehicles per hour
            of this section.
    """
    section_internal_id: InternalId
    speed_limit_in_km_per_hour: float
    capacity_in_vehicles_per_hour: float

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Section Speed Limit And Capacity:\n"
        if hasattr(self, 'section_internal_id'):
            string += f"Section Internal ID: {self.section_internal_id}\n"
        if hasattr(self, 'speed_limit_in_km_per_hour'):
            string += (f"Speed Limit (km/hr): {self.speed_limit_in_km_per_hour}"
                       "\n")
        if hasattr(self, 'capacity_in_vehicles_per_hour'):
            string += ("Capacity (vehicles/hr): "
                       f"{self.capacity_in_vehicles_per_hour}\n")
        return string


class SectionSpeedLimitsAndCapacities:
    """Aggregate class containing a list of SectionSpeedLimitAndCapacity objects

    The SectionSpeedLimitsAndCapacities class stores a list of
    SectionSpeedLimitAndCapacity objects to simplify storage and access of
    SectionSpeedLimitAndCapacity objects. By utilizing the pickle module, we can
    save one object instead of a group of SectionSpeedLimitAndCapacity objects.
    This will make file storage simpler and data access more general in use.

    Attributes:
        speed_limit_and_capacity_list: A list of SectionSpeedLimitAndCapacity
            objects.
    """
    speed_limit_and_capacity_list: list[SectionSpeedLimitAndCapacity]

    def __init__(self, filepath: str = ''):
        if filepath:
            self.__import_from_file(filepath)

    def export_to_file(self, filepath: str):
        """Function to export SectionSpeedLimitsAndCapacities
        object using pickle.

        Each if not/raise block is used to ensure the file we export using this
        function is a stable and complete SectionSPeedLimitsAndCapacitis object.
        The blocks check each attribute of every object within the class.
        For this class, it checks all attributes for each
        SectionSpeedLimitAndCapacity object have been filled out correctly.

        Args:
            filepath: Location where this object should be exported to. The path
                must point to a '.pkl' file, otherwise the code will throw an
                error.
        """
        verify_filepath(filepath, 'pkl')
        if not isinstance(self.speed_limit_and_capacity_list, list):
            raise TypeError(
                "Attribute speed_limit_and_capacity_list is not type List.")
        for i, slc in enumerate(self.speed_limit_and_capacity_list):
            if not isinstance(slc, SectionSpeedLimitAndCapacity):
                raise TypeError(
                    f"Object at index {i} in list speed_limit_and_capacity_list"
                    " is not a SectionSpeedLimitAndCapacity object.")
            if not isinstance(slc.section_internal_id, int):
                raise TypeError(
                    f"Object at index {i} in list "
                    "speed_limit_and_capacity_list; attribute "
                    "section_internal_id is not type InternalId.")
            if not isinstance(slc.speed_limit_in_km_per_hour, float):
                raise TypeError(
                    f"Object at index {i} in list "
                    "speed_limit_and_capacity_list; attribute "
                    "speed_limit_in_km_per_hour is not type float.")
            if not isinstance(slc.capacity_in_vehicles_per_hour, float):
                raise TypeError(
                    f"Object at index {i} in list "
                    "speed_limit_and_capacity_list; attribute"
                    "capacity_in_vehicles_per_hour is not type float.")
        with open(filepath, 'wb') as file:
            pickle.dump(self.speed_limit_and_capacity_list, file)

    def __import_from_file(self, filepath: str):
        """Function to import SectionSpeedLimitsAndCapacities
        object using pickle.

        As objects should only be created and exported through this script, we
        only need to type check the basics of each imported file: valid
        filepath, file extension, and correct attribute types.

        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, "rb") as file:
            imported_slc_list = pickle.load(file)
            if not isinstance(imported_slc_list, list):
                raise TypeError("imported_slc_list is not type List.")
            for i, slc_obj in enumerate(imported_slc_list):
                if not isinstance(slc_obj, SectionSpeedLimitAndCapacity):
                    raise TypeError(
                        f"Object at index {i} in list imported_slc_list is not "
                        "a SectionSpeedLimitAndCapacity object.")
            self.speed_limit_and_capacity_list = imported_slc_list

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Section Speed Limits and Capacities:\n"
        if hasattr(self, 'speed_limit_and_capacity_list'):
            string += 'Speed Limit and Capacity List:\n'.join(
                map(str, self.speed_limit_and_capacity_list))
        return string


# ************************************************************
# *************** AIMSUN OBJECT FOR SIMULATION ***************
# ************************************************************


class AimsunGeoObject(AimsunObject):
    """Data class for Aimsun geometry object. Corresponds to Aimsun GKGeoObject.
    """
    layer_id: InternalId


class AimsunSectionObject(AimsunGeoObject):
    """This type of object will always be added on top of a Section. It is a
    parent class that holds functionality for other section objects, such as
    Detectors or Meterings.

    This class corresponds to the GKSectionObject object in Aimsun.

    Attributes:
        aimsun_section_internal_id: The Aimsun GKSection object's
            Internal ID assigned by Aimsun.
        from_lane: The first lane the Section Object covers.
        to_lane: The last lane the Section Object covers.
        length: The length of the Section Object.
        position: The location as an offset from the entrance of the section.
    """
    aimsun_section_internal_id: InternalId
    from_lane: int
    to_lane: int
    length: float
    position: float

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self):
        string = "AimsunSectionObject -> " + super().__str__()
        if hasattr(self, 'aimsun_section_internal_id'):
            string += ("Aimsun Section Internal ID: "
                       f"{self.aimsun_section_internal_id}\n")
        if hasattr(self, 'from_lane'):
            string += f"From Lane: {self.from_lane}\n"
        if hasattr(self, 'to_lane'):
            string += f"To Lane: {self.to_lane}\n"
        if hasattr(self, 'length'):
            string += f"Length: {self.length}\n"
        if hasattr(self, 'position'):
            string += f"Position: {self.position}\n"
        return string

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if not super().check_attributes_type():
            return False
        if hasattr(self, 'aimsun_section_internal_id'):
            if not isinstance(self.aimsun_section_internal_id, int):
                return False
        if hasattr(self, 'from_lane'):
            if not isinstance(self.from_lane, int):
                return False
        if hasattr(self, 'to_lane'):
            if not isinstance(self.to_lane, int):
                return False
        if hasattr(self, 'length'):
            if not isinstance(self.length, float):
                return False
        if hasattr(self, 'position'):
            if not isinstance(self.position, float):
                return False
        return True


class Detector(AimsunSectionObject):
    """Detectors lie along sections and record vehicle information, such as
    flow, occupancy, etc. These are used to capture data that will be used to
    build and calibrate demand matrices. This class inherits attributes from
    AimsunSectionObject and AimsunObject, which means its External ID is listed
    in a parent attribute.

    This class corresponds to the GKDetector object in Aimsun.

    Attributes:
        detect_count: A boolean that determines if this detector can count the
            number of vehicles that pass over it.
        detect_density: A boolean that determines if this detector can
            calculate the density of a section.
            # Check what density means - scripting documentation is not specific
        detect_equipped_vehicles: A boolean that determines if this detector
            can detect specialized vehicles, such as snow bulldozing trucks.
        detect_headway: A boolean that determines if this detector can detect
            the distance between vehicles.
        detect_occupancy: A boolean that determines if this detector can measure
            the total percentage of cars in relation to the maximum occupancy of
            a section.
        detect_presence: A boolean that determines if this detector can check if
            there exists a vehicle on a given section.
        detect_speed: A boolean that determines if this detector can measure the
            speed of vehicles that pass over a given section.
        extended_length: Provided for SCATS Interface. Not useful here.
        number_of_lanes: Number of lanes in the given section.
        offset: A float that allows the detector to offset itself from the
            actual position of the detector. An example could be if a detector
            was made to work a bit after a stop line.
        position_from_end: Detector position from the end of a section.
    """
    detect_count: bool
    detect_density: bool
    detect_equipped_vehicles: bool
    detect_headway: bool
    detect_occupancy: bool
    detect_presence: bool
    detect_speed: bool
    extended_length: float
    number_of_lanes: int
    offset: float
    position_from_end: float

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Detector -> " + super().__str__()
        if hasattr(self, 'detect_count'):
            string += f"Count? {self.detect_count}\n"
        if hasattr(self, 'detect_density'):
            string += f"Density? {self.detect_density}\n"
        if hasattr(self, 'detect_equipped_vehicles'):
            string += f"Equipped vehicles? {self.detect_equipped_vehicles}\n"
        if hasattr(self, 'detect_headway'):
            string += f"Headway? {self.detect_headway}\n"
        if hasattr(self, 'detect_occupancy'):
            string += f"Occupancy? {self.detect_occupancy}\n"
        if hasattr(self, 'detect_presence'):
            string += f"Presence? {self.detect_presence}\n"
        if hasattr(self, 'detect_speed'):
            string += f"Speed? {self.detect_speed}\n"
        if hasattr(self, 'extended_length'):
            string += f"Extended length: {self.extended_length}\n"
        if hasattr(self, 'number_of_lanes'):
            string += f"Number of lanes: {self.number_of_lanes}\n"
        if hasattr(self, 'offset'):
            string += f"Offset: {self.offset}\n"
        if hasattr(self, 'position_from_end'):
            string += f"Position from end: {self.position_from_end}\n"
        return string

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if not super().check_attributes_type():
            return False
        if hasattr(self, 'detect_count'):
            if not isinstance(self.detect_count, bool):
                return False
        if hasattr(self, 'detect_density'):
            if not isinstance(self.detect_density, bool):
                return False
        if hasattr(self, 'detect_equipped_vehicles'):
            if not isinstance(self.detect_equipped_vehicles, bool):
                return False
        if hasattr(self, 'detect_headway'):
            if not isinstance(self.detect_headway, bool):
                return False
        if hasattr(self, 'detect_occupancy'):
            if not isinstance(self.detect_occupancy, bool):
                return False
        if hasattr(self, 'detect_presence'):
            if not isinstance(self.detect_presence, bool):
                return False
        if hasattr(self, 'detect_speed'):
            if not isinstance(self.detect_speed, bool):
                return False
        if hasattr(self, 'extended_length'):
            if not isinstance(self.extended_length, float):
                return False
        if hasattr(self, 'number_of_lanes'):
            if not isinstance(self.number_of_lanes, int):
                return False
        if hasattr(self, 'offset'):
            if not isinstance(self.offset, float):
                return False
        if hasattr(self, 'position_from_end'):
            if not isinstance(self.position_from_end, float):
                return False
        return True


class Metering(AimsunSectionObject):
    """Metering class assigns type and maximum vehicle flow into one object.

    This class corresponds to the GKMetering object in Aimsun.

    Attributes:
        metering_type: Stores the type of meter this object represents.
        vehicle_flow: The maximum number of vehicles that can pass through the
            signal at any given time.
    """
    metering_type: MeteringType
    vehicle_flow: int

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Metering -> " + super().__str__()
        if hasattr(self, 'metering_type'):
            string += f"Metering Type: {self.metering_type}\n"
        if hasattr(self, 'vehicle_flow'):
            string += f"Vehicle Flow: {self.vehicle_flow}\n"
        return string


class Detectors:
    """Aggregate class containing a list of Detector objects.

    The Detectors class stores a list of Detector objects to simplify storage
    and access of Detector objects. By utilizing the pickle module, we can
    save one object instead of a group of Detector objects. This will make file
    storage simpler and data access more general in use.

    Attributes:
        detector_list: A list of Detector objects.
    """
    detector_list: list[Detector]

    def __init__(self, filepath: str = ''):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.detector_list = []

    def export_to_file(self, filepath: str):
        """Function to export Detectors object using pickle.

        Each if not/raise block is used to ensure the file we export using this
        function is a stable and complete Detectors object. The blocks check
        each attribute of every object within the class. For this class, it
        checks all attributes for each Detector object have been filled out
        correctly.

        Args:
            filepath: Location where this object should be exported to. The path
                must point to a '.pkl' file, otherwise the code will throw an
                error.
        """
        verify_filepath(filepath, 'pkl')
        if not isinstance(self.detector_list, list):
            raise TypeError("Attribute detector_list is not a list.")
        # Check if aimsun_detector_locations is empty
        if not self.detector_list:
            raise ValueError('Detectors has no data. Export aborted.')
        for det in self.detector_list:
            if not isinstance(det, Detector):
                raise TypeError(f"{det} is not a Detector object.")
            assert det.check_attributes_type()
        # Check if file exists at given filepath
        if path.exists(filepath):
            warnings.warn('File already exists at filepath. Overwriting file.')
        with open(filepath, 'wb') as file:
            pickle.dump(self.detector_list, file)

    def __import_from_file(self, filepath: str):
        """Function to import Detectors object using pickle.

        As objects should only be created and exported through this script, we
        only need to type check the basics of each imported file: valid
        filepath, file extension, and correct attribute types.

        Args:
            filepath: Location where this object should be imported from. The
                path must point to a '.pkl' file, otherwise the code will throw
                an error.
        """
        verify_filepath(filepath, 'pkl')
        with open(filepath, "rb") as file:
            imported_det_list = pickle.load(file)
            if not isinstance(imported_det_list, list):
                raise TypeError("imported_det_list is not type List.")
            for det_obj in imported_det_list:
                if not isinstance(det_obj, Detector):
                    raise TypeError(f"{det_obj} is not a Detector object.")
            self.detector_list = imported_det_list

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Detectors:\n"
        if hasattr(self, 'detector_list'):
            string += 'Detector List:\n'.join(
                map(str, self.detector_list))
        return string


class FlowRealData(Detector):
    """Data class for output flow data from one detector.

    Attributes:
        flow_data: Flow data of the detector. Contains flow count at each
            timestep.
    """
    flow_data: dict[datetime.timedelta, float]


class AimsunFlowRealDataSet(AimsunObject):
    """Data class for output flow data from multiple detectors.

    The object corresponds to a list of OutputFlowData from multiple detectors.

    To export the AimsunFlowRealDataSet, use the following command:
        >>> real_data_set = AimsunFlowRealDataSet()
        >>> real_data_set.export_to_file(filepath)

    To import the AimsunFlowRealDataSet, use the following command:
        >>> real_data_set = AimsunFlowRealDataSet(filepath)

    Attributes:
        flow_data_set: List of FlowRealData.
        filename: Name of the CSV file that Aimsun can read.
        line_to_skip: Number of line to skip for Aimsun when reading the CSV
            file.
    """
    flow_data_set: list[FlowRealData]
    filename: str
    line_to_skip: int

    def __init__(
        self, filepath: str = "",
        external_id: str = REAL_DATA_SET_EXTERNAL_ID
    ):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.external_id = external_id

    def export_to_file(self, filepath: str):
        """Export OutputFlowDataSet to file by serializing `flow_data_set`
        and `year`.

        Raises exception if the detectors_location_dict is empty. Warns the
        user if a file already exists at filepath and overwrites it.

        Args:
            filepath: Location to export object attributes.
        """
        # Check if flow_data_set is empty
        if len(self.flow_data_set) == 0:
            raise ValueError('OutputFlowDataSet has no data. Export aborted.')
        # Check if file exists at given filepath
        if path.exists(filepath):
            warnings.warn('File already exists at filepath. Overwriting file.')
        for detector_flow_data in self.flow_data_set:
            assert isinstance(detector_flow_data, FlowRealData)
            assert isinstance(detector_flow_data.external_id, str)
            assert isinstance(
                detector_flow_data.aimsun_section_internal_id, int)
        # Serialize flow_data_set and write to filepath
        with open(filepath, 'wb') as file:
            if not isinstance(self.external_id, str):
                raise TypeError('external_id is not type string.')
            if not all(isinstance(fds, FlowRealData) for fds
                       in self.flow_data_set):
                raise TypeError(
                    'flow_data_set contains non-FlowRealData object.')
            pickle.dump(self.flow_data_set, file)
            pickle.dump(self.external_id, file)
            pickle.dump(self.filename, file)
            pickle.dump(self.line_to_skip, file)

    def __import_from_file(self, filepath: str):
        """Import OutputFlowDataSet from file by deserializing `flow_data_set`
        and `year`.

        Raises exception if the given file does not match the data type of
        flow_data_set (list[OutputFlowData]) and year (int).

        Args:
            filepath: Location to import object attributes from.
        """
        # Deserialize flow_data_set from filepath
        with open(filepath, 'rb') as file:
            imported_flow_data_set = pickle.load(file)
            external_id = pickle.load(file)
            filename = pickle.load(file)
            line_to_skip = pickle.load(file)
        # Check if imported data matches data type of flow_data_set
        if not isinstance(imported_flow_data_set, list):
            raise TypeError("imported_flow_data_set is not a list.")
        for detector_flow_data in imported_flow_data_set:
            assert isinstance(detector_flow_data, FlowRealData)
            assert isinstance(detector_flow_data.external_id, str)
            assert isinstance(
                detector_flow_data.aimsun_section_internal_id, int)
        assert isinstance(external_id, str)
        assert isinstance(filename, str)
        self.flow_data_set = imported_flow_data_set
        self.external_id = external_id
        self.filename = filename
        self.line_to_skip = line_to_skip

    def export_to_aimsun_real_data_set_csv(self, directory: str, filename: str):
        """Export flow dataset as a CSV file for Aimsun.

        Aimsun GKRealDataSet object requires the flow data to be a CSV file.
        The columns of the CSV file output are detector_external_id, time and
        count.
        Args:
            directory: directory where the CSV file is.
            filename: filename toward the CSV file.
        """
        self.filename = filename
        self.line_to_skip = 1
        with open(path.join(directory, filename), 'wt',
                  encoding='utf-8') as file:
            csv_file = csv.writer(file)
            csv_file.writerow(
                ['Detector External Id', '15 minutes Count', 'Time'])
            for detector_flow_data in self.flow_data_set:
                assert isinstance(detector_flow_data.external_id, str)
                for time, count in detector_flow_data.flow_data.items():
                    # csv_data should be consistent with T1 script:
                    # detector external id, count, time in seconds.
                    seconds_passed_from_minight = int(time.total_seconds())
                    assert isinstance(count, (float, int))
                    assert isinstance(seconds_passed_from_minight, int)
                    csv_data = [detector_flow_data.external_id,
                                count, seconds_passed_from_minight]
                    csv_file.writerow(csv_data)

    def __eq__(self, other):
        """Evaluates object equality based on attributes."""
        # Check if name-related attributes are the same
        if (self.external_id != other.external_id
                or self.filename != other.filename
                or self.line_to_skip != other.line_to_skip):
            return False
        # Check if length of flow_data_set equals each other
        if len(self.flow_data_set) != len(other.flow_data_set):
            return False
        # Check all attributes of flow_data_set against each other
        for self_val, other_val in zip(self.flow_data_set, other.flow_data_set):
            if (self_val.external_id != other_val.external_id
                    or self_val.flow_data != other_val.flow_data
                    or self_val.aimsun_section_internal_id != other_val.
                    aimsun_section_internal_id):
                return False
        return True


class ControlDetector:
    """Data class that corresponds to Aimsun GKControlDetector object. Used for
    NE3 and N5 Aimsun scripts.

    Attributes:
        detector_external_id: External ID of the control detector.
        locking: Boolean whether the control detector is locked or not.
        call_delay: Call delay time of the control detector.
        phase_activation: Boolean whether the control detector activates phase.
        phase_extension: Boolean whether the control detector extends phase.
    """
    detector_external_id: ExternalId
    locking: bool
    call_delay: float
    phase_activation: bool
    phase_extension: bool

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'detector_external_id'):
            if not isinstance(self.detector_external_id, str):
                print('Wrong detector_external_id type.')
                return False
        if hasattr(self, 'locking'):
            if not isinstance(self.locking, bool):
                print('Wrong locking type.')
                return False
        if hasattr(self, 'call_delay'):
            if not isinstance(self.call_delay, float):
                print('Wrong call_delay type.')
                return False
        if hasattr(self, 'phase_activation'):
            if not isinstance(self.phase_activation, bool):
                print('Wrong phase_activation type.')
                return False
        if hasattr(self, 'phase_extension'):
            if not isinstance(self.phase_extension, bool):
                print('Wrong phase_extension type.')
                return False
        return True


class ControlMetering:
    """Data class that corresponds to Aimsun GKControlMetering object.

    Attributes:
        control_metering_type: Type of control metering.
        metering_external_id: External ID of the control metering.
    """
    control_metering_type: ControlMeteringType
    metering_external_id: ExternalId

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'control_metering_type'):
            if not isinstance(self.control_metering_type, ControlMeteringType):
                print('Wrong control_metering_type type.')
                return False
        if hasattr(self, 'metering_external_id'):
            if not isinstance(self.metering_external_id, str):
                print('Wrong metering_external_id type.')
                return False
        return True


class ControlPhaseSignal:
    """Data class that corresponds to Aimsun GKControlPhaseSignal object.

    Attributes:
        signal: Signal number of the control phase.
        name: Name of the control phase signal.
        flashing_type: Type of flashing for control phase signal.
    """
    signal: int
    name: str
    flashing_type: FlashingType

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'signal'):
            if not isinstance(self.signal, int):
                print('Wrong signal type.')
                return False
        if hasattr(self, 'name'):
            if not isinstance(self.name, str):
                print('Wrong name type.')
                return False
        if hasattr(self, 'flashing_type'):
            if not isinstance(self.flashing_type, FlashingType):
                print('Wrong flashing_type type.')
                return False
        return True

    def __str__(self):
        return_string = ""
        if hasattr(self, 'signal'):
            return_string += f"signal: {self.signal}"
        if hasattr(self, 'name'):
            return_string += f"name: {self.name}"
        if hasattr(self, 'flashing_type'):
            return_string += f"flashing_type: {self.flashing_type}"
        return return_string


class ControlPhase:
    """Data class that corresponds to Aimsun GKControlPhase object. Used for NE3
    and N5 Aimsun scripts.

    Attributes:
        from_time: Start time of the control phase.
        duration: Duration of the control phase.
        signals: List of control signals over the duration of the phase.
    """
    from_time: float
    duration: float
    signals: list[ControlPhaseSignal]

    def __init__(self):
        self.signals = []

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'from_time'):
            if not isinstance(self.from_time, float):
                print('Wrong from_time type.')
                return False
        if hasattr(self, 'duration'):
            if not isinstance(self.duration, float):
                print('Wrong duration type.')
                return False
        if hasattr(self, 'signals'):
            if not all(isinstance(signal, ControlPhaseSignal)
                       for signal in self.signals):
                print('Some wrong signal types.')
                return False
            if not all(signal.check_attributes_type()
                       for signal in self.signals):
                print('Some wrong signal types.')
                return False
        return True

    def __str__(self):
        return_string = ""
        if hasattr(self, 'from_time'):
            return_string += f"from_time: {self.from_time}"
        if hasattr(self, 'duration'):
            return_string += f"duration: {self.duration}"
        if hasattr(self, 'interphase'):
            return_string += "[" + ",".join(map(str, self.signals)) + "]"
        return return_string


class NonActuatedControlPhase(ControlPhase):
    """Child class that contains attributes specific to a non-actuated Aimsun
    GKControlPhase object. Used for NE3 and N5 Aimsun scripts.

    Attributes:
        interphase: Boolean indicating whether interphase time exists in control
            phase.
    """
    interphase: bool

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if not super().check_attributes_type():
            return False
        if hasattr(self, 'interphase'):
            if not isinstance(self.interphase, bool):
                print('Wrong interphase type.')
                return False
        return True

    def __str__(self):
        return_string = "{"
        return_string += super().__str__()
        if hasattr(self, 'interphase'):
            return_string += f"interphase: {self.interphase}"
        return_string += "}"
        return return_string


class ActuatedControlPhase(ControlPhase):
    """Child class that contains attributes specific to an actuated Aimsun
    GKControlPhase object.

    See detailed information at
    https://docs.aimsun.com/next/22.0.1/UsersManual/ControlPlanEditing.html#actuated-parameters

    Attributes:
        id_ring: ID of the control phase ring.
        interphase: Boolean indicating whether interphase time exists in control
            phase.
        recall: Activates the specified phase.
        is_default: Boolean indicating whether the control phase is default.
        min_duration: Minimum duration of the control phase.
        max_duration: Maximum duration of the control phase.
        passage_time: Maximum allowed time difference between detector
            actuations.
        permissive_period_from: Starting time of the permissive period.
        permissive_period_to: End time of the permissive period.
        force_off: For each phase there is a point in the cycle, called
            force-off, at which the phase must terminate at the most, in order
            to maintain a fixed cycle (the force-off of the coordinated phase is
            0 by default).
        hold: If a phase has this feature activated, the current green interval
            is retained until it yields to a conflicting call. It is the
            opposite command to Rest in Red.
        maximum_initial: The maximum value up to which the initial time can be
            extended.
        seconds_actuation: The number of seconds the Minimum Green is extended
            for each actuation taking place when an Extensible Initial method
            is used and while that phase is not active.
        gap_reduction: Gap reduction is a process that reduces the allowable gap
            from the Passage Time down to the Minimum Gap.
        minimum_gap: The value to which the allowable gap will be reduced when
            using a Gap Reduction feature.
        time_before_reduce: Time point that signals start of Gap Reduction.
        time_to_reduce: Time point that signals end of Gap Reduction.
        detectors: List of detectors in the area of study.
    """
    id_ring: int
    interphase: bool
    recall: ControlPhaseRecall
    is_default: bool
    min_duration: float
    max_duration: float
    passage_time: float
    permissive_period_from: float
    permissive_period_to: float
    force_off: float
    hold: bool
    maximum_initial: float
    seconds_actuation: float
    gap_reduction: bool
    minimum_gap: float
    time_before_reduce: float
    time_to_reduce: float
    detectors: list[ControlDetector]

    def __init__(self):
        super().__init__()
        self.detectors = []

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if not super().check_attributes_type():
            return False
        if hasattr(self, 'id_ring'):
            if not isinstance(self.id_ring, int):
                print('Wrong id_ring type.')
                return False
        if hasattr(self, 'interphase'):
            if not isinstance(self.interphase, bool):
                print('Wrong interphase type.')
                return False
        if hasattr(self, 'recall'):
            if not isinstance(self.recall, ControlPhaseRecall):
                print('Wrong recall type.')
                return False
        if hasattr(self, 'is_default'):
            if not isinstance(self.is_default, bool):
                print('Wrong is_default type.')
                return False
        if hasattr(self, 'min_duration'):
            if not isinstance(self.min_duration, float):
                print('Wrong min_duration type.')
                return False
        if hasattr(self, 'max_duration'):
            if not isinstance(self.max_duration, float):
                print('Wrong max_duration type.')
                return False
        if hasattr(self, 'passage_time'):
            if not isinstance(self.passage_time, float):
                print('Wrong passage_time type.')
                return False
        if hasattr(self, 'permissive_period_from'):
            if not isinstance(self.permissive_period_from, float):
                print('Wrong permissive_period_from type.')
                return False
        if hasattr(self, 'permissive_period_to'):
            if not isinstance(self.permissive_period_to, float):
                print('Wrong permissive_period_to type.')
                return False
        if hasattr(self, 'force_off'):
            if not isinstance(self.force_off, float):
                print('Wrong force_off type.')
                return False
        if hasattr(self, 'hold'):
            if not isinstance(self.hold, bool):
                print('Wrong hold type.')
                return False
        if hasattr(self, 'maximum_initial'):
            if not isinstance(self.maximum_initial, float):
                print('Wrong maximum_initial type.')
                return False
        if hasattr(self, 'seconds_actuation'):
            if not isinstance(self.seconds_actuation, float):
                print('Wrong seconds_actuation type.')
                return False
        if hasattr(self, 'gap_reduction'):
            if not isinstance(self.gap_reduction, bool):
                print('Wrong gap_reduction type.')
                return False
        if hasattr(self, 'minimum_gap'):
            if not isinstance(self.minimum_gap, float):
                print('Wrong minimum_gap type.')
                return False
        if hasattr(self, 'time_before_reduce'):
            if not isinstance(self.time_before_reduce, float):
                print('Wrong time_before_reduce type.')
                return False
        if hasattr(self, 'time_to_reduce'):
            if not isinstance(self.time_to_reduce, float):
                print('Wrong time_to_reduce type.')
                return False
        if hasattr(self, 'detectors'):
            if not all(isinstance(detector, ControlDetector)
                       for detector in self.detectors):
                print('Some wrong detector types.')
                return False
            if not all(detector.check_attributes_type()
                       for detector in self.detectors):
                print('Some wrong detector types.')
                return False
        return True


class ControlJunction:
    """Data class that corresponds to Aimsun GKControlJunction object. Used for
    NE3 and N5 Aimsun scripts.

    Attributes:
        node_id: ID for the junction.
        junction_type: Type of junction.
        cycle: Cycle of junction.
        offset: Offest of junction.
    """
    node_id: str
    junction_type: ControlJunctionType
    cycle: float
    offset: float

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'nodeId'):
            if not isinstance(self.node_id, str):
                print('Wrong node_id type.')
                return False
        if hasattr(self, 'junction_type'):
            if not isinstance(self.junction_type, ControlJunctionType):
                print('Wrong junction_type type.')
                return False
        if hasattr(self, 'cycle'):
            if not isinstance(self.cycle, float):
                print('Wrong cycle type.')
                return False
        if hasattr(self, 'offset'):
            if not isinstance(self.offset, float):
                print('Wrong offset type.')
                return False
        return True


class NonActuatedControlJunction(ControlJunction):
    """This child class of ControlJunction houses the attributes of a
    non-actuated control junction.
    """
    phases: list[NonActuatedControlPhase]

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if not super().check_attributes_type():
            return False
        if hasattr(self, 'phases'):
            if not all(isinstance(phase, NonActuatedControlPhase)
                       for phase in self.phases):
                for phase in self.phases:
                    if not isinstance(phase, NonActuatedControlPhase):
                        print(f"{type(phase)} is not NonActuatedControlPhase.")
                return False
            if not all(phase.check_attributes_type()
                       for phase in self.phases):
                print('Some wrong phases type.')
                return False
        return True


class ActuatedControlJunction(ControlJunction):
    """This child class of ControlJunction houses the many more attributes of
    an actuated control junction has over a non-actuated junction. It also uses
    ActuatedControlPhases, a child of ControlPhases.
    """
    barriers: list[int]
    num_phases: int
    rest_in_red: bool
    matches_offset_with_end_of_phase: bool
    yellow_time: float
    single_entry: bool
    phases: list[ActuatedControlPhase]

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if not super().check_attributes_type():
            return False
        if hasattr(self, 'barriers'):
            if not all(isinstance(barrier, int)
                       for barrier in self.barriers):
                print('Some wrong barrier types.')
                return False
        if hasattr(self, 'num_phases'):
            if not isinstance(self.num_phases, int):
                print('Wrong num_phases type.')
                return False
        if hasattr(self, 'rest_in_red'):
            if not isinstance(self.rest_in_red, bool):
                print('Wrong rest_in_red type.')
                return False
        if hasattr(self, 'matches_offset_with_end_of_phase'):
            if not isinstance(self.matches_offset_with_end_of_phase, bool):
                print('Wrong matches_offset_with_end_of_phase type.')
                return False
        if hasattr(self, 'yellow_time'):
            if not isinstance(self.yellow_time, float):
                print('Wrong yellow_time type.')
                return False
        if hasattr(self, 'single_entry'):
            if not isinstance(self.single_entry, bool):
                print('Wrong single_entry type.')
                return False
        if hasattr(self, 'phases'):
            if not all(isinstance(phase, ActuatedControlPhase)
                       for phase in self.phases):
                for phase in self.phases:
                    if not isinstance(phase, ActuatedControlPhase):
                        print(
                            (f"Some wrong phases type {type(phase)} is not "
                             "ActuatedControlPhase."))
                return False
            if not all(phase.check_attributes_type()
                       for phase in self.phases):
                print('Some wrong phases type.')
                return False
        return True


class ControlPlan(AimsunObject):
    """Data class that corresponds to Aimsun GKControlPlan object.

    Attributes:
        control_junctions: List of control junctions in the plan.
        control_meterings: List of control meterings in the plan.
        offset: Offest of control plan.
    """
    control_junctions: list[ControlJunction]
    control_meterings: list[ControlMetering]
    offset: int

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'control_junctions'):
            if not all(isinstance(control_junction, ControlJunction)
                       for control_junction in self.control_junctions):
                print('Some wrong control junctions types')
                return False
            if not all(control_junction.check_attributes_type()
                       for control_junction in self.control_junctions):
                print('Some wrong control junctions types')
                return False
        if hasattr(self, 'control_meterings'):
            if not all(isinstance(control_metering, ControlMetering)
                       for control_metering in self.control_meterings):
                print('Some wrong control metering types.')
                return False
            if not all(control_metering.check_attributes_type()
                       for control_metering in self.control_meterings):
                print('Some wrong control metering types.')
                return False
        if hasattr(self, 'offset'):
            if not isinstance(self.offset, int):
                print('Wrong offset type.')
                return False
        return True


class MasterControlPlanItem:
    """Data class that corresponds to Aimsun GKScheduleMasterControlPlanItem
    object.

    Attributes:
        control_plan_external_id: External ID of the control plan.
        duration: Duration of the control plan.
        from_time: Start time of the control plan.
        zone: Zone enumerator identifier of the control plan.
    """
    control_plan_external_id: ExternalId
    duration: int
    from_time: int
    zone: int

    def check_attributes_type(self):
        """Check that attributes have correct object type."""
        if hasattr(self, 'control_plan_external_id'):
            if not isinstance(self.control_plan_external_id, str):
                print('Wrong control_plan_external_id type.')
                return False
        if hasattr(self, 'duration'):
            if not isinstance(self.duration, int):
                print('Wrong duration type.')
                return False
        if hasattr(self, 'from_time'):
            if not isinstance(self.from_time, int):
                print('Wrong from_time type.')
                return False
        if hasattr(self, 'zone'):
            if not isinstance(self.zone, int):
                print('Wrong zone type.')
                return False
        return True

    def __str__(self):
        return_string = "{"
        if hasattr(self, 'control_plan_external_id'):
            return_string += f"Control plan: {self.control_plan_external_id}, "
        if hasattr(self, 'duration'):
            return_string += f"Duration: {self.duration}, "
        if hasattr(self, 'from_time'):
            return_string += f"From time: {self.from_time}, "
        if hasattr(self, 'zone'):
            return_string += f"Zone: {self.zone}, "
        return return_string[:-2] + "}"


class MasterControlPlan(AimsunObject):
    """Data class that corresponds to Aimsun GKMasterControlPlan object. Used
    for NE3 and N5 Aimsun scripts.

    Attributes:
        control_plans: Full list of control plans.
        detectors: Full list of detectors in the area of study.
        meterings: Full list of meterings in the area of study.
        schedule: List of schedules for control plans.
    """
    control_plans: list[ControlPlan]
    detectors: list[Detector]
    meterings: list[Metering]
    schedule: list[MasterControlPlanItem]

    def __init__(self, filepath: str = "",
                 external_id: str = MASTER_CONTROL_PLAN_EXTERNAL_ID):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.control_plans = []
            self.external_id = external_id
            self.schedule = []
            self.detectors = []

    def export_to_file(self, filepath: str):
        """Export MasterControlPlan to file by serializing `schedule`.

        Raises exception if the schedule is empty. Warns the
        user if a file already exists at filepath and overwrites it.

        Args:
            filepath: Location to export object attributes.
        """
        # Check if flow_data_set is empty
        if len(self.schedule) == 0:
            raise Exception('MasterControlPlan has no data. Export aborted.')
        # Check if file exists at given filepath
        if path.exists(filepath):
            warnings.warn('File already exists at filepath. Overwriting file.')
        # Verify schedule attribute
        if not isinstance(self.schedule, list):
            raise TypeError("imported_schedule is not a list.")
        if not all(isinstance(item, MasterControlPlanItem) for item
                   in self.schedule):
            raise TypeError("schedule elements are not MasterControlPlanItem.")
        # Verify control_plans attribute
        if not isinstance(self.control_plans, list):
            raise TypeError("control_plans is not a list.")
        if not all(isinstance(item, ControlPlan) for item
                   in self.control_plans):
            raise TypeError("control_plan elements are not ControlPlan items.")
        # Verify meterings attribute
        if not isinstance(self.meterings, list):
            raise TypeError("meterings is not a list.")
        if not all(isinstance(item, Metering) for item in self.meterings):
            raise TypeError("meterings elements are not Metering items.")
        # Verify detectors attribute
        if not isinstance(self.detectors, list):
            raise TypeError("detectors is not a list.")
        if not all(isinstance(item, Detector) for item in self.detectors):
            raise TypeError("detectors elements are not Detector items.")
        # Verify external_id attribute
        if not isinstance(self.external_id, str):
            raise TypeError("external_id attribute is not a string.")
        # Verify name attribute
        if not isinstance(self.name, str):
            raise TypeError("name attribute is not a string.")
        # Serialize attributes and write to file
        with open(filepath, 'wb') as file:
            pickle.dump(self.schedule, file)
            pickle.dump(self.control_plans, file)
            pickle.dump(self.meterings, file)
            pickle.dump(self.detectors, file)
            pickle.dump(self.external_id, file)
            pickle.dump(self.name, file)

    def __import_from_file(self, filepath: str):
        """Import MasterControlPlan from file by deserializing `schedule`.

        Raises exception if the given file does not match the data type of
        schedule (list[MasterControlPlanItem]).

        Args:
            filepath: Location to import object attributes from.
        """
        # Check validity of given filepath
        if not path.exists(filepath):
            raise FileNotFoundError('No file exists in given filepath.')
        # Deserialize schedule from filepath
        with open(filepath, 'rb') as file:
            imported_schedule = pickle.load(file)
            imported_control_plans = pickle.load(file)
            imported_meterings = pickle.load(file)
            imported_detectors = pickle.load(file)
            imported_external_id = pickle.load(file)
            imported_name = pickle.load(file)
        # Check if imported data matches data type of schedule
        # Verify schedule attribute
        if not isinstance(imported_schedule, list):
            raise TypeError("imported_schedule is not a list.")
        if not all(isinstance(item, MasterControlPlanItem) for item
                   in imported_schedule):
            raise TypeError(
                "imported_schedule elements are not MasterControlPlanItem.")
        # Verify control_plans attribute
        if not isinstance(imported_control_plans, list):
            raise TypeError("imported_control_plans is not a list.")
        if not all(isinstance(item, ControlPlan) for item
                   in imported_control_plans):
            raise TypeError(
                "imported_control_plans elements are not ControlPlan items.")
        # Verify meterings attribute
        if not isinstance(imported_meterings, list):
            raise TypeError("imported_meterings is not a list.")
        if not all(isinstance(item, Metering) for item in imported_meterings):
            raise TypeError(
                "imported_meterings elements are not Metering items.")
        # Verify detectors attribute
        if not isinstance(imported_detectors, list):
            raise TypeError("imported_detectors is not a list.")
        if not all(isinstance(item, Detector) for item in imported_detectors):
            raise TypeError(
                "imported_detectors elements are not Detector items.")
        # Verify external_id attribute
        if not isinstance(imported_external_id, str):
            raise TypeError("imported_external_id is not a string.")
        # Verify name attribute
        if not isinstance(imported_name, str):
            raise TypeError("imported_name is not a string.")
        # Assign imported attributes to object instance
        self.schedule = imported_schedule
        self.control_plans = imported_control_plans
        self.meterings = imported_meterings
        self.detectors = imported_detectors
        self.external_id = imported_external_id
        self.name = imported_name

    def __str__(self):
        return_string = "{"
        return_string += super().__str__()
        return_string += (
            "control_plans: [" + ",".join(map(str, self.control_plans)) + "], ")
        return_string += "schedule: [" + ",".join(map(str, self.schedule)) + "]"
        return_string += "}"
        return return_string


class TurningClosingChange(AimsunObject):
    """Class describing the changes to a turning section. This is used in the
    traffic policies to show possible sets of changes that may reduce traffic.

    Inherits name, external_id, and internal_id from AimsunObject.
    This class corresponds to the Aimsun object GKTurningClosingChange.
    """
    from_section_internal_id: InternalId
    scenario_change_type: ScenarioChangeType
    to_section_internal_id: InternalId

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Turning Closing Change: -> " + super().__str__()
        if hasattr(self, 'to_section_internal_id'):
            string += f'To section: {self.to_section_internal_id}\n'
        if hasattr(self, 'from_section_internal_id'):
            string += f'From section: {self.from_section_internal_id}\n'
        if hasattr(self, 'scenario_change_type'):
            string += f'Scenario Change Type: {self.scenario_change_type}\n'
        return string


class TrafficPolicy(AimsunObject):
    """Class describing the group of scenario changes (also known as
    TurningClosingChange objects) that are a part of a single traffic policy.

    Inherits name, external_id, and internal_id from AimsunObject.
    This class corresponds to the Aimsun object GKPolicy.
    """
    scenario_changes: list[TurningClosingChange]

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Traffic Policy: -> " + super().__str__()
        if hasattr(self, 'scenario_changes'):
            string += 'Scenario Changes:\n'.join(
                map(str, self.scenario_changes))
        return string


class TrafficManagementStrategy(AimsunObject):
    """Class describing a traffic management strategy that may be employed
    to reduce traffic within the studied city.

    This class corresponds to the Aimsun object GKStrategy.
    """
    policies: list[TrafficPolicy]

    def __init__(self, filepath: str = "",
                 external_id: str = TRAFFIC_STRATEGY_EXTERNAL_ID):
        if filepath:
            self.__import_from_file(filepath)
        else:
            self.external_id = external_id

    def export_to_file(self, filepath: str):
        """Export TrafficManagementStrategy to file by serializing
        `policies`. Raises exception if the policy list is empty. Warns the
        user if a file already exists at filepath and overwrites it.
        Args:
            filepath: Location to export object attributes.
        """
        # Check if flow_data_set is empty
        if len(self.policies) == 0:
            raise Exception('TrafficManagementStrategy has no data. '
                            'Export aborted.')
        # Check if file exists at given filepath
        if path.exists(filepath):
            warnings.warn('File already exists at filepath. Overwriting file.')
        # Check that all attributes are of valid object type

        # Serialize flow_data_set and write to filepath
        with open(filepath, 'wb') as file:
            pickle.dump(self.policies, file)
            pickle.dump(self.name, file)
            pickle.dump(self.external_id, file)

    def __import_from_file(self, filepath: str):
        """Import TraffiCManagementStrategy from file by deserializing
        `policies`. Raises exception if the given file does not match the data
        type of policies (list[TrafficPolicy]).
        Args:
            filepath: Location to import object attributes from.
        """
        # Deserialize policies from filepath
        verify_filepath(filepath, 'pkl')
        with open(filepath, 'rb') as file:
            imported_policies = pickle.load(file)
            imported_name = pickle.load(file)
            imported_external_id = pickle.load(file)
        # Check if imported policies data matches data type of policies
        if not isinstance(imported_policies, list):
            raise TypeError("imported_policies is not a list.")
        if not all(isinstance(item, TrafficPolicy) for item
                   in imported_policies):
            raise TypeError("imported_policies elements are not TrafficPolicy.")
        # Check if imported data matches data type for names
        if not isinstance(imported_name, str):
            raise TypeError("imported_name is not a string.")
        # Check if imported external ID matches data type for external IDs
        if not isinstance(imported_external_id, str):
            raise TypeError("imported_external_id is not a string.")
        self.policies = imported_policies
        self.name = imported_name
        self.external_id = imported_external_id

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        string = "Traffic Management Strategy -> " + super().__str__()
        if hasattr(self, 'policies'):
            string += 'Policies:\n'.join(
                map(str, self.policies))
        return string
