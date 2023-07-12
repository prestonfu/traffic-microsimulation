"""Verification functions to test the correctness of filepaths before export
and import methods in all other util files.

This file serves to reduce redundancies between path-checking assert
statements by defining common verification methods.
"""

from os import path
from typing import Any, List


def verify_filepath(filepath: str, filetype_extension: str):
    """Determine that the given filepath is a valid and working path with the
    specified filetype extension.

    Args:
        filepath: Filepath to check.
        filetype_extension: Filetype extension to check.
    """
    if not path.exists(path.dirname(filepath)):
        raise FileNotFoundError(
            f"The given filepath {filepath} is not a valid filepath."
        )
    if f".{filetype_extension}" not in filepath:
        raise ValueError(f"Filepath does not point to a .{filetype_extension} file.")


def verify_attributes(obj: Any, attribute_list: List[Any], message: str = ""):
    """Determine that the given object contains all attributes in the manually
    defined list of attributes.

    Args:
        obj: Object to check if it contains the defined attributes.
        attribute_list: List of attributes to check if it exists in obj.
        message: Message to display when the given object does not contain all
            attributes in attribute_list.
    """
    if not all((hasattr(obj, x) for x in attribute_list)):
        if message:
            raise AttributeError(message)
        raise AttributeError
