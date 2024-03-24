# pyenv のインストール（すでにインストールされていればスキップ）
if ! type pyenv > /dev/null; then
  brew install pyenv
fi

# poetry のインストール（すでにインストールされていればスキップ）
if ! type poetry > /dev/null; then
  brew install poetry
fi

# Python 3.12.1 のインストール（すでにインストールされていればスキップ）
if ! pyenv versions | grep -q 3.12.1; then
  pyenv install 3.12.1
fi

# Python のローカルバージョンを設定
pyenv local 3.12.1

# 依存関係のインストール（poetry によるプロジェクト依存関係）
poetry install
