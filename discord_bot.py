#!/usr/bin/env python3

import discord
from discord import app_commands
import os
from termcolor import colored
import pandas as pd
pd.set_option('display.max_columns', None)
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()

client = discord.Client(intents=None)
tree = discord.app_commands.CommandTree(client)

BOT_MEMORY_FILE = "bot_memory.json"

try:
    with open(BOT_MEMORY_FILE) as f:
        memory = json.load(f)
except FileNotFoundError:
    memory = {}
except json.decoder.JSONDecodeError:
    print(colored(f"Error: {BOT_MEMORY_FILE} is not valid JSON", "red"))
    memory = {}

def save_memory():
    print("Saving memory: ", memory)
    with open(BOT_MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4, sort_keys=True)

async def get_channel(channel):
    if channel["type"] == "DM":
        user = await client.fetch_user(channel["id"])
        channel = await user.create_dm()
    else:
        channel = client.get_channel(channel["id"])
    return channel

@client.event
async def on_ready():
    await tree.sync()
    user = await client.fetch_user(200793152167084034)
    channel = await user.create_dm()
    await channel.send("I'm back online!")
    while True:
        print("Checking for new exchange rate...")
        df = pd.read_csv("exchange_rates.csv")
        rate = df.iloc[-1].CubeToQred
        if rate != memory.get("last_exchange_rate"):
            for channel in memory.get("exchange_rate_channels", []):
                channel = await get_channel(channel)
                await channel.send(f"Today's exchange rate is {rate} Qredits per Qube")
            memory["last_exchange_rate"] = int(rate)
            save_memory()
        print("Checking for new MAZ...")
        df = pd.read_csv("battlestats.csv")
        latest_date = df.Date.max()
        if latest_date != memory.get("last_MAZ_date"):
            df = df[df.Date == latest_date]
            for channel in memory.get("MAZ_channels", []):
                channel = await get_channel(channel)
                await channel.send(format_MAZ(df))
            memory["last_MAZ_date"] = latest_date
            save_memory()
        await asyncio.sleep(60 * 15)

@tree.command(name="register", description="Register this channel for daily exchange rate updates or MAZ updates")
@app_commands.choices(option=[
        app_commands.Choice(name="Exchange rates", value="exchange_rate"),
        app_commands.Choice(name="Most Active Zones", value="MAZ")
    ])
async def register(interaction: discord.Interaction, option: app_commands.Choice[str]):
    if type(interaction.channel) is discord.channel.DMChannel:
        channel = {
            "type": "DM",
            "id": interaction.user.id,
            "name": interaction.user.name,
        }
    elif type(interaction.channel) is discord.channel.TextChannel:
        channel = {
            "type": "Text",
            "id": interaction.channel_id,
            "name": interaction.channel.name,
            "guild": interaction.guild.name,
        }
    key = f"{option.value}_channels"
    memory[key] = memory.get(key, []) + [channel]
    save_memory()
    await interaction.response.send_message("✅")

@tree.command(name="unregister", description="Un-register this channel for daily exchange rate updates or MAZ updates")
@app_commands.choices(option=[
        app_commands.Choice(name="Exchange rates", value="exchange_rate"),
        app_commands.Choice(name="Most Active Zones", value="MAZ")
    ])
async def unregister(interaction: discord.Interaction, option: app_commands.Choice[str]):
    if type(interaction.channel) is discord.channel.DMChannel:
        channel_id = interaction.user.id
    elif type(interaction.channel) is discord.channel.TextChannel:
        channel_id = interaction.channel_id
    key = f"{option.value}_channels"
    memory[key] = [c for c in memory.get(key, []) if c["id"] != channel_id]
    save_memory()
    await interaction.response.send_message("✅")

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

def format_MAZ(df=None):
    if df is None:
        df = pd.read_csv("battlestats.csv")
    latest_date = df.Date.max()
    df = df[df.Date == latest_date]
    result = f"Most Active Zones for {latest_date} QST:\n\n"
    for i, row in df.iterrows():
        link = f'https://portal.qonqr.com/Home/BattleStatistics/{row["Battle Report Number"]}'
        result += f'[{row["Zone Name"]}, {row["Region"]}, {row["Country"]}](<{link}>)\n'
    assert len(result) <= 2000
    return result

@tree.command(name="maz", description="Show today's Most Active Zones")
async def maz(interaction: discord.Interaction):
    await interaction.response.send_message(format_MAZ())

format_MAZ()
client.run(os.getenv("DISCORD_BOT_TOKEN"))
