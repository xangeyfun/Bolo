from dotenv import load_dotenv
from discord.ext import commands
import discord
import random
import time
import os

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="$", intents=intents, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | Bolo"))
TOKEN = os.getenv("TOKEN")
GAMES_USER_ID = os.getenv("GAMES_USER_ID")

@bot.event
async def on_ready():
    if bot.user:
        print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print(f"Syncing commands...")
    start = time.time()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands in {time.time() - start} seconds")

    except Exception as e:
        print(f"Error in syncing commands: {e}")
        exit(1)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        print(f"Command '/{interaction.data['name']}' invoked by '{interaction.user}' in '{interaction.guild}' (ID: {interaction.guild_id})")
    elif interaction.type == discord.InteractionType.component:
        print(f"Component interaction invoked by '{interaction.user}' in '{interaction.guild}' (ID: {interaction.guild_id})")

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms", ephemeral=True)

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="github", description="Get the bot's GitHub repository link") #, guild=guild)
async def github(interaction: discord.Interaction):
    await interaction.response.send_message("You can find the bot's source code on GitHub:\nhttps://github.com/xangeyfun/Bolo", ephemeral=True)

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    status = None
    member = interaction.user

    if isinstance(member, discord.Member):
        for activity in member.activities:
            if isinstance(activity, discord.CustomActivity):
                status = activity.name
                break

    if status and "Bolo" in status.lower():
        result = "Heads"
    else:
        result = random.choice(["Heads", "Tails"])

    await interaction.response.send_message(f"{result}!")


if __name__ == "__main__":
    bot.run(TOKEN)