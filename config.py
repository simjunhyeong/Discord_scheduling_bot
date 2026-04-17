import discord
from discord import app_commands as ac
import os
from dotenv import load_dotenv

#------------------ 전역변수 및 함수 --------------------------$
WEEK_ORDER = ["월", "화", "수", "목", "금", "토", "일"]


load_dotenv()
my_token = os.getenv("DISCORD_TOKEN")
server_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

#--------------- 필요 정보-------------------------#
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = ac.CommandTree(client)
guild = discord.Object(id=server_ID)