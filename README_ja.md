[English Version](https://github.com/opthub-org/opthub-runner-admin) 👈

# OptHub Runner

![Skills](https://skillicons.dev/icons?i=py,aws,graphql,docker,vscode,github)

OptHub Runnerは、以下の2つの機能を提供するPythonパッケージです。

- Evaluator(評価機)\*: Docker Imageを使って、OptHubでユーザから提出された解を評価する機能
- Scorer(スコア計算機)\*:  Docker Imageを使って評価の系列からスコアを計算する機能

\* EvaluatorとScorerの詳細な説明は、[OptHub チュートリアル](https://opthub.notion.site/OptHub-1b96e2f4e9424db0934f297ee0351403)の 4.競技の確認 をご覧ください。

このリポジトリでは、OptHub Runnerのインストールや実行方法を説明しています。

## 利用方法

### 推奨環境

以下の環境で利用することを推奨します。

- [AWS EC2](https://aws.amazon.com/jp/ec2/)
- [GCP Compute Engine](https://cloud.google.com/products/compute?hl=ja)
- [Sakura Cloud](https://www.sakura.ad.jp/?gad_source=1&gclid=Cj0KCQjwmOm3BhC8ARIsAOSbapUD6m2okjosfvKuZvb91rdY4lmgMOZeFtMr2eTZqQLTCrw5naQCE0saAtzWEALw_wcB)
- その他、Dockerを利用できる常時実行可能な環境

### 前提条件

- Python 3.10以上をインストール
- pipを使えるように設定
- Dockerをインストールして起動*

\*Macの場合は、[Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)をインストールして起動できます。

### 1. インストール

PyPIから`opthub-runner-admin`をインストールします。

```bash
pip install opthub-runner-admin
```

### 2. YAMLファイルの構成

[config.default.yml](https://github.com/opthub-org/opthub-runner-admin/blob/main/config.default.yml)を参考に、EvaluatorやScorerを起動するためのオプションを記述したYAMLファイルを作成します。ファイルに設定するオプションの詳細は、[YAMLファイルのオプション](#yamlファイルのオプション)を参照してください。

### 3. Evaluator/Scorerの起動

始めに、Dockerを起動します。**Evaluator/Scorerを起動している間は、Dockerを起動し続ける必要があることに注意してください。**

次に、以下のコマンドでEvaluator/Scorerを起動します。`<evaluator|scorer>`には、`evaluator`もしくは`scorer`を入れてください。`--config`には、[2.YAMLファイルの構成](#2-yamlファイルの構成) で作成したYAMLファイルのパスを設定します。指定しない場合は、実行ディレクトリ直下の`config.yml`が使用されます。

```bash
opthub-runner <evaluator|scorer> --config <yaml file path>
```

ユーザ名とパスワードを求められるので、それぞれ入力します。ここで入力するユーザ名とパスワードは、コンペの管理者のものである必要があります。

```bash
Username: (your username)
Password: (your password)
```

**コンペティションの開催中は、Evaluator/Scorerを起動し続ける必要があることに注意してください。** その他の問題が発生した場合には、[トラブルシューティング](#トラブルシューティング)を参照してください。

## YAMLファイルのオプション

以下の表に、YAMLファイルに記述するオプションとその型、デフォルト値、説明を記載します。以下のオプションのデフォルト値は、OptHubの担当者に確認してください。連絡先は[こちら](#連絡先)です。

- evaluator_queue_url
- scorer_queue_url
- access_key_id
- secret_access_key
- region_name
- table_name

| オプション | 型 | デフォルト値 | 説明 |
| ---- | ---- | ---- | ---- |
| interval | int | 2 | Amazon SQSからメッセージを取得する間隔 |
| timeout | int | 43200 | Docker Imageを使った解評価・スコア計算の制限時間 |
| rm | bool | True | 解評価・スコア計算後にDocker Containerを削除するかどうか。デバッグ時以外はTrueを推奨します。Falseに設定すると、解評価・スコア計算の際に作成されたDocker Containerが削除されず、蓄積していくので注意してください。 |
| log_level | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | INFO | 出力するログのレベル |
| force | bool | False | フラグファイルを強制的に新規作成するか |
| evaluator_queue_url | path | - | Evaluatorが用いるSQSのキューURL |
| scorer_queue_url | path | - | Scorerが用いるSQSのキューURL |
| access_key_id | str | - | AWS Access Key ID |
| secret_access_key | str | - | AWS Secret Access Key |
| region_name | str | - | AWS default Region Name |
| table_name | str | - | 解・評価・スコアを保存するDynamoDBのテーブル名 |

## トラブルシューティング

### Dockerを起動していない

下記のエラーは、Dockerを起動していない場合に発生します。

```plaintext
Error: Unable to communicate with Docker. Please ensure Docker is running and accessible. (Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory')))
```

Macの場合は、Docker Desktopを起動することで解決できます。Docker Desktopは、[こちら](https://docs.docker.com/desktop/install/mac-install/)からインストールできます。

Ubuntuの場合は、ターミナルで以下のコマンドを実行し、Dockerをインストールすることで解決できます。

```plaintext
sudo apt install docker.io
```

### Dockerソケットへのアクセス権限がない

以下のエラーは、現在のユーザにDockerソケットへのアクセス権限がない場合に発生します。

```plaintext
Error: Unable to communicate with Docker. Please ensure Docker is running and accessible. (Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied')))
```

Ubuntuの場合は、ユーザをdockerグループに追加し、再ログインすることで解決できます。具体的には、以下の手順で解決できます。

1. ターミナルで以下のコマンドを実行

    ```plaintext
    sudo usermod -aG docker $USER
    ```

2. ユーザに再ログインするか、ターミナルで以下のコマンドを実行

    ```plaintext
    newgrp docker
    ```

### コンペ管理者のアカウントでログインしていない

以下のエラーは、Evaluator/Scorer起動時に、コンペ管理者のアカウントでログインしなかった場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
opthub_runner_admin.models.exception.DockerImageNotFoundError: Cannot access the Docker image. Please check your permissions. If you're not authenticated using the competition administrator's account, please do so.
```

Evaluator/Scorer起動時に、コンペ管理者のアカウントでログインすることで解決できます。以下の画面が表示された際に、コンペ管理者のUsernameとPasswordを入力してください。

```plaintext
Note: Make sure to authenticate using the competition administrator's account.
Username: (コンペ管理者のユーザ名)
Password: (コンペ管理者のパスワード)
```

### YAMLファイルが存在しない

以下のエラーは、Evaluator/Scorerの設定を記述したYAMLファイルが存在しない場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
FileNotFoundError: Configuration file not found: config.yml
```

[2.YAMLファイルの構成](#2-yamlファイルの構成)を参考に、`config.yml`を作成してください。

### AWS Access Key IDが間違っている

以下のエラーは、`config.yml`に設定したAWS Access Key ID(`access_key_id`)が間違っている場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId) when calling the ReceiveMessage operation: The security token included in the request is invalid.
```

`config.yml`に設定したAWS Access Key IDを確認し、正しい値を入力してください。

### AWS Secret Access Keyが間違っている

以下のエラーは、`config.yml`に設定したAWS Secret Access Key(`secret_access_key`)が間違っている場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
botocore.exceptions.ClientError: An error occurred (SignatureDoesNotMatch) when calling the ReceiveMessage operation: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details.

```

`config.yml`に設定したAWS Secret Access Keyを確認し、正しい値を入力してください。

### SQSのキュー名が間違っている

以下のエラーは、`config.yml`に設定したSQSのキュー名(`evaluator_queue_name` / `scorer_queue_name`)が間違っている場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
botocore.errorfactory.QueueDoesNotExist: An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the ReceiveMessage operation: The specified queue does not exist.
```

`config.yml`に設定したSQSのキュー名を確認し、正しい値を入力してください。

### DynamoDBのテーブル名が間違っている

以下のエラーは、`config.yml`に設定したAmazon DynamoDBのテーブル名(`table_name`)が間違っている場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
botocore.errorfactory.ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the GetItem operation: Requested resource not found

```

`config.yml`に設定したDynamoDBのテーブル名を確認し、正しい値を入力してください。

### AWS Default Region Nameが間違っている

以下のエラーは、`config.yml`に設定したAWS Default Region Name(`region_name`)が間違っている場合に発生します。

```plaintext
Traceback (most recent call last):
  ･･･
urllib3.exceptions.NameResolutionError: <botocore.awsrequest.AWSHTTPSConnection object at 0x104d8bce0>: Failed to resolve 'sqs.ap-northeas-1.amazonaws.com' ([Errno 8] nodename nor servname provided, or not known)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  ･･･
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "https://sqs.ap-northeas-1.amazonaws.com/"
```

`config.yml`に設定したAWS Default Region Nameを確認し、正しい値を入力してください。

### Docker Container内のエラー

以下のエラーは、Docker Container内でエラーが発生した場合に出力されます。

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

このエラーを詳細に調べるためには、Docker Containerのログを確認する必要があります。`config.yml`に設定した`rm`を`False`に変更した後、再度Evaluator/Scorerを起動し、実行後のContainerのログを確認してください。Docker Containerのログは、以下のコマンドで確認できます。

```bash
$ docker ps # Container IDの確認
$ docker logs <Container ID> # ログの出力
```

ログを確認して、Docker Containerの出力が正しいフォーマットになるようにDocker Imageを変更してください。

また、以下のContainerのログは、ビルドされたDocker Imageが互換性のないプラットフォームで実行された場合に発生するエラーを表しています。

```plaintext
exec /usr/bin/sh: exec format error
```

Docker Imageをビルドする環境とEvaluator/Scorerを実行する環境をそろえるか、`buildx`を使い、互換性を持ったDocker Imageを作成してください。

## 開発者の方へ

以下のステップに従って、環境設定をしてください。

1. 本リポジトリをclone
2. Poetryの設定
3. `poetry install`を実行
4. 推奨されたVS Codeの拡張機能をダウンロード
5. 他のパッケージとの競合を避けるため、以下のVS Codeの拡張機能を無効にする
    - ms-python.pylint
    - ms-python.black-formatter
    - ms-python.flake8
    - ms-python.isort
6. `config.default.yml`を参考に、オプションを記述した`config.yml`を作成
    - config.ymlはopthub-runner-admin直下に配置してください。
    - config.default.ymlでコメントアウトされているオプションの設定値は、OptHubの担当者に確認してください。連絡先は[こちら](#連絡先)です。

上記のセットアップ完了後、プロジェクトのrootディレクトリで`opthub-runner`コマンドが使用可能になります。

## 連絡先

ご質問やご不明な点がございましたら、お気軽にお問い合わせください (Email: dev@opthub.ai)。

<img src="https://opthub.ai/assets/images/logo.svg" width="200">
