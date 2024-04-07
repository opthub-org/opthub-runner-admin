"""Tests for zfill.py."""

import pytest

from opthub_runner.utils.zfill import zfill


def test_zfill() -> None:
    """Test for zfill."""
    if zfill(12, 3) != "012":
        msg = "zfill(12, 3) != 012"
        raise ValueError(msg)

    if zfill(100, 3) != "100":
        msg = "zfill(100, 3) != 100"
        raise ValueError(msg)

    with pytest.raises(ValueError, match="length of number != digit."):
        zfill(1000, 3)
