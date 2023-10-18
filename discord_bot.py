#!/usr/bin/env python3

import discord
import os
from termcolor import colored
import pandas as pd
pd.set_option('display.max_columns', None)
from dotenv import load_dotenv
load_dotenv()

client = discord.Client(intents=None)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()

@tree.command(name="ping", description="Respond with pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@tree.command(name="exchange_rate", description="Respond with the current Qube to Qredits exchange rate")
async def exchange_rate(interaction: discord.Interaction):
    df = pd.read_csv("exchange_rates.csv")
    rate = df.iloc[-1].CubeToQred
    await interaction.response.send_message(f"The current exchange rate is {rate} Qredits per Qube")

colormap = {
    "Swarm": "green",
    "Legion": "red",
    "Faceless": "magenta",
}

def format_MAZ():
    df = pd.read_csv("battlestats.csv")
    latest_date = df.Date.max()
    df = df[df.Date == latest_date]
    print(df)
    result = f"Most Active Zones for {latest_date} QST:\n\n"
    for i, row in df.iterrows():
        link = f'https://portal.qonqr.com/Home/BattleStatistics/{row["Battle Report Number"]}'
        result += f'[{row["Zone Name"]}, {row["Region"]}, {row["Country"]}](<{link}>)\n'
    print(result)
    print(len(result))
    assert len(result) <= 2000
    return result

@tree.command(name="maz", description="Show today's Most Active Zones")
async def maz(interaction: discord.Interaction):
    await interaction.response.send_message(format_MAZ())

format_MAZ()
client.run(os.getenv("DISCORD_BOT_TOKEN"))
