import time
import random
from discord.ext import commands

class eightball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def eightball(self, ctx):
        randomint = random.randrange(1, 100)
        if randomint > 50:
            await ctx.send("yes")
        else:
            await ctx.send("no")

async def setup(bot):
    await bot.add_cog(eightball(bot))
