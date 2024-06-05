"""Test for cache.py."""

import pytest

from opthub_runner_admin.scorer.cache import Cache, Trial


def test_cache() -> None:
    """Test for Cache."""
    cache = Cache()

    with pytest.raises(ValueError, match="No file loaded."):
        cache.append(
            Trial({"trial_no": "1", "objective": 0.1, "constraint": None, "info": {}, "score": 0.1, "feasible": True}),
        )

    cache.load("Match#1#Team#1")
    values_of_cache1 = [
        Trial({"trial_no": "1", "objective": 0.1, "constraint": None, "info": {}, "score": 0.1, "feasible": True}),
        Trial({"trial_no": "2", "objective": 0.2, "constraint": None, "info": {}, "score": 0.2, "feasible": False}),
        Trial({"trial_no": "3", "objective": 0.3, "constraint": None, "info": {}, "score": 0.3, "feasible": None}),
    ]
    values_of_cache2 = [
        Trial({"trial_no": "1", "objective": 1.0, "constraint": None, "info": {}, "score": 1.0, "feasible": None}),
    ]
    cache.append(
        Trial({"trial_no": "1", "objective": 0.1, "constraint": None, "info": {}, "score": 0.1, "feasible": True}),
    )
    cache.append(
        Trial({"trial_no": "2", "objective": 0.2, "constraint": None, "info": {}, "score": 0.2, "feasible": False}),
    )
    cache.append(
        Trial({"trial_no": "3", "objective": 0.3, "constraint": None, "info": {}, "score": 0.3, "feasible": None}),
    )
    cache.load("Match#1#Team#2")
    cache.append(
        Trial({"trial_no": "1", "objective": 1.0, "constraint": None, "info": {}, "score": 1.0, "feasible": None}),
    )
    cache.load("Match#1#Team#1")

    if cache.get_values() != values_of_cache1:
        msg = "cache.get_values() != values_of_cache1"
        raise ValueError(msg)
    cache.load("Match#1#Team#2")
    if cache.get_values() != values_of_cache2:
        msg = "cache.get_values() != values_of_cache2"
        raise ValueError(msg)

    cache.clear()

    with pytest.raises(ValueError, match="No file loaded."):
        cache.get_values()
    with pytest.raises(ValueError, match="No file loaded."):
        cache.append(
            Trial({"trial_no": "1", "objective": 0.1, "constraint": None, "info": {}, "score": 0.1, "feasible": True}),
        )

    cache.load("Match#1#Team#1")
    if cache.get_values() != values_of_cache1:
        msg = "cache.get_values() != values_of_cache1"
        raise ValueError(msg)
