import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

ownerid = os.getenv("ownerid")

class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def load(self, ctx, cog_name: str = None):
        if str(ctx.author.id) != str(ownerid):
            await ctx.send("You do not have permission to use this command.")
            return
        if cog_name is None:
            await ctx.send("Please provide the cog name to load.")
            return
        try:
            await self.bot.load_extension(f"cogs.{cog_name}")
            await ctx.send(f"Loaded cog `{cog_name}` successfully.")
        except Exception as e:
            await ctx.send(f"Error loading cog `{cog_name}`: {e}")

    @commands.command()
    async def unload(self, ctx, cog_name: str = None):
        if str(ctx.author.id) != str(ownerid):
            await ctx.send("You do not have permission to use this command.")
            return
        if cog_name is None:
            await ctx.send("Please provide the cog name to unload.")
            return
        try:
            await self.bot.unload_extension(f"cogs.{cog_name}")
            await ctx.send(f"Unloaded cog `{cog_name}` successfully.")
        except Exception as e:
            await ctx.send(f"Error unloading cog `{cog_name}`: {e}")

    @commands.command()
    async def reload(self, ctx, cog_name: str = None):
        if str(ctx.author.id) != str(ownerid): #ownerid:
            await ctx.send("You do not have permission to use this command.")
            return
        if cog_name is None:
            await ctx.send("Please provide the cog name to reload.")
            return
        try:
            await self.bot.unload_extension(f"cogs.{cog_name}")
            await self.bot.load_extension(f"cogs.{cog_name}")
            await ctx.send(f"Reloaded cog `{cog_name}` successfully.")
        except Exception as e:
            await ctx.send(f"Error reloading cog `{cog_name}`: {e}")

    @commands.command()
    async def listcogs(self, ctx):
        """Lists all currently loaded cogs in an embed."""
        cogs = list(self.bot.cogs.keys())
        if not cogs:
            await ctx.send("No cogs are currently loaded.")
            return

        embed = discord.Embed(title="Loaded Cogs", description="Here is a list of all currently loaded cogs:", color=0x7B79FF)
        embed.add_field(name="Cogs", value="\n".join(cogs), inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CogManager(bot))
