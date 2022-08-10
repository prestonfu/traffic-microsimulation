# Repository utils

This folder contains all utility files used to standardize filepaths and dataclasses throughout the repository.

**Important**: All private variables in `metadata_settings.py` must be defined to use this repository.

## Structure

- `aimsun_attribute_utils.py`: Attribute definitions for Aimsun-specific objects and parameters.
- `aimsun_config_utils.py`: Dataclasses to standardize Aimsun simulation configuration files.
- `aimsun_folder_utils.py`: Folder utils to standardize Aimsun input and output related files.
- `aimsun_input_utils.py`: Dataclasses to standardize Aimsun input data.
- `metadata_settings.py`: Metadata setting to configure for the entire repository. Must be set to use the repo.
- `verification_utils.py`: Helper methods to verify correctness of dataclasses.
