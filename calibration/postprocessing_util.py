"""Data classes for Aimsun Micro/Macrosimulation output analysis."""

from __future__ import annotations
import utils.aimsun_input_utils

import datetime
import enum
import os
import sqlite3
import sys
from typing import Any, Dict

ALL_VEHICLE_TYPES = 0
ALL_TIME_AGGREGATED = 0


class SimInfoColumns(enum.Enum):
    """Column names of the SIM_INFO (Simulation Information) table. This table
    contains all metadata related to the simulation that was run.

    Attributes:
        START_TIME_INTERVAL: Time in seconds of when the simulation starts.
        TOTAL_DURATION: Duration of the simulation in seconds.
        NUM_TIME_INTERVALS: Number of time intervals within the simulation.
    """

    START_TIME_INTERVAL = "from_time"
    TOTAL_DURATION = "duration"
    NUM_TIME_INTERVALS = "totalstatintervals"
    # Add more columns as needed.


class MaSectColumns(enum.Enum):
    """Column names of the MASECT (Macro Sections) table. This table contains
    statistical information of road sections for each time interval from
    macrosimulation results. The information contained include the number of
    vehicles, occupancy, and cost through each road section at a certain time
    interval.

    Attributes:
        STA_EXPERIMENT_ID: Static assignment experiment identification number.
        SECTION_INTERNAL_ID: Internal ID of a certain road section.
        SECTION_EXTERNAL_ID: External ID of a certain road section.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. Unique value is set to 1 for macrosimulation since there is a
            different file for each macrosimulation result.
        VOLUME: Number of vehicles through the specified road section at a
            certain time interval. Units are vehicles per time interval length.
        FLOW: Number of vehicles through the specified road section at a certain
            time interval. Units are vehicles per hour.
        OCCUPANCY: Percentage of the road occupancy for the specified road
            section at a certain time interval.
        COST: Cost of the Volume-Delay Function (VDF) for the specified road
            section at a certain time interval.
    """

    STA_EXPERIMENT_ID = "did"
    SECTION_INTERNAL_ID = "oid"
    SECTION_EXTERNAL_ID = "eid"
    VEHICLE_TYPE = "sid"
    TIME_INTERVAL = "ent"
    VOLUME = "volume"
    FLOW = "flow"
    OCCUPANCY = "occupancy"
    COST = "cost"
    # Add more columns as needed.


class MaDetColumns(enum.Enum):
    """Column names of the MADET (Macro Detectors) table. This table contains
    statistical information about detectors from macrosimulation results. The
    information contained include the number of vehicles through each detector
    at a certain time interval.

    Attributes:
        STA_EXPERIMENT_ID: Static assignment experiment identification number.
        DETECTOR_INTERNAL_ID: Internal ID of a certain detector.
        DETECTOR_EXTERNAL_ID: External ID of a certain detector.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. Unique value is set to 1 for macrosimulation since there is a
            different file for each macrosimulation result.
        VOLUME: Number of vehicles through the specified detector at a certain
            time interval. Units are vehicles per time interval length.
        FLOW: Number of vehicles through the specified detector at a certain
            time interval. Units are vehicles per hour.
    """

    STA_EXPERIMENT_ID = "did"
    DETECTOR_INTERNAL_ID = "oid"
    DETECTOR_EXTERNAL_ID = "eid"
    VEHICLE_TYPE = "sid"
    TIME_INTERVAL = "ent"
    VOLUME = "volume"
    FLOW = "flow"
    # Add more columns as needed.


class MiSysColumns(enum.Enum):
    """Column names of the MISYS (Micro Systems) table. This table contains
    statistical information of the entire network for each time interval from
    microsimulation results. The information contained include the average
    number of vehicles passing, average travel time, and average speed through
    each road section at each time interval.

    Attributes:
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. 0 corresponds to all time intervals aggregated.
        FLOW: Number of vehicles in the entire network at a certain time
            interval. Units are vehicles per hour.
        DELAY_TIME: Delay time in the entire network at a certain time
            interval. Units are in seconds.
    """

    VEHICLE_TYPE = "sid"
    TIME_INTERVAL = "ent"
    FLOW = "flow"
    DELAY_TIME = "dtime"
    # Add more columns as needed.


class MiSectColumns(enum.Enum):
    """Column names of the MISECT (Micro Sections) table. This table contains
    statistical information of road sections for each time interval from
    microsimulation results. The information contained include the average
    number of vehicles passing, average travel time, and average speed through
    each road section at each time interval.

    Attributes:
        REPLICATION_INTERNAL_ID: Experiment replication identification number.
        SECTION_INTERNAL_ID: Internal ID of a certain road section.
        SECTION_EXTERNAL_ID: External ID of a certain road section.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. 0 corresponds to all time intervals aggregated.
        MEAN_SPEED: Average speed through the specified road section at a
            certain time interval.
    """

    REPLICATION_INTERNAL_ID = "did"
    SECTION_INTERNAL_ID = "oid"
    SECTION_EXTERNAL_ID = "eid"
    VEHICLE_TYPE = "sid"
    TIME_INTERVAL = "ent"
    MEAN_SPEED = "speed"
    # Add more columns as needed.


class MiDetColumns(enum.Enum):
    """Column names of the MIDETEC (Micro Detectors) table. This table contains
    statistical information about detectors from microsimulation results. The
    information contained include the number of vehicles through each detector
    at each time interval.

    Attributes:
        REPLICATION_INTERNAL_ID: Experiment replication identification number.
        DETECTOR_INTERNAL_ID: Internal ID of a certain detector.
        DETECTOR_EXTERNAL_ID: External ID of a certain detector.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. 0 corresponds to all time intervals aggregated.
        COUNT: Number of vehicles through the specified detector at a certain
            time interval. Units are vehicles per time interval length.
        FLOW: Number of vehicles through the specified detector at a certain
            time interval. Units are vehicles per hour.
    """

    REPLICATION_INTERNAL_ID = "did"
    DETECTOR_INTERNAL_ID = "oid"
    DETECTOR_EXTERNAL_ID = "eid"
    VEHICLE_TYPE = "sid"
    TIME_INTERVAL = "ent"
    COUNT = "countveh"
    FLOW = "flow"
    # Add more columns as needed.


class TotalRgapColumns(enum.Enum):
    """Column names of the Rgap (Total Relative Gap) table. This table contains
    statistical information about the instantaneous and experienced relative gap
    in the total network at each timestep.

    Attributes:
        REPLICATION_INTERNAL_ID: Experiment replication identification number.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. 0 corresponds to all time intervals aggregated.
        RGAP_EXPERIENCED: Experienced relative gap of the total network at the
            given time interval.
        RGAP_INSTANT: Instaneous relative gap of the total network at the given
            time interval.
    """

    REPLICATION_INTERNAL_ID = "did"
    VEHICLE_TYPE = "sid"
    TIME_INTERVAL = "ent"
    RGAP_INSTANT = "rgapinstantaneous"
    RGAP_EXPERIENCED = "rgapexperienced"
    # Add more columns as needed.


class MicentOriginColumns(enum.Enum):
    """Column names of the MICENT_O (Micro Centroid Origin) table. This table
    contains statistical information about the origin centroids for each time
    interval. Mainly used to compute travel times between various origin
    destination centroid pairs.

    Attributes:
        ORIGIN_CENTROID_INTERNAL_ID: Internal ID of the origin centroid.
        ORIGIN_CENTROID_EXTERNAL_ID: External ID of the origin centroid.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        DEST_CENTROID_INTERNAL_ID: Internal ID of the destination centroid.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. 0 corresponds to all time intervals aggregated.
        TRAVEL_TIME: Average travel time for all vehicles between the specified
            origin and destination centroids.
        DISTANCE: Total travel distance of all vehicles between the specified
            origin and destination centroids in kilometers.
    """

    ORIGIN_CENTROID_INTERNAL_ID = "oid"
    ORIGIN_CENTROID_EXTERNAL_ID = "eid"
    NUM_VEHICLES = "nbveh"
    VEHICLE_TYPE = "sid"
    DEST_CENTROID_INTERNAL_ID = "destination"
    TIME_INTERVAL = "ent"
    TRAVEL_TIME = "ttime"
    DISTANCE = "travel"
    # Add more columns as needed.


class MicentDestinationColumns(enum.Enum):
    """Column names of the MICENT_D (Micro Centroid Destination) table. This table
    contains statistical information about the origin centroids for each time
    interval. Mainly used to compute travel times between various origin
    destination centroid pairs.

    Attributes:
        ORIGIN_CENTROID_INTERNAL_ID: Internal ID of the origin centroid.
        ORIGIN_CENTROID_EXTERNAL_ID: External ID of the origin centroid.
        VEHICLE_TYPE: Integer identifer for type of vehicles included in the
            data. 0 for all vehicles, 1 for cars only, and 2 for trucks only.
        DEST_CENTROID_INTERNAL_ID: Internal ID of the destination centroid.
        TIME_INTERVAL: Index of the time interval of when the data was collected
            from. 0 corresponds to all time intervals aggregated.
        TRAVEL_TIME: Average travel time for all vehicles between the specified
            origin and destination centroids.
        DISTANCE: Total travel distance of all vehicles between the specified
            origin and destination centroids in kilometers.
    """

    ORIGIN_CENTROID_INTERNAL_ID = "oid"
    ORIGIN_CENTROID_EXTERNAL_ID = "eid"
    NUM_VEHICLES = "nbveh"
    VEHICLE_TYPE = "sid"
    DEST_CENTROID_INTERNAL_ID = "destination"
    TIME_INTERVAL = "ent"
    TRAVEL_TIME = "ttime"
    DISTANCE = "travel"
    # Add more columns as needed.


class SQLiteTable:
    """Data class for one SQL table from Aimsun Micro/Macrosimulation output.

    Attributes:
        __cursor: Cursor instance of the SQLite table to enable SQL operations
            from Python.
        table_name: Name of the table.
    """

    __cursor: sqlite3.Cursor
    table_name: str

    def __init__(self, database: sqlite3.Connection, table_name: str):
        self.__cursor = database.cursor()
        self.table_name = table_name

    def get_data_on_condition(
        self, data_column_name: str, condition_column_name_value: Dict[str, str] = None
    ) -> Any:
        """Gets data on condition.

        Args:
            data_column_name: Name of the column that contains the data to be
                queried in the output database SQL file.
            condition_column_name_value: Mapping of conditions that need to be
                satisfied to query data. Key of the dictionary is column name
                in the output database SQL file, and value of the dictionary is
                the value of the column that needs to be equal to.
        Returns:
            Queried data from data_column_name that abides conditions in
                condition_column_name_value.
        """
        if condition_column_name_value is None:
            self.__cursor.execute(f"SELECT {data_column_name} FROM {self.table_name}")
        else:
            condition_list = [
                f"{condition_column_name} = '{condition_value}'"
                for condition_column_name, condition_value in condition_column_name_value.items()
            ]
            self.__cursor.execute(
                f"SELECT {data_column_name} FROM {self.table_name} "
                + "WHERE "
                + " AND ".join(condition_list)
            )
        result = self.__cursor.fetchall()
        # assert len(result) == 1  # only one row for the condition.
        # assert len(result[0]) == 1  # only one data returned.
        return result[0][0]


class AimsunOutputDatabase:
    """Data class to store common output data between both Aimsun micro and
    macro simulation results.

    Attributes:
        database: SQL connection to the specified Aimsun output sqlite file.
        sim_info: SQL table that contains the ID of the object that
            generated the data. Named SIM_INFO.
        meta_info: SQL table that contains the information about all stored
            tables (for sections, nodes, turns). Named META_INFO.
        meta_sub_info: SQL table that contains the information about the
            vehicles types used to gather the data. Named META_SUB_INFO.
        meta_cols: SQL table that contains the fields stored and its type for
            all other tables. Named META_COLS.
    """

    database: sqlite3.Connection
    sim_info: SQLiteTable
    meta_info: SQLiteTable
    meta_sub_info: SQLiteTable
    meta_cols: SQLiteTable

    def __init__(self, database_path):
        self.database = sqlite3.connect(database_path)
        self.sim_info = SQLiteTable(self.database, "SIM_INFO")
        self.meta_info = SQLiteTable(self.database, "META_INFO")
        self.meta_sub_info = SQLiteTable(self.database, "META_SUB_INFO")
        self.meta_cols = SQLiteTable(self.database, "META_COLS")


class AimsunMacroOutputDatabase(AimsunOutputDatabase):
    """Data class to store all output data from Aimsun macrosimulations.

    Attributes:
        sections_table: SQL table data that maps various macrosimulation data
            to each road section ID. Named 'MASECT' in the original SQLite file.
        detectors_table: SQL table data that maps various microsimulation data
            to each detector ID. Named 'MADET' in the original SQLite file.
    """

    sections_table: SQLiteTable
    detectors_table: SQLiteTable

    def __init__(self, database_path: str):
        super().__init__(database_path)
        self.sections_table = SQLiteTable(self.database, "MASECT")
        self.detectors_table = SQLiteTable(self.database, "MADET")
        # Add more tables here if needed.

    def get_road_section_flow(self, road_id: aimsun_input_utils.InternalId) -> float:
        """Get flow of a specified road section. Used for Macrosimulations.

        Args:
            road_id: Internal ID of the road section we want the flow from.
        Returns:
            flow_count: Number of flow at the road section.
        """
        return self.sections_table.get_data_on_condition(
            MaSectColumns.FLOW.value,
            {
                MaSectColumns.SECTION_INTERNAL_ID.value: road_id,
                MaSectColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
            },
        )

    def get_detector_flow(
        self, detector_external_id: aimsun_input_utils.ExternalId
    ) -> float:
        """Get simulated flow through the specified detector. Used for
        Macrosimulations.

        Args:
            detector_external_id: External ID of the detector we want the flow
                data from.
        Returns:
            flow_value: Flow through a detector.
        """
        return self.detectors_table.get_data_on_condition(
            MaDetColumns.FLOW.value,
            {
                MaDetColumns.DETECTOR_EXTERNAL_ID.value: detector_external_id,
                MaDetColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
            },
        )

    # Define more methods as needed.


class AimsunMicroOutputDatabase(AimsunOutputDatabase):
    """Data class to store all output data from Aimsun microsimulations.

    Attributes:
        sections_table: SQL table data that maps various microsimulation data
            to each road section ID. Named 'MISECT' in the original SQLite file.
        detectors_table: SQL table data that maps various microsimulation data
            to each detector ID. Named 'MIDETEC' in the original SQLite file.
    """

    sections_table: SQLiteTable
    detectors_table: SQLiteTable
    total_rgap_table: SQLiteTable
    origin_centroids_table: SQLiteTable
    section_trajectories_table: SQLiteTable

    def __init__(self, database_path: str):
        super().__init__(database_path)
        self.system_table = SQLiteTable(self.database, "MISYS")
        self.sections_table = SQLiteTable(self.database, "MISECT")
        self.detectors_table = SQLiteTable(self.database, "MIDETEC")
        self.total_rgap_table = SQLiteTable(self.database, "RGap")
        # Add more tables here if needed.

    def convert_time_to_int(self, time_interval: datetime.time) -> int:
        """Convert a given time interval to its corresponding index within the
        Aimsun Microsimulation output SQLite database.

        Args:
            time_interval: Time to convert into its corresponding index within
                the Microsimulation SQL table. Must be of type datetime.time.
        Returns:
            time_index: Corresponding index of time_interval in the simulation
                output database.
        """
        start_time_seconds = self.sim_info.get_data_on_condition(
            SimInfoColumns.START_TIME_INTERVAL.value
        )
        time_step = self.sim_info.get_data_on_condition(
            SimInfoColumns.TOTAL_DURATION.value
        ) // self.sim_info.get_data_on_condition(
            SimInfoColumns.NUM_TIME_INTERVALS.value
        )
        time_index = (
            time_interval.hour * 3600 + time_interval.minute * 60 - start_time_seconds
        ) // time_step + 1
        assert isinstance(time_index, int) and time_index >= 1
        return time_index

    def get_road_section_flow(
        self, road_id: aimsun_input_utils.InternalId, time_interval: datetime.time
    ) -> float:
        """Get flow of a road section at the specified time interval.
        Used for Microsimulations.

        Args:
            road_id: Internal ID of the road section we want the flow from.
            time_interval: Time interval of when we want the flow from.
        Returns:
            flow_count: Number of flow at the road section in the given time
                interval.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        return self.sections_table.get_data_on_condition(
            MiSectColumns.MEAN_FLOW.value,
            {
                MiSectColumns.SECTION_INTERNAL_ID.value: road_id,
                MiSectColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                MiSectColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )

    def get_road_section_speed(
        self, road_id: aimsun_input_utils.InternalId, time_interval: datetime.time
    ) -> float:
        """Get average speed of a road section at the specified time interval.
        Used for Microsimulations.

        Args:
            road_id: Internal ID of the road section we want the speed from.
            time_interval: Time interval of when we want the speed from.
        Returns:
            avg_speed: Average speed at the road section in the given time
                interval.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        return self.sections_table.get_data_on_condition(
            MiSectColumns.MEAN_SPEED.value,
            {
                MiSectColumns.SECTION_INTERNAL_ID.value: road_id,
                MiSectColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                MiSectColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )

    def get_road_section_travel_time(
        self, road_id: aimsun_input_utils.InternalId, time_interval: datetime.time
    ) -> float:
        """Get travel time of a road section at the specified time interval.
        Used for Microsimulations.

        Args:
            road_id: Internal ID of the road section we want to compute the
                travel time from.
            time_interval: Time interval of when we want the travel time from.
        Returns:
            travel_time: Travel time for the given road section in the given
                time interval.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        return self.sections_table.get_data_on_condition(
            MiSectColumns.MEAN_TRAVEL_TIME.value,
            {
                MiSectColumns.SECTION_INTERNAL_ID.value: road_id,
                MiSectColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                MiSectColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )

    def get_detector_flow(
        self,
        detector_external_id: aimsun_input_utils.ExternalId,
        time_interval: datetime.time,
    ) -> float:
        """Get simulated flow through a detector at the specified time interval.
        Used for Microsimulations.

        Args:
            detector_external_id: External ID of the detector we want the flow
                data from.
            time_interval: Time interval of when we want the flow from.
        Returns:
            flow_value: Flow through a detector at the given time interval.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        return self.detectors_table.get_data_on_condition(
            MiDetColumns.FLOW.value,
            {
                MiDetColumns.DETECTOR_EXTERNAL_ID.value: detector_external_id,
                MiDetColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                MiDetColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )

    def get_total_delay_time(self, time_interval: datetime.time) -> float:
        """Get total delay time across the network.

        Args:
            time_interval: Time interval of when we want the delay time from.
        Returns:
            delay_time: Delay time of the entire network at given time.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        return self.system_table.get_data_on_condition(
            MiSysColumns.DELAY_TIME.value,
            {
                MiDetColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                MiDetColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )

    def get_total_instantaneous_rgap(self, time_interval: datetime.time) -> float:
        """Get instantaneous relative gap for the entire network at the given
        time interval.

        Args:
            time_interval: Time interval of when we want the Rgap from.
        Returns:
            rgap_instant: Instantaneous relative gap for the entire network.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        rgap_instant = self.total_rgap_table.get_data_on_condition(
            TotalRgapColumns.RGAP_INSTANT.value,
            {
                TotalRgapColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                TotalRgapColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )
        return rgap_instant

    def get_total_experienced_rgap(self, time_interval: datetime.time) -> float:
        """Get experienced relative gap for the entire network at the given
        time interval.

        Args:
            time_interval: Time interval of when we want the Rgap from.
        Returns:
            rgap_experience: Experienced relative gap for the entire network.
        """
        time_interval_int = self.convert_time_to_int(time_interval)
        rgap_experience = self.total_rgap_table.get_data_on_condition(
            TotalRgapColumns.RGAP_EXPERIENCED.value,
            {
                TotalRgapColumns.VEHICLE_TYPE.value: ALL_VEHICLE_TYPES,
                TotalRgapColumns.TIME_INTERVAL.value: str(time_interval_int),
            },
        )
        return rgap_experience

    # Define more methods as needed.
