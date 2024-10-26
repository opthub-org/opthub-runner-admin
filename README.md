[日本語版](https://github.com/opthub-org/opthub-runner-admin/blob/main/README_ja.md) 👈

# OptHub Runner

![Skills](https://skillicons.dev/icons?i=py,aws,graphql,docker,vscode,github)

Opthub Runner is a Python package that provides the following two features:

- Evaluator\*: Feature to evaluate user-submitted solutions on Opthub using Docker Image.
- Scorer\*: Feature to calculate scores from a series of evaluations using Docker Image.

Please refer to 4.競技の確認 in [OptHub Tutorial](https://opthub.notion.site/OptHub-1b96e2f4e9424db0934f297ee0351403) for detailed explanations of the Evaluator and Scorer.

This repository describes how to install and run Opthub Runner.

## Getting Started

### Recommended Environment

We recommend using the following environments:

- [AWS EC2](https://aws.amazon.com/ec2/).
- [GCP Compute Engine](https://cloud.google.com/products/compute).
- [Sakura Cloud](https://www.sakura.ad.jp/?gad_source=1&gclid=Cj0KCQjwmOm3BhC8ARIsAOSbapUD6m2okjosfvKuZvb91rdY4lmgMOZeFtMr2eTZqQLTCrw5naQCE0saAtzWEALw_wcB).
- Any other environment that supports Docker and can run continuously.

### Prerequisites

- Install Python 3.10 or newer.
- Set up pip for package management.
- Install and start Docker.*

\*For Mac users, you can install and start [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/).

### 1. Installation

Install `opthub-runner-admin` from PyPI.

```bash
pip install opthub-runner-admin
```

### 2. Configuring YAML File

Create a YAML file with the options needed to run the Evaluator and Scorer, based on [config.default.yml](https://github.com/opthub-org/opthub-runner-admin/blob/main/config.default.yml). For details on the options to set in the file, please refer to [YAML File Options](#yaml-file-options).

### 3. Starting the Evaluator/Scorer

At first, start Docker. **Please note that Docker must remain running while the Evaluator/Scorer is active.**

Then, run the Evaluator/Scorer using the following command. Replace `<evaluator|scorer>` with either `evaluator` or `scorer`. For `--config`, specify the path to the YAML file you created in [2. Configuring YAML File](#2-configuring-yaml-file). If not specified, the `config.yml` in the current directory will be used.

```bash
opthub-runner <evaluator|scorer> --config <yaml file path>
```

You will be prompted to enter the username and password. These must be the ones of the competition administrator.

```bash
Username: (your username)
Password: (your password)
```

**Please note that the Evaluator/Scorer must remain running during the competition.** If you have any other issues, please refer to [Troubleshooting](#troubleshooting).

## YAML File Options

The following table lists the options to include in the YAML file, along with their type, default values, and descriptions. Please confirm the default values for the following options with the OptHub representative. Contact information is [here](#contact).

- evaluator_queue_url
- scorer_queue_url
- access_key_id
- secret_access_key
- region_name
- table_name

| Option | Type | Default Value | Description |
| ------ | ---- | ------------- | ----------- |
| interval | int | 2 | Interval to fetch messages from Amazon SQS. |
| timeout | int | 43200 | Timeout for evaluation and score calculation using Docker Image. |
| rm | bool | True | Whether to remove the Docker container after evaluation and score calculation. True is recommended except for debugging. If set to False, the Docker containers created during evaluation and scoring will not be removed, accumulating over time. |
| log_level | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | INFO | Log level to output. |
| evaluator_queue_url | path | - | Amazon SQS queue URL used by the Evaluator. |
| scorer_queue_url | path | - | Amazon SQS queue URL used by the Scorer. |
| access_key_id | str | - | AWS Access Key ID. |
| secret_access_key | str | - | AWS Secret Access Key. |
| region_name | str | - | AWS default Region Name. |
| table_name | str | - | DynamoDB table name to store solutions, evaluations, and scores. |

## Troubleshooting

### Docker is Not Running

The following error occurs when Docker is not running.

```plaintext
Error: Unable to communicate with Docker. Please ensure Docker is running and accessible. (Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory')))
```

For Mac, you can resolve this issue by starting Docker Desktop. You can install Docker Desktop [here](https://docs.docker.com/desktop/install/mac-install/).

For Ubuntu, you can resolve this issue by installing Docker via the terminal with the following command.

```plaintext
sudo apt install docker.io
```

### No Permission to Access Docker Socket

The following error occurs when the current user does not have permission to access the Docker socket.

```plaintext
Error: Unable to communicate with Docker. Please ensure Docker is running and accessible. (Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied')))
```

For Ubuntu, you can resolve this issue by adding the user to the Docker group and then logging in again. Specifically, follow these steps:

1. Run the following command in the terminal:

    ```plaintext
    sudo usermod -aG docker $USER
    ```

2. Either log in again or run the following command in the terminal:

    ```plaintext
    newgrp docker
    ```

### Not Logged in with Competition Administrator Account

The following error occurs if you did not log in with the competition administrator account when starting the Evaluator/Scorer.

```plaintext
Traceback (most recent call last):
  ･･･
opthub_runner_admin.models.exception.DockerImageNotFoundError: Cannot access the Docker image. Please check your permissions. If you're not authenticated using the competition administrator's account, please do so.
```

You can resolve this issue by logging in with the competition administrator’s account when starting the Evaluator/Scorer. When the following prompt appears, enter the administrator’s username and password.

```plaintext
Note: Make sure to authenticate using the competition administrator's account.
Username: (The administrator's username)
Password: (The administrator's password)
```

### YAML File Not Found

The following error occurs when the YAML file containing the Evaluator/Scorer settings does not exist.

```plaintext
Traceback (most recent call last):
  ･･･
FileNotFoundError: Configuration file not found: config.yml
```

Please create a `config.yml` file by referring to [2. Configuring YAML File](#2-configuring-yaml-file).

### Incorrect AWS Access Key ID

The following error occurs when the AWS Access Key ID (`access_key_id`) set in `config.yml` is incorrect.

```plaintext
Traceback (most recent call last):
  ･･･
botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId) when calling the ReceiveMessage operation: The security token included in the request is invalid.
```

Please check the AWS Access Key ID set in `config.yml` and enter the correct value.

### Incorrect AWS Secret Access Key

The following error occurs when the AWS Secret Access Key (`secret_access_key`) set in `config.yml` is incorrect.

```plaintext
Traceback (most recent call last):
  ･･･
botocore.exceptions.ClientError: An error occurred (SignatureDoesNotMatch) when calling the ReceiveMessage operation: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details.

```

Please check the AWS Secret Access Key set in `config.yml` and enter the correct value.

### Incorrect SQS Queue Name

The following error occurs when the SQS queue name (`evaluator_queue_name` / `scorer_queue_name`) set in `config.yml` is incorrect.

```plaintext
Traceback (most recent call last):
  ･･･
botocore.errorfactory.QueueDoesNotExist: An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the ReceiveMessage operation: The specified queue does not exist.
```

Please check the SQS queue name set in `config.yml` and enter the correct value.

### Incorrect DynamoDB Table Name

The following error occurs when the Amazon DynamoDB table name (`table_name`) set in `config.yml` is incorrect.

```plaintext
Traceback (most recent call last):
  ･･･
botocore.errorfactory.ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the GetItem operation: Requested resource not found

```

Please check the DynamoDB table name set in `config.yml` and enter the correct value.

### Incorrect AWS Default Region Name

The following error occurs when the AWS Default Region Name (`region_name`) set in `config.yml` is incorrect.

```plaintext
Traceback (most recent call last):
  ･･･
urllib3.exceptions.NameResolutionError: <botocore.awsrequest.AWSHTTPSConnection object at 0x104d8bce0>: Failed to resolve 'sqs.ap-northeas-1.amazonaws.com' ([Errno 8] nodename nor servname provided, or not known)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  ･･･
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "https://sqs.ap-northeas-1.amazonaws.com/"
```

Please check the AWS Default Region Name set in `config.yml` and enter the correct value.

### Error Inside the Docker Container

The following error is displayed when an error occurs inside the Docker container.

```plaintext
ERROR:opthub_runner_admin.evaluator.main:Error occurred while evaluating solution.
Traceback (most recent call last):
  File "/home/opthub/.venv/lib/python3.11/site-packages/opthub_runner_admin/evaluator/main.py", line 125, in evaluate
    evaluation_result = execute_in_docker(
                        ^^^^^^^^^^^^^^^^^^
  File "/home/opthub/.venv/lib/python3.11/site-packages/opthub_runner_admin/lib/docker_executor.py", line 88, in execute_in_docker
    raise RuntimeError(msg)
RuntimeError: Failed to parse stdout.
```

To investigate this error in detail, you need to check the Docker container logs. Modify the `rm` setting in `config.yml` to `False`, then restart the Evaluator/Scorer and, after execution, check the logs of the container. You can view the Docker container logs with the following command:

```bash
$ docker ps # Check Container ID
$ docker logs <Container ID> # View logs
```

Check the logs and modify the Docker image to ensure the Docker container output is in the correct format.

Additionally, the following container log shows an error that occurs when the built Docker image is run on an incompatible platform.

```plaintext
exec /usr/bin/sh: exec format error
```

To ensure compatibility, either match the environment used to build the Docker image with the environment used to run the Evaluator/Scorer, or use `buildx` to create a compatible Docker image.

## For Contributors

Follow these steps to set up the environment:

1. Clone this repository.
2. Set up Poetry.
3. Run `poetry install`.
4. Download the recommended VSCode Extensions.
5. Disable the following VS Code Extensions for this workspace to avoid conflicts with other packages:
    - ms-python.pylint
    - ms-python.black-formatter
    - ms-python.flake8
    - ms-python.isort
6. Create `config.yml` with options based on `config.default.yml`.
    - Place `config.yml` directly under opthub-runner-admin.
    - For the values of the options commented out in `config.default.yml`, please contact the Opthub representative. Contact information is [here](#contact).

Once you have completed the above setup, you can use the `opthub-runner` command in the project's root directory.

## Contact

If you have any questions or concerns, please feel free to contact us (Email: dev@opthub.ai).

<img src="https://opthub.ai/assets/images/logo.svg" width="200">
