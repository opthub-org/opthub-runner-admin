from opthub_runner.lib.docker_executor import execute_in_docker


def test() -> None:
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
        "[1, 1, 1]\n",
    )

    print(std_out)

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
        '{"objective": [0.11999999999999994, 0.2700000000000001], "constraint": null}\n[]\n',
    )
    print(std_out)
