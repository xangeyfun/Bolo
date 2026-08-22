from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import random
import sys
import time
import os

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.messages = True
bot = commands.Bot(command_prefix="$", intents=intents, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | Bolo"))
TOKEN = os.getenv("TOKEN")
GAMES_USER_ID = os.getenv("GAMES_USER_ID")
startup = time.time()

async def setup_hook():
    print("Syncing commands...")
    start = time.time()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands in {time.time() - start} seconds")

    except Exception as e:
        print(f"Error in syncing commands: {e}")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    if bot.user:
        print(f"Logged in as {bot.user.name} ({bot.user.id})")

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
@bot.tree.command(name="uptime", description="Check the bot's uptime") #, guild=guild)
async def uptime(interaction: discord.Interaction):
    current_time = time.time()
    seconds = int(current_time - startup)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    await interaction.response.send_message(
        f"⏱️ **Bot Uptime**\n> {uptime_str}\n\n"
        f"🔗 **Links**\n"
        f"> Status Page: <https://status.xangey.dev/>\n"
        f"> GitHub: <https://github.com/xangeyfun/Bolo>\n",
        ephemeral=True,
    )

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction, hidden: bool = False):
    status = None
    member = interaction.user

    if isinstance(member, discord.Member):
        for activity in member.activities:
            if isinstance(activity, discord.CustomActivity):
                status = activity.name
                break

    if status and "bolo" in status.lower():
        result = "Heads"
    else:
        result = random.choice(["🪙 Heads", "🪙 Tails"])

    await interaction.response.send_message(f"🪙 Flipping...", ephemeral=hidden)
    await asyncio.sleep(1)
    await interaction.edit_original_response(content=result)

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(question="Ask anything!", hidden="hide the command from others")
@bot.tree.command(name="8ball", description="Get a wise answer from the 8 ball")
async def ball(interaction: discord.Interaction, question: str, hidden: bool = False):
    answers = [
        # Positive
        "It is certain.",
        "Without a doubt.",
        "Absolutely.",
        "Definitely.",
        "The stars say yes.",
        "Signs point to yes.",
        "Most likely.",
        "Yes. Do it.",
        "Hell yeah.",
        "100%",
        "Probably, yeah.",

        # Maybe
        "Ask again later.",
        "Maybe.",
        "Could go either way.",
        "The universe hasn't decided yet.",
        "Unclear, try again.",
        "I'm not sure, chief.",
        "Perhaps...",
        "There is a chance.",

        # Negative
        "Don't count on it",
        "Probably not.",
        "My sources say no.",
        "Absolutely not.",
        "Signs point to no.",
        "Not happening.",
        "The answer is no.",
        "Yeah... no.",
        "You might wanna reconsider.",
        "I'd start making other plans.",

        # Extra
        "Bro, what??",
        "Are you seriously asking me this?",
        "You already know.",
        "Ask your mother.",
        "My lawyer advises against it.",
        "I'm legally obligated to say no.",
        "The voices say yes.",
        "Absolutely fucking not.",
        "It depends how many chickens you have.",
        "I flipped a coin, it landed on your face.",
    ]

    await interaction.response.send_message(f"🎱 '{question}'...", ephemeral=hidden)
    await asyncio.sleep(1)
    await interaction.edit_original_response(content=f"🎱 {random.choice(answers)}")

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(options="Seperated by | max 25 (e.g. option1|option2|option3)", hidden="Hide the command from others")
@bot.tree.command(name="choose", description="Randomly pick between options")
async def choose(interaction: discord.Interaction, options: str, hidden: bool = False):
    choices = options.split("|")

    if len(choices) > 25:
        return await interaction.response.send_message(f"❗ Too many options! Max 25, you gave `{len(choices)}`")

    await interaction.response.send_message(f"❓ picking...", ephemeral=hidden)
    await asyncio.sleep(1)
    await interaction.edit_original_response(content=f"❓ {random.choice(choices)}")

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="rate", description="Rate something from 1 to 100")
async def rate(interaction: discord.Interaction, hidden: bool = False):
    await interaction.response.send_message(f"I'd give it a solid {random.randint(1, 100)}", ephemeral=hidden)

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="ship", description="Ship 2 people together")
async def ship(interaction: discord.Interaction, person1: discord.Member, person2: discord.Member, hidden: bool = False):
    if person1 == person2:
        return await interaction.response.send_message("❗ Can't be the same member!")

    percentage = random.randint(1, 100)

    responses = {
        10: {
            "text": "Absolutely not.",
            "emoji": "💀"
        },
        20: {
            "text": "Not happening.",
            "emoji": "🪦"
        },
        30: {
            "text": "Yeah... no.",
            "emoji": "😬"
        },
        40: {
            "text": "There might be something...",
            "emoji": "👀"
        },
        50: {
            "text": "Could go either way.",
            "emoji": "🤷"
        },
        60: {
            "text": "Hmm, promising...",
            "emoji": "👀"
        },
        70: {
            "text": "Okayyy, i see it!",
            "emoji": "💕"
        },
        80: {
            "text": "Pretty cute together!",
            "emoji": "🥰"
        },
        90: {
            "text": "Now we're talking!",
            "emoji": "💖"
        },
        99: {
            "text": "JUST DATE ALREADY!",
            "emoji": "💘"
        },
        100: {
            "text": "THEY'RE LITERALLY PERFECT.",
            "emoji": "💍"
        },
    }

    # Placeholder vars
    emoji = "♥️"
    text = "Theyre cute together!"

    for maximum, response in responses.items():
        if percentage <= maximum:
            text = response["text"]
            emoji = response["emoji"]
            break

    await interaction.response.send_message(f"{person1.mention} {emoji} {person2.mention}\n{text} {percentage}", ephemeral=hidden)

@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="avatar", description="Show someone's avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member, hidden: bool = False):
    embed = discord.Embed(
        title=f"{member.display_name}'s avatar"
    )
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=hidden)
    
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="factcheck", description="Fact-check a statement")
async def factcheck(interaction: discord.Interaction, statement: str, hidden: bool = False):
    factcheck_responses = {
        True: [
            "Yep, That's completely true.",
            "Confirmed. The science checks out.",
            "After extensive research, I can confirm this.",
            "True, I have absolutely no evidence to prove otherwise.",
            "Correct. The council has verified this.",
        ],
        False: [
            "Nope. That's completely false.",
            "Incorrect. Nice try though.",
            "False. The evidence has been destroyed.",
            "Absolutely not. Who told you this??",
            "False. I consulted the expers (trust me).",
        ]
    }

    result = random.choice([True, False])
    response = random.choice(factcheck_responses[result])

    await interaction.response.send_message(f"## 🔎 Fact Check\n**Statement**: {statement}\n{'✅' if result else '❌'} **{response}**", ephemeral=hidden)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TOKEN is not set. Add it to your .env file.")
        sys.exit(1)

    bot.run(TOKEN)
