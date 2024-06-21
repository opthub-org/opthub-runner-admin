# OptHub Runner

![Skills](https://skillicons.dev/icons?i=py,aws,graphql,docker,vscode,github)

Opthub Runnerは、以下の2つの機能を提供するPythonパッケージです。

- Evaluator: Docker Imageを使って、Opthubでユーザから提出された解を評価する機能
- Scorer:  Docker Imageを使って評価の系列からスコアを計算する機能

このリポジトリでは、Opthub Runnerのインストールや実行方法を説明しています。

## 利用方法
### 前提条件
- Python 3.8以上をインストール
- pipを使えるように設定
- Dockerをインストールして起動*

\*Macの場合は、[Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)をインストールして起動できます。

### 1. Installation

PyPIから`opthub-runner-admin`をインストールします。
```bash
pip install opthub-runner-admin
```

### 2. YAMLファイルの構成
EvaluatorやScorerを起動するためのオプションをYAMLファイルに記述します。ファイルに設定するオプションの詳細は、[YAMLファイルのオプション](#YAMLFileOptions)を参照してください。

### 3. 実行
#### Evaluatorの実行方法

まず、以下のコマンドでEvaluatorを起動します。

`--config`には、Configure Optionsで設定したYAMLファイルのパスを設定します。

```bash
opthub-runner evaluator --config (yaml file path)
```

ユーザ名とパスワードを求められるので、それぞれ入力します。ここで入力するユーザ名とパスワードは、コンペの管理者のものである必要があります。

```bash
Username: (your username)
Password: (your password)
```

#### Scorerの実行方法
まず、以下のコマンドでScorerを起動します。

`--config`には、Configure Optionsで設定したYAMLファイルのパスを設定します。指定しない場合は、実行ディレクトリ直下の`config.yml`が使用されます。

```bash
opthub-runner scorer --config (yaml file path)
```

UsernameとPasswordを求められるので、それぞれ入力します。ここで入力するユーザ名とパスワードは、コンペの管理者のものである必要があります。
```bash
Username: (your username)
Password: (your password)
```

## YAMLファイルのオプション <a id="YAMLFileOptions"></a>
以下の表は、YAMLファイルに記述するオプションとその型、デフォルト値、説明を表しています。

| オプション | 型 | デフォルト値 | 説明 |
| ---- | ---- | ---- | ---- |
| interval | int | 2 | Amazon SQSからメッセージを取得する間隔 |
| timeout | int | 43200 | Docker Imageを使った解評価・スコア計算の制限時間 |
| rm | bool | True | 解評価・スコア計算後にDocker Containerを削除するかどうか |
log_level | [DEBUG、INFO、WARNING、ERROR、CRITICAL] | INFO | 出力するログのレベル |evaluator_queue_name | str | opthub_evaluator_sqs_Default_dev | Evaluatorが用いるAmazon SQSのキュー名 |
| evaluator_queue_name | str | - | Evaluatorが用いるAmazon SQSのキュー名 |
| evaluator_queue_url | path | - | Evaluatorが用いるAmazon SQSのキューURL |
| scorer_queue_name | str | - | Scorerが用いるAmazon SQSのキュー名 |
| scorer_queue_url | path | - | Scorerが用いるAmazon SQSのキューURL |
| access_key_id | str | - | AWS Access Key ID |
| secret_access_key | str | - | AWS Secret Access Key |
| region_name | str | - | AWS default Region Name |
| table_name | str | - | 解・評価・スコアを保存するDynamoDBのテーブル名 |

以下のオプションの設定値は、OptHubの担当者に確認してください。連絡先は[こちら](#Contact
)です。

- evaluator_queue_name
- evaluator_queue_url
- scorer_queue_name
- scorer_queue_url
- access_key_id
- secret_access_key
- region_name
- table_name

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

上記のセットアップ完了後、プロジェクトのrootディレクトリで`opthub-runner`コマンドが使用可能になります。

## 連絡先 <a id="Contact"></a>

ご質問やご不明な点がございましたら、お気軽にお問い合わせください (Email: dev@opthub.ai)。

<img src="https://opthub.ai/assets/images/logo.svg" width="200">



