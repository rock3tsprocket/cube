import discord
from discord.ext import commands

class bean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def bean(self, ctx, beaned: discord.User, arg2=None):
        embed = discord.Embed()
        embed.add_field(name=f"{beaned.display_name} was beaned!", value=f"{beaned.mention} was beaned by {ctx.author.mention}", inline=False)
        if arg2:
            embed.add_field(name="Reason", value=arg2)
        if beaned.display_name == ctx.author.display_name:
            await ctx.send("You can't bean yourself, silly.")
            return
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(bean(bot))
