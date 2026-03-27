import markovify
from random import randint
from json import loads, dumps
from discord.ext import commands

class markov(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        f = open("settings.json", "r")
        self.prefix = loads(f.read())["prefix"]
        f.close()

    @commands.hybrid_command()
    async def talk(self, ctx):
        """ Prepare the corpus """
        with open("memory.json", "r") as f:
            memorylist = loads(f.read())
        
        corpus = ""
        randnumlist = []
        for i in memorylist:
            corpus+=f"{i}\n"

        """ Build the model """
        model = markovify.NewlineText(corpus)

        """ Talk """
        sentence = model.make_sentence(tries=100)
        if not sentence:
            sentence = "Not enough messages in memory to generate a unique sentence."
        await ctx.send(sentence)

    @commands.Cog.listener(name="on_message")
    async def markov_on_message(self, message):
        if message.author.bot:
            return
        if message.content.startswith(self.prefix):
            return

        # Reading file
        with open("memory.json", "r") as f:
            memory = loads(f.read())
            memory.append(message.content)

        with open("memory.json", "w") as f:
            f.write(dumps(memory, sort_keys=True, indent=4))

async def setup(bot):
    try:
        open("memory.json", "x")
        with open("memory.json", "w") as f:
            f.write("""[\n]""")
    except FileExistsError:
        pass
    await bot.add_cog(markov(bot))
