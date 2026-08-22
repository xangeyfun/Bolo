from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import discord
import logging
import random
import sys
import time
import os

log = logging.getLogger("bolo")

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.messages = True
bot = commands.Bot(command_prefix="$", intents=intents, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="/help | Bolo"))
TOKEN = os.getenv("TOKEN")
startup = time.time()
armed_rigs = {}

OPTIMISTIC_FORECASTS = [
    "☀️ Endless sunshine with light winds of confidence",
    "🌤️ Mostly clear skies, zero regrets expected",
    "🌈 Scattered rainbows followed by free snacks",
    "😎 Cool breeze with a high chance of main character energy",
    "🌻 Warm and cozy, perfect for doing absolutely nothing",
]

PESSIMISTIC_FORECASTS = [
    "🌧️ Persistent drizzle with bursts of mild regret",
    "🌩️ Thunderstorms and a side of existential dread",
    "🌫️ Dense fog of confusion lasting all day",
    "🥶 Freezing winds, staying in bed is strongly advised",
    "🌪️ Chaos with scattered responsibilities",
]

async def setup_hook():
    log.info("Syncing commands...")
    start = time.time()
    try:
        synced = await bot.tree.sync()
        log.info("Synced %d commands in %.2f seconds", len(synced), time.time() - start)
    except Exception as e:
        log.error("Error syncing commands: %s", e)

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    if bot.user:
        log.info("Logged in as %s (%s)", bot.user.name, bot.user.id)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    user = f"{interaction.user} ({interaction.user.id})"

    if interaction.guild:
        place = interaction.guild.name
        channel_name = getattr(interaction.channel, "name", None)
        if channel_name:
            place += f" #{channel_name}"
    else:
        place = "DMs"

    if interaction.type == discord.InteractionType.application_command:
        options = ", ".join(f"{opt['name']}={opt['value']!r}" for opt in (interaction.data.get("options") or []))
        log.info("/%s (%s) by %s in %s", interaction.data["name"], options, user, place)
    elif interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        log.info("Component '%s' pressed by %s in %s", custom_id, user, place)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms", ephemeral=True)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="github", description="Get the bot's GitHub repository link") #, guild=guild)
async def github(interaction: discord.Interaction):
    await interaction.response.send_message("You can find the bot's source code on GitHub:\nhttps://github.com/xangeyfun/Bolo", ephemeral=True)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction, hidden: bool = False):
    armed = armed_rigs.pop(interaction.user.id, None)

    if armed and armed[1] >= time.monotonic():
        result = armed[0]
        log.info("/coinflip is rigged via /forecast for %s -> %s", interaction.user, result)
    else:
        result = random.choice(["Heads", "Tails"])
        log.info("/coinflip is fair for %s", interaction.user)

    await interaction.response.send_message("🪙 Flipping...", ephemeral=hidden)
    await asyncio.sleep(1)
    await interaction.edit_original_response(content=f"🪙 It landed on **{result}**!")

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(question="Ask anything!", hidden="Hide the command from others")
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

    answer = random.choice(answers)
    question = question if len(question) <= 100 else question[:97] + "..."

    await interaction.response.send_message("🎱 Shaking the ball...", ephemeral=hidden)
    await asyncio.sleep(1)
    await interaction.edit_original_response(content=f"❓ **{question}**\n🎱 {answer}")

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(options="Separated by | max 25 (e.g. option1|option2|option3)", hidden="Hide the command from others")
@bot.tree.command(name="choose", description="Randomly pick between options")
async def choose(interaction: discord.Interaction, options: str, hidden: bool = False):
    choices = [choice.strip() for choice in options.split("|") if choice.strip()]

    if len(choices) < 2:
        return await interaction.response.send_message("❗ Give at least 2 options separated by `|`, e.g. `pizza|sushi|tacos`", ephemeral=True)

    if len(choices) > 25:
        return await interaction.response.send_message(f"❗ Too many options! Max 25, you gave `{len(choices)}`", ephemeral=True)

    pick = random.choice(choices)
    thinking = random.choice(["🤔 Thinking...", "⚖️ Weighing my options...", "🎲 Rolling the dice..."])

    await interaction.response.send_message(thinking, ephemeral=hidden)
    await asyncio.sleep(1)

    content = f"🎲 I choose **{pick}**!"
    options_str = " | ".join(choices)
    if len(options_str) <= 500:
        content += f"\n-# Options: {options_str}"

    await interaction.edit_original_response(content=content)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(thing="The thing to rate", hidden="Hide the command from others")
@bot.tree.command(name="rate", description="Rate something from 1 to 100")
async def rate(interaction: discord.Interaction, thing: str, hidden: bool = False):
    score = random.randint(1, 100)

    if score >= 90:
        vibe = "an absolute masterpiece"
    elif score >= 70:
        vibe = "pretty solid ngl"
    elif score >= 50:
        vibe = "mid tbh"
    elif score >= 30:
        vibe = "kinda rough"
    else:
        vibe = "just plain bad"

    await interaction.response.send_message(f"I'd give **{thing}** a **{score}/100** - {vibe}", ephemeral=hidden)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="ship", description="Ship 2 people together")
async def ship(interaction: discord.Interaction, person1: discord.User, person2: discord.User, hidden: bool = False):
    if person1 == person2:
        return await interaction.response.send_message("❗ Can't be the same member!", ephemeral=True)

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
    text = "They're cute together!"

    for maximum, response in responses.items():
        if percentage <= maximum:
            text = response["text"]
            emoji = response["emoji"]
            break

    filled = round(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)

    await interaction.response.send_message(
        f"{person1.mention} 💘 {person2.mention}\n{bar} **{percentage}%**\n{emoji} {text}",
        ephemeral=hidden,
    )

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(hidden="Hide the command from others")
@bot.tree.command(name="avatar", description="Show someone's avatar")
async def avatar(interaction: discord.Interaction, member: discord.User, hidden: bool = False):
    embed = discord.Embed(
        title=f"{member.display_name}'s avatar"
    )
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=hidden)
    
@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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
            "False. I consulted the experts (trust me).",
        ]
    }

    result = random.choice([True, False])
    response = random.choice(factcheck_responses[result])

    await interaction.response.send_message(f"## 🔎 Fact Check\n**Statement**: {statement}\n{'✅' if result else '❌'} **{response}**", ephemeral=hidden)

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.describe(vibe="How do you feel about tomorrow?", hidden="Hide the command from others")
@discord.app_commands.choices(vibe=[
    discord.app_commands.Choice(name="Optimistic ☀️", value="optimistic"),
    discord.app_commands.Choice(name="Pessimistic 🌧️", value="pessimistic"),
])
@bot.tree.command(name="forecast", description="Get tomorrow's forecast")
async def forecast(interaction: discord.Interaction, vibe: discord.app_commands.Choice[str], hidden: bool = False):
    if vibe.value == "optimistic":
        condition = random.choice(OPTIMISTIC_FORECASTS)
        temp = random.randint(18, 29)
    else:
        condition = random.choice(PESSIMISTIC_FORECASTS)
        temp = random.randint(-9, 7)

    armed_rigs[interaction.user.id] = ("Heads" if vibe.value == "optimistic" else "Tails", time.monotonic() + 120)
    log.info("/forecast armed %s for %s (vibe: %s)", armed_rigs[interaction.user.id][0], interaction.user, vibe.value)

    await interaction.response.send_message(
        f"🌦️ **Tomorrow's forecast**\n> {condition}\n> 🌡️ {temp}°C",
        ephemeral=hidden,
    )

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TOKEN is not set. Add it to your .env file.")
        sys.exit(1)

    if sys.stdout.isatty():
        bot.run(TOKEN, root_logger=True)
    else:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[{levelname:<8}] {name}: {message}", style="{")
        bot.run(TOKEN, log_handler=handler, log_formatter=formatter, root_logger=True)
