# Open source tools for traffic microsimulation creation, calibration and validation with Aimsun

This repository aims to provide open source tools to create traffic microsimulation of any city.

It has been created during a project with the objective to replicate Fremont San Jose neighborhood traffic with the traffic microsimulator software Aimsun.
This work is part of a larger body of research done by members of the Mobile sensing lab at UC Berkeley about modelling the impact of routing behaviors on road traffic.

## Structure

This repository contains three folders and one submodule.

The three folders contain files used to create, calibrate, and validate the Aimsun traffic microsimulation. 
A high-level overview of the strucutre is as below.

- `aimsun_scripts`: Contains files that interact directly with Aimsun to create and execute the simulation.
- `calibration`: Contains files that calibrate and/or analyze simulations after it has been run.
- `utils`: Contains files that standardize dataclasses and filepaths throughout the repository.

The submodule contains example data for the city of Fremont to help users understand the structure and outputs of this repository as well as the traffic simulation.
- `fremont-public-data`: Contains files that contain processed data from public sources for the city of Fremont.

## Process

The process to create & analyze a traffic microsimulation for a city is largely divided into three steps - generating Aimsun input data, creating the simulation in Aimsun, and analyzing the simulation results.

The steps to do so are detailed below.

### 1. Configure settings
To start using this repository, users must define private variables in `utils/metadata_settings.py`. The default is set to the Fremont project example.

### 2. Generating Aimsun input data
This step varies largely from city to city, and so users must create their own pipeline to convert raw data into Aimsun input data. Some examples of raw data sources users can reference are [StreetLight](https://www.alamedactc.org/wp-content/uploads/2020/12/SR_262-Local_Existing_Memorandum_Final_Dec2019.pdf) and [San Francisco City Transportation Authority (SFCTA)](https://github.com/sfcta).

However, as long as the user is able to create Aimsun input data that follow the dataclasses and filepaths specified in the table below, the data will be compatible with this pipeline.

| Aimsun Input Data Name | Dataclass | Filepath |
|---|---|---|
| Centroid Configuration | `utils.aimsun_input_utils.CentroidConfiguration` | Given by `utils.aimsun_folder_utils.centroid_connections_aimsun_input_file()` |
| Origin-Destination Demand Matrices | `utils.aimsun_input_utils.OriginDestinationMatrices` | Given by  `utils.aimsun_folder_utils.od_demand_aimsun_input_file()` |
| Master Control Plan | `utils.aimsun_input_utils.MasterControlPlan` | Given by  `utils.aimsun_folder_utils.master_control_plan_aimsun_input_file()` |
| Speed Limits and Capacities | `utils.aimsun_input_utils.SectionSpeedLimitsAndCapacities` | Given by  `utils.aimsun_folder_utils.speed_and_capacity_aimsun_input_file()` |
| Traffic Management Strategies | `utils.aimsun_input_utils.TrafficManagementStrategy` | Given by  `utils.aimsun_folder_utils.traffic_management_aimsun_input_file()` |
| Flow Detectors | `utils.aimsun_input_utils.AimsunFlowRealDataSet` | Given by  `utils.aimsun_input_utils.detector_flow_aimsun_input_file()` |

### 3. Creating the simulation in Aimsun
Once Aimsun input data is ready, the user should create a configuration file for the simulation by running Step 1 (Configure microsimulations) in `calibration/microsimulation_config_and_analysis.ipynb`.

Then, the user should execute Aimsun scripts to automatically load and run the simulation.
The process to do so is detailed in the README under `aimsun_scripts/`.

### 4. Analyzing the simulation
Once the simulation is complete and the output database is available, the user can further proceed with next steps in the analysis notebook at `calibration/microsimulation_config_and_analysis.ipynb`.

At this step, it is up to the user to assess the accuracy of the simulation according to real data sets and calibrate the simulation.

## Dependencies

Python dependencies are listed in requirements.txt.
Please run `pip3 install -r requirements.txt` to install all packages.

***

Last updated for Aimsun v22.0.1
