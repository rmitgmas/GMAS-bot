import discord
from discord.ext import commands
from datetime import datetime, timedelta
import pytz

class sandbox(commands.Cog, name="Sandbox"):
    """Do stuff with red orbs, the currency/points of the server"""
    def __init__(self, bot):
        self.bot=bot
        self.ramen_msg_time = {}
    
    @commands.command(aliases=['jeffonlyfans'])
    async def jeff_onlyfans(self, ctx: commands.Context):
        await ctx.message.delete()
        await ctx.channel.send('https://cdn.discordapp.com/attachments/527487652979802132/748879614046109766/SmartSelect_20200828-205239_Discord.jpg')

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return
        if "ramen" in msg.content.lower():
            if msg.channel.id not in self.ramen_msg_time:
                self.ramen_msg_time[msg.channel.id] = datetime.min
                
            if self.ramen_msg_time[msg.channel.id] < datetime.now(pytz.timezone('Australia/Melbourne')) - timedelta(minutes=2):
                m = await msg.channel.send('https://i.imgur.com/gOaXCNQ.png')
                self.ramen_msg_time[msg.channel.id] = m.created_at
            else:
                print("Ramen already in this chan in the last 2 minutes")

        if "mom" in msg.content.lower().split(' ') and msg.author.id == 180990269355851776:
            await msg.channel.send('I\'m sorry, did you mean mum?')

    @commands.command(aliases=['vcl'])
    async def voice_channel_list(self, ctx: commands.Context):
        channels = ctx.guild.voice_channels

        for c in channels:
            m_names = [r.name for r in c.members]
            print(f"{c.name} - {', '.join(m_names)}")

    @commands.is_owner()
    @commands.command()
    async def tts(self, ctx: commands.Context, *, msg):
        await ctx.message.delete()
        m = await ctx.channel.send(msg, tts=True)
        await m.delete()

    def audit_log(self, ctx):
        # Can we get onAuditLog event?
        print('not implemented')

def setup(bot):
    bot.add_cog(sandbox(bot))
