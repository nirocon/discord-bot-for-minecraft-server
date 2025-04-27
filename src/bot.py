import discord
from discord.ext import commands
from dotenv import load_dotenv
import subprocess
import os

load_dotenv(dotenv_path=os.path.expanduser('../.env')) # .envファイルから環境変数を読み込む
TOKEN = os.getenv('DISCORD_TOKEN') # トークン取得

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

minecraft_user = "minecraft_controll_account"  # マイクラサーバーを実行しているユーザー名
minecraft_server_path = "~/bedrock-server"  # サーバーのパス

# マイクラサーバーを起動する関数
def start_minecraft_server():
    command = f"sudo -u {minecraft_user} bash -c 'whoami && cd {minecraft_server_path} && LD_LIBRARY_PATH=. screen -dmS minecraft_server ./bedrock_server'"
    subprocess.run(command, shell=True)

# マイクラサーバーを停止する関数
def stop_minecraft_server():
    try:
        # サーバーを停止するために`stop`コマンドを送る
        subprocess.run(f"sudo -u {minecraft_user} screen -S minecraft_server -p 0 -X stuff 'stop\n'", shell=True)
    except Exception as e:
        print(f"Error stopping Minecraft server: {e}")

# スラッシュコマンド登録
@bot.tree.command(name="start", description="マイクラサーバーを起動します")
async def start(interaction: discord.Interaction):
    """Minecraftサーバーを起動するコマンド"""
    await interaction.response.send_message("Minecraftサーバーを起動します...")
    start_minecraft_server()
    await interaction.followup.send("Minecraftサーバーが起動しました！")

@bot.tree.command(name="stop", description="マイクラサーバーを停止します")
async def stop(interaction: discord.Interaction):
    """Minecraftサーバーを停止するコマンド"""
    await interaction.response.send_message("Minecraftサーバーを停止します...")
    stop_minecraft_server()
    await interaction.followup.send("Minecraftサーバーが停止しました！")

# 起動時にコマンド同期
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
