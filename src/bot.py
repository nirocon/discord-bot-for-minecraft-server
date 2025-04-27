import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.expanduser('../.env')) # .envファイルから環境変数を読み込む
TOKEN = os.getenv('DISCORD_TOKEN') # トークン取得

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# スラッシュコマンド登録
@bot.tree.command(name="start", description="マイクラサーバーを起動します")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message("サーバー起動コマンドを受け取りました！")

@bot.tree.command(name="stop", description="マイクラサーバーを停止します")
async def stop(interaction: discord.Interaction):
    await interaction.response.send_message("サーバー停止コマンドを受け取りました！")

# 起動時にコマンド同期
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
