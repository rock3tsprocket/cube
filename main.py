from glob import glob
import json
import discord
from discord.ext import commands

with open("settings.json", "r") as f:
    settings = json.loads(f.read())

versionnumber = "1.1.1"

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
@commands.is_owner()
async def sync(ctx):
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
    embed.add_field(name="Core commands:",
                    value=f"{settings["prefix"]}help\n"
                          f"{settings["prefix"]}mem\n"
                          f"{settings["prefix"]}ping\n"
                          f"{settings["prefix"]}version\n"
                          f"{settings["prefix"]}stats\n"
                          f"{settings["prefix"]}sync (Owner only)\n")
    commands = ""
    for cog in bot.cogs:
        for command in bot.cogs[cog].get_commands():
            commands+=f"{settings["prefix"]}{command}\n"
        embed.add_field(name=cog, value=commands)
        commands = ""

    await ctx.send(embed=embed)


@bot.hybrid_command()
async def stats(ctx):
    owner_id = await bot.application_info()
    owner_id = owner_id.owner.id
    try:
        nomemory = False
        f = open("memory.json", "r")
        memorylen = len(f.read())
        f.seek(0)
        memorylines = len(f.readlines())
    except OSError:
        nomemory = True
    finally:
        f.close()

    embed = discord.Embed(title="Bot Stats")
    if not nomemory:
        embed.add_field(name="File Stats",
                        value=f"Size: {memorylen} bytes\n"
                        f"Lines: {memorylines}", inline=False)
    embed.add_field(name="Version",
                    value=f"Current version: {versionnumber}", inline=False)
    embed.add_field(name="Settings",
                    value=f"Prefix: {settings["prefix"]}\n"
                    f"Owner ID: {owner_id}\n", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_ready():
    for cog in glob("cogs/*.py"):
        cog = cog.replace("/", ".")[0:-3]
        await bot.load_extension(cog)
        print(f"Loaded cog {cog[5:]} successfully")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.send("Error: You are not allowed to run this command.")
    else:
        raise error

    print(f"Bot is up as {bot.user.name}#{bot.user.discriminator}!")

if __name__ == "__main__":
    exit(bot.run(settings["token"]))

