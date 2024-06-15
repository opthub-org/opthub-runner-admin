# OptHub Runner

![Skills](https://skillicons.dev/icons?i=py,aws,graphql,docker,vscode,github)

Opthub Runnerは, 以下の2つの機能を提供するPythonパッケージです.

- Evaluator: Docker Imageを使って, Opthubでユーザから提出された解を評価
- Scorer:  Docker Imageを使って評価の系列からスコアを計算

このリポジトリでは, Opthub Runnerのインストールや実行方法を説明しています.

## Get Started
### 前提条件
- Python 3.8 or newerをインストール

- [こちら](https://docs.docker.com/desktop/install/mac-install/)からDocker Desktopをインストールし, Docker Desktopを起動

### 1. Installation
PyPIからインストール
```bash
pip install opthub-runner-admin
```

### 2. Configure Options
Optionを設定するために, Optionを記述したYAMLファイルを作成

Optionの詳細は[YAML File Options](#YAMLFileOptions)を参照

### 3. 実行
- Evaluatorの実行方法
    
    まず, 以下のコマンドでEvaluatorを起動

    `--config`には, Configure Optionsで設定したYAMLファイルのパスを設定
    ```bash
    opthub-runner evaluator --config (yaml file path)
    ```

    UsernameとPasswordを求められるので, それぞれ入力
    ```bash
    Username: (your username)
    Password: (your password)
    ```

- Scorerの実行方法
    
    まず, 以下のコマンドでScorerを起動

    `--config`には, Configure Optionsで設定したYAMLファイルのパスを設定
    ```bash
    opthub-runner scorer --config (yaml file path)
    ```

    UsernameとPasswordを求められるので, それぞれ入力
    ```bash
    Username: (your username)
    Password: (your password)
    ```


## YAML File Options <a id="YAMLFileOptions"></a>
以下の表は, YAMLファイルに記述するOptionとそのType, Default値, 説明 (Description) を表しています.

| Option | Type | Default | Description |
| ---- | ---- | ---- | ---- |
| interval | int | 2 | Amazon SQSからメッセージを取得する間隔 |
| timeout | int | 43200 | Docker Imageを使った解評価・スコア計算の制限時間 |
| rm | bool | True | 解評価・スコア計算後にDocker Containerを削除するかどうか |
log_level | [DEBUG, INFO, WARNING, ERROR, CRITICAL] | INFO | 出力するログのレベル |evaluator_queue_name | str | opthub_evaluator_sqs_Default_dev | Evaluatorが用いるAmazon SQSのキュー名 |
| evaluator_queue_name | str | - | Evaluatorが用いるAmazon SQSのキュー名 |
| evaluator_queue_url | path | - | Evaluatorが用いるAmazon SQSのキューURL |
| scorer_queue_name | str | - | Scorerが用いるAmazon SQSのキュー名 |
| scorer_queue_url | path | - | Scorerが用いるAmazon SQSのキューURL |
| access_key_id | str | - | AWS Access Key ID | 
| secret_access_key | str | - | AWS Secret Access Key |
| region_name | str | - | AWS default Region Name |
| table_name | str | - | 解・評価・スコアを保存するDynamoDBのテーブル名 |

**evaluator_queue_name**, **evaluator_queue_url**, **scorer_queue_name**, **scorer_queue_url**,**access_key_id**, **secret_access_key**, **region_name**, **table_name**が必要な場合は, Opthub administrators (Email: dev@opthub.ai) に連絡してください.


## For Contributors

以下のステップに従って環境をセットアップしてください.

1. このリポジトリをclone
2. Poetryの設定
3. `poetry install`を実行
4. 推奨されたVS Codeの拡張機能をダウンロード
5. 他のパッケージとの競合を避けるため, 以下のVS Codeの拡張機能を無効にする
    - ms-python.pylint
    - ms-python.black-formatter
    - ms-python.flake8
    - ms-python.isort

上記のセットアップ完了後, プロジェクトのrootディレクトリで`opthub-runner`コマンドが使用可能になります.

## Contact

ご質問やご不明な点がございましたら, お気軽にお問い合わせください (Email: dev@opthub.ai).

<img src="https://opthub.ai/assets/images/logo.svg" width="200">



