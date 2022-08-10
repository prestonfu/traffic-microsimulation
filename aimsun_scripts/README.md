# Aimsun scripts

This folder contains all files that should be imported into the Aimsun software to interact with it.
The files in this folder import necessary data to create the simulation, generates the simulation scenario, and executes the simulation in Aimsun.

## Structure

### Utility files
- `aimsun_utils_functions.py`: Helper functions to import and create data in Aimsun.

### Scripts for simulation
- `append_github_path_to_python.py`: Appends repository path to Aimsun. This enables other scripts to access functions from different folders.
- `clean_project.py`: Cleans all imported data from the Aimsun network file.
- `create_simulation.py`: Generate simulation scenarios.
- `import_model.py`: Imports all necessary data into Aimsun.
- `run_simulation.py`: Runs created simulation scenario.
- `set_yellow_box.py`: Draws a yellow box around all nodes in Aimsun.

## Process

To create and execute the microsimulation in Aimsun, you must have a Aimsun base network file and input data ready. An example base network file can be found at `../fremont-public-data/fremont_network.ang`.

Once the Aimsun base network file and input data is available, please follow the following steps:

1. Change `__REPO_PATH` in `append_github_path_to_python.py` to your absolute path for this repository (traffic-microsimulation).
2. Change `MICRO_BASELINE = True` in `create_simulations.py` and `run_simulation.py`.
3. Open Aimsun base network file in Aimsun.
4. Import all Python files in Aimsun by clicking File > Import > Python Script.
5. Execute `append_github_path_to_python.py`. This will let Aimsun know the location of the repository.
6. Execute `import_model.py` This will import all necessary data (listed below) into Aimsun.
    - Centroid connections
    - OD matrices
    - Master control plan with the associated control plans, ramp meterings and traffic light detectors
    - Speed limits and road capacities
    - Flow detectors
    - Traffic management strategies. 
7. Execute `create_simulation.py`. This will create the simulation.
8. Run the simulation within Aimsun by using the GUI or by executing `run_simulation.py`.

After the last step, the simulation will produce an output database defined at `../utils/aimsun_folder_utils.aimsun_micro_databases_file()`. This output database can then be used to validate/calibrate the simulation using notebooks under `../calibration/`.
