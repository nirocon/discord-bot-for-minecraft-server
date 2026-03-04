# Discord 管理ボット (Minecraft Server)

このリポジトリは、Discord から Minecraft (Bedrock) サーバーを操作・管理するボットの実装です。

**主な機能**

- サーバー起動 / 停止
- サーバーバックアップ作成
- サーバーのアップデート（ダウンロード → 展開 → 設置 → 設定/ワールドのコピー）
- ホワイトリストの管理（追加 / 削除 / 表示）
- サブプロセスの実行ログをプロジェクト内に保存
- 長時間処理は操作が重複しないようグローバルロックで保護

## 要求環境

- Python 3.12
- Linux 互換環境（`sudo`、`screen`、`wget`、`unzip`、`tar` などが利用可能）

## セットアップ（簡易）

1. プロジェクトルートに `.env` を用意して以下の環境変数を設定します:

```
DISCORD_TOKEN = your_discord_bot_token  # Discord Bot トークン
MINECRAFT_CONTROLL_ACCOUNT = minecraft_user # マイクラサーバーを実行しているユーザー
SERVER_DIR_PATH = /path/to/bedrock-server # マイクラサーバーサーバーのパス
BACKUP_DIR_PATH = /path/to/backups # サーバーバックアップのパス
```

2. 依存をインストールして起動（`bot_start.sh` を利用することを推奨）:

```bash
./bot_start.sh
```

`bot_start.sh` は仮想環境を作成し `requirements.txt` をインストールした上で bot を起動します。

## 使い方（Discord 上のスラッシュコマンド）

- `/start` — サーバー起動
- `/stop` — サーバー停止
- `/create-backup` — バックアップ作成
- `/update-server <version>` — サーバーを指定バージョンに更新（例: `/update-server 1.26.3.1`）
- `/whitelist-add <username>` — ホワイトリスト追加
- `/whitelist-remove <username>` — ホワイトリスト削除
- `/whitelist-list` — ホワイトリスト表示

注意: `/update-server` は `N.N.N.N`（例 `1.26.3.1`）の形式を受け付けます。

コマンド名は `/` 以降を変更することができます。![「.envの設定」参照](###envの設定)

## トラブルシューティング

- Discord トークンが無い、または無効: bot 起動時に例外が出ます。`.env` を確認してください。
- サブプロセスが失敗した場合は `.bin/log/*` を確認してください。

## 補足

### .envの設定

`.env`ファイルには以下のような設定を記述することもできます

```
# === 必須設定 ===
DISCORD_TOKEN = your_discord_bot_token  # Discord Bot トークン
MINECRAFT_CONTROLL_ACCOUNT = minecraft_user # マイクラサーバーを実行しているユーザー
SERVER_DIR_PATH = /path/to/bedrock-server # マイクラサーバーサーバーのパス
BACKUP_DIR_PATH = /path/to/backups # サーバーバックアップのパス

# === 追加設定 ===
SESSION_NAME = minecraft_bedrock_server # screenのセッション名

# 各種コマンド名の変更
START_SERVER = start # デフォルトは `start`
STOP_SERVER = stop # デフォルトは `stop`
WHITELIST_ADD = whitelist-add # デフォルトは `whitelist-add`
WHITELIST_REMOVE = whitelist-remove
WHITELIST_LIST = whitelist-list
CREATE_BACKUP = create-backup
UPDATE_SERVER = update-server

```

### ログ

- サブプロセスの標準出力/標準エラーはプロジェクトルートの `.bin/log/` にタイムスタンプ付きファイルとして保存されます。
- 例: `.bin/log/20260304_123045.log`

ログを確認すれば `mv: cannot move ... Permission denied` のような詳細な原因が見られます。

### 同時実行ガード

- ボットは `asyncio.Lock()` によるグローバルロックを用いて、重い処理（起動・停止・バックアップ・アップデート・ホワイトリスト操作など）の同時実行を防止します。
- 処理中に別コマンドが来た場合は `別の処理が実行中です。処理完了後にお試しください。` と返ります。

### 権限エラーへの対処

- ログに `Permission denied` が出た場合、サーバーディレクトリの所有者が適切でない可能性があります。次のコマンドを実行してください（管理者権限が必要）：

```bash
sudo chown -R <minecraft_user>:<minecraft_user> /path/to/bedrock-server
```

- ボットから自動で `chown` を試みる処理がありますが、ボット実行ユーザーが `sudo` をパスワードなしで実行できる設定でないと成功しません。運用上は対象ディレクトリの所有者を事前に設定しておくことを推奨します。

## 開発者向けメモ

- ログ処理は `src/bot_lib.py` の `run_logged` を利用しています。必要であればログローテーションやファイル名ルールをここで変更してください。
- 重い処理はイベントループのブロックを避けるため `asyncio.to_thread` でスレッド化しています。
