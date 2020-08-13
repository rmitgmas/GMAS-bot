import discord
import random
import json
from discord.ext import commands, tasks

class mainCommands(commands.Cog, name="Main"):
    def __init__(self, bot):
        self.bot=bot
        
    # #Help Command
    # @commands.command()
    # async def help(self, ctx):
    #     embed = discord.Embed(title ="GMAS bot command list", description="Here are my commands!")
    #     embed.add_field(name="sample command", value="sample text")
    #     await ctx.send(content= None, embed = embed)

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

    #Repeat whatever
    @commands.command(aliases=['d'])
    @commands.is_owner()
    async def delete(self, ctx, *msg_ids):
        for msg_id in msg_ids:
            m = await ctx.channel.fetch_message(msg_id)
            if m:
                await m.delete()
        await ctx.message.delete()

    #Repeat whatever AND delete
    @commands.command()
    @commands.guild_only()
    async def sayd(self, ctx, *, message):
        await ctx.message.delete(delay=None)
        await ctx.send(message)

    #Kill bot
    @commands.command(hidden=True)
    async def kill(self, ctx):
        if 733212159940624446 in [r.id for r in ctx.author.roles]:
            await ctx.send("Terminating...")
            try:
                await self.bot.logout()
            except:
                print("EnvironmentError")
                self.bot.clear()
        else:
            await ctx.send("You cannot kill me, I am Omega. You cannot kill me, I am SUBHUMAN!")

def setup(bot):
    bot.add_cog(mainCommands(bot))