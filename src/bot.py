import discord
from discord.ext import commands
from dotenv import load_dotenv
import subprocess
import os

load_dotenv(dotenv_path=os.path.expanduser('.env')) # .envファイルから環境変数を読み込む
TOKEN                       = os.getenv('DISCORD_TOKEN') # トークン取得
MINECRAFT_CONTROLL_ACCOUNT  = os.getenv('MINECRAFT_CONTROLL_ACCOUNT')  # マイクラサーバーを実行しているユーザー名
MINECRAFT_SERVER_DER_PATH   = os.getenv('SERVER_DIR_PATH')  # サーバーのパス

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# マイクラサーバーを起動する関数
def start_minecraft_server():
    try:
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} bash -c 'cd {MINECRAFT_SERVER_DER_PATH} && LD_LIBRARY_PATH=. screen -dmS minecraft_server ./bedrock_server'"
        process_return = subprocess.run(command, shell=True)
        if process_return.returncode != 0: raise Exception(str(process_return.stderr))
        return "Minecraftサーバーを起動しました!"
    except Exception as e:
        return f"サーバー起動時にエラー: {e}"

# マイクラサーバーを停止する関数
def stop_minecraft_server():
    try:
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'stop\n'"
        process_return = subprocess.run(command, shell=True)
        if process_return.returncode != 0: raise Exception(str(process_return.stderr))
        return "Minecraftサーバーを停止しました!"
    except Exception as e:
        return f"サーバー停止時にエラー: {e}"

# ホワイトリストに追加する関数
def whitelist_add(username):
    try:
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'whitelist add {username}\n'"
        process_return = subprocess.run(command, shell=True)
        if process_return.returncode != 0: raise Exception(str(process_return.stderr))
        return f"{username}をホワイトリストに追加しました!"
    except Exception as e:
        return f"ホワイトリスト追加時にエラー: {e}"

# ホワイトリストから削除する関数 
def whitelist_remove(username):
    try:
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'whitelist remove {username}\n'"
        process_return = subprocess.run(command, shell=True)
        if process_return.returncode != 0: raise Exception(str(process_return.stderr))
        return f"{username}をホワイトリストから削除しました!"
    except Exception as e:
        return f"ホワイトリスト削除時にエラー: {e}"
    
# ホワイトリストを表示する関数
def whitelist_list():
    try:
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'whitelist list\n'"
        process_return = subprocess.run(command, shell=True)
        if process_return.returncode != 0: raise Exception(str(process_return.stderr)) # エラーが発生した場合
        output = str(process_return.stdout)
        return "ホワイトリスト:\n" + output
    except Exception as e:
        return f"ホワイトリスト表示時にエラー: {e}"

# スラッシュコマンド登録
@bot.tree.command(name="start-test", description="マイクラサーバーを起動します")
async def start(interaction: discord.Interaction):
    """Minecraftサーバーを起動するコマンド"""
    await interaction.response.send_message("Minecraftサーバーを起動します...")
    mes = start_minecraft_server()
    print(mes)
    await interaction.followup.send(mes)

@bot.tree.command(name="stop-test", description="マイクラサーバーを停止します")
async def stop(interaction: discord.Interaction):
    """Minecraftサーバーを停止するコマンド"""
    await interaction.response.send_message("Minecraftサーバーを停止します...")
    mes = stop_minecraft_server()
    print(mes)
    await interaction.followup.send(mes)

@bot.tree.command(name="whitelist-add", description="ホワイトリストに追加します")
@discord.app_commands.describe(username="ユーザー名")
async def whitelist_add_command(interaction: discord.Interaction, username: str):
    """ホワイトリストに追加するコマンド"""
    await interaction.response.send_message(f"{username}をホワイトリストに追加します...")
    mes = whitelist_add(username)
    print(mes)
    await interaction.followup.send(mes)

@bot.tree.command(name="whitelist-remove", description="ホワイトリストから削除します")
@discord.app_commands.describe(username="ユーザー名")
async def whitelist_remove_command(interaction: discord.Interaction, username: str):
    """ホワイトリストから削除するコマンド"""
    await interaction.response.send_message(f"{username}をホワイトリストから削除します...")
    mes = whitelist_remove(username)
    print(mes)
    await interaction.followup.send(mes)

@bot.tree.command(name="whitelist-list", description="ホワイトリストを表示します")
async def whitelist_list_command(interaction: discord.Interaction):
    """ホワイトリストを表示するコマンド"""
    await interaction.response.send_message("ホワイトリストを表示します...")
    mes = whitelist_list()
    print(mes)
    await interaction.followup.send(mes)

# 起動時にコマンド同期
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user}としてDiscordにログインしました")

bot.run(TOKEN)
