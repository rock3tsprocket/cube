import json
from discord.ext import commands

class cogmgr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        f = open("settings.json", "r")
        self.ownerid = json.loads(f.read())["ownerid"]
        f.close()

    @commands.hybrid_command()
    async def load(self, ctx, arg1 = None):
        if int(ctx.author.id) != int(self.ownerid):
            return

        if not arg1:
            await ctx.send("No cog specified!")
            return
        try:
            await self.bot.load_extension(f"cogs.{arg1}")
            await ctx.send(f"Loaded cog `{arg1}` successfully")
        except Exception as e:
            await ctx.send(f"Failed to load cog `{arg1}`: {e}")

    @commands.hybrid_command()
    async def unload(self, ctx, arg1 = None):
        if int(ctx.author.id) != int(self.ownerid):
            return

        if not arg1:
            await ctx.send("No cog specified.")
            return
        try:
            await self.bot.unload_extension(f"cogs.{arg1}")
            await ctx.send(f"Unloaded cog `{arg1}` successfully")
        except Exception as e:
            await ctx.send(f"Failed to unload cog `{arg1}`: {e}")

    @commands.hybrid_command()
    async def reload(self, ctx, arg1 = None):
        if int(ctx.author.id) != int(self.ownerid):
            return

        if not arg1:
            await ctx.send("No cog specified.")
            return
        try:
            await self.bot.reload_extension(f"cogs.{arg1}")
            await ctx.send(f"Reloaded cog `{arg1}` successfully")
        except Exception as e:
            await ctx.send(f"Failed to reload cog `{arg1}`: {e}")

async def setup(bot):
    await bot.add_cog(cogmgr(bot))
