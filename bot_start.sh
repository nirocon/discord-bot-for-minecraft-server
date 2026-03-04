#!/bin/bash

# Minecraftサーバー管理Discord Botを起動するスクリプト

# スクリプトのディレクトリ(プロジェクトのルート)を取得
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Python仮想環境を準備
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "仮想環境を作成しています..."
    python3 -m venv "$PROJECT_ROOT/venv"
fi

# 仮想環境をアクティベート
# shellcheck source=/dev/null
source "$PROJECT_ROOT/venv/bin/activate"

# .env ファイルが存在するか確認
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "警告: プロジェクトルートに .env ファイルが見つかりません。"
    echo "DISCORD_TOKEN などの環境変数を設定してください。"
fi

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"

# srcディレクトリに移動してbot.pyを実行
cd "$PROJECT_ROOT/src"

# bot.pyを実行
python bot.py
