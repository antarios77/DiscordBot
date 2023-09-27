import discord
import os
import random
from discord.ext import commands, tasks
import wikipedia
import requests
import re
import asyncio
import datetime
import json
import wolframalpha
from bs4 import BeautifulSoup
import aiohttp
from utility import greetings, bot_nicknames, affectionate_messages, affectionate_responses, gratitude_messages
from utility import gratitude_responses, fun_fact_activation_phrases
from utility import coffee_activation_phrases, coffee_messages
from utility import wrong_article_phrases, shuffle_operations, get_fun_fact, get_coffee_image
from utility import get_wikipedia_info, get_game_info_by_name, get_game_info
from events import register_events
from utility import bot, intents
from utility import lookup, pick_for_me, roll_d1000


# Initialize bot_primed dictionary and last_greeting_time dictionary
bot_primed = {}
last_greeting_time = {}
last_command_time = {}
last_bot_wiki_message = None


# Set Wikipedia language
wikipedia.set_lang("en")


# Function to get user's local time
def get_user_local_time(user_id):
    # Placeholder function, you can implement this if needed
    pass

# Register events
register_events(bot)


# BadArgument Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        if ctx.command.name == 'convert':
            await ctx.send("Format's wrong, desu! Please use '!convert X (source currency) to (target currency)'. There is a [space] between the amount and the source currency, desu.")
        else:
            # Handle other BadArgument errors for different commands
            pass
    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'convert':
            await ctx.send("You're missing some arguments! Please use '!convert X (source currency) to (target currency)', desu.")
        else:
            # Handle other MissingRequiredArgument errors for different commands
            pass
    else:
        await ctx.send(f"An error occurred: {error}")

#BOT READYING
@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
#GOOD MORNING GREETING
@tasks.loop(hours=24)  # Set the interval to 24 hours
async def greet():      
  guild = discord.utils.get(bot.guilds, name='Potato Salad')
  channel = discord.utils.get(guild.channels, name='general')
  now = datetime.now(timezone('Asia/Singapore'))  # Get current time in GMT+8
        # Check if it's 9:00 AM
  if now.hour == 9 and now.minute == 0:
      await channel.send("Good morning, everyone! Good luck with your day")
# Initialize the WolframAlpha client
app_id = os.environ.get("WOLFRAM_ALPHA_APP_ID")  # Get your App ID from environment variables
client = wolframalpha.Client(app_id)
#Bot Tutorial
@bot.command(name='commands')
async def commands(ctx):
    response = """Here are the list of !commands:
    !lookup = I'll try to look up a wikipedia article for you
    !gameinfo = I'll pull up some info on a game in Steam. (Currently not working for some reason)
    !dice = I'll roll a die for you. You have to specify the die type and the amount of dice (1d20, 2d6, etc)
    !ask = I'll try and answer an inquiry via Wolfram Alpha

    Here are some of my extra features:
    I can pin the immediate previous message for you if you ask me (say "please pin" or "please pin that" or "pin please")
    I can help you pick from a list (say "pick for me: X, Y, Z" or "pick for me: X or Y or Z")
    I have way more features than the aforementioned but you'll have to discover them yourself."""

    await ctx.send(response)
# Function to query WolframAlpha and get a short answer
async def ask_wolframalpha(query):
    res = client.query(query)
    try:
        answer = next(res.results).text
        return answer
    except StopIteration:
        return "I dunno, actually."

# Command to ask WolframAlpha
@bot.command(name='ask')
async def ask(ctx, *, question):
    answer = await ask_wolframalpha(question)
    await ctx.send(answer)


#Steam Command
STEAM_API_URL = "https://api.steampowered.com/ISteamApps/GetAppDetails/v1/"
async def game_info(ctx, app_id):
    app_data = get_game_info(app_id)

    if app_data:
        # Extract and send relevant information
        name = app_data['name']
        price_overview = app_data.get('price_overview', {})
        price = price_overview.get('final_formatted', 'Price not available')
        discount_percent = price_overview.get('discount_percent', 0)
        discount = f'{discount_percent}% off' if discount_percent > 0 else 'No discount'
        system_requirements = app_data.get('pc_requirements', {}).get('minimum', 'System requirements not available')
        description = app_data.get('detailed_description', 'Description not available')

        message = f"**Name:** {name}\n" \
                  f"**Price:** {price}\n" \
                  f"**Discount:** {discount}\n" \
                  f"**System Requirements:** {system_requirements}\n" \
                  f"**Description:** {description}"

        await ctx.send(message)
    else:
        await ctx.send("Error retrieving game information. Please check the app ID and try again.")
@bot.command(name='gameinfo')
async def game_info(ctx, app_id):
    app_data = get_game_info(app_id)
    if app_data:
        name = app_data['name']
        price = app_data['price_overview']['final'] / 100  # Convert to dollars
        discount = app_data['price_overview'].get('discount_percent', 0)
        description = app_data['detailed_description']
        sys_requirements = app_data.get('pc_requirements', {}).get('minimum', 'Not specified')

        response = f"**Game:** {name}\n" \
                   f"**Price:** ${price}\n" \
                   f"**Discount:** {discount}%\n" \
                   f"**System Requirements:** {sys_requirements}\n" \
                   f"**Description:** {description}"

        await ctx.send(response)
    else:
        await ctx.send("Game not found or data not available.")

token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)
