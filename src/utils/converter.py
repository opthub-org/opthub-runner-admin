import sys
import math
import logging
import decimal

LOGGER = logging.getLogger(__name__)


def float_to_json_float(value):
    """Convert a float value to a JSON float value.

    :param value: float value
    :return float: JSON float value
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


def decimal_to_number(value):
    """
    decimal型の数をfloatに変換する．

    """
    if isinstance(value, list):
        return [decimal_to_number(v) for v in value]
    if isinstance(value, dict):
        return {k: decimal_to_number(v) for k, v in value.items()}
    if isinstance(value, decimal.Decimal):
        return float(value)
    else:
        return value

def number_to_decimal(value):
    if isinstance(value, list):
        return [number_to_decimal(v) for v in value]
    if isinstance(value, dict):
        return {k: number_to_decimal(v) for k, v in value.items()}
    if isinstance(value, int) or isinstance(value, float):
        return decimal.Decimal(value)
    else:
        return value