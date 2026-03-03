import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

import minecraft_server_updater
import bot_start
import bot_stop
import bot_whitelist

# プロジェクトルートにある .env を読み込む
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(dotenv_path=os.path.join(root, '.env'))  # .envファイルから環境変数を読み込む
TOKEN = os.getenv('DISCORD_TOKEN')  # トークン取得
if not TOKEN:
    raise RuntimeError('DISCORD_TOKEN が設定されていません (.env または環境変数を確認してください)')
MINECRAFT_CONTROLL_ACCOUNT = os.getenv('MINECRAFT_CONTROLL_ACCOUNT')  # マイクラサーバーを実行しているユーザー名
MINECRAFT_SERVER_DIR_PATH = os.getenv('SERVER_DIR_PATH')  # サーバーのパス
MINECRAFT_BACKUP_DIR_PATH = os.getenv('BACKUP_DIR_PATH')  # バックアップのパス

START_SERVER = os.getenv('START_SERVER', 'start')
STOP_SERVER = os.getenv('STOP_SERVER', 'stop')
WHITELIST_ADD = os.getenv('WHITELIST_ADD', 'whitelist-add')
WHITELIST_REMOVE = os.getenv('WHITELIST_REMOVE', 'whitelist-remove')
WHITELIST_LIST = os.getenv('WHITELIST_LIST', 'whitelist-list')
CREATE_BACKUP = os.getenv('CREATE_BACKUP', 'create-backup')

SESSION_NAME = os.getenv('SESSION_NAME', 'minecraft_bedrock_server')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


# スラッシュコマンド登録
@bot.tree.command(name=START_SERVER, description="マイクラサーバーを起動します")
async def start(interaction: discord.Interaction):
    """Minecraftサーバーを起動するコマンド"""
    await interaction.response.send_message("Minecraftサーバーを起動します...")
    mes = bot_start.start_minecraft_server(
        minecraft_controll_account=MINECRAFT_CONTROLL_ACCOUNT,
        minecraft_server_dir_path=MINECRAFT_SERVER_DIR_PATH,
        session_name=SESSION_NAME
    )
    print(mes)
    await interaction.followup.send(mes)


@bot.tree.command(name=STOP_SERVER, description="マイクラサーバーを停止します")
async def stop(interaction: discord.Interaction):
    """Minecraftサーバーを停止するコマンド"""
    await interaction.response.send_message("Minecraftサーバーを停止します...")
    mes = bot_stop.stop_minecraft_server(
        minecraft_controll_account=MINECRAFT_CONTROLL_ACCOUNT,
        session_name=SESSION_NAME,
        start_server_command=START_SERVER
    )
    print(mes)
    await interaction.followup.send(mes)


@bot.tree.command(name=WHITELIST_ADD, description="ホワイトリストに追加します")
@discord.app_commands.describe(username="ユーザー名")
async def whitelist_add_command(interaction: discord.Interaction, username: str):
    """ホワイトリストに追加するコマンド"""
    await interaction.response.send_message(f"{username}をホワイトリストに追加します...")
    mes = bot_whitelist.whitelist_add(
        minecraft_controll_account=MINECRAFT_CONTROLL_ACCOUNT,
        session_name=SESSION_NAME,
        start_server_command=START_SERVER,
        username=username
    )
    print(mes)
    await interaction.followup.send(mes)


@bot.tree.command(name=WHITELIST_REMOVE, description="ホワイトリストから削除します")
@discord.app_commands.describe(username="ユーザー名")
async def whitelist_remove_command(interaction: discord.Interaction, username: str):
    """ホワイトリストから削除するコマンド"""
    await interaction.response.send_message(f"{username}をホワイトリストから削除します...")
    mes = bot_whitelist.whitelist_remove(
        minecraft_controll_account=MINECRAFT_CONTROLL_ACCOUNT,
        session_name=SESSION_NAME,
        start_server_command=START_SERVER,
        username=username
    )
    print(mes)
    await interaction.followup.send(mes)


@bot.tree.command(name=WHITELIST_LIST, description="ホワイトリストを表示します")
async def whitelist_list_command(interaction: discord.Interaction):
    """ホワイトリストを表示するコマンド"""
    await interaction.response.send_message("ホワイトリストを表示します...")
    mes = bot_whitelist.whitelist_list(
        minecraft_controll_account=MINECRAFT_CONTROLL_ACCOUNT,
        minecraft_server_dir_path=MINECRAFT_SERVER_DIR_PATH
    )
    print(mes)
    await interaction.followup.send(mes)


@bot.tree.command(name=CREATE_BACKUP, description="マイクラサーバーのバックアップを作成します", guild=discord.Object(id=1312576908805799946))
async def create_backup_command(interaction: discord.Interaction):
    """マイクラサーバーのバックアップを作成するコマンド"""
    await interaction.response.send_message("マイクラサーバーのバックアップを作成します...")
    mes = minecraft_server_updater.back_up_minecraft_server(
        server_path=MINECRAFT_SERVER_DIR_PATH,
        backup_path=MINECRAFT_BACKUP_DIR_PATH
    )
    print(mes)
    await interaction.followup.send(mes)


# 起動時にコマンド同期
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user}としてDiscordにログインしました")


bot.run(TOKEN)
