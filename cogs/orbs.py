import discord
import random
import json
from discord.ext import commands, tasks
from backgroundTasks import *

class orbs(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    #Get user profile
    @commands.command()
    async def profile(self, ctx):
        with open("users.json", "r") as f:
            users = json.load(f)

        await update_data(users, ctx.author)

        numberOfRedOrbs = get_red_orbs(users, ctx.message.author)
        name = str(ctx.message.author)
        embed = discord.Embed(title=name +'s profile')
        embed.add_field(name="Number of Red Orbs", value=str(numberOfRedOrbs) + "<:redorb:729815039329959947>")
            
        await ctx.send(content= None, embed = embed)

    #Add orbs
    @commands.command()
    async def redOrb(self, ctx):
        with open("users.json", "r") as f:
            users = json.load(f)

        await update_data(users, ctx.message.author)

        numberOfRedOrbs = randint(500,1000)
        await add_red_orbs(users, ctx.message.author, numberOfRedOrbs)
        await ctx.send("You have gained {} red orbs".format(numberOfRedOrbs))

        with open("users.json", "w") as f:
            json.dump(users, f, indent = 4)


def setup(bot):
    bot.add_cog(orbs(bot))