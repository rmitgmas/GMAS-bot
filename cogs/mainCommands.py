import discord
import random
import json
from discord.ext import commands, tasks

class mainCommands(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        
    #Help Command
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title ="GMAS bot command list", description="Here are my commands!")
        embed.add_field(name="sample command", value="sample text")
        await ctx.send(content= None, embed = embed)

    #Latency
    @commands.command()
    async def ping(self, ctx):
        ping = round(self.bot.latency * 1000)
        await ctx.send("pong " + str(ping) + "ms")

    #Repeat whatever
    @commands.command()
    @commands.guild_only()
    async def say(self, ctx, *, message):
        await ctx.send(message)

    #Repeat whatever AND delete
    @commands.command()
    @commands.guild_only()
    async def sayd(self, ctx, *, message):
        await ctx.message.delete(delay=None)
        await ctx.send(message)

    #Kill bot
    @commands.command()
    async def kill(self, ctx):
        if ctx.message.author.id == 253253450765172747:
            await ctx.send("Terminating...")
            exit()
        else:
            await ctx.send("You cannot kill me, I am Omega. You cannot kill me, I am SUBHUMAN!")

def setup(bot):
    bot.add_cog(mainCommands(bot))