import json
import discord
from discord.ext import commands

with open("settings.json", "r") as f:
    settings = json.loads(f.read())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix="s.")

@bot.hybrid_command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")
    return


if __name__ == "__main__":
    bot.run(settings["token"])
