import os
import requests
from dotenv import load_dotenv
import discord
import json
from discord.ext import commands

load_dotenv()

key = os.getenv("friisitetoken")

class friisite(commands.Cog):
    def __init__(self, bot):
        global bott
        bott = bot
        self.bot = bot
    global header
    header = { "X-API-Token": key }

    @commands.hybrid_command()
    async def registerdomain(self, ctx, arg1, arg2, arg3):
        if str(os.getenv("ownerid")) != str(ctx.author.id):
            return
        register = requests.post("https://beta.frii.site/api/domain", headers=header, data=json.dumps(
                               { "domain": arg1,
                                 "value": arg2,
                                 "type": arg3
                               }))
        if register.status_code == 200:
            await ctx.send("Domain registered successfully!")
        else:
            await ctx.send(f'An error has occurred: {register.status_code} {register.text}')

    @commands.hybrid_command()
    async def isdomainavailable(self, ctx, arg1):
        availability = requests.get(f"https://beta.frii.site/api/domain/available?name={arg1}")
        if availability.status_code == 200:
            await ctx.send(f"The domain {arg1}.frii.site is available!")
        elif availability.status_code == 409:
            await ctx.send(f"The domain {arg1}.frii.site is not available.")
        elif availability.status_code == 422:
            await ctx.send(f"Validation error: {availability.json()}")
        else:
            await ctx.send(f"An error has occured: {availability.status_code} {availability.text}")
    
    @commands.hybrid_command()
    async def deletedomain(self, ctx, arg1, arg2):
        if str(os.getenv("ownerid")) != str(ctx.author.id):
            return
        delete = requests.delete(f"https://beta.frii.site/api/domain?domain={arg1}", headers=header, data=json.dumps({"type": arg2}))
        if delete.status_code == 200:
            await ctx.send("Domain deleted successfully!")
        else:
            await ctx.send(f"An error has occurred while deleting the domain: {delete.status_code} {delete.text}")

    @commands.hybrid_command()
    async def modifydomain(self, ctx, arg1, arg2, arg3):
        if str(os.getenv("ownerid")) != str(ctx.author.id):
            return
        modify = requests.patch(f"https://beta.frii.site/api/domain?domain={arg1}&value={arg2}&type={arg3}", headers=header)
        if modify.status_code == 200:
            await ctx.send("Domain modified successfully!")
        else:
            await ctx.send(f"An error occurred during the modification of the domain: {modify.status_code} {modify.text}")

    @commands.hybrid_command()
    async def listdomains(self, ctx):
        if str(os.getenv("ownerid")) != str(ctx.author.id):
            return
        domains = requests.get("https://beta.frii.site/api/domains", headers=header)
        if domains.status_code == 200:
            with open("temp.json", "w") as f:
                f.write(json.dumps(domains.json(), sort_keys=True, indent=4))
            await ctx.send("DMing the domain list...\nIf you didn't recieve it, make sure to enable DMs.")
            user = await bott.fetch_user(str(ctx.author.id))
            await user.send(file=discord.File("./temp.json"))
            os.remove("temp.json")
        else:
            await ctx.send(f"An error has occurred: {domains.status_code} {domains.text}")

async def setup(bot):
    await bot.add_cog(friisite(bot))
