import json

from opthub_runner.lib.docker_executor import execute_in_docker


def test() -> None:
    std_out = execute_in_docker(
        {
            "image": "mysphere:latest",
            "environments": {
                # "SPHERE_OPTIMA": "[[1, 2, 3], [4, 5, 6]]",
            },
            "command": [],
            "timeout": 100,
            "rm": True,
        },
        [json.dumps([1, 1]) + "\n"],
    )

    print(std_out)

    # std_out = execute_in_docker(
    #     {
    #         "image": "opthub/hypervolume:latest",
    #         "environments": {
    #             "HV_REF_POINT": "[1, 1]",
    #         },
    #         "command": [],
    #         "timeout": 100,
    #         "rm": True,
    #     },
    #     '{"objective": [0.1, 0.2], "constraint": null, "info": null}\n[]\n',
    # )
    # print(std_out)
