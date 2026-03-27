from glob import glob
import json
import discord
from discord.ext import commands

try:
    open("memory.json", "x")
    with open("memory.json", "w") as f:
        f.write("""[\n]""")
except FileExistsError:
    pass

with open("settings.json", "r") as f:
    settings = json.loads(f.read())

versionnumber = "1.0-beta1"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix=settings["prefix"], help_command=None)

@bot.hybrid_command(name="ping")
async def ping(ctx):
    embed = discord.Embed(title="Pong!")
    embed.add_field(name="Latency:", value=f"{round(bot.latency*1000, 2)}ms", inline=True)

    await ctx.send(embed=embed)
    return

@bot.hybrid_command(name="version")
async def version(ctx):
    await ctx.send(versionnumber)
    return

@bot.hybrid_command(name="sync")
async def sync(ctx):
    if int(ctx.author.id) != int(settings["ownerid"]):
        return

    synced = len(await bot.tree.sync())
    await ctx.send(f"Synced {synced} commands successfully!")
    print(f"Synced {synced} commands successfully!")
    return

@bot.hybrid_command(name="mem")
async def mem(ctx):
    await ctx.send(file=discord.File("memory.json"))
    return

@bot.hybrid_command(name="help")
async def help(ctx):
    embed = discord.Embed(title="Help")
    embed.add_field(name="Core commands:", value=f"{settings["prefix"]}help\n"
                                            f"{settings["prefix"]}mem\n"
                                            f"{settings["prefix"]}ping\n"
                                            f"{settings["prefix"]}version\n"
                                            f"{settings["prefix"]}sync (Owner only)\n")
    commands = ""
    for cog in bot.cogs:
        for command in bot.cogs[cog].get_commands():
            commands+=f"{settings["prefix"]}{command}\n"

    embed.add_field(name="Cog commands:", value=commands)

    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith(settings["prefix"]):
        with open("memory.json", "r") as f:
            memory = f.read()

        # yeah this is big brain time
        memory = memory.replace("\n]", "")
        memory+=f',\n"{message.content.replace('"', "")}"'
        memory+="\n]"
        with open("memory.json", "w") as f:
            f.write(memory.replace("[,\n", "[\n"))
        return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    for cog in glob("cogs/*.py"):
        cog = cog.replace("/", ".")[0:-3]
        await bot.load_extension(cog)
        print(f"Loaded cog {cog[5:]} successfully")

    print(f"Bot is up as {bot.user.name}#{bot.user.discriminator}!")

if __name__ == "__main__":
    exit(bot.run(settings["token"]))

