import discord
from discord.ext import commands, tasks

class roles(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.command(aliases=["addrole", "ar", "r"])
    async def role(self, ctx, *, role: discord.Role):
        user = ctx.message.author
        try:
            await user.add_roles(role)
        except:
            await ctx.message.add_reaction('❌')
            return
        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["removerole", "rr"])
    async def removeRole(self, ctx, *, role: discord.Role):
        user = ctx.message.author
        if role in user.roles:
            try:
                await user.remove_roles(role)
            except Exception as e:
                print(e)
                await ctx.message.add_reaction('❌')
                return
            await ctx.message.add_reaction('✅')
        else:
            print("no role")

def setup(bot):
    bot.add_cog(roles(bot))