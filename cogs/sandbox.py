import discord
from discord.ext import commands

class sandbox(commands.Cog, name="Sandbox"):
    """Do stuff with red orbs, the currency/points of the server"""
    def __init__(self, bot):
        self.bot=bot
        self.last_ramen_user_id = None
        self.same_ramen_user_count = 0
    
    @commands.command(aliases=['jeffonlyfans'])
    async def jeff_onlyfans(self, ctx: commands.Context):
        await ctx.message.delete()
        await ctx.channel.send('https://cdn.discordapp.com/attachments/527487652979802132/748879614046109766/SmartSelect_20200828-205239_Discord.jpg')

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return
        if "ramen" in msg.content.lower():
            if self.last_ramen_user_id == msg.author.id:
                self.same_ramen_user_count += 1
            else:
                self.last_ramen_user_id = msg.author.id
            if self.same_ramen_user_count < 3:
                await msg.channel.send('https://i.imgur.com/gOaXCNQ.png')
            else:
                await msg.channel.send('Stop saying ramen you idiot!')
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
