import discord
from discord.ext import commands
import aiohttp
import requests
import random
import re
#Put all the lists and pools in here!
#List of Responses and Messages
# List of potential greetings
# Initialize bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   intents=intents)  # Removed the '!' prefix
last_bot_wiki_message = None
greetings = ["Yes?", "You called?", "I heard my name!", "Ayo", "Sup", "はいはい", "Heyy", "Hi!"]

# List of bot nicknames and aliases
bot_nicknames = [
    "Astolfo", "Astolfo bot", "astolfo", "stolfo", "stolfy", "astolfy",
    "asstolfy", "sstolfo", "Rider", "ant's bot", "ants bot", "raida", "stulfy"
]

# List of affectionate messages
affectionate_messages = ["good boy", "i love you", "love you", "luv u"]

# List of affectionate responses
affectionate_responses = ["Ehehe", ":D !", "<3", ";)"]
#List of gratitude messages the bot recognizes
gratitude_messages = [
    "thanks", "thank you", "thx", "danke", "arigato", "ありがとう"
]
#List of messages for gratitude response
gratitude_responses = ["No Problem!", "You're welcome!", "🫡", "うん！"]
# List of activation phrases for fun facts
fun_fact_activation_phrases = [
    "give me a fun fact", "tell me something fun", "fun fact",
    "tell me a fact", "trivia please", "i want a fun fact"
]
# List of activation phrases for coffee request
coffee_activation_phrases = [
    "i want coffee", "i'm sleepy", "i'm so sleepy", "i'm thirsty",
    "i want a drink"
]
# List of messages for coffee response
coffee_messages = [
    "Have a sip, babes", "Here you go!", "Fresh off the pot!",
    "I can't give you actual coffee but I hope a digital one is fine!"
]

#List of messages for getting the wrong Wiki page
wrong_article_phrases = [
    "wrong", "wrong wiki"
    "wrong topic"
    "that's a different wiki"
    "that's not right"
    "that's not it"
    "wrong one"
]
#List of messages that users who need to chill might post
nono_messages = [
    "i want you",
    "sexy",
    "you're sexy",
    "you're hot"
]
#List of messages for horny denial
comedic_responses = [
    "🗡 Go to horny jail 🗡",
    "It's time 👏👏to touch 👏👏 some grass 👏👏",
    "Yeah I know you want me 💅",
    "You should probably go get some help",
    "Get~ Get~ Get some help~ 🔨🔨"
]

#DEFS
#MATH SHUFFLE
def shuffle_operations(equation):
    operators = '+-*/'
    parts = []
    current_part = ''
    for char in equation:
        if char in operators:
            parts.append(current_part)
            parts.append(char)
            current_part = ''
        else:
            current_part += char
    parts.append(current_part)

    # Shuffle the operations (keeping numbers together)
    numbers = [parts[i] for i in range(len(parts)) if i % 2 == 0]
    operations = [parts[i] for i in range(len(parts)) if i % 2 == 1]

    random.shuffle(operations)

    # Recreate the shuffled equation
    shuffled_equation = ''.join([
        numbers[i//2] if i % 2 == 0 else operations.pop(0) for i in range(len(parts))
    ])

    return shuffled_equation


#gratitude check
def check_gratitude_message(message_content, bot_nicknames):
    return any(phrase in message_content for phrase in gratitude_messages) and any(alias in message_content for alias in bot_nicknames)

#Affection check
def check_affectionate_message(message_content, bot_nicknames):
    return any(phrase in message_content for phrase in affectionate_messages) and any(alias in message_content for alias in bot_nicknames)

#nono check
def check_nono_message(message_content, bot_nicknames):
    return any(phrase in message_content for phrase in nono_messages) and any(alias in message_content for alias in bot_nicknames)

#DESU COUNTER
def count_specific_words(text):
    specific_words = ["desu", "dess", "death", "deth"]
    words = [word.strip('.,!?()[]{}"\'') for word in text.lower().split()]
    specific_word_count = sum(1 for word in words if word in specific_words)
    return specific_word_count
# Function to get a random fun fact
def get_fun_fact():
  response = requests.get(
      'https://uselessfacts.jsph.pl/random.json?language=en')
  data = response.json()
  return data['text']


# Function to fetch a random coffee image
def get_coffee_image():
  url = "https://coffee.alexflipnote.dev/random.json"
  response = requests.get(url)
  data = response.json()
  return data['file']


#WIKIAPI
def get_wikipedia_info(query):
  # Define the base URL for the Wikipedia API
  base_url = "https://en.wikipedia.org/w/api.php"

  # Define the parameters for the API request
  params = {
      "action": "query",
      "format": "json",
      "list": "search",
      "srsearch": query
  }
# Function to count specific words
  # Make the API request
  response = requests.get(base_url, params=params)
  data = response.json()

  # Check if there are any search results
  if data['query']['search']:
    # Get the title of the first search result
    title = data['query']['search'][0]['title']

    # Get the URL of the Wikipedia page
    page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

    # Get the first 1-2 paragraphs of the article
    content_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "titles": title
    }

    content_response = requests.get(base_url, params=content_params)
    content_data = content_response.json()

    # Extract the article content
    page_content = next(iter(
        content_data['query']['pages'].values()))['extract']

    return page_url, page_content

  else:
    return None, None


#STEAM API
def get_game_info_by_name(game_name):
  url = f"https://store.steampowered.com/api/storesearch/?term={game_name}"
  response = requests.get(url)

  if response.status_code == 200:
    data = response.json()
    if data.get('items', []):
      return data['items'][0]['id']

  return None


def get_game_info(game_name):
  app_id = get_game_info_by_name(game_name)

  if app_id:
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)

    if response.status_code == 200:
      data = response.json()
      if data.get(str(app_id), {}).get('success', False):
        game_data = data[str(app_id)]['data']

        if game_data.get('is_free', False):
          return {
              'name':
              game_data.get('name', 'Unknown'),
              'is_free':
              True,
              'price':
              'Free to Play',
              'discount_percent':
              0,
              'short_description':
              game_data.get('short_description', 'No description available')
          }
        else:
          return {
              'name':
              game_data.get('name', 'Unknown'),
              'is_free':
              False,
              'price':
              game_data.get('price_overview', {}).get('final_formatted',
                                                      'Price not available'),
              'discount_percent':
              game_data.get('price_overview', {}).get('discount_percent', 0),
              'short_description':
              game_data.get('short_description', 'No description available')
          }

  return None
# Lookup Command that also uses What's X keyphrase
@bot.command(name='lookup')
async def lookup(message, topic):
    global last_bot_wiki_message
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={topic}&prop=extracts&exintro&explaintext&redirects=1") as response:
            try:
                data = await response.json()
                page = next(iter(data['query']['pages'].values()))
                extract = page.get('extract')
                if extract:
                    if len(extract) > 750:
                        extract = extract[:750] + '...'
                    wiki_link = f"https://en.wikipedia.org/wiki/{topic}"
                    if last_bot_wiki_message is not None:
                        await last_bot_wiki_message.delete()
                    last_bot_wiki_message = await message.channel.send(f"Here's what I found on {topic.capitalize()}:\n{extract}\n\nRead more on [Wikipedia]({wiki_link} )")
                else:
                    await message.channel.send(f"Sorry, I couldn't find any information on {topic.capitalize()}.")
            except Exception as e:
                await message.channel.send(f"An error occurred while looking up '{topic}': {e}")
#BOT GOT THE WRONG WIKI
async def wrong_article(message):
    global last_bot_wiki_message
    if last_bot_wiki_message is not None:
        await last_bot_wiki_message.delete()
        last_bot_message = None  # Reset the reference
    await message.channel.send("Sorry! Maybe try rephrasing your search topic?")

#Pick For Me
async def pick_for_me(message, options):
    if len(options) < 2:
        await message.channel.send("I need at least two options to choose from.")
        return

    choice = random.choice(options)
    await message.channel.send(f"I choose: {choice}")
@bot.command(name='roll')
async def roll_command(ctx, dice_string='1d6'):
    try:
        if dice_string.isdigit():
            dice_string = '1d' + dice_string

        rolls, total = await roll_dice(dice_string)
        await ctx.send(f"You rolled {', '.join(map(str, rolls))}. Total: {total}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
# Dice Roll    
async def roll_d1000(channel):
    result = random.randint(1, 1000)
    await channel.send(f"Isn't... isn't that just a ball with a lot of numbers at this point?? Anyways, you rolled a {result}!")

async def roll(channel, dice):
    if dice == 'd1000':
        await roll_d1000(channel)
        return
    try:
        rolls, total = await roll_dice(dice)
        await channel.send(f"You rolled {', '.join(map(str, rolls))}. Total: {total}")
    except Exception as e:
        await channel.send(f"An error occurred: {e}")

async def roll_dice(dice):
    match = re.match(r'(\d+)d(\d+)', dice)
    if match:
        num_dice = int(match.group(1))
        num_sides = int(match.group(2))
        if num_dice > 0 and num_sides > 1:
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            return rolls, sum(rolls)
    raise ValueError("Invalid dice notation. Please use the format 'NdX' (e.g., '1d6', '2d10', etc.).")