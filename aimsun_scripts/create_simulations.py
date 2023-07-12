"""Executes Aimsun simulation scenario."""

from typing import List
from aimsun_utils_functions import run_experiments

from aimsun_scripts import aimsun_config_utils
from aimsun_scripts import aimsun_input_utils
from utils.aimsun_folder_utils import (
    aimsun_macro_simulation_config_input_file,
    aimsun_micro_simulation_config_input_file,
)


MACRO_BASELINE = False
MICRO_BASELINE = True

LIST_EXPERIMENT_EXTERNAL_ID: List[aimsun_input_utils.ExternalId] = []

if MACRO_BASELINE:
    LIST_EXPERIMENT_EXTERNAL_ID = [
        scenario.experiment.external_id
        for scenario in aimsun_config_utils.AimsunStaticMacroScenarios(
            aimsun_macro_simulation_config_input_file()
        ).aimsun_static_macroscenarios
    ]
elif MICRO_BASELINE:
    LIST_EXPERIMENT_EXTERNAL_ID = [
        aimsun_config_utils.AimsunScenario(
            aimsun_micro_simulation_config_input_file()
        ).experiment.external_id
    ]

run_experiments(LIST_EXPERIMENT_EXTERNAL_ID, model, GKSystem.getSystem())
