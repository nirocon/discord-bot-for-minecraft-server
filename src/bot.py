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

def get_screen_session():
    try:
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -ls"
        process_return = subprocess.run(command, check=True, capture_output=True, shell=True)
        output = process_return.stdout.decode('utf-8')
        return output
    except subprocess.CalledProcessError as e:
        if e.returncode == 1: # screenが起動していないとき
            return ""
        else:
            raise
    except Exception as e:
        raise

def check_screen_session(session_name : str):
    session = get_screen_session()
    return session_name in session

# マイクラサーバーを起動する関数
def start_minecraft_server():
    try:
        if check_screen_session("minecraft_server"):
            return "Minecraftサーバーはすでに起動しています"
        
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} bash -c 'cd {MINECRAFT_SERVER_DER_PATH} && LD_LIBRARY_PATH=. screen -dmS minecraft_server ./bedrock_server'"
        subprocess.run(command, check=True, shell=True)
        return "Minecraftサーバーを起動しました!"
    except Exception as e:
        return f"サーバー起動時にエラー: {e}"

# マイクラサーバーを停止する関数
def stop_minecraft_server():
    try:
        if not check_screen_session("minecraft_server"):
            return "Minecraftサーバーは起動していません\n`/start-test`で起動してください"
        
        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'stop\n'"
        subprocess.run(command, check=True, shell=True)
        return "Minecraftサーバーを停止しました!"
    except Exception as e:
        return f"サーバー停止時にエラー: {e}"

# ホワイトリストに追加する関数
def whitelist_add(username):
    try:
        if not check_screen_session("minecraft_server"):
            return "Minecraftサーバーは起動していません\n`/start-test`で起動してください"

        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'whitelist add {username}\n'"
        subprocess.run(command, check=True, shell=True)
        return f"{username}をホワイトリストに追加しました!"
    except Exception as e:
        return f"ホワイトリスト追加時にエラー: {e}"

# ホワイトリストから削除する関数 
def whitelist_remove(username):
    try:
        if not check_screen_session("minecraft_server"):
            return "Minecraftサーバーは起動していません\n`/start-test`で起動してください"

        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'whitelist remove {username}\n'"
        subprocess.run(command, check=True, shell=True)
        return f"{username}をホワイトリストから削除しました!"
    except Exception as e:
        return f"ホワイトリスト削除時にエラー: {e}"
    
# ホワイトリストを表示する関数
def whitelist_list():
    try:
        if not check_screen_session("minecraft_server"):
            return "Minecraftサーバーは起動していません\n`/start-test`で起動してください"

        command = f"sudo -u {MINECRAFT_CONTROLL_ACCOUNT} screen -S minecraft_server -p 0 -X stuff 'whitelist list\n'"
        process_return = subprocess.run(command, check=True, capture_output=True, shell=True)
        output = process_return.stdout.decode('utf-8')
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
