import json
import discord
from discord.ext import commands

try:
    open("memory.json", "x")
    with open("memory.json", "w") as f:
        f.write("""{\n}""")
except FileExistsError:
    pass

with open("settings.json", "r") as f:
    settings = json.loads(f.read())

version = "1.0-alpha1"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix=settings["prefix"])

@bot.hybrid_command(name="ping")
async def ping(ctx):
    await ctx.reply("Pong!")
    return

@bot.hybrid_command(name="version")
async def ping(ctx):
    await ctx.reply(version)
    return

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith(settings["prefix"]):
        with open("memory.json", "r") as f:
            memory = f.read()

        # yeah this is big brain time
        memory = memory.replace("\n}", "")
        memory+=f',\n"{message.author.id}": "{message.content}"'
        memory+="\n}"
        with open("memory.json", "w") as f:
            f.write(memory.replace("{,\n", "{\n"))
        return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Bot is up as {bot.user.name}#{bot.user.discriminator}!")

if __name__ == "__main__":
    bot.run(settings["token"])


