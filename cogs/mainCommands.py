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
    # use mention_everyone and mentions instead
        if "@" in message:
            await ctx.send("I won't say it...")
            if "@everyone" in message:
                await ctx.author.edit(nick=f"{ctx.author.nick[:9]} [TRIED TO @everyone]😂", reason="[TRIED TO PING EVERYONE] 😂")
        else:
            await ctx.send(message)

    #Repeat whatever AND delete
    @commands.command()
    @commands.guild_only()
    async def sayd(self, ctx, *, message):
        # use mention_everyone and mentions instead
        await ctx.message.delete(delay=None)
        if "@" in message:
            await ctx.send("I won't say it...")
            if "@everyone" in message:
                await ctx.author.edit(nick=f"{ctx.author.nick[:9]} [TRIED TO @everyone]😂", reason="[TRIED TO PING EVERYONE] 😂")
        else:
            await ctx.send(message)

    @commands.command(aliases=['d'])
    @commands.is_owner()
    async def delete(self, ctx, *msg_ids):
        for msg_id in msg_ids:
            m = await ctx.channel.fetch_message(msg_id)
            if m:
                await m.delete()
        await ctx.message.delete()

    @commands.command(aliases=['w'])
    @commands.is_owner()
    async def write(self, ctx, *, msg):
        
        msg_arr = msg.split(' ')
        print(msg_arr[0])

        if msg_arr[0].isdigit():
            channel = ctx.guild.get_channel(int(msg_arr[0]))
            if channel is None:
                channel = ctx.channel
            else:
                msg_arr.pop(0)
        else:
            channel = ctx.channel
        msg = ' '.join(msg_arr)
        
        if not msg:
            await ctx.channel.send('No message included')
            return 

        await channel.send(msg)
        await ctx.message.delete()

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