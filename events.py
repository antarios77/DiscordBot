import discord
from discord.ext import commands
import random
import wikipedia
import aiohttp
import requests
from utility import greetings, bot_nicknames, affectionate_messages, affectionate_responses, gratitude_messages
from utility import gratitude_responses, fun_fact_activation_phrases
from utility import coffee_activation_phrases, coffee_messages, comedic_responses, nono_messages
from utility import wrong_article_phrases, shuffle_operations, get_fun_fact, get_coffee_image
from utility import get_wikipedia_info, get_game_info_by_name, get_game_info, check_nono_message
from utility import bot, check_gratitude_message, count_specific_words, check_affectionate_message
from utility import lookup, wrong_article, pick_for_me, roll_command
from utility import roll_dice, roll_command, roll_d1000, roll
import re
# Define your intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Initialize bot_primed dictionary and last_greeting_time dictionary
bot_primed = {}
last_greeting_time = {}
last_command_time = {}
last_bot_wiki_message = None

# Set Wikipedia language
wikipedia.set_lang("en")

# Cooldown for greetings (in seconds)
greeting_cooldown = 10  # Adjust this as needed

bot = commands.Bot(command_prefix='!', intents=intents)


def register_events(bot):

  @bot.event
  async def on_message(message):
    if message.author == bot.user:
      return
    global bot_primed, last_greeting_time, last_bot_wiki_message

    # Name detection
    mentioned_aliases = [alias.lower() for alias in bot_nicknames]
    content = message.content.lower()
    await respond_to_queries(message)
    if message.content.lower().startswith("hey"):
      if any(alias in content for alias in mentioned_aliases):
        bot_primed[message.guild.id] = True
        primed_responses = [
            "Yes, I've been called specifically?", "Do you need something?",
            "How can I help?"
        ]
        await message.channel.send(random.choice(primed_responses))
        return  # Exit the function to avoid further processing
    # Check if the bot is primed
    if bot_primed.get(message.guild.id, False):
      specific_word_count = count_specific_words(message.content)
      if specific_word_count > 0:
        if specific_word_count > 1:
          response = f"Desu! You've said 'desu' {specific_word_count} times!"
        elif specific_word_count == 1:
          response = "I found a 'desu', desu!"
        await message.channel.send(response)

      # Check for keyphrases to override the need for priming
      if content.startswith(("what's", "what is")):
        topic = content.split(' ', 1)[1]
        await message.channel.send(
            "I can look it up for you. Should I do that? (Yes/No)")
        response = await bot.wait_for("message",
                                      check=lambda m: m.author == message.
                                      author and m.channel == message.channel)
        if response.content.lower().strip() in ("yes", "ye", "yep", "yeah",
                                                "y", "ya"):
          await lookup(message, topic)
          return
        else:
          await message.channel.send("Okay!")
# In the on_message event
    if any(phrase in content for phrase in wrong_article_phrases):
      await wrong_article(message)
# Random greeting
    mentioned_aliases = [alias.lower() for alias in bot_nicknames]
    for alias in mentioned_aliases:
      if alias in content:
          last_greeting = last_greeting_time.get(message.guild.id, 0)
          current_time = message.created_at.timestamp()

          if current_time - last_greeting >= greeting_cooldown:
              if not check_gratitude_message(content, mentioned_aliases) and not check_affectionate_message(content, mentioned_aliases) and not check_nono_message(content, mentioned_aliases):
                  greeting = random.choice(greetings)
                  await message.channel.send(greeting)
                  last_greeting_time[message.guild.id] = current_time

          break


#Message checks
    if check_affectionate_message(content, bot_nicknames):
        affectionate_response = random.choice(affectionate_responses)
        await message.channel.send(affectionate_response)

    if check_gratitude_message(content, bot_nicknames):
        gratitude_response = random.choice(gratitude_responses)
        await message.channel.send(gratitude_response)

    if check_nono_message(content, bot_nicknames):
        comedic_response = random.choice(comedic_responses)
        await message.channel.send(comedic_response)
      # Check if user wants to pin the previous message
    if "please pin" in content.lower() or "please pin that" in content.lower(
    ) or "pin please" in content.lower():
      async for msg in message.channel.history(before=message, limit=2):
        if msg.id == message.id:  # Skip the current message
          continue
        await msg.pin()
        await message.channel.send("I've pinned the previous message for you!")
        break
    # Fun fact command activation
    if any(phrase in content for phrase in fun_fact_activation_phrases):
      fun_fact = get_fun_fact()
      await message.channel.send(fun_fact)
      return
    # Coffee request activation
    if any(phrase in content for phrase in coffee_activation_phrases):
      coffee_image_url = get_coffee_image()
      coffee_message = random.choice(coffee_messages)
      await message.channel.send(f"{coffee_message} ☕")
      await message.channel.send(coffee_image_url)

    # Check if the message contains the keyphrase "roll me a X"
    if content.startswith("roll me a "):
      dice_string = content.replace("roll me a ", "")
      if not re.match(r'^\d+d\d+$', dice_string):
        dice_string = '1' + dice_string  # Add '1' if not specified
      await roll(message.channel, dice_string)
      return
    # Check if user indicates the article is wrong
    mentioned_aliases = [alias.lower() for alias in bot_nicknames]
    if any(phrase in content.lower()
           for phrase in wrong_article_phrases) and any(
               alias in content.lower() for alias in mentioned_aliases):
      await wrong_article(message)
    if content.startswith("!lookup"):
      topic = content[8:]
      await lookup(message, topic)
    # Handle other commands or processes here
#Pick for Me On_message
    if content.startswith("pick for me:"):
      options = content[13:].replace(' or ', ', ').split(", ")
      await pick_for_me(message, options)
    # Example for owo/uwu converter
    if "OwO" in str(message.content):
      await message.channel.send("UwU")
    elif "owo" in str(message.content):
      await message.channel.send("UwU")
    elif "UwU" in str(message.content):
      await message.channel.send("OwO")
    elif "uwu" in str(message.content):
      await message.channel.send("OwO")


#MATH SHUFFLE ON MESSAGE
# Math Detection

    if any(operator in message.content for operator in ['+', '-', '*', '/']):
      equation = message.content.replace(' ', '')
      try:
        result = None  # Initialize result to None

        if len(equation) <= 5:
            result = eval(equation)
            random_offset = random.randint(-5, 5)
            final_result = round(result + random_offset, equation.count('.') + 1)
        else:
            equation = shuffle_operations(equation)
            final_result = eval(equation)

        responses = [
            "{final_result} !", "Oh oh! The answer is {final_result}",
            "EZ. It's {final_result}!", "I got it! {final_result}!",
            "Is that {final_result}?"
        ]

        response = random.choice(responses)

        if result is not None and abs(result - final_result) < 0.01:
            response += "\n...Wait I got it right for once? SWEET!"

        await message.channel.send(response.format(final_result=final_result))

      except Exception:
        response = "Wat."
        await message.channel.send(response)
    await bot.process_commands(message)

#Purpose of Bot
async def respond_to_queries(message):
    mentioned_aliases = [alias.lower() for alias in bot_nicknames]
    content = message.content.lower()

    if any(alias in content for alias in mentioned_aliases):
        queries = [
            "what are you",
            "what is your purpose",
            "what's",
        ]

        for query in queries:
            if query in content:
                response = "I'm Antarios' special Discord bot project: Astolfo! I am held up by hopes, duct tape, and sheer insane luck. I have a number of features that you can learn about and some of them can be found by using !commands."
                await message.channel.send(response)
                break