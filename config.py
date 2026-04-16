import discord
from discord import app_commands as ac
import os
from dotenv import load_dotenv
import os



#--------------- 필요 정보-------------------------#
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = ac.CommandTree(client)

server_ID =1494186329926537358
guild = discord.Object(id=server_ID)
load_dotenv()
my_token =os.getenv("DISCORD_TOKEN")

