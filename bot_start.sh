#!/bin/bash
set -euo pipefail

# Minecraftサーバー管理Discord Botを起動するスクリプト

# スクリプトのディレクトリ(プロジェクトのルート)を取得
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Python仮想環境を準備
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "仮想環境を作成しています..."
    python3 -m venv "$PROJECT_ROOT/venv"
fi

# 移動前のパスがactivateに残っていても、現在の仮想環境を直接使う
if [ ! -x "$VENV_PYTHON" ]; then
    echo "仮想環境のPythonが見つかりません: $VENV_PYTHON" >&2
    exit 1
fi

# .env ファイルが存在するか確認
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "警告: プロジェクトルートに .env ファイルが見つかりません。"
    echo "DISCORD_TOKEN などの環境変数を設定してください。"
fi

# 依存パッケージをインストール
"$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/requirements.txt"

# srcディレクトリに移動してbot.pyを実行
cd "$PROJECT_ROOT/src"

# bot.pyを実行
exec "$VENV_PYTHON" bot.py
