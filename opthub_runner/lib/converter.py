"""This module contains the functions to convert the data types of the values in the object."""

import decimal
import logging
import math
import sys

LOGGER = logging.getLogger(__name__)


def float_to_json_float(value: object) -> object:  # noqa: PLR0911
    """Convert float values to JSON float values.

    Args:
        value (object): The object consists of float values.

    Returns:
        object: The object consists of json float values.
    """
    if isinstance(value, list):
        return [float_to_json_float(v) for v in value]
    if isinstance(value, dict):
        return {k: float_to_json_float(v) for k, v in value.items()}
    if not isinstance(value, float):
        return value
    if value == math.inf:
        LOGGER.warning("math.inf is converted to sys.float_info.max")
        return sys.float_info.max
    if value == -math.inf:
        LOGGER.warning("-math.inf is converted to -sys.float_info.max")
        return -sys.float_info.max
    if math.isnan(value):
        LOGGER.warning("math.nan is converted to None")
        return None
    return value


def decimal_to_int(value: object) -> object:
    """Convert decimal values to int values.

    Args:
        value (object): The object consists of decimal values.

    Returns:
        object:  The object consists of int values.
    """
    if isinstance(value, list):
        return [decimal_to_int(v) for v in value]
    if isinstance(value, dict):
        return {k: decimal_to_int(v) for k, v in value.items()}
    if isinstance(value, decimal.Decimal):
        return int(value)
    return value


def decimal_to_float(value: object) -> object:
    """Convert decimal values to float values.

    Args:
        value (object): The object consists of decimal values.

    Returns:
        object: The object consists of float values.
    """
    if isinstance(value, list):
        return [decimal_to_float(v) for v in value]
    if isinstance(value, dict):
        return {k: decimal_to_float(v) for k, v in value.items()}
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value


def number_to_decimal(value: object) -> object:
    """Convert number values to decimal values.

    Args:
        value (object): The object consists of int and float values.

    Returns:
        object: The object consists of decimal values.
    """
    if isinstance(value, list):
        return [number_to_decimal(v) for v in value]
    if isinstance(value, dict):
        return {k: number_to_decimal(v) for k, v in value.items()}
    if isinstance(value, float | int):
        return decimal.Decimal(str(value))
    return value
