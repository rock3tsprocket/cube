import discord
from discord.ext import commands, tasks
import json
import markovify
import nltk
from nltk.tokenize import word_tokenize
import random
import time
import re
import os
import requests
from dotenv import load_dotenv
from glob import glob

# Load the .env file
load_dotenv()

VERSION_URL = "https://goober.whatdidyouexpect.eu"
UPDATE_URL = "https://raw.githubusercontent.com/rock3tsprocket/cube/refs/heads/main/current_version.json"
print(UPDATE_URL)
LOCAL_VERSION_FILE = "current_version.json" 
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = os.getenv("BOT_PREFIX")
PING_LINE = os.getenv("PING_LINE")
hourlyspeak = int(os.getenv("hourlyspeak"))
PING_LINE = os.getenv("PING_LINE")
random_talk_channel_id1 = int(os.getenv("rnd_talk_channel1"))
random_talk_channel_id2 = int(os.getenv("rnd_talk_channel2"))
cooldown_time = os.getenv("cooldown")
splashtext = os.getenv("splashtext")
ownerid = int(os.getenv("ownerid"))
showmemenabled = os.getenv("showmemenabled")
BLACKLISTED_USERS = os.getenv("BLACKLISTED_USERS", "").split(",")
USERTRAIN_ENABLED = os.getenv("USERTRAIN_ENABLED", "true").lower() == "true"
NAME = os.getenv("NAME")
last_random_talk_time = 0
MEMORY_FILE = "memory.json"
DEFAULT_DATASET_FILE = "defaultdataset.json"
MEMORY_LOADED_FILE = "MEMORY_LOADED"
gooberTOKEN = os.getenv("gooberTOKEN")  
ALIVEPING = os.getenv("ALIVEPING")
RANDOMTALK = os.getenv("RANDOMTALK")
song = os.getenv("song")

print(splashtext) # you can use https://patorjk.com/software/taag/ for 3d text or just remove this entirely

def get_latest_version_info():
    """Fetch the latest version information from the server."""
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        response.raise_for_status()  # Will raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error: Unable to connect to the update server. {e}")
        return None

def get_local_version():
    """Read the current version from the local file."""
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            return json.loads(f.read().strip())["version"]
    return "0.0.0"

latest_version = "0.0.0"
local_version = "0.0.0"

def check_for_update():
    global latest_version, local_version 
    
    latest_version_info = get_latest_version_info()
    if not latest_version_info:
        print("Could not fetch update information.")
        return None, None 

    latest_version = latest_version_info.get("version")
    download_url = "https://raw.githubusercontent.com/rock3tsprocket/cube/refs/heads/main/bot.py"

    if not latest_version or not download_url:
        print("Error: Invalid version information received from server.")
        return None, None 

    local_version = get_local_version() 
    if local_version != latest_version:
        print(f"New version available: {latest_version} (Current: {local_version})")
        print(f"Check out the commit messages for cube (https://github.com/rock3tsprocket/cube)!\n\n")
    else:
        print(f"You're using the latest version: {local_version}")
        print(f"Check out the commit messages for cube (https://github.com/rock3tsprocket/cube)!\n\n")


check_for_update()

def get_file_info(file_path):
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, "r") as f:
            lines = f.readlines()
        return {"file_size_bytes": file_size, "line_count": len(lines)}
    except Exception as e:
        return {"error": str(e)}


def is_name_available(NAME):
    if os.getenv("gooberTOKEN"):
        return
    try:
        response = requests.post(f"{VERSION_URL}/check-if-available", json={"name": NAME}, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            return data.get("available", False)
        else:
            print(f"{get_translation(LOCALE, 'name_check')}", response.json())
            return False
    except Exception as e:
        print(f"{get_translation(LOCALE, 'name_check2')}", e)
        return False


def register_name(NAME):
    try:
        if ALIVEPING == False:
            return
        # check if the name is avaliable
        if not is_name_available(NAME):
            if os.getenv("gooberTOKEN"):
                return
            print(f"Name is already taken. Please choose a different name.")
            quit()
        
        # if it is register it
        response = requests.post(f"{VERSION_URL}/register", json={"name": NAME}, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            
            if not os.getenv("gooberTOKEN"):
                print(f"Token: {token}\nPlease add this token to your .env file as gooberTOKEN=<token>.")
                quit()
            else:
                print(f"")
            
            return token
        else:
            print(f"Token already exists in .env. Continuing with the existing token.", response.json())
            return None
    except Exception as e:
        print(f"Error during registration:", e)
        return None

register_name(NAME)

nltk.download('punkt')




def load_memory():
    data = []

    # load data from MEMORY_FILE
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        pass

    if not os.path.exists(MEMORY_LOADED_FILE):
        try:
            with open(DEFAULT_DATASET_FILE, "r") as f:
                default_data = json.load(f)
                data.extend(default_data) 
        except FileNotFoundError:
            pass
        with open(MEMORY_LOADED_FILE, "w") as f:
            f.write("Data loaded") 
    return data

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def train_markov_model(memory, additional_data=None):
    if not memory:
        return None
    text = "\n".join(memory)
    if additional_data:
        text += "\n" + "\n".join(additional_data)
    model = markovify.NewlineText(text, state_size=2)
    return model
#this doesnt work and im extremely pissed and mad
def append_mentions_to_18digit_integer(message):
    pattern = r'\b\d{18}\b'
    return re.sub(pattern, lambda match: f"<@{match.group(0)}>", message)

def preprocess_message(message):
    message = append_mentions_to_18digit_integer(message)
    tokens = word_tokenize(message)
    tokens = [token for token in tokens if token.isalnum()]
    return " ".join(tokens)


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, activity=discord.Activity(name=song, type=discord.ActivityType.listening))
memory = load_memory() 
markov_model = train_markov_model(memory)

generated_sentences = set()
used_words = set()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # the following code has been taken from Titanium (https://github.com/RestartB/titanium)
    for filename in glob(
        os.path.join("cogs", "**"), recursive=True, include_hidden=False
    ):
        if not os.path.isdir(filename):
            # Determine if file is a python file
            if filename.endswith(".py") and not filename.startswith("."):
                filename = filename.replace("\\", "/").replace("/", ".")[:-3]

                print(f"[INIT] Loading normal cog: {filename}...")
                await bot.load_extension(filename)
                print(f"[INIT] Loaded normal cog: {filename}")
    # the rest of this is either written by me or from goober
    ping_server()
    post_message.start()

positive_keywords = ["happy", "good", "great", "amazing", "awesome", "joy", "love", "fantastic", "positive", "cheerful", "victory", "favorite", "lmao", "lol", "xd", "XD", "xD", "Xd", "nice"]

def ping_server():
    if ALIVEPING == "false":
        print(f"Pinging is disabled! Not telling the server im on...")
        return

    # Alert from goober central
    goobres = requests.get(f"{VERSION_URL}/alert")
    if goobres.status_code == 200:
        print(f"Alert from goober central: \n{goobres.text}")
    else:
        print(f"Alert from cube: \nGoober Central is down: {goobres.status_code}")
    file_info = get_file_info(MEMORY_FILE)
    payload = {
        "name": NAME,
        "memory_file_info": file_info,
        "version": local_version,
        "slash_commands": "no",
        "token": gooberTOKEN
    }
    try:
        response = requests.post(VERSION_URL+"/ping", json=payload)
        if response.status_code == 200:
            print(f"Sent alive ping to goober central!")
        else:
            print(f"Failed to send data. Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending data: {str(e)}")



positive_gifs = [
    "https://tenor.com/view/chill-guy-my-new-character-gif-2777893510283028272",
    "https://tenor.com/view/goodnight-goodnight-friends-weezer-weezer-goodnight-gif-7322052181075806988",
    "https://cdn.discordapp.com/attachments/1319416099917271122/1393959079763902524/rust.gif?ex=6875110f&is=6873bf8f&hm=80e3fd861d53402456b050c3cb66727f800a08620aad99bc4edbbdcc1741cb0d&"
    ]

def is_positive(sentence):
    sentence_lower = sentence.lower()
    return any(keyword in sentence_lower for keyword in positive_keywords)

async def send_message(ctx, message=None, embed=None, file=None, edit=False, message_reference=None):
    if edit and message_reference:
        try:
            # Editing the existing message
            await message_reference.edit(content=message, embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to edit message: {e}")
    else:
        if hasattr(ctx, "respond"):
            # For slash command contexts
            sent_message = None
            if embed:
                sent_message = await ctx.respond(embed=embed, ephemeral=False)
            elif message:
                sent_message = await ctx.respond(message, ephemeral=False)
            if file:
                sent_message = await ctx.respond(file=file, ephemeral=False)
        else:

            sent_message = None
            if embed:
                sent_message = await ctx.send(embed=embed)
            elif message:
                sent_message = await ctx.send(message)
            if file:
                sent_message = await ctx.send(file=file)
        return sent_message

@bot.command()
async def ask(ctx, *, argument: str):
    if markov_model:
        response = None
        for _ in range(20):
            try:
                response = markov_model.make_sentence_with_start(argument, tries=100)
                if response and response not in generated_sentences:
                    response = improve_sentence_coherence(response)
                    generated_sentences.add(response)
                    break
            except KeyError as e:
                continue  
            except markovify.text.ParamError as e:
                continue 
        if response:
                cleaned_response = re.sub(r'[^\w\s]', '', response)
                cleaned_response = cleaned_response.lower()
                coherent_response = rephrase_for_coherence(cleaned_response)
                if random.random() < 0.9:
                    if is_positive(coherent_response):
                        gif_url = random.choice(positive_gifs)
                        combined_message = f"{coherent_response}\n[jif]({gif_url})"
                        await send_message(ctx, combined_message)
                    else:
                        await send_message(ctx, coherent_response)
                else:
                    await send_message(ctx, coherent_response)
        else:
            await send_message(ctx, "I couldn't come up with something relevant to that!")
    else:
        await send_message(ctx, "I need to learn more from messages before I can talk.")

@bot.command()
async def talk(ctx):
    if markov_model:
        response = None
        for _ in range(100):  # im going to shit my pants 10 times to get a coherent sentence
            response = markov_model.make_sentence(tries=100)
            if response and response not in generated_sentences:
                # preprocess shit for grammer
                response = improve_sentence_coherence(response)
                generated_sentences.add(response)
                break
        
        if response:
            async with ctx.typing():            
                cleaned_response = re.sub(r'[^\w\s]', '', response)  
                cleaned_response = cleaned_response.lower() 
                coherent_response = rephrase_for_coherence(cleaned_response)
                if random.random() < 0.9:
                    if is_positive(coherent_response):
                        gif_url = random.choice(positive_gifs)  
                        combined_message = f"{coherent_response}\n[jif]({gif_url})"  
                        await ctx.send(combined_message)
                    else:
                        await ctx.send(coherent_response)
                else:
                    await ctx.send(coherent_response)
        else:
            await ctx.send("I have nothing to say right now!")
    else:
        await ctx.send("I need to learn more from messages before I can talk.")

def improve_sentence_coherence(sentence):

    sentence = sentence.replace(" i ", " I ")  
    return sentence

def rephrase_for_coherence(sentence):

    words = sentence.split()

    coherent_sentence = " ".join(words)
    return coherent_sentence

bot.help_command = None


@bot.command()
async def help(ctx, *args):

    if args:
        command_name = args[0]
        command = bot.get_command(command_name)
        
        if command:
            embed = discord.Embed(
                title=f"Help: {PREFIX}{command_name}",
                description=f"**Description:** {command.help}",
                color=0x7B79FF
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Command `{command_name}` not found.")
    else:

        embed = discord.Embed(
            title="Bot Help",
            description="List of commands grouped by category.",
            color=0x7B79FF
        )

        command_categories = {
            "General": ["mem", "talk", "ask", "ping", "echo"],
            "Administration": ["stats"]
        }
        custom_commands: List[str] = []
        for cog_name, cog in bot.cogs.items():
            for command in cog.get_commands():
                if command.name not in command_categories["General"] and command.name not in command_categories["Administration"]:
                    custom_commands.append(command.name)

        if custom_commands:
            embed.add_field(name="Custom Commands", value="\n".join([f"{PREFIX}{command}" for command in custom_commands]), inline=False)
        #    embed.set_footer(text="This bot has Super Cube Powers.")

        for category, commands_list in command_categories.items():
            commands_in_category = "\n".join([f"{PREFIX}{command}" for command in commands_list])
            embed.add_field(name=category, value=commands_in_category, inline=False)

        await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    global memory, markov_model, last_random_talk_time

    if message.author.bot:
        return

    if not USERTRAIN_ENABLED:
        return

    if str(message.author.id) in BLACKLISTED_USERS:
        return

    random_talk_channels = [random_talk_channel_id2, random_talk_channel_id1] 
    cooldowns = {
        random_talk_channel_id2: 1, 
    }
    default_cooldown = 10800

    if message.content.startswith((f"{PREFIX}talk", f"{PREFIX}mem", f"{PREFIX}help", f"{PREFIX}stats", f"{PREFIX}")):
        await bot.process_commands(message)
        return

    if any(word in message.content for word in ["faggot", "fag", "nigger", "nigga"]):
        await bot.process_commands(message)
        return

    if message.content:
        formatted_message = append_mentions_to_18digit_integer(message.content)
        cleaned_message = preprocess_message(formatted_message)
        if cleaned_message:
            memory.append(cleaned_message)
            save_memory(memory)
            markov_model = train_markov_model(memory)


    cooldown_time = cooldowns.get(message.channel.id, default_cooldown)
    if message.reference and message.reference.message_id:
        replied_message = await message.channel.fetch_message(message.reference.message_id)
        if replied_message.author == bot.user:  
            print("Bot is replying to a message directed at it!")
            response = None
            for _ in range(10):  
                response = markov_model.make_sentence(tries=100)
                if response and response not in generated_sentences:
                    response = improve_sentence_coherence(response)
                    generated_sentences.add(response)
                    break
            if response:
                await message.channel.send(response)
            return 

    # random chance for bot to talk
    random_chance = random.randint(0, 20)

    # talk randomly only in the specified channels
    if RANDOMTALK == "True":
        if message.channel.id in random_talk_channels and random_chance >= 10:
            current_time = time.time()
            print(f"Random chance: {random_chance}, Time passed: {current_time - last_random_talk_time}")

            if current_time - last_random_talk_time >= cooldown_time:
                print("Bot is talking randomly!")
                last_random_talk_time = current_time

                response = None
                for _ in range(10): 
                    response = markov_model.make_sentence(tries=100)
                    if response and response not in generated_sentences:
                        response = improve_sentence_coherence(response)
                        generated_sentences.add(response)
                        break

                if response:
                    await message.channel.send(response)

    # process any commands in the message
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.defer()
    #stolen from my expect bot very proud
    latency = round(bot.latency * 1000)

    LOLembed = discord.Embed(
        title="Pong!!",
        description=(
            f"{PING_LINE}\n"
            f"`Bot Latency: {latency}ms`\n"
        ),
        color=0x7B79FF
    )
    LOLembed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=LOLembed)  # use ctx.send instead of respond because it has nothing to respond to and its not a slash command

@bot.command()
async def echo(ctx, *args):
    arguments = ' '.join(args)
    if "@" in arguments:
        await ctx.send("don't ping")
        return
    else:
        await ctx.send(arguments)

@bot.command()
async def echo_ping(ctx, *args):
    arguments = ' '.join(args)
    if ctx.author.id != ownerid:
        await ctx.send("You do not have permission to use this command!")
        return
    else:
        await ctx.send(arguments)

# backported about command
@bot.command()
async def about(ctx):
    print("-----------------------------------\n\n")
    check_for_update()
    print("-----------------------------------")
    embed: discord.Embed = discord.Embed(title=f"About me", description="", color=0x7B79FF)
    embed.add_field(name=f"Name", value=f"{NAME}", inline=False)
    embed.add_field(name=f"Version", value=f"Local: {local_version}\n Latest: {latest_version}\nSource Code: https://github.com/rock3tsprocket/cube\n License: GNU AGPL-3.0", inline=False)

    await send_message(ctx, embed=embed)


@bot.command()
async def stats(ctx):
    if ctx.author.id != ownerid :
        await ctx.send("You do not have permission to use this command!")
        return

    memory_file = 'memory.json'
    file_size = os.path.getsize(memory_file)
    
    with open(memory_file, 'r') as file:
        line_count = sum(1 for _ in file)

    embed = discord.Embed(title="Bot Stats", description="Data about the the bot's memory.", color=0x7B79FF)
    embed.add_field(name="File Stats", value=f"Size: {file_size} bytes\nLines: {line_count}", inline=False)
    embed.add_field(name="Version", value=f"Local: {local_version} \nLatest: {latest_version}", inline=False)
    embed.add_field(name="Variable Info", value=f"Prefix: {PREFIX} \nOwner ID: {ownerid} \nCooldown: {cooldown_time} \nPing line: {PING_LINE} \nListening to: {song}", inline=False)

    
    await ctx.send(embed=embed)
@bot.command()
async def mem(ctx):
    if showmemenabled != "true":
        return
    memory = load_memory()
    memory_text = json.dumps(memory, indent=4)
    if len(memory_text) > 1024:
        with open(MEMORY_FILE, "r") as f:
            await ctx.send(" ", file=discord.File(f, MEMORY_FILE))
    else:
        embed = discord.Embed(title="Memory Contents", description="The bot's memory.", color=0x7B79FF)
        embed.add_field(name="Memory Data", value=f"```json\n{memory_text}\n```", inline=False)
        await ctx.send(embed=embed)

def improve_sentence_coherence(sentence):
    sentence = sentence.replace(" i ", " I ")
    return sentence

@bot.command()
async def shell(ctx):
    if ctx.author.id != ownerid : 
        return
    os.system("bash")

@bot.command()
async def changestatus(ctx, *args):
    global song
    if ctx.author.id != ownerid:
        await ctx.send("You do not have permission to use this command!")
        return
    arguments = ' '.join(args)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=arguments, type=discord.ActivityType.listening))
    if arguments == "":
        await ctx.send("Disabled status")
    else:
        await ctx.send(f"Now listening to: {arguments}")
    song = arguments

@tasks.loop(minutes=60)
async def post_message():
    channel_id = hourlyspeak
    channel = bot.get_channel(channel_id)
    if channel and markov_model:
        response = None
        for _ in range(10): 
            response = markov_model.make_sentence(tries=100)
            if response and response not in generated_sentences:
                generated_sentences.add(response)
                break

        if response:
            await channel.send(response)


bot.run(TOKEN)
