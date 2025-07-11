import time
import random
from discord.ext import commands

class coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def coinflip(self, ctx):
        randomint = random.randrange(1, 100)
        if randomint > 50:
            await ctx.send("heads")
        else:
            await ctx.send("tails")

async def setup(bot):
    await bot.add_cog(coinflip(bot))
