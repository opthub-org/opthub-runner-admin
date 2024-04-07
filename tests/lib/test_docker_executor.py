"""Tests for docker_executor.py."""

from opthub_runner.lib.docker_executor import execute_in_docker


def test_execute_in_docker() -> None:
    """Test execute_in_docker function."""
    std_out = execute_in_docker(
        {
            "image": "opthub/sphere:latest",
            "environments": {
                "SPHERE_OPTIMA": "[[1, 2, 3], [4, 5, 6]]",
            },
            "command": [],
            "timeout": 100,
            "rm": True,
        },
        ["[1, 1, 1]\n"],
    )

    if "objective" not in std_out:
        msg = "objective is not in std_out"
        raise ValueError(msg)

    std_out = execute_in_docker(
        {
            "image": "opthub/hypervolume:latest",
            "environments": {
                "HV_REF_POINT": "[1, 1]",
            },
            "command": [],
            "timeout": 100,
            "rm": True,
        },
        ['{"objective": [0.1, 0.2], "constraint": null, "info": null}\n[]\n'],
    )

    if "score" not in std_out:
        msg = "score is not in std_out"
        raise ValueError(msg)
