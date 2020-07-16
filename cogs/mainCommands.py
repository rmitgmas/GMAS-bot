import discord
import random
import json
from discord.ext import commands, tasks
from backgroundTasks import *

class mainCommands(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        
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

    @commands.command()
    async def redOrb(self, ctx):
        with open("users.json", "r") as f:
            users = json.load(f)

        await update_data(users, ctx.message.author)

        numberOfRedOrbs = randint(500,1000)
        await add_red_orbs(users, ctx.message.author, numberOfRedOrbs)
        await ctx.send("You have gained {} red orbs".format(numberOfRedOrbs))

        with open("users.json", "w") as f:
            json.dump(users, f)
        
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title ="GMAS bot command list", description="Here are my commands!")
        embed.add_field(name="sample command", value="sample text")
        await ctx.send(content= None, embed = embed)

    @commands.command()
    async def ping(self, ctx):
        ping = round(self.bot.latency * 1000)
        await ctx.send("pong " + str(ping) + "ms")

    ##Repeat whatever
    @commands.command()
    @commands.guild_only()
    async def say(self, ctx, *, message):
        await ctx.send(message)

    ##Repeat whatever AND delete
    @commands.command()
    @commands.guild_only()
    async def sayd(self, ctx, *, message):
        await ctx.message.delete(delay=None)
        await ctx.send(message)


def setup(bot):
    bot.add_cog(mainCommands(bot))