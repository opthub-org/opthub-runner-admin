"""This module provides a function to fill the number with zeros in the digit."""


def zfill(number: int, digit: int) -> str:
    """Fill the number with zeros in the digit.

    If the number of digits of the filled number exceeds the digit, an error occurs.

    Args:
        number (int): The number to fill with zeros.
        digit (int): The number of digits to fill with zeros.

    Raises:
        ValueError: If the length of the number is not equal to the digit, an error occurs.

    Returns:
        str: The number filled with zeros.
    """
    number_str = str(number).zfill(digit)

    if len(number_str) != digit:
        msg = "length of number != digit."
        raise ValueError(msg)

    return number_str
