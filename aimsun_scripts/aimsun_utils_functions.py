"""This script holds most of the needed utility functions that are used to
create, manage, and export Aimsun and Python objects. The file is divided into
sections based on their use:
    General - These functions are used throughout the project to find or create
        useful objects.
    Demand - These functions relate to creation and manipulation of Origin
        Destination matrices, as well as the centroids used with those matrices.
    Network - These functions relate to the network that the vehicles travel
        on, including speed limits, road capacities, meterings, detectors,
        control plans, strategies, and associated subclasses to each class.
    Traffic - These functions relate to the traffic data used for simulations.
        They allow for importing and creating data sets readable for Aimsun.
    Simulation - These functions help set up and execute experiments and
        simulations. Other functions are used to create parts of said
        experiments.
"""

import os
import sqlite3
import sys
from typing import Any, Dict, Mapping, NewType, List, Tuple

import aimsun_config_utils
import aimsun_input_utils


GKControlPhaseSignal = NewType('GKControlPhaseSignal', Any)
GKControlPlan = NewType('GKControlPlan', Any)
GKControlJunction = NewType('GKControlJunction', Any)
GKDataBaseInfo = NewType('GKDataBaseInfo', Any)
GKDetector = NewType('GKDetector', Any)
GKExperiment = NewType('GKExperiment', Any)
GKMasterControlPlan = NewType('GKMasterControlPlan', Any)
GKMetering = NewType('GKMetering', Any)
GKModel = NewType('GKModel', Any)
GKPolicy = NewType('GKPolicy', Any)
GKObject = NewType('GKObject', Any)
GKRealDataSet = NewType('GKRealDataSet', Any)
GKStrategy = NewType('GKStrategy', Any)
GKScenarioInputData = NewType('GKScenarioInputData', Any)
GKSectionObject = NewType('GKSectionObject', Any)
GKSystem = NewType('GKSystem', Any)
GKTurningClosingChange = NewType('GKTurningClosingChange', Any)
MacroExperiment = NewType('MacroExperiment', Any)


# ****************************************************************************
# ************************** General util functions **************************
# ****************************************************************************


def create_detector_external_id(
    internal_id: aimsun_input_utils.InternalId
) -> aimsun_input_utils.ExternalId:
    """Takes in a road_section_internal_id and converts it to a usable external
    ID for detector objects.

    Args:
        internal_id: An integer of Internal ID type defined in
            aimsun_input_utils.
    Returns:
        external_id: A string that concatenates a detector tag with its
            internal ID.
    """
    return f'act_det_{internal_id}'


def get_list_of_objects(
    object_type: str, aimsun_model: GKModel
) -> List[GKObject]:
    """Takes in an object type and the Aimsun model. Using the model's root
    folder, the function returns a list of objects within the model's catalog
    that have the same type as the given object_type.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        object_type: A string describing the type of object that needs to be
            returned from the catalog.
    Returns:
        object_list: A list of objects from the Aimsun model that are of type
            object_type.
    Raises:
        aimsun_report_error: Throws an error if the folder doesn't exist.
    """
    folder = aimsun_model.getCreateRootFolder().findFolder(object_type)
    if folder is None:
        aimsun_model.reportError(
            'aimsun_utils_functions',
            f"There are no objects with the associated type {object_type}.")
        sys.exit()
    return list(map(aimsun_model.getCatalog().find, folder.getContents()))


def get_object_per_external_id(
    external_id: aimsun_input_utils.ExternalId,
    object_types: List[str],
    aimsun_model: GKModel
):
    """Takes in an External ID, list of object types, and the Aimsun model. The
    function takes the External ID and searches the model's catalog for the
    associated Aimsun object. If the object found exists and matches one of
    the given types in the list object_types, the function returns the found
    object.

    If the object doesn't exist or doesn't match the given types, the function
    raises a model error and returns None.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        external_id: An string of External ID type defined in
            aimsun_input_utils.
        object_types: A list of object types that can be found within Aimsun.
            Each item within the list should be strings.
    Returns:
        aimsun_object: If the object exists, the function returns an Aimsun
            object with the given external_id. If the object doesn't exist or
            doesn't match the object types, the function returns None.
    """
    if not isinstance(external_id, str):
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"External id type {external_id} is not str.")
        return None
    aimsun_objects = aimsun_model.getCatalog().findObjectsByExternalId(
        external_id)
    if not aimsun_objects:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"No objects have external id {external_id}.")
        return None
    if len(set(aimsun_obj.getId() for aimsun_obj in aimsun_objects)) != 1:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"Multiple objects have the external id {external_id}. This should"
            " not happen.")
        return None
    aimsun_object = aimsun_objects[0]
    if aimsun_object.getTypeName() not in object_types:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"{external_id} type is not in {object_types} but "
            f"{aimsun_object.getTypeName()}.")
        return None
    return aimsun_object


def get_object_per_internal_id(
    internal_id: aimsun_input_utils.InternalId,
    object_types: List[str],
    aimsun_model: GKModel
) -> GKObject:
    """Takes in an Internal ID, list of object types, and the Aimsun model. The
    function takes the Internal ID and searches the model's catalog for the
    associated Aimsun object. If the object found exists and matches one of
    the given types in the list object_types, the function returns the found
    object.

    If the object doesn't exist or doesn't match the given types, the function
    raises a model error and returns None.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        internal_id: An integer of Internal ID type defined in
            aimsun_input_utils.
        object_types: A list of object types that can be found within Aimsun.
            Each item within the list should be strings.

    Returns:
        aimsun_object: If the object exists, the function returns an Aimsun
            object with the given internal_id. If the object doesn't exist or
            doesn't match the object types, the function returns None.
    """
    aimsun_object = aimsun_model.getCatalog().find(internal_id)
    return aimsun_object
    if aimsun_object is None:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"No objects have internal id {internal_id}.")
        return None
    if aimsun_object.getTypeName() not in object_types:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"{internal_id} type is not in {object_types} but "
            f"{aimsun_object.getTypeName()}.")
        return None
    return aimsun_object


# ****************************************************************************
# ************************ Demand data util functions ************************
# ****************************************************************************


def create_new_configuration(
    centroid_config_ext_id: str,
    aimsun_model: GKModel,
    aimsun_system
):
    """Takes in a centroid configuration External ID, Aimsun model, and Aimsun
    system objects. The function searches the catalog for the associated
    centroid configuration object based on the given ID.

    If the External ID is already within the catalog, the function errors, as
    there should only be one centroid config per External ID.

    If the External ID isn't associated with an object, then the centroid
    configuration is created by assigning attributes. Finally, the Aimsun
    object is added to the root folder.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        centroid_config_ext_id: An External ID of type string. Should point to
            a new centroid config object.
    """
    centroid_config = aimsun_system.newObject(
        "GKCentroidConfiguration", aimsun_model)
    if aimsun_model.getCatalog().findObjectByExternalId(
            centroid_config_ext_id) is not None:
        aimsun_model.reportError(
            "create_centroids",
            f"{centroid_config_ext_id} centroid configuration already exists.")
        sys.exit()
    centroid_config.setName(centroid_config_ext_id)
    centroid_config.setExternalId(centroid_config_ext_id)
    centroid_config.activate()
    aimsun_model.getCreateRootFolder().findFolder(
        "GKModel::centroidsConf").append(centroid_config)


def get_vehicle_type_id(
    vehicle_type_name: aimsun_input_utils.VehicleTypeName,
    aimsun_model: GKModel
) -> aimsun_input_utils.VehicleTypeInternalId:
    """Takes in the vehicle type name and Aimsun model. It compares the vehicle
    type name with the VehicleTypeNames defined in aimsun_input_utils. If it
    matches one of the defined types, the function returns the internal ID for
    the associated VehicleTypeName.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        vehicle_type_name: A VehicleTypeName defined within aimsun_input_utils.
    Returns:
        internal_id: The associated Internal ID of either VehicleTypeNames.
            Throws an error if the parameter vehicle_type_name doesn't match
            either VehicleTypeName defined within aimsun_input_utils.
    """
    if vehicle_type_name == aimsun_input_utils.VehicleTypeName.RESIDENT:
        return (aimsun_input_utils.VehicleTypeInternalId
                .RESIDENT_TYPE_INTERNAL_ID)
    if vehicle_type_name == aimsun_input_utils.VehicleTypeName.TRAVELER:
        return (aimsun_input_utils.VehicleTypeInternalId
                .TRAVELLER_TYPE_INTERNAL_ID)
    aimsun_model.reportError(
        "create_OD_demand",
        f"Vehicle type name {vehicle_type_name} is not correct.")
    sys.exit()


def create_new_centroid(
    configuration, cen_ext_id: str, gk_point,
    aimsun_model: GKModel
):
    """Creates a centroid at location given by the GKPoint. The new centroid is
    part of the centroid configuration. A centroid is the center of mass for a
    TAZ. A TAZ (Traffic Analysis Zone) is a mutually exclusive plot of land
    that is a partition of the entire network. These are used as zones that
    serve as the starts and ends of vehicle trips.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        cen_ext_id: The External ID of the centroid. Has type str.
        configuration: The centroid configuration object associated with the
            Aimsun system.
        gk_point: An Aimsun GKPoint object denoting a point on the network.
    Returns:
        centroid: The created Aimsun object representing a centroid on the
            network.
    """
    cmd = aimsun_model.createNewCmd(aimsun_model.getType("GKCentroid"))
    cmd.setData(gk_point, configuration)
    aimsun_model.getCommander().addCommand(cmd)
    centroid = cmd.createdObject()
    centroid.setManualPosition(gk_point)
    centroid.setName(cen_ext_id)
    centroid.setExternalId(cen_ext_id)
    return centroid


def create_new_connection(
    source_object, destination_object, aimsun_model: GKModel
):
    """Creates a centroid connection between the source and the destination. A
    centroid connection is the connection between the centroid and Aimsun road
    sections within its respective TAZ.

    If the source object is a centroid, then the destination object should be a
    road section that can be used as an source object of another centroid. If
    the destination object is a centroid, then the source object should be a
    road section that can be used as a destination to another centroid.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        destination_object: The destination for the created connection. It
            should be an Aimsun object.
        source_object: The source of the created connection. It should be an
            Aimsun object.
    """
    cmd = aimsun_model.createNewCmd(aimsun_model.getType("GKCenConnection"))
    cmd.setData(source_object, destination_object)
    aimsun_model.getCommander().addCommand(cmd)


def create_centroids(
    centroid_connections_obj: aimsun_input_utils.CentroidConfiguration,
    aimsun_model: GKModel,
    aimsun_system,
    create_gk_point
):
    """Create a centroid configuration corresponding to the
    centroid_connections_obj.

    First, the function initiates the configuration, network, and osm objects
    associated with the given centroid connections object and global variables
    defined within aimsun_input_utils. Then, in order to add objects to the
    network and osm, the function sets AllowObjectsEdition to True for both. It
    then checks whether this change worked; if it didn't the code raises an
    error and quits.

    After checking for object edition, the function loops through each
    centroid connection Python object within the centroid connections object.
    Using the attributes of the centroid connection object, the function
    creates centroid Aimsun objects, as well as connections between the given
    centroid and the to/from centroids. If a from or to section is ever None,
    its ID is added to themissing_road_sections list. If that list has any
    IDs within it at the end of the for loop through the centroid connections,
    the code warns about missing road sections.

    Finally, the function sets object edition to false so that the objects
    won't be modified on accident elsewhere. The code then checks if this
    change was documented. If the change was not, the code raises an error and
    quits.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        centroid_connections_obj: A Python CentroidConfiguration object.
        create_gk_point: A function used to create Aimsun GKPoint objects. Its
            definition can be found within the python script
            end_to_end_model_importer.
    """
    centroid_configuration_external_id =\
        centroid_connections_obj.external_id
    create_new_configuration(
        centroid_configuration_external_id, aimsun_model, aimsun_system)
    config = aimsun_model.getCatalog().findObjectByExternalId(
        centroid_configuration_external_id)

    network = aimsun_model.getCatalog().findByName(
        aimsun_input_utils.NETWORK_LAYER_NAME)
    osm = aimsun_model.getCatalog().findByName(
        aimsun_input_utils.OSM_LAYER_NAME)
    network.setAllowObjectsEdition(True)
    osm.setAllowObjectsEdition(True)
    if not network.allowObjectsEdition():
        aimsun_model.reportError(
            "create_centroids",
            "Error Network ObjectsEdition not allowed.")
        sys.exit()
    if not osm.allowObjectsEdition():
        aimsun_model.reportError(
            "create_centroids",
            "Error OSM ObjectsEdition not allowed.")
        sys.exit()

    missing_road_sections = set()
    for centroid_connection in (
            centroid_connections_obj.centroid_connection_list):
        lat = centroid_connection.center_latitude_epsg_32610
        lon = centroid_connection.center_longitude_epsg_32610
        centroid = create_new_centroid(
            config, centroid_connection.external_id, create_gk_point(lon, lat),
            aimsun_model)
        for from_section_id in centroid_connection.from_section_internal_ids:
            from_section = get_object_per_internal_id(
                from_section_id, ['GKSection'], aimsun_model)
            if from_section is None:
                missing_road_sections.add(from_section_id)
            else:
                create_new_connection(centroid, from_section, aimsun_model)

        for to_section_id in centroid_connection.to_section_internal_ids:
            to_section = get_object_per_internal_id(
                to_section_id, ['GKSection'], aimsun_model)
            if to_section is None:
                missing_road_sections.add(to_section_id)
            else:
                create_new_connection(to_section, centroid, aimsun_model)

    if missing_road_sections:
        aimsun_model.reportError(
            "create_centroids",
            f"WARNING: sections {missing_road_sections} not found.")
    network.setAllowObjectsEdition(False)
    osm.setAllowObjectsEdition(False)
    if network.allowObjectsEdition():
        aimsun_model.reportError(
            "create_centroids",
            "Error Network ObjectsEdition allowed.")
    if osm.allowObjectsEdition():
        aimsun_model.reportError(
            "create_centroids",
            "Error OSM ObjectsEdition allowed.")


def create_od_matrices(
    od_demand_matrices: aimsun_input_utils.OriginDestinationMatrices,
    aimsun_model: GKModel,
    aimsun_system,
    get_duration,
    get_from_time
):
    """This function loads the OD matrix to AIMSUN from the OD matrix file. An
    OD matrix (Origin-Destination matrix) provides the number of trips
    departing from every origin centroid to every other destination centroid,
    along with the departure time within the time period.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        od_demand_matrices: A Python OriginDestinationMatrices object. Its
            attributes store the data needed to recreate a GKODMatrix within
            Aimsun.
        get_duration: A function used to create Aimsun GKTimeDuration objects.
            Its definition can be found within the python script
            end_to_end_model_importer.
        get_from_time: A function used to create QTime objects. Its definition
            can be found within the python script end_to_end_model_importer.
    """
    centroid_conf = get_object_per_external_id(
        od_demand_matrices.centroid_configuration_external_id,
        ['GKCentroidConfiguration'], aimsun_model)

    existing_od_demand_matrix = set()
    for od_matrix in od_demand_matrices.od_matrices:
        od_demand_external_id = aimsun_input_utils.od_matrix_name_generation(
            od_matrix.begin_time_interval, od_matrix.vehicle_type)
        if aimsun_model.getCatalog().findObjectByExternalId(
                od_demand_external_id) is not None:
            aimsun_model.reportError(
                "load_od_demand",
                f"{od_demand_external_id} already exists.")
            sys.exit()
        matrix = aimsun_system.newObject("GKODMatrix", aimsun_model)
        matrix.setName(od_demand_external_id)
        matrix.setExternalId(od_demand_external_id)
        centroid_conf.addODMatrix(matrix)
        existing_od_demand_matrix.add(od_demand_external_id)
        # set vehicle ID
        gk_vehicle = get_object_per_internal_id(
            get_vehicle_type_id(od_matrix.vehicle_type, aimsun_model),
            ['GKVehicle'],
            aimsun_model)
        if gk_vehicle is None:
            sys.exit()
        matrix.setVehicle(gk_vehicle)
        # set time
        matrix.setFrom(get_from_time(od_matrix.begin_time_interval))

        matrix.setDuration(
            get_duration(od_matrix.begin_time_interval,
                         od_matrix.end_time_interval))

        for od_trips_count in od_matrix.od_trips_count:
            # extract values from line
            from_centroid = get_object_per_external_id(
                od_trips_count.origin_centroid_external_id, ['GKCentroid'],
                aimsun_model)
            to_centroid = get_object_per_external_id(
                od_trips_count.destination_centroid_external_id, ['GKCentroid'],
                aimsun_model)
            if from_centroid is None or to_centroid is None:
                sys.exit()
            trips = od_trips_count.num_trips
            matrix.setTrips(from_centroid, to_centroid, trips)


# ****************************************************************************
# *********************** Network data util functions ************************
# ****************************************************************************


def set_section_object_attributes(
    aimsun_model: GKModel,
    gk_section_obj: GKSectionObject,
    aimsun_section_object: aimsun_input_utils.AimsunSectionObject
):
    """Takes in the Aimsun model, an Aimsun GKSectionObject, and an
    associated Python AimsunSectionObject. The function sets the attributes of
    the Python AimsunSectionObject to the Aimsun GKSectionObject, checking
    whether the layer attribute is consistent across the levels of abstraction
    in the Python AimsunSectionObject.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_section_object: A Python AimsunSectionObject that contains the
            data needed for the Aimsun GKSectionObject.
        gk_section: An Aimsun GKSectionObject that needs its attributes set.
    """
    gk_section_obj.setExternalId(aimsun_section_object.external_id)
    if not hasattr(aimsun_section_object, 'name'):
        aimsun_section_object.name = aimsun_section_object.external_id
    gk_section_obj.setName(aimsun_section_object.name)
    gk_section = get_object_per_internal_id(
        aimsun_section_object.aimsun_section_internal_id, ['GKSection'],
        aimsun_model)
    if gk_section is None:
        sys.exit()
    if hasattr(aimsun_section_object, 'layer_id'):
        gk_layer = get_object_per_internal_id(
            aimsun_section_object.layer_id, ['GKLayer'], aimsun_model)
        if gk_layer is None:
            sys.exit()
        if gk_section.getLayer() != gk_layer:
            aimsun_model.reportError(
                "aimsun_utils_functions",
                "The section's layer is not the aimsun_section_object's layer.")
            sys.exit()
    else:
        gk_layer = gk_section.getLayer()
    gk_section_obj.setLayer(gk_layer)
    aimsun_model.getGeoModel().add(gk_layer, gk_section_obj)
    gk_section.addTopObject(gk_section_obj)


def get_section_object_attributes(
    aimsun_model: GKModel,
    gk_section: GKSectionObject,
    aimsun_section_object: aimsun_input_utils.AimsunSectionObject
):
    """Takes in the Aimsun model, an Aimsun GKSectionObject, and an associated
    Python AimsunSectionObject. The function gets the attributes of the Aimsun
    GKSectionObject and assigns the data to the Python AimsunSectionObject,
    checking whether the layer and section attributes of the Aimsun
    GKSectionObject exist.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_section_object: A Python object that needs its attributes set.
        gk_section: An Aimsun object that contains the data needed for the
            Python object.
    """
    aimsun_section_object.name = gk_section.getName()
    if gk_section.getLayer() is None:
        aimsun_model.reportError(
            'aimsun_utils_functions',
            f'Aimsun Object {gk_section.getId()} is not associated '
            'to a layer.')
        sys.exit()
    aimsun_section_object.layer_id = gk_section.getLayer().getId()
    if gk_section.getSection() is None:
        aimsun_model.reportError(
            'aimsun_utils_functions',
            f'Aimsun Object {gk_section.getId()} is not associated '
            'to a section.')
        sys.exit()
    aimsun_section_object.aimsun_section_internal_id = (
        gk_section.getSection().getId())
    aimsun_section_object.from_lane = gk_section.getFromLane()
    aimsun_section_object.to_lane = gk_section.getToLane()
    aimsun_section_object.length = gk_section.getLength()
    aimsun_section_object.position = gk_section.getPosition()


def update_speed_and_capacity(
    speed_and_capacities: aimsun_input_utils.SectionSpeedLimitsAndCapacities,
    aimsun_model: GKModel
):
    """Update speed limits and capacities of Aimsun road sections from the
    speed_and_capacities object.

    Takes in a Python SectionSpeedLimitsAndCapacities object and the Aimsun
    model. The function loops through the Python object and sets the speed
    limits and road capacities by looking up the section object through
    Internal ID.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        speed_and_capacities: A Python SectionSpeedLimitsAndCapacities object.
            Stores the speed limit and road capacity data that will be matched
            to road sections within Aimsun.
    """
    for speed_and_capacity in (
            speed_and_capacities.speed_limit_and_capacity_list):
        section = get_object_per_internal_id(
            speed_and_capacity.section_internal_id, ['GKSection'], aimsun_model)
        if not section:
            continue
        section.setSpeed(speed_and_capacity.speed_limit_in_km_per_hour)
        section.setCapacity(speed_and_capacity.capacity_in_vehicles_per_hour)


def create_metering(
    metering: aimsun_input_utils.Metering,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Create a GKMetering corresponding to the Metering.

    The function does this by using the attribute data of the Python metering
    object and assigning the related attributes from the Python object to the
    attributes of the Aimsun object. During this process, the function will
    check if the metering's layer exists and is on the same layer as the
    section. A metering is a device used to regulate the flow of vehicles.
    Meterings hold back the flow of vehicles and released them based on their
    type.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        metering: A Python Metering object. Its attributes hold the data for an
            Aimsun metering object.
    Raises:
        aimsun_report_error: If a metering's layer doesn't exist or if the
            metering and section layers are not the same, the code raises an
            error and quits.
    """
    # Creates new GKDetector object.
    gk_metering = aimsun_system.newObject('GKMetering', aimsun_model)
    set_section_object_attributes(aimsun_model, gk_metering, metering)
    gk_metering.setLanes(metering.to_lane, metering.from_lane)
    gk_metering.setLength(metering.length)
    gk_metering.setPosition(metering.position)

    # GKMetering attributes.
    if metering.metering_type in [aimsun_input_utils.MeteringType.FLOW,
                                  aimsun_input_utils.MeteringType.FLOW_ALINEA]:
        gk_metering.setVehFlow(metering.vehicle_flow)
    gk_metering.setDataValue(
        aimsun_model.getColumn("GKMetering::typeAtt"),
        int(metering.metering_type))


def convert_gkmetering_to_metering_class(
    gk_metering: GKMetering,
    aimsun_model: GKModel
) -> aimsun_input_utils.Metering:
    """Return Metering corresponding to the GKMetering to export.

    The function pulls the attributes of the Aimsun object and assigns them to
    similarly-named attributes within the Python object.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        gk_metering: An Aimsun GKMetering object that needs to be converted to
            a Python object for exporting.
    Returns:
        metering: The Python Metering object created from the attributes of the
            gk_metering Aimsun object.
    Raises:
        aimsun_report_error: Throws an error and quits if the
            GKMetering object doesn't have an associated layer or section.
    """
    metering = aimsun_input_utils.Metering()
    get_section_object_attributes(aimsun_model, gk_metering, metering)
    metering.external_id = f'meter_on_{metering.aimsun_section_internal_id}'

    metering.metering_type = aimsun_input_utils.MeteringType(
        gk_metering.getDataValue(
            aimsun_model.getColumn("GKMetering::typeAtt"))[0])

    if metering.metering_type in [aimsun_input_utils.MeteringType.FLOW,
                                  aimsun_input_utils.MeteringType.FLOW_ALINEA]:
        metering.vehicle_flow = gk_metering.getVehFlow()
    return metering


def get_gk_detector_attributes(att: str, aimsun_model: GKModel) -> Any:
    """Takes in some attribute and the Aimsun model object. This function
    searches the model for the given attribute, and if it exists, returns the
    attribute from the model.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        att: An attribute of some Aimsun object, described as a string.
    Returns:
        attribute: An Aimsun object attribute. If the model does not have the
            attribute att, the function returns nothing.
    Raises:
        aimsun_report_error: If att does not exist, the function throws an
            error and quits.
    """
    attribute = aimsun_model.getColumn(f"GKDetector::{att}")
    if attribute is None:
        aimsun_model.reportError(
            'aimsun_utils_functions',
            (f'Attribute does not exists in Aimsun: GKDetector::{att}.'
             ' Quitting on error.'))
        sys.exit()
    return attribute


def get_gk_detector_attributes_value(
    att: str, gk_detector: GKDetector, aimsun_model: GKModel
) -> Any:
    """Takes in an attribute, Aimsun Detector object, and Aimsun model object.
    The function searches for the Aimsun attribute, then returns the data value
    in the Aimsun Detector object associated with said attribute.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        att: An attribute of some Aimsun object, described as a string.
        gk_detector: An Aimsun GKDetector object. The attribute in question
            is found within this object.

    Returns:
        attribute_value: The first attribute value in the attribute_value
            list. THe list is associated with the given Aimsun Detector object.
    """
    attribute = get_gk_detector_attributes(att, aimsun_model)
    attribute_value = gk_detector.getDataValue(attribute)
    return attribute_value[0]


def convert_gkdetector_to_detector_class(
    gk_detector: GKDetector,
    aimsun_model: GKModel
) -> aimsun_input_utils.Detector:
    """Returns the Detector object corresponding to the given GKDetector Aimsun
    object that is being exported. The function pulls the attributes of the
    Aimsun object and assigns them to similarly-named attributes within the
    Python object, which can be exported later as a pickle file.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        gk_detector: An Aimsun GKDetector object. This object will be converted
            into an Aimsun object.
    Returns:
        detector: The Python Detector object. It is created from the Aimsun
            GKDetector object.
    Raises:
        aimsun_report_error: Throws an error and quits if the GKDetector object
            doesn't have an associated layer or section.
    """
    detector = aimsun_input_utils.Detector()
    # GKObject attributes.
    detector.external_id = create_detector_external_id(gk_detector.getId())
    get_section_object_attributes(aimsun_model, gk_detector, detector)

    # GKDetectors attributes.
    # GKDetector has a method getCoverage(). Coverage describes the percentage
    # of lanes a detector or detector station should cover in order to be
    # included in the adjustment process. However, because there is no function
    # setCoverage(), we do not export detector coverage data as we do not know
    # how to import it back.
    detector.detect_count = get_gk_detector_attributes_value(
        'countAtt', gk_detector, aimsun_model)
    detector.detect_density = get_gk_detector_attributes_value(
        'densityAtt', gk_detector, aimsun_model)
    detector.detect_equipped_vehicles = get_gk_detector_attributes_value(
        'equippedAtt', gk_detector, aimsun_model)
    detector.detect_headway = get_gk_detector_attributes_value(
        'headwayAtt', gk_detector, aimsun_model)
    detector.detect_occupancy = get_gk_detector_attributes_value(
        'occupancyAtt', gk_detector, aimsun_model)
    detector.detect_presence = get_gk_detector_attributes_value(
        'presenceAtt', gk_detector, aimsun_model)
    detector.detect_speed = get_gk_detector_attributes_value(
        'speedAtt', gk_detector, aimsun_model)
    detector.extended_length = get_gk_detector_attributes_value(
        'extendedLengthAtt', gk_detector, aimsun_model)
    detector.number_of_lanes = get_gk_detector_attributes_value(
        'numberOfLanesAtt', gk_detector, aimsun_model)
    detector.offset = get_gk_detector_attributes_value(
        'offsetAtt', gk_detector, aimsun_model)
    detector.position_from_end = gk_detector.getPositionFromEnd()
    return detector


def create_detector(
    detector: aimsun_input_utils.Detector,
    is_flow_detector: bool,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Takes in a Python Detector object, a boolean denoting if the detector is
    a flow detector, the Aimsun model object, and Aimsun system object. The
    function creates an Aimsun GKDetector object by taking the Python object's
    attribute data and assigning them to the GKDetector object. A detector is
    an object that lies on a road segment. It records vehicle flow and speed
    for vehicles passing over itself.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        detector: A Python Detector object. This object has the data that needs
            to be imported into Aimsun.
        is_flow_detector: A boolean denoting whether the Python Detector object
            is a flow detector or not.
    """
    # Creates new GKDetector object.
    gk_detector = aimsun_system.newObject("GKDetector", aimsun_model)
    set_section_object_attributes(aimsun_model, gk_detector, detector)
    gk_section = get_object_per_internal_id(
        detector.aimsun_section_internal_id, ['GKSection'], aimsun_model)
    if gk_section is None:
        sys.exit()
    gk_layer = gk_section.getLayer()
    aimsun_model.getGeoModel().add(gk_layer, gk_detector)
    gk_detector.setLayer(gk_layer)
    if hasattr(gk_detector, 'layer_id'):
        if gk_layer != get_object_per_internal_id(
                detector.layer_id, ['GKLayer'], aimsun_model):
            aimsun_model.reportError(
                "create_detectors",
                "The section's layer is not the detector's layer.")
            sys.exit()
    gk_section.addTopObject(gk_detector)

    if is_flow_detector:
        gk_detector.setLength(4.5)
        gk_detector.setPosition(gk_section.length2D() / 2.0)
        # https://github.com/Fremont-project/whole-code-repo/issues/407
        if detector.external_id == 'pems_detector_418422':
            # HOV lane
            gk_detector.setLanes(0, 0)
        elif detector.external_id == 'pems_detector_402793':
            gk_detector.setLanes(1, len(gk_section.getLanes()) - 1)
        else:
            # By defaults the detector covers all the lanes in this section.
            gk_detector.setLanes(0, len(gk_section.getLanes()) - 1)
    else:
        gk_detector.setLength(detector.length)
        gk_detector.setPosition(detector.position)

        # GKDetector attributes.
        for key, value in {
            'countAtt': detector.detect_count,
            'densityAtt': detector.detect_density,
            'equippedAtt': detector.detect_equipped_vehicles,
            'headwayAtt': detector.detect_headway,
            'occupancyAtt': detector.detect_occupancy,
            'presenceAtt': detector.detect_presence,
            'speedAtt': detector.detect_speed,
            'extendedLengthAtt': detector.extended_length,
            'numberOfLanesAtt': detector.number_of_lanes,
            'offsetAtt': detector.offset,
        }.items():
            gk_detector.setDataValue(
                get_gk_detector_attributes(key, aimsun_model), value)
        gk_detector.setPositionFromEnd(detector.position_from_end)
        gk_detector.setLanes(detector.from_lane, detector.to_lane)


def create_detectors(
    detectors: aimsun_input_utils.Detectors,
    is_flow_detectors: bool,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Creates a group of detectors from the list of Python Detector objects
    within the Python Detectors aggregate object.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        detectors: A Python Detectors object. This object has the data that
            needs to be imported into Aimsun.
        is_flow_detectors: A boolean denoting whether the Python Detectors
            object is a group of flow detectors or not.
    """
    for detector in detectors.detector_list:
        create_detector(
            detector, is_flow_detectors, aimsun_model, aimsun_system)


def create_control_metering(
    aimsun_control_plan: GKControlPlan,
    control_metering: aimsun_input_utils.ControlMetering,
    mapping_control_metering_type: Dict[
        aimsun_input_utils.ControlMeteringType, Any],
    aimsun_model: GKModel
):
    """Creates a new GKControlMetering object within the Aimsun Control Plan
    using the data saved within the Python ControlMetering object.

    Args:
        aimsun_control_plan: An Aimsun GKControlPlan object. It needs an Aimsun
            control metering to be added.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        control_metering: A Python ControlMetering object. The data from this
            object will be used to create an Aimsun GKControlMetering.
        mapping_control_metering_type: A dict of control metering types.
    """
    metering_external_id = control_metering.metering_external_id
    aimsun_metering = get_object_per_external_id(
        metering_external_id, ['GKMetering'], aimsun_model)
    aimsun_control_metering = aimsun_control_plan.createControlMetering(
        aimsun_metering)
    aimsun_control_metering.setControlMeteringType(
        mapping_control_metering_type[control_metering.control_metering_type])
    aimsun_model.getCommander().addCommand(None)


def create_phase(
    control_plan_node: GKControlJunction,
    junction: aimsun_input_utils.ControlJunction,
    aimsun_model: GKModel
):
    """Creates a phase using the data from a Python ControlJunction object. A
    phase is an object that holds all the signal groups that will be green
    during the given time period. Signal groups are all the stoplights that
    flash the same color at any given point in an intersection. The resulting
    phase data is added to a control plan node.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        control_plan_node: The Aimsun GKControlJunction that may need extra
            data depending on the type of junction type.
        junction: The Python object storing the control junction data. Its
            attributes are assigned to their mirror counterparts in an Aimsun
            object.
    """
    # This variable is made to shorten line lengths.
    j_type = junction.junction_type
    # If the control junction is not actuated.
    if j_type in [
        aimsun_input_utils.ControlJunctionType.UNSPECIFIED,
        aimsun_input_utils.ControlJunctionType.UNCONTROLLED,
        aimsun_input_utils.ControlJunctionType.FIXED_CONTROL,
        aimsun_input_utils.ControlJunctionType.EXTERNAL
    ]:
        for phase in junction.phases:
            # phase_characteristics is given by
            # NE3 generate_phases_characteristics
            aimsun_phase = control_plan_node.createPhase()
            aimsun_phase.setFrom(phase.from_time)
            aimsun_phase.setDuration(phase.duration)
            aimsun_phase.setInterphase(phase.interphase)
            for signal in phase.signals:
                aimsun_phase.addSignal(signal.signal)

    # If the control junction is actuated.
    elif j_type == aimsun_input_utils.ControlJunctionType.ACTUATED:
        # addBarrier adds a barrier at the specified second.
        for barrier in junction.barriers:
            control_plan_node.addBarrier(barrier)

        control_plan_node.setRestInRed(junction.rest_in_red)
        control_plan_node.setMatchesOffsetWithEndOfPhase(
            junction.matches_offset_with_end_of_phase)
        control_plan_node.setYellowTime(junction.yellow_time)
        control_plan_node.setSingleEntry(junction.single_entry)

        for phase in junction.phases:
            aimsun_phase = control_plan_node.createPhase()

            aimsun_phase.setFrom(phase.from_time)
            aimsun_phase.setDuration(phase.duration)
            aimsun_phase.setIdRing(phase.id_ring)
            aimsun_phase.setInterphase(phase.interphase)
            aimsun_phase.setRecall(phase.recall)
            aimsun_phase.setIsDefault(phase.is_default)
            aimsun_phase.setMinDuration(phase.min_duration)
            aimsun_phase.setMaxDuration(phase.max_duration)
            aimsun_phase.setPassageTime(phase.passage_time)
            aimsun_phase.setPermissivePeriodFrom(phase.permissive_period_from)
            aimsun_phase.setPermissivePeriodTo(phase.permissive_period_to)
            aimsun_phase.setForceOff(phase.force_off)
            aimsun_phase.setHold(phase.hold)
            aimsun_phase.setMaximumInitial(phase.maximum_initial)
            aimsun_phase.setSecondsActuation(phase.seconds_actuation)
            aimsun_phase.setUsingGapReduction(phase.gap_reduction)
            aimsun_phase.setMinimumGap(phase.minimum_gap)
            aimsun_phase.setTimeBeforeReduce(phase.time_before_reduce)
            aimsun_phase.setTimeToReduce(phase.time_to_reduce)

            for signal in phase.signals:
                aimsun_phase.addSignal(signal.signal)

            for control_detector in phase.detectors:
                aimsun_detector = (
                    get_object_per_external_id(
                        control_detector.detector_external_id,
                        ['GKDetector'], aimsun_model))
                if aimsun_detector is None:
                    sys.exit()
                gk_control_detector = aimsun_phase.createControlDetector(
                    aimsun_detector)
                gk_control_detector.setLocking(control_detector.locking)
                gk_control_detector.setCallDelay(control_detector.call_delay)
                gk_control_detector.setPhaseActivation(
                    control_detector.phase_activation)
                gk_control_detector.setPhaseExtension(
                    control_detector.phase_extension)
                aimsun_phase.addControlDetector(gk_control_detector)
    else:
        aimsun_model.reportError(
            'import_master_control_plan',
            "Error, the  type of the control junction type "
            f"{junction.junction_type} is not correct.")
        sys.exit()


def create_control_plan(
    control_plan: aimsun_input_utils.ControlPlan,
    mapping_control_metering_type: Dict[
        aimsun_input_utils.ControlMeteringType, Any],
    gk_object_status_modified,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Creates an Aimsun GKControlPlan object from the attributes of the
    ControlPlan Python object. A control plan is an object that manages the
    cycles, duration of phases per signal, and signal groups at multiple
    intersections within the network. The data from the Python object is added
    to the attributes of the Aimsun object.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        control_plan: A Python ControlPlan object that stores the data needed
            to create a GKControlPlan object within Aimsun.
        gk_object_status_modified: The status of the Aimsun Control Plan after
            this function modifies its attributes.
        mapping_control_metering_type: A dict of control metering types.
    Returns:
        aimsun_control_plan: An Aimsun GKControlPlan object.
    Raises:
        aimsun_report_error: Quits if the associated GKNode in a junction
            does not exist.
    """
    aimsun_control_plan = aimsun_system.newObject("GKControlPlan", aimsun_model)
    aimsun_model.getCreateRootFolder().findFolder(
        'GKModel::controlPlans').append(aimsun_control_plan)
    aimsun_control_plan.setName(control_plan.name)
    aimsun_control_plan.setExternalId(control_plan.external_id)
    for junction in control_plan.control_junctions:
        node_id = int(junction.node_id)
        node = get_object_per_internal_id(
            node_id, ['GKNode'], aimsun_model)
        if node is None:
            sys.exit()
        # We create a yellow box to forbid vehicles to engage in the
        # intersection if it is congested.
        node.setYellowBox(True)

        control_plan_node = aimsun_control_plan.createControlJunction(node_id)
        control_plan_node.setControlJunctionType(junction.junction_type)
        control_plan_node.setCycle(junction.cycle)
        control_plan_node.setOffset(junction.offset)
        create_phase(control_plan_node, junction, aimsun_model)
    for control_metering in control_plan.control_meterings:
        create_control_metering(
            aimsun_control_plan, control_metering,
            mapping_control_metering_type, aimsun_model)
    aimsun_control_plan.setStatus(gk_object_status_modified)
    return aimsun_control_plan


def import_master_control_plan(
    imported_master_control_plan: aimsun_input_utils.MasterControlPlan,
    aimsun_model: GKModel,
    aimsun_system: GKSystem,
    gk_object_status_modified,
    create_master_control_plan_item,
    mapping_control_metering_type: Dict[
        aimsun_input_utils.ControlMeteringType, Any]
):
    """Takes in the Aimsun model and an imported master control plan and
    unpacks the metering, detector, and control plan data. Then the function
    adds the imported master control plan to the Aimsun model.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        create_master_control_plan_item: The function that creates master
            control plan items.
        gk_object_status_modified: The status of the Aimsun Control Plan after
            this function modifies its attributes.
        imported_master_control_plan: A MasterControlPlan object created from
            importing the .pkl file from the saved filepath.
        mapping_control_metering_type: A dict of control metering types.
    """
    # Import the meterings.
    for metering in imported_master_control_plan.meterings:
        create_metering(
            metering, aimsun_model, aimsun_system)
    # Import the detectors.
    for detector in imported_master_control_plan.detectors:
        create_detector(
            detector, False, aimsun_model, aimsun_system)
    # Import the control plans.
    for control_plan in imported_master_control_plan.control_plans:
        create_control_plan(
            control_plan,
            mapping_control_metering_type,
            gk_object_status_modified,
            aimsun_model,
            aimsun_system)
    # Create the master control plan.
    master_control_plan_aimsun = aimsun_system.newObject(
        'GKMasterControlPlan', aimsun_model)
    master_control_plan_aimsun.setName(imported_master_control_plan.name)
    master_control_plan_aimsun.setExternalId(
        imported_master_control_plan.external_id)
    for item in imported_master_control_plan.schedule:
        # Here we check if control plan already exists based on its name.
        # We should make sure that control plan name is unique!
        control_plan = get_object_per_external_id(
            item.control_plan_external_id, ['GKControlPlan'],
            aimsun_model)
        if control_plan is None:
            sys.exit()
        # We add the control plan to the master control plan.
        master_control_plan_item = create_master_control_plan_item()
        master_control_plan_item.setControlPlan(control_plan)
        master_control_plan_item.setFrom(item.from_time)
        master_control_plan_item.setDuration(item.duration)
        master_control_plan_item.setZone(item.zone)
        master_control_plan_aimsun.addToSchedule(master_control_plan_item)
    aimsun_model.getCreateRootFolder().findFolder(
        'GKModel::masterControlPlans').append(master_control_plan_aimsun)


def add_turning_closing_change(
    scenario_change: aimsun_input_utils.TurningClosingChange,
    aimsun_policy: GKPolicy,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Takes in the model, scenario, and policy in order to create a scenario
    within Aimsun. The scenario is then added onto the passed in policy.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_policy: The policy object within Aimsun.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        scenario_change: The TurningClosingChange Python object containing the
            data for a possible scenario to control traffic at one
            intersection.
    """
    aimsun_scenario_change = aimsun_system.newObject(
        'GKTurningClosingChange', aimsun_model)
    from_section = get_object_per_internal_id(
        scenario_change.from_section_internal_id,
        ['GKSection'], aimsun_model)
    to_section = get_object_per_internal_id(
        scenario_change.to_section_internal_id,
        ['GKSection'], aimsun_model)
    if not scenario_change.name:
        aimsun_model.reportError(
            'import_traffic_management',
            f"The scenario change {scenario_change} does not have a name. "
            "Quitting on error.")
        sys.exit()
    if not scenario_change.external_id:
        aimsun_model.reportError(
            'import_traffic_management',
            f"The scenario change {scenario_change} does not have an External "
            "ID. Quitting on error.")
        sys.exit()
    aimsun_scenario_change.setName(scenario_change.name)
    aimsun_scenario_change.setExternalId(scenario_change.external_id)
    aimsun_scenario_change.setFromSection(from_section)
    aimsun_scenario_change.setToSection(to_section)
    aimsun_policy.addChange(aimsun_scenario_change)


def import_scenarios(
    scenario: aimsun_input_utils.TrafficManagementStrategy,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Takes in the Aimsun model and the .pkl Traffic Management object and
    unpacks the data into Aimsun. It calls the method add_scenario_change in
    order to unpack the data from each possible scenario.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        scenario: The Python object containing the data for a
            Traffic Management strategy.
    """
    aimsun_strategy = aimsun_system.newObject('GKStrategy', aimsun_model)
    aimsun_strategy.setName(scenario.name)
    aimsun_strategy.setExternalId(scenario.external_id)
    for policy in scenario.policies:
        aimsun_policy = aimsun_system.newObject('GKPolicy', aimsun_model)
        if not policy.name:
            aimsun_model.reportError(
                'import_traffic_management',
                f"The policy {policy} does not have a name. Quitting on error.")
            sys.exit()
        if not policy.external_id:
            aimsun_model.reportError(
                'import_traffic_management',
                f"The policy {policy} does not have an External ID. Quitting "
                "on error.")
            sys.exit()
        aimsun_policy.setName(policy.name)
        aimsun_policy.setExternalId(policy.external_id)
        aimsun_strategy.addPolicy(aimsun_policy)

        for scenario_change in policy.scenario_changes:
            if (scenario_change.scenario_change_type != aimsun_input_utils
                    .ScenarioChangeType.TURNING_RESTRICTION):
                aimsun_model.reportError(
                    'import_traffic_management',
                    f"The scenario type {scenario_change.scenario_change_type} "
                    "is not a turning restriction. Quitting on error.")
                sys.exit()
            add_turning_closing_change(
                scenario_change,
                aimsun_policy,
                aimsun_model,
                aimsun_system)
    aimsun_model.getCreateRootFolder().findFolder(
        'GKModel::strategies').append(aimsun_strategy)


def generate_turning_closing_change(
    aimsun_scenario_change: GKTurningClosingChange,
    aimsun_model: GKModel
) -> aimsun_input_utils.TurningClosingChange:
    """Takes the current Aimsun turning closing change and converts it into a
    Python object in order to export it to a .pkl file.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_scenario_change: The Aimsun turning closing change that needs to
            be converted into a Python object for exporting.
    Returns:
        turning_closing_change: A Python object created from the attributes of
            the argument aimsun_scenario_change. This will be exported in the
            .pkl file in the method export_strategy.
    """
    turning_closing_change = aimsun_input_utils.TurningClosingChange()
    turning_closing_change_name = aimsun_scenario_change.getName()
    turning_change_external_id = aimsun_scenario_change.getExternalId()
    if not turning_closing_change_name and not turning_change_external_id:
        aimsun_model.reportError(
            'export_traffic_management',
            "The scenario change does not have a name neither an external id. "
            "Quitting on error.")
        sys.exit()
    if not turning_closing_change_name:
        print(("The scenario change does not have a name. Setting it to "
               f"external id {turning_change_external_id}."))
        turning_closing_change_name = turning_change_external_id
    if not turning_change_external_id:
        print(("The scenario change does not have a external id. Setting it to "
               f"name {turning_closing_change_name}."))
        turning_change_external_id = turning_closing_change_name
    turning_closing_change.name = turning_closing_change_name
    turning_closing_change.external_id = turning_change_external_id
    turning_closing_change.to_section_internal_id = (
        aimsun_scenario_change.getToSection().getId())
    turning_closing_change.from_section_internal_id = (
        aimsun_scenario_change.getFromSection().getId())
    turning_closing_change.scenario_change_type = (
        aimsun_input_utils.ScenarioChangeType(
            aimsun_scenario_change.getChangeType()))
    if (turning_closing_change.scenario_change_type
            != aimsun_input_utils.ScenarioChangeType.TURNING_RESTRICTION):
        aimsun_model.reportError(
            'export_traffic_management',
            "The code is wrong, please change it.")
    return turning_closing_change


def generate_policy(
    aimsun_policy: GKPolicy,
    mapping_scenario_change_type: Dict[
        aimsun_input_utils.ScenarioChangeType, Any],
    aimsun_model: GKModel
) -> aimsun_input_utils.TrafficPolicy:
    """Takes the current Aimsun policy and converts it into a Python object
    in order to export it to a .pkl file. A policy is a collection of actions
    that are activated together at the same time. Actions are single effect
    events that build a situation on the network that may change driver action.
    Policies are made from strategies.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_policy: The Aimsun policy that needs to be converted into
            a Python object for exporting.
        mapping_scenario_change_type: The list of scenario change types.
    Returns:
        policy: A Python object created from the attributes of the argument
            aimsun_policy. This will be exported in the .pkl file in the method
            export_strategy.
    """
    policy = aimsun_input_utils.TrafficPolicy()
    policy_name = aimsun_policy.getName()
    policy_external_id = aimsun_policy.getExternalId()
    if not policy_name and not policy_external_id:
        aimsun_model.reportError(
            'export_traffic_management',
            "The policy does not have a name neither an external id. Quitting "
            "on error.")
        sys.exit()
    if not policy_name:
        print(("The policy does not have a name. Setting it to external id "
               f"{policy_external_id}."))
        policy_name = policy_external_id
    if not policy_external_id:
        print(("The policy does not have a external id. Setting it to name "
               f"{policy_name}."))
        policy_external_id = policy_name
    policy.name = policy_name
    policy.external_id = policy_external_id
    policy.scenario_changes = []
    aimsun_scenario_changes = aimsun_policy.getChanges()
    for aimsun_scenario_change in aimsun_scenario_changes:
        aimsun_scenario_change_type = aimsun_scenario_change.getChangeType()
        if aimsun_scenario_change_type != mapping_scenario_change_type[
                aimsun_input_utils.ScenarioChangeType.TURNING_RESTRICTION]:
            aimsun_model.reportError(
                'N2_export_traffic_management',
                f"The scenario type {aimsun_scenario_change_type} is not a "
                "turning restriction. Quitting on error.")
            sys.exit()
        policy.scenario_changes.append(generate_turning_closing_change(
            aimsun_scenario_change, aimsun_model))
    return policy


def export_strategy(
    filepath: str,
    mapping_scenario_change_type: Dict[
        aimsun_input_utils.ScenarioChangeType, Any],
    aimsun_model: GKModel
):
    """Takes the current Aimsun strategy and converts it into a Python object
    in order to export it to a .pkl file.

    The Python object is an object that holds the output of generate_strategies
    as an attribute.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        filepath: The absolute path where the Python object will be exported.
        mapping_scenario_change_type: The list of scenario change types.
    """
    traffic_strategy = aimsun_input_utils.TrafficManagementStrategy()
    traffic_strategy.policies = []

    aimsun_strategies = aimsun_model.getCatalog().getObjectsByType(
        aimsun_model.getType('GKStrategy')).values()
    if len(aimsun_strategies) != 1:
        aimsun_model.reportError(
            'N2_export_traffic_management',
            "There is more than one strategy. Please change the code. Quitting "
            "on error.")
        sys.exit()
    aimsun_strategy = list(aimsun_strategies)[0]
    strategy_name = aimsun_strategy.getName()
    strategy_external_id = aimsun_strategy.getExternalId()
    if not strategy_name and not strategy_external_id:
        aimsun_model.reportError(
            'N2_export_traffic_management',
            "The strategy does not have a name neither an external id. Quitting"
            " on error.")
        sys.exit()
    if not strategy_name:
        print(("The strategy does not have a name. Setting it to external id "
               f"{strategy_external_id}."))
        strategy_name = strategy_external_id
    if not strategy_external_id:
        print(("The policy does not have a external id. Setting it to name "
               f"{strategy_name}."))
        strategy_external_id = strategy_name
    traffic_strategy.name = strategy_name
    traffic_strategy.external_id = strategy_external_id
    for aimsun_policy in aimsun_strategy.getPolicies():
        traffic_strategy.policies.append(generate_policy(
            aimsun_policy, mapping_scenario_change_type, aimsun_model))
    traffic_strategy.export_to_file(filepath)


def generate_phase_signal(
    control_phase_signal: GKControlPhaseSignal
) -> aimsun_input_utils.ControlPhaseSignal:
    """Takes in an Aimsun GKControlPlanSignal object. Creates a Python object
    based on the signal data from the Aimsun object. A control phase signal
    links data between control phases and their respective signals. Control
    phases are different blocks of time within a control plan for certain
    signals (like traffic lights) to be showing a certain color or light
    pattern.

    Args:
        control_phase_signal: An Aimsun GKControlPhaseSignal.
    Returns:
        phase_signal: A Python ControlPhaseSignal object.
    """
    phase_signal = aimsun_input_utils.ControlPhaseSignal()
    phase_signal.signal = control_phase_signal.signal
    return phase_signal


def generate_actuated_phases(
    aimsun_model: GKModel, control_junction: GKControlJunction,
    actuated_control_junction_enum: aimsun_input_utils.ControlJunctionType
) -> Tuple[List[aimsun_input_utils.ActuatedControlPhase],
           Mapping[aimsun_input_utils.ExternalId, aimsun_input_utils.Detector]]:
    """Takes in a control_junction and unpacks the phase data from the junction.
    Each attribute of the phase is mirrored to an attribute of the associated
    Python object. The resulting list of Python objects are returned, to be
    fully exported as a .pkl in the export_to_master_control_plan method.

    Actuated phases are defined as phases in a stoplight that are activated due
    to some set detection. Thus, there are more attributes to unpack.

    Args:
        actuated_control_junction_enum: The enumeration for the type of
            actuated control junction.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        control_junction: An Aimsun GKControlJunction object.
    Returns:
        actuated_control_phases: A list of Python ActuatedControlPhase objects.
        detectors: A list of Python Detector objects and their associated
            External IDs.
    """
    actuated_control_phases = []
    phases = control_junction.getPhases()
    detectors = {}

    if not (control_junction.getControlJunctionType()
            == actuated_control_junction_enum):
        aimsun_model.reportError(
            'export_master_control_plan',
            "Error, the control junction should be actuated.")
        sys.exit()
    for aimsun_control_phase in phases:
        phase = aimsun_input_utils.ActuatedControlPhase()
        phase.from_time = aimsun_control_phase.getFrom()
        phase.duration = aimsun_control_phase.getDuration()
        phase.id_ring = aimsun_control_phase.getIdRing()
        phase.interphase = aimsun_control_phase.getInterphase()
        phase.recall = aimsun_input_utils.ControlPhaseRecall(
            aimsun_control_phase.getRecall())
        phase.is_default = aimsun_control_phase.getIsDefault()
        phase.min_duration = aimsun_control_phase.getMinDuration()
        phase.max_duration = aimsun_control_phase.getMaxDuration()
        phase.passage_time = aimsun_control_phase.getPassageTime()
        phase.permissive_period_from = (
            aimsun_control_phase.getPermissivePeriodFrom())
        phase.permissive_period_to = (
            aimsun_control_phase.getPermissivePeriodTo())
        phase.force_off = aimsun_control_phase.getForceOff()
        phase.hold = aimsun_control_phase.getHold()
        phase.maximum_initial = aimsun_control_phase.getMaximumInitial()
        phase.seconds_actuation = aimsun_control_phase.getSecondsActuation()
        phase.gap_reduction = aimsun_control_phase.isUsingGapReduction()
        phase.minimum_gap = aimsun_control_phase.getMinimumGap()
        phase.time_before_reduce = aimsun_control_phase.getTimeBeforeReduce()
        phase.time_to_reduce = aimsun_control_phase.getTimeToReduce()
        for aimsun_signal in aimsun_control_phase.getSignals():
            phase.signals.append(generate_phase_signal(aimsun_signal))
        for aimsun_detector, aimsun_control_detector in (
                aimsun_control_phase.getControlDetectors().items()):
            control_detector = aimsun_input_utils.ControlDetector()
            detector_external_id = (
                create_detector_external_id(
                    aimsun_detector.getId()))
            control_detector.detector_external_id = detector_external_id
            control_detector.locking = aimsun_control_detector.getLocking()
            control_detector.call_delay = aimsun_control_detector.getCallDelay()
            control_detector.phase_activation = (
                aimsun_control_detector.getPhaseActivation())
            control_detector.phase_extension = (
                aimsun_control_detector.getPhaseExtension())
            phase.detectors.append(control_detector)
            detectors[detector_external_id] = (
                convert_gkdetector_to_detector_class(
                    aimsun_detector, aimsun_model))

        actuated_control_phases.append(phase)
    return actuated_control_phases, detectors


def generate_nonactuated_phases(
    control_junction: GKControlJunction
) -> List[aimsun_input_utils.NonActuatedControlPhase]:
    """Takes in a control_junction and unpacks the phase data from the junction.
    Each attribute of the phase is mirrored to an attribute of the associated
    Python object. The resulting list of Python objects are returned, to be
    fully exported as a .pkl in the export_to_master_control_plan method.

    Nonactuated phases are defined as traffic signals that always follows a set
    pattern. As such, there are less attributes necessary to determine what
    phase a signal may be in.

    Args:
        control_junction: An Aimsun GKControlJunction object.
    Returns:
        nonactuated_control_phases: A list of NonActuatedControlPhase objects.
    """
    nonactuated_control_phases = []
    aimsun_phases = control_junction.getPhases()

    for aimsun_phase in aimsun_phases:
        phase = aimsun_input_utils.NonActuatedControlPhase()
        phase.from_time = aimsun_phase.getFrom()
        phase.duration = aimsun_phase.getDuration()
        phase.interphase = aimsun_phase.getInterphase()
        if not aimsun_phase.getInterphase():
            for aimsun_signal in aimsun_phase.getSignals():
                phase.signals.append(generate_phase_signal(aimsun_signal))
        nonactuated_control_phases.append(phase)
    return nonactuated_control_phases


def generate_junctions(
    control_plan: GKControlPlan,
    mapping_control_junction_type: Dict[
        aimsun_input_utils.ControlJunctionType, Any],
    aimsun_model: GKModel
) -> Tuple[List[aimsun_input_utils.ControlJunction],
           Mapping[aimsun_input_utils.ExternalId, aimsun_input_utils.Detector]]:
    """Takes in a control plan and unpacks the junction data from the control
    plan. Each attribute is added to a Python object, and some of them are
    tested for validity, such as uniqueness in node_ids. The created Python
    object is then appended to the control_junctions list and returned. It will
    be exported as a part of the master_control_plan in the function
    export_master_control_plan.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        control_plan: An Aimsun GKControlPlan object.
        mapping_control_junction_type: The list of control junction types.
    Returns:
        control_junctions: A list of Python ControlJunction objects.
        dict_of_detectors: A dictionary of Python Detector objects with their
            corresponding External IDs.
    """
    control_junctions = []
    control_junction_ids = []
    dict_of_detectors = {}
    # It seems that there is only one control junction per control plan.
    for aimsun_control_junction in control_plan.getControlJunctions().values():
        control_junction_type = aimsun_control_junction.getControlJunctionType()
        # We do not export unspecified and uncontrolled traffic signals has they
        # are not part of the traffic master control plan.
        if control_junction_type in [
                mapping_control_junction_type[
                    aimsun_input_utils.ControlJunctionType.FIXED_CONTROL],
                mapping_control_junction_type[
                    aimsun_input_utils.ControlJunctionType.EXTERNAL]]:
            control_junction = aimsun_input_utils.NonActuatedControlJunction()
            node_id = aimsun_control_junction.getNodeId()
            if node_id in control_junction_ids:
                aimsun_model.reportError(
                    'export_master_control_plan',
                    f"{node_id} needs to be twice in the control_plan_dict. The"
                    " current code cannot do that, please change the code. "
                    "Quitting on error.")
                sys.exit()

            control_junction.node_id = node_id
            control_junction.junction_type = (
                aimsun_input_utils.ControlJunctionType(control_junction_type))
            control_junction.cycle = aimsun_control_junction.getCycle()
            control_junction.offset = aimsun_control_junction.getOffset()
            control_junction.phases = generate_nonactuated_phases(
                aimsun_control_junction)
        elif control_junction_type == mapping_control_junction_type[
                aimsun_input_utils.ControlJunctionType.ACTUATED]:
            control_junction = aimsun_input_utils.ActuatedControlJunction()
            node_id = aimsun_control_junction.getNodeId()
            if node_id in control_junction_ids:
                aimsun_model.reportError(
                    'export_master_control_plan',
                    f"{node_id} needs to be twice in the control_plan_dict. The"
                    " current code cannot do that, please change the code. "
                    "Quitting on error.")
                sys.exit()
            control_junction.node_id = node_id
            control_junction.junction_type = (
                aimsun_input_utils.ControlJunctionType(control_junction_type))
            control_junction.cycle = aimsun_control_junction.getCycle()
            control_junction.offset = aimsun_control_junction.getOffset()
            control_junction.barriers = [0]
            for barrier in aimsun_control_junction.getBarriers():
                control_junction.barriers.append(barrier)
            control_junction.rest_in_red = (
                aimsun_control_junction.getRestInRed())
            control_junction.matches_offset_with_end_of_phase = (
                aimsun_control_junction.getMatchesOffsetWithEndOfPhase())
            control_junction.yellow_time = (
                aimsun_control_junction.getYellowTime())
            control_junction.single_entry = (
                aimsun_control_junction.getSingleEntry())

            phases = aimsun_control_junction.getPhases()
            control_junction.num_phases = len(phases)
            (control_junction.phases,
             dict_of_detectors_control_junction) = generate_actuated_phases(
                aimsun_model, aimsun_control_junction,
                mapping_control_junction_type[
                    aimsun_input_utils.ControlJunctionType.ACTUATED])
            dict_of_detectors.update(dict_of_detectors_control_junction)
        else:
            aimsun_model.reportError(
                "export_master_control_plan",
                f"{control_junction_type} type should not be in master control "
                "plan. Please fix the code.")
        control_junctions.append(control_junction)
    return control_junctions, dict_of_detectors


def generate_meterings(
    aimsun_model: GKModel,
    control_meterings: Dict[aimsun_input_utils.InternalId, GKMetering]
) -> Tuple[List[aimsun_input_utils.ControlMetering],
           Mapping[aimsun_input_utils.ExternalId, aimsun_input_utils.Metering]]:
    """Returns a dictionary corresponding to the control metering to export.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        control_meterings: A list of GKControlMetering objects.
    Returns:
        control_meters: A list of ControlMetering Python objects.
        meterings: A dictionary of Python Metering objects with their
            respective External IDs.
    """
    control_meters = []
    meterings = {}
    for aimsun_control_metering in control_meterings.values():
        control_metering = aimsun_input_utils.ControlMetering()
        metering = convert_gkmetering_to_metering_class(
            aimsun_control_metering.getMetering(), aimsun_model)
        metering_external_id = metering.external_id
        if metering_external_id not in meterings:
            meterings[metering_external_id] = metering
        control_metering.control_metering_type =\
            aimsun_input_utils.ControlMeteringType(
                aimsun_control_metering.getControlMeteringType())
        control_metering.metering_external_id = metering_external_id
        control_meters.append(control_metering)
    return control_meters, meterings


def generate_master_control_plan(
    aimsun_master_control_plan: GKMasterControlPlan,
    mapping_control_junction_type: Dict[
        aimsun_input_utils.ControlJunctionType, Any],
    aimsun_model: GKModel
) -> aimsun_input_utils.MasterControlPlan:
    """Returns the master control plan Python object. A master control plan is
    an object that holds a collection of control plans by both time intervals
    and zones. The time intervals are the start and end times that a control
    plan runs for, and the zones are regions defined in the network.

    The control plan characteristics are given by generate_junctions and
    generate_meterings functions.

    Args:
        aimsun_master_control_plan: An Aimsun GKModel::masterControlPlan object.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        mapping_control_junction_type: The list of control junction types.
    Returns:
        return_master_control_plan: A Python MasterControlPlan object.
    """
    return_master_control_plan = aimsun_input_utils.MasterControlPlan()

    mcp_external_id = aimsun_master_control_plan.getExternalId()
    if mcp_external_id:
        return_master_control_plan.external_id = mcp_external_id
    mcp_name = aimsun_master_control_plan.getName()
    if not mcp_name:
        mcp_name = return_master_control_plan.external_id
    return_master_control_plan.name = mcp_name

    mcp_schedule = aimsun_master_control_plan.getSchedule()
    control_plans_external_ids = set()
    dict_of_meterings = {}
    dict_of_detectors = {}

    for mcp_schedule_item in mcp_schedule:
        master_control_plan_item = aimsun_input_utils.MasterControlPlanItem()

        control_plan = mcp_schedule_item.getControlPlan()
        control_plan_name = control_plan.getName()
        control_plan_external_id = control_plan.getExternalId()
        if not control_plan_name and not control_plan_external_id:
            aimsun_model.reportError(
                'export_master_control_plan',
                "Control plan has neither an external id neither a name, "
                "quitting on error")
            sys.exit()
        if not control_plan_external_id and control_plan_name:
            print(("Control plan has no external id but a name, setting its "
                   f"external id to the name {control_plan_name}"))
            control_plan_external_id = control_plan_name
            control_plan.setExternalId(control_plan_external_id)
        if not control_plan_name and control_plan_external_id:
            print(("Control plan has no name but an external id, setting its "
                   f"name to the external id {control_plan_external_id}"))
            control_plan_name = control_plan_external_id
            control_plan.setName(control_plan_name)

        master_control_plan_item.control_plan_external_id = (
            control_plan_external_id)
        master_control_plan_item.duration = mcp_schedule_item.getDuration()
        master_control_plan_item.from_time = mcp_schedule_item.getFrom()
        master_control_plan_item.zone = mcp_schedule_item.getZone()
        # append master control plan items to the schedule
        return_master_control_plan.schedule.append(master_control_plan_item)

        # Export control plan if it has not been seen/exported before.
        if control_plan_external_id not in control_plans_external_ids:
            control_plans_external_ids.add(control_plan_external_id)
            # Create control plan with name and external id.
            converted_control_plan = aimsun_input_utils.ControlPlan()
            converted_control_plan.name = control_plan_name
            converted_control_plan.external_id = control_plan_external_id
            converted_control_plan.offset = control_plan.getOffset()
            # Add the control junctions to the plan. Memoize the detectors.
            (converted_control_plan.control_junctions,
             dict_of_detectors_control_junctions) = generate_junctions(
                control_plan, mapping_control_junction_type, aimsun_model)
            dict_of_detectors.update(dict_of_detectors_control_junctions)
            # Add the control meterings to the plan. Memoize the meterings.
            (converted_control_plan.control_meterings,
             dict_of_meterings_control_plan) = generate_meterings(
                aimsun_model, control_plan.getControlMeterings())
            dict_of_meterings.update(dict_of_meterings_control_plan)
            # Save the control plan in master control plan object.
            return_master_control_plan.control_plans.append(
                converted_control_plan)

    return_master_control_plan.meterings = list(dict_of_meterings.values())
    return_master_control_plan.detectors = list(dict_of_detectors.values())
    return return_master_control_plan


def export_master_control_plan(
    master_control_plan_file: str,
    mapping_control_junction_type: Dict[
        aimsun_input_utils.ControlJunctionType, Any],
    aimsun_model: GKModel
):
    """Export all traffic light master control plans and every traffic light
    control plan in Aimsun as a .pkl.

    The .pkl file is a pickled Python object that stores all the data for the
    master control plan.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        mapping_control_junction_type: The list of control junction types.
        master_control_plan_file: The absolute path to export the .pkl file.
    Raises:
        aimsun_report_error: If there isn't exactly one master control
            plan, the code throws and error and quits.
    """
    mcp = get_list_of_objects(
        'GKModel::masterControlPlans', aimsun_model)
    if len(mcp) > 1:
        aimsun_model.reportError(
            'export_master_control_plan',
            "Master Control Plan is not uniquely defined. The current code "
            "cannot take into account this possibility, please change the "
            "code. Quitting on error.")
        sys.exit()
    if len(mcp) == 0:
        aimsun_model.reportError(
            'export_master_control_plan',
            "Master Control Plan does not exist. The current code cannot "
            "take into account this possibility, please change the code. "
            "Quitting on error.")
        sys.exit()
    master_control_plan = generate_master_control_plan(
        mcp[0], mapping_control_junction_type, aimsun_model)
    master_control_plan.export_to_file(master_control_plan_file)


# ****************************************************************************
# *********************** Traffic data util functions ************************
# ****************************************************************************


def get_and_restore_real_dataset(
    real_dataset_external_id: aimsun_input_utils.ExternalId,
    aimsun_model: GKModel
) -> GKRealDataSet:
    """Restores the real data set with the External ID real_dataset_external_id.
    The function will return the dataset if found.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        real_dataset_external_id: An External ID for a Real Dataset. It's used
            to retrieve the Real Dataset object from within Aimsun.
    Returns:
        gk_real_dataset: The Aimsun GKRealDataSet object associated with the
            real_dataset_external_id External ID. None if
            real_dataset_external_id is not the external id of a GKRealDataSet.
    Raises:
        aimsun_report_error: If the gk_real_dataset cannot be restored or read,
            the function raises an error, but does not quit. If a
            gk_real_dataset does not exist with the given external ID, the
            function raises an error and quits.
    """
    gk_real_dataset = get_object_per_external_id(
        real_dataset_external_id, ['GKRealDataSet'], aimsun_model)
    if gk_real_dataset is None:
        aimsun_model.reportError(
            'T1_create_real_data_set',
            "Cannot find a real data set with external ID "
            f"{real_dataset_external_id}.")
        sys.exit()
    if not gk_real_dataset.restoreData():
        aimsun_model.reportError(
            'T1_create_real_data_set',
            f"Cannot restore real data set {real_dataset_external_id}.")
    if not gk_real_dataset.readed():
        aimsun_model.reportError(
            'T1_create_real_data_set',
            f"Real data set {real_dataset_external_id} has not been readed.")
    return gk_real_dataset


def create_real_data_set(
    real_data_set: aimsun_input_utils.AimsunFlowRealDataSet,
    aimsun_model: GKModel,
    aimsun_system,
    id_type,
    columns,
    time_type,
    time,
    path_to_csv_dataset_directory: str
):
    """Creates an Aimsun GKRealDataSet from a Python AimsunFlowRealDataSet
    object.

    The function goes through the attributes of the Python object and assigning
    them to the associated attribute in the Aimsun object. The rest of the data
    is restored using an Aimsun object called a GKRealDataSetRestorerSimple.
    This object attempts to restore data from an ASCII file, creating a column
    within the object by the referenced type.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        columns: Sets the columns types to restore.
        id_type: An enumeration describing how the restorer should search for
            objects to restore - by Internal ID, External ID, or name.
        real_data_set: A Python AimsunFlowRealDataSet object that stores the
            data for both the Dataset and the DatasetRestorer.
        time_type: An enumeration describing how the time variables should be
            set up within this object.
        time: A GKTime or QTime object.
        path_to_csv_dataset_directory: path to csv directory.
    """
    gk_real_dataset = aimsun_system.newObject('GKRealDataSet', aimsun_model)
    gk_real_dataset.setName(real_data_set.external_id)
    gk_real_dataset.setExternalId(real_data_set.external_id)
    aimsun_model.getCreateRootFolder().findFolder(
        'GKModel::realDataSets').append(gk_real_dataset)

    restorer = gk_real_dataset.addRestorer('GKRealDataSetRestorerSimple')
    restorer.setBaseDate(time)
    restorer.setFileName(
        os.path.join(path_to_csv_dataset_directory, real_data_set.filename))
    restorer.setIdType(id_type)
    restorer.setColumns(columns)
    # Skip the column names of the csv file.
    restorer.setLinesToSkip(real_data_set.line_to_skip)
    restorer.setSeparator(aimsun_input_utils.CSV_SEPARATOR)
    restorer.setTimeType(time_type)
    restorer.setVehicles([None, None, None])
    restorer.setObjectType(aimsun_model.getType('GKDetector'))
    # Checks
    if not gk_real_dataset.restoreData():
        aimsun_model.reportError(
            'T1_create_real_data_set',
            "Cannot restore real data set.")
    if gk_real_dataset.getBaseDate() != time:
        aimsun_model.reportError(
            'T1_create_real_data_set',
            "Error in date handling, code should be changed.")
    if not gk_real_dataset.readed():
        aimsun_model.reportError(
            'T1_create_real_data_set',
            "Real data set has not been readed.")


# ****************************************************************************
# ********************** Simulation data util functions **********************
# ****************************************************************************


def update_database_info(
    db_info: GKDataBaseInfo,
    database_info: aimsun_config_utils.AimsunDataBaseInfo,
    aimsun_model: GKModel,
    path_to_database_directory: str
) -> GKDataBaseInfo:
    """Updates the Aimsun database information with the saved data within the
    Python AimsunDataBaseInfo object.

    Args:
    aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        db_info: An empty Aimsun GKDataBaseInfo object, which needs its
            attributes updated with the Python object's attributes.
        database_info: A Python AimsunDataBaseInfo object that has the data
            needed to update db_info.
        path_to_database_directory: Filepath to the simulation output database.
    Returns:
        db_info: The Aimsun GKDataBaseInfo object with updated attributes from
            the Python AimsunDataBaseInfo object.
    Raises:
        aimsun_report_error: Raises an error if the current model
            has a database.
    """
    db_info.setUseProjectDB(database_info.use_project_db)
    db_info.setAutomatic(database_info.automatic)
    db_info.setAutomaticallyCreated(database_info.automatically_created)
    db_info.setDriverName(database_info.database_driver_name)
    database_path = os.path.join(
        path_to_database_directory, database_info.database_path)
    db_info.setDatabaseName(database_path)
    if database_info.database_driver_name == "QSQLITE":
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        if cursor.fetchone():
            aimsun_model.reportError(
                'aimsun_utils_functions',
                'Error. Database is not empty.')
            sys.exit()
    return db_info


def run_experiment(
    experiment_external_id: aimsun_input_utils.ExternalId,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Finds an experiment object using the given External ID. Then, runs the
    experiment. An experiment is a run of a scenario where parameters not
    specific to the network are defined. Experiments need to be defined before
    they can be used to run a simulation.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        experiment_external_id: The External ID pointing to a GKExperiment or
            MacroExperiment object within Aimsun.
    Raises:
        aimsun_report_error: Raises an error if the experiment had an issue
            being executed or if the experiment does not exist.
    """
    experiment = get_object_per_external_id(
        experiment_external_id, ['MacroExperiment', 'GKExperiment'],
        aimsun_model)
    if experiment is None:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"Experiment {experiment_external_id} does not exist.")
        sys.exit()
    action_executed = aimsun_system.executeAction(
        "execute", experiment, [], "")
    if not action_executed:
        aimsun_model.reportError(
            "aimsun_utils_functions",
            f"Error running {experiment_external_id}.")


def run_experiments(
    list_experiment_external_id: aimsun_input_utils.ExternalId,
    aimsun_model: GKModel,
    aimsun_system: GKSystem
):
    """Runs Aimsun simulation experiments.

    Args:
        list_experiment_external_id: A list of GKExperiment external IDs object
            within Aimsun.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
    Raises:
        aimsun_report_error: Raises an error if the experiment had an issue
            being executed or if the experiment does not exist.
    """
    for experiment_external_id in list_experiment_external_id:
        run_experiment(experiment_external_id, aimsun_model, aimsun_system)


def create_traffic_demand(
    traffic_demand_list: aimsun_config_utils.AimsunTrafficDemands,
    aimsun_model: GKModel,
    aimsun_system,
    create_schedule_demand_item,
    create_gk_time_duration
):
    """Create traffic demand object in Aimsun."""
    for traffic_demand in traffic_demand_list.traffic_demands:
        # Create the traffic demand.
        gk_traffic_demand = aimsun_system.newObject(
            "GKTrafficDemand", aimsun_model)
        gk_traffic_demand.setName(traffic_demand.name)
        gk_traffic_demand.setExternalId(traffic_demand.external_id)
        aimsun_model.getCreateRootFolder().findFolder(
            "GKModel::trafficDemand").append(gk_traffic_demand)

        for schedule_demand_item in traffic_demand.demand_items:
            gk_od_matrix = get_object_per_external_id(
                schedule_demand_item.demand_external_id, ['GKODMatrix'],
                aimsun_model)

            gk_schedule_demand_item = create_schedule_demand_item()
            seconds_from_midnight = create_gk_time_duration(
                gk_od_matrix.getFrom()).toSeconds()[0]
            gk_schedule_demand_item.setFrom(seconds_from_midnight)
            gk_schedule_demand_item.setDuration(
                gk_od_matrix.getDuration().toSeconds()[0])
            gk_schedule_demand_item.setTrafficDemandItem(gk_od_matrix)
            gk_schedule_demand_item.setFactor(
                schedule_demand_item.demand_factor)
            gk_traffic_demand.addToSchedule(gk_schedule_demand_item)


def create_macroexperiment(
    macroexperiment: aimsun_config_utils.AimsunStaticMacroExperiment,
    aimsun_model: GKModel,
    aimsun_system
) -> MacroExperiment:
    """Creates an experiment within Aimsun using the data from the python
    AimsunStaticMacroExperiment object. Each attribute of the python object is
    assigned to its relative counter part in the Aimsun object.

    Args:
        macroexperiment: A Python AimsunStaticMacroExperiment object that
            houses the data needed to be imported into Aimsun.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
    Returns:
        experiment: An Aimsun MacroExperiment object with the data imported from
            the Python AimsunStaticMacroExperiment object.
    """

    # Create experiment
    experiment = aimsun_system.newObject("MacroExperiment", aimsun_model)
    experiment.setName(macroexperiment.name)
    experiment.setExternalId(macroexperiment.external_id)
    experiment.setEngine(macroexperiment.engine)

    exp_params = experiment.createParameters()
    exp_params.setMaxIterations(macroexperiment.parameters.max_iterations)
    exp_params.setFrankWolfeMethod(macroexperiment.parameters.method)
    exp_params.setMaxRelativeGap(macroexperiment.parameters.max_relative_gap)
    experiment.setParameters(exp_params)
    return experiment


def create_macroscenario(
    macroscenario: aimsun_config_utils.AimsunStaticMacroScenario,
    aimsun_model: GKModel,
    aimsun_system,
    create_q_date,
    aimsun_output_directory_path
):
    """Creates a scenario within Aimsun using the data from the Python
    AimsunStaticMacroScenario object. The function sets most attributes of the
    scenario using the imported Python object, but other attributes (master
    control plan, demand, date, dataset, and strategy) are imported from
    elsewhere, using the Aimsun Model to pull related objects.

    Args:
        macroscenario: A Python AimsunStaticMacroScenario object that houses
            the data needed to be imported into Aimsun.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        create_q_date: Function that creates a QDate object that corrseponds to
            a specific year, month, and date.
        aimsun_output_directory_path: File path to the Aimsun simulation output
            database.
    """
    master_control_plan = get_object_per_external_id(
        macroscenario.master_control_plan_external_id, ["GKMasterControlPlan"],
        aimsun_model)
    demand = get_object_per_external_id(
        macroscenario.traffic_demand_external_id, ["GKTrafficDemand"],
        aimsun_model)

    # Create scenario
    aimsun_macro_scenario = aimsun_system.newObject(
        "MacroScenario", aimsun_model)
    aimsun_macro_scenario.setName(macroscenario.name)
    aimsun_macro_scenario.setExternalId(macroscenario.external_id)
    # setting control plan of the scenario
    aimsun_macro_scenario.setMasterControlPlan(master_control_plan)
    # setting the demand
    aimsun_macro_scenario.setDemand(demand)

    # setting the real data set and the date
    begin_date = macroscenario.begin_date
    aimsun_macro_scenario.setDate(
        create_q_date(begin_date.year, begin_date.month, begin_date.day))
    real_dataset = get_and_restore_real_dataset(
        macroscenario.real_dataset_external_id, aimsun_model)
    if real_dataset is not None:
        aimsun_macro_scenario.setRealDataSet(real_dataset)

    # create the experiement
    experiment = create_macroexperiment(
        macroscenario.experiment, aimsun_model, aimsun_system)

    def get_strategy(strategy_id: aimsun_input_utils.ExternalId) -> GKStrategy:
        return get_object_per_external_id(
            strategy_id, ['GKStrategy'], aimsun_model)
    traffic_management_strategies = map(
        get_strategy, macroscenario.traffic_strategy_external_ids)
    for traffic_management_strategy in traffic_management_strategies:
        if traffic_management_strategy is not None:
            aimsun_macro_scenario.addStrategy(traffic_management_strategy)
            for policy in traffic_management_strategy.getPolicies():
                experiment.addPolicy(policy)

    aimsun_macro_scenario.addExperiment(experiment)

    db_info = update_database_info(
        aimsun_macro_scenario.getDB(True), macroscenario.database_info,
        aimsun_model, aimsun_output_directory_path)
    aimsun_macro_scenario.setDB(db_info)

    # adding the scenario to the scenario folder
    aimsun_model.getCreateRootFolder().findFolder(
        "GKModel::top::scenarios").append(aimsun_macro_scenario)


def create_macroscenarios(
    macroscenarios: aimsun_config_utils.AimsunStaticMacroScenarios,
    aimsun_model: GKModel,
    aimsun_system,
    create_q_date,
    aimsun_output_directory_path
):
    """Creates all the scenarios associated with the imported Python
    AimsunStaticMacroScenarios object. The function loops through the
    macroscenarios assigned to the python object and creates them using the
    function create_secnario().

    Args:
        macroscenarios: Macrosimulation object to create in Aimsun.
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        create_q_date: Function that creates a QDate object that corrseponds to
            a specific year, month, and date.
        aimsun_output_directory_path: File path to the Aimsun simulation output
            database.
    """
    for aimsun_static_macroscenario in (
            macroscenarios.aimsun_static_macroscenarios):
        create_macroscenario(
            aimsun_static_macroscenario, aimsun_model, aimsun_system,
            create_q_date, aimsun_output_directory_path)


def set_gk_scenario_config(
    # scenario_input_data: aimsun_config_utils.AimsunScenarioInputData,
    gk_scenario_input_data: GKScenarioInputData,
    scenario_input_data: aimsun_config_utils.AimsunScenarioInputData,
    aimsun_model: GKModel,
    aimsun_system,
    create_trajectory_condition
) -> GKScenarioInputData:
    """Sets the scenario configurations based on the given input data. The
    function then loops through the centroid origin/destinations pairs and
    creates trajectory conditions using the O/D IDs.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        gk_scenario_input_data: An Aimsun GKScenarioInputData object that is
            modified to fit the scenario needed.
        scenario_input_data: The Python object that stores all the scenario
            input data needed to set the configs for the Aimsun scenario.
        create_trajectory_condition: Function that returns an empty Aimsun
            GKTrajectoryCondition object.
    Returns:
        gk_scenario_input_data: The modified GKScenarioInputData object that
            was passed into this function.
    """
    statistical_interval_time = gk_scenario_input_data.getStatisticalInterval()
    seconds = scenario_input_data.statistical_interval.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    statistical_interval_time.setHMS(hours, minutes, seconds)
    gk_scenario_input_data.setStatisticalInterval(statistical_interval_time)
    detection_interval_time = gk_scenario_input_data.getDetectionInterval()
    seconds = scenario_input_data.detection_interval.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    detection_interval_time.setHMS(hours, minutes, seconds)
    gk_scenario_input_data.setDetectionInterval(detection_interval_time)

    gk_scenario_input_data.setTrajectoriesStatistics(
        scenario_input_data.trajectories_statistics)
    gk_scenario_input_data.setGlobalTrajectoriesStatistics(
        scenario_input_data.global_trajectories_statistics)
    gk_scenario_input_data.setSectionTrajectoriesStatistics(
        scenario_input_data.section_trajectories_statistics)
    # enable subsampling 5% of the trajectories that departs and finishes at
    # external centroids
    centroid_ids = aimsun_model.getCatalog().getObjectsByType(
        aimsun_system.getActiveModel().getType("GKCentroid"))
    for o_centroid_id in centroid_ids:
        for d_centroid_id in centroid_ids:
            trajectory_condition = create_trajectory_condition()
            trajectory_condition.origin = o_centroid_id
            trajectory_condition.destination = d_centroid_id
            o_centroid_ext_id = aimsun_model.getCatalog().find(
                o_centroid_id).getExternalId()
            d_centroid_ext_id = aimsun_model.getCatalog().find(
                d_centroid_id).getExternalId()
            if "ext" in o_centroid_ext_id and "ext" in d_centroid_ext_id:
                # 5% for external to external.
                trajectory_condition.percentage = 5
            else:
                trajectory_condition.percentage = 0
            gk_scenario_input_data.addTrajectoryListStatistics(
                trajectory_condition)
    # Alternative way: sample per vehicle type.
    return gk_scenario_input_data


def create_gk_experiment(
    experiment: aimsun_config_utils.AimsunMicroExperiment,
    aimsun_model: GKModel,
    aimsun_system
) -> GKExperiment:
    """Creates a micro experiment from the generic GKExperiment Aimsun class.
    The attributes from the AimsunMicroExperiment are copied into an Aimsun
    object.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        experiment: A Python AimsunMicroExperiment that houses the data
            needed to be imported into Aimsun.
    Returns:
        gk_experiment: An Aimsun GKExperiment object created from the
            attributes given by the imported Python object
            AimsunMicroExperiment.
    """
    # Creating the experiment
    gk_experiment = aimsun_system.newObject('GKExperiment', aimsun_model)
    gk_experiment.setName(experiment.name)
    gk_experiment.setExternalId(experiment.external_id)
    gk_experiment.setSimulatorEngine(experiment.dynamic_simulator_engine)
    gk_experiment.setEngineMode(experiment.engine_mode)

    aimsun_to_python_attributes = {
        "GKExperiment::cycleTimeAtt": experiment.cycle_time,
        "GKExperiment::intervalsAtt": experiment.intervals,
        "GKExperiment::capacityWeigthAtt": experiment.capacity_weight,
        "GKExperiment::dynamicAtt": experiment.dynamic,
        "GKExperiment::maxAssignPathsAtt": experiment.max_assign_paths
    }

    if experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.MICROSIMULATION:
        aimsun_to_python_attributes.update({
            "GKExperiment::simStepAtt": experiment.micro_sim_step,
            "GKExperiment:carFollowingVersionAtt":
            int(experiment.car_following_version),
            "GKExperiment::carFollowingConsiderMinHeadwayAtt":
            experiment.car_following_consider_min_headway,
            "GKExperiment::applyTwoLanesAtt": experiment.apply_two_lanes,
            "GKExperiment::applyTwopasAtt": experiment.apply_twopas_slope_model,
            "GKExperiment::applyTwoDimAtt":
            experiment.apply_non_lane_based_movement,
            "GKExperiment::applyTwoWayAtt":
            experiment.apply_two_way_overtaking_model,
            "GKExperiment::queueUpSpeedAtt": experiment.micro_queue_up_speed,
            "GKExperiment::queueLeavingSeepAtt":
            experiment.micro_queue_leaving_speed,
            "GKExperiment::activateExternalBehavioralModelAtt":
            experiment.micro_activate_external_behavior_model,
            "GKExperiment::reactionTimeTypeAtt":
            int(experiment.reaction_time_type),
            "GKExperiment::reactionAtStopAtt": experiment.reaction_at_stop,
            "GKExperiment::reactionAtTrafficLightAtt":
            experiment.reaction_at_traffic_light
        })
        if experiment.apply_two_lanes:
            aimsun_to_python_attributes.update({
                "GKExperiment::maxDistanceAtt": experiment.max_distance,
                "GKExperiment::twoLanesCarFollowingModelAtt":
                int(experiment.two_lane_car_following_model),
                "GKExperiment::nbVehiclesAtt": experiment.micro_num_of_vehicles,
                "GKExperiment::maxSpeedDiffAtt":
                experiment.micro_max_speed_diff,
                "GKExperiment::maxSpeedDiffRampAtt":
                experiment.micro_max_speed_diff_ramp
            })
        if experiment.apply_two_way_overtaking_model:
            aimsun_to_python_attributes.update({
                "GKExperiment::delayTreshold": experiment.delay_time_threshold,
                "GKExperiment::speedDiffMin":
                experiment.speed_difference_min_threshold,
                "GKExperiment::speedDiffMax":
                experiment.speed_difference_max_threshold,
                "GKExperiment::rankTreshold":
                experiment.rank_threshold,
                "GKExperiment::traveltimeTreshold":
                experiment.remaining_travel_time_threshold,
                "GKExperiment::numberOfSimultaneousOvertakingAllowed":
                experiment.number_of_simultaneous_overtaking_allowed,
                "GKExperiment::delayOfSimultaneousOvertakingAllowed":
                experiment.delay_between_simultaneous_overtaking,
                "GKExperiment::sensitivityFactorReducedGapCF":
                experiment.sensitivity_factor_reduce_car_following,
                "GKExperiment::speedAcceptance4Overtaking":
                experiment.overtaking_speed_magnification,
                "GKExperiment::speedDiffTreshold4OvertakingSpeedAcceptance":
                experiment.speed_difference_overtaking_threshold
            })
        if not experiment.replications:
            aimsun_model.reportError(
                'S2_create_dynamic_simulation',
                'No replications for the experiment.')
            sys.exit()
        for replication in experiment.replications:
            gk_replication = aimsun_system.newObject(
                'GKReplication', aimsun_model)
            gk_replication.setRandomSeed(replication.random_seed)
            gk_replication.setRecordSimulation(replication.results_to_generate)
            gk_experiment.addReplication(gk_replication)
    elif experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.MESOSIMULATION:
        aimsun_model.reportError(
            'create_dynamic_simulation',
            'Mesosimulation not implemented.')
        sys.exit()
    elif experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.HYBRID_SIMULATION:
        aimsun_model.reportError(
            'create_dynamic_simulation',
            'Hybrid simulation not implemented.')
        sys.exit()
    elif experiment.dynamic_simulator_engine == \
            aimsun_config_utils.DynamicSimulatorEngine.DYNAMIC_MACROSIMULATION:
        aimsun_model.reportError(
            'create_dynamic_simulation',
            'Dynamic macrosimulation not implemented.')
        sys.exit()
    else:
        aimsun_model.reportError(
            'S2_create_dynamic_simulation',
            'Wrong dynamic simulator engine.')
        sys.exit()

    if (experiment.engine_mode
            == aimsun_config_utils.DynamicSimulationEngineMode.
            ITERATIVE_ASSIGNMENT):
        gk_experiment.setStoppingCriteriaIterations(
            experiment.stopping_criteria_iterations)
        gk_experiment.setStoppingCriteriaRGAP(experiment.stopping_criteria_rgap)
    elif (experiment.engine_mode
            == aimsun_config_utils.DynamicSimulationEngineMode.
            ONE_SHOT_ASSIGNMENT):
        aimsun_to_python_attributes.update({
            "GKExperiment::routeChoiceTypeAtt":
            int(experiment.stochastic_route_choice_model),
            "GKExperiment::userDefinedCostWeigthAtt":
            experiment.user_defined_cost_weight,
            "GKExperiment::initialSPTreesAtt":
            experiment.initial_shortest_paths_trees,
            "GKExperiment::maxRoutesAtt": experiment.max_routes
        })
        if (experiment.stochastic_route_choice_model
                == aimsun_config_utils.StochasticRouteChoiceModel.BINOMIAL):
            aimsun_to_python_attributes.update({
                "GKExperiment::probabilityAtt": experiment.probability
            })
        if (experiment.stochastic_route_choice_model
                == aimsun_config_utils.StochasticRouteChoiceModel.LOGIT):
            aimsun_to_python_attributes.update({
                "GKExperiment::scaleFactorAtt": experiment.low_variance_factor
            })
        if (experiment.stochastic_route_choice_model
                == aimsun_config_utils.StochasticRouteChoiceModel.C_LOGIT):
            aimsun_to_python_attributes.update({
                "GKExperiment::scaleFactorAtt": experiment.low_variance_factor,
                "GKExperiment::betaFactorAtt": experiment.beta,
                "GKExperiment::gammaFactorAtt": experiment.gamma,
                "GKExperiment::pastCostReplicationAtt":
                experiment.c_logit_past_cost_replication
            })
        else:
            aimsun_model.reportError(
                'create_dynamic_simulation',
                'Wrong SRC routing model.')
            sys.exit()

    for aimsun_attribute_name, python_attribute in (
            aimsun_to_python_attributes.items()):
        gk_experiment.setDataValue(
            aimsun_model.getColumn(aimsun_attribute_name),
            python_attribute)
    return gk_experiment


def create_gk_scenario_and_experiment(
    microscenario: aimsun_config_utils.AimsunScenario,
    aimsun_model: GKModel,
    aimsun_system,
    create_q_date,
    create_trajectory_condition,
    aimsun_output_directory_path: str
):
    """Creates a scenario and experiment based on the Python AimsunScenario
    object. The function finds the master control plan, demand, and real
    data set from the Aimsun model, then assigns it to a new GKScenario object.
    Then, the function updates the database and creates a corresponding
    experiment from the microscenario data. Finally, the experiment is added to
    the GKStrategy.

    Args:
        aimsun_model: The model variable within Aimsun, used to simplify
            variable definitions and locations within the code.
        aimsun_system: The Aimsun object denoting the entire system. New object
            will be created using an object type and Aimsun model.
        microscenario: A Python AimsunScenario object that houses the data
            needed to create a GKScenario within Aimsun for a microsimulation.
        create_q_date: Function that creates a QDate object that corrseponds to
            a specific year, month, and date.
        create_trajectory_condition: Function that returns an empty Aimsun
            GKTrajectoryCondition object.
        aimsun_output_directory_path: File path to the Aimsun simulation output
            database.
    """
    master_control_plan = get_object_per_external_id(
        microscenario.master_control_plan_external_id, ["GKMasterControlPlan"],
        aimsun_model)
    demand = get_object_per_external_id(
        microscenario.traffic_demand_external_id,
        ["GKTrafficDemand"], aimsun_model)

    def get_strategy(strategy_id: aimsun_input_utils.ExternalId) -> GKStrategy:
        return get_object_per_external_id(
            strategy_id, ['GKStrategy'], aimsun_model)
    traffic_management_strategies = map(
        get_strategy, microscenario.traffic_strategy_external_ids)

    gk_scenario = aimsun_system.newObject('GKScenario', aimsun_model)
    gk_scenario.setName(microscenario.name)
    gk_scenario.setExternalId(microscenario.external_id)
    # setting control plan of the scenario
    gk_scenario.setMasterControlPlan(master_control_plan)
    # setting the demand
    gk_scenario.setDemand(demand)

    gk_scenario_input_data = set_gk_scenario_config(
        gk_scenario.getInputData(),
        microscenario.scenario_input_data, aimsun_model, aimsun_system,
        create_trajectory_condition)
    gk_scenario.setInputData(gk_scenario_input_data)

    # setting the real data set and the date
    begin_date = microscenario.begin_date
    gk_scenario.setDate(create_q_date(begin_date.year, begin_date.month,
                                      begin_date.day))

    db_info = update_database_info(
        gk_scenario.getDB(True), microscenario.database_info, aimsun_model,
        aimsun_output_directory_path)
    gk_scenario.setDB(db_info)

    gk_experiment = create_gk_experiment(
        microscenario.experiment, aimsun_model, aimsun_system)

    for traffic_management_strategy in traffic_management_strategies:
        if traffic_management_strategy is not None:
            gk_scenario.addStrategy(traffic_management_strategy)
            for policy in traffic_management_strategy.getPolicies():
                gk_experiment.addPolicy(policy)

    gk_scenario.addExperiment(gk_experiment)

    aimsun_model.getCreateRootFolder().findFolder(
        'GKModel::top::scenarios').append(gk_scenario)
