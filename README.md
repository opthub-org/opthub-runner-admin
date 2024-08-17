[日本語版](https://github.com/opthub-org/opthub-runner-admin/blob/main/README_ja.md) 👈

# OptHub Runner

![Skills](https://skillicons.dev/icons?i=py,aws,graphql,docker,vscode,github)

Opthub Runner is a Python package that provides the following two features:

- Evaluator: Feature to evaluate user-submitted solutions on Opthub using Docker Image.
- Scorer: Feature to calculate scores from a series of evaluations using Docker Image.

This repository describes how to install and run Opthub Runner.

## Getting Started
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
Specify the options for starting the Evaluator and Scorer in a YAML file. For detailed information on the options set in the file, please refer to [YAML File Options](#YAMLFileOptions).

### 3. Execution
#### Running Evaluator

First, start the Evaluator using the following command.

Set the path to the YAML file configured with the options in `--config`.


```bash
opthub-runner evaluator --config (yaml file path)
```

You will be prompted to enter a username and password. Please enter **the administrator** username and password for the competition.

```bash
Username: (your username)
Password: (your password)
```

#### Running Scorer
First, start the Scorer using the following command.

Set the path to the YAML file configured with the options in `--config`.

```bash
opthub-runner scorer --config (yaml file path)
```

You will be prompted to enter a username and password. Please enter **the administrator** username and password for the competition.
```bash
Username: (your username)
Password: (your password)
```

## YAML File Options <a id="YAMLFileOptions"></a>
The following table describes the options to be specified in the YAML file, including their types, default values, and descriptions.

| Option | Type | Default Value | Description |
| ------ | ---- | ------------- | ----------- |
| interval | int | 2 | Interval to fetch messages from Amazon SQS. |
| timeout | int | 43200 | Timeout for evaluation and score calculation using Docker Image. |
| rm | bool | True | Whether to remove the Docker Container after evaluation and score calculation. |
| log_level | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | INFO | Log level to output. |
| evaluator_queue_url | path | - | Amazon SQS queue URL used by the Evaluator. |
| scorer_queue_url | path | - | Amazon SQS queue URL used by the Scorer. |
| access_key_id | str | - | AWS Access Key ID. |
| secret_access_key | str | - | AWS Secret Access Key. |
| region_name | str | - | AWS default Region Name. |
| table_name | str | - | DynamoDB table name to store solutions, evaluations, and scores. |

Please check the values for the following options with the OptHub representative. Contact information is [here](#Contact).

- evaluator_queue_url
- scorer_queue_url
- access_key_id
- secret_access_key
- region_name
- table_name

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
    - For the values of the options commented out in `config.default.yml`, please contact the Opthub representative. Contact information is [here](#Contact).

Once you have completed the above setup, you can use the `opthub-runner` command in the project's root directory.

## Contact <a id="Contact"></a>

If you have any questions or concerns, please feel free to contact us (Email: dev@opthub.ai).

<img src="https://opthub.ai/assets/images/logo.svg" width="200">
