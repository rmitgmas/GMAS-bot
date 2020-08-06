import discord
from discord.ext import commands, tasks

class roles(commands.Cog, name="Roles"):
    
    def __init__(self, bot):
        self.bot=bot

    @commands.command(aliases=["addrole", "ar", "r"])
    async def role(self, ctx, *, role: discord.Role = None):

        guild_roles = ctx.guild.roles
        i = guild_roles.index(ctx.guild.me.top_role)
        assignable_roles = [gr for gr in guild_roles[:i] if gr.managed is False \
            and gr.name != "@everyone"\
            and gr.name != "bots"\
            and gr.name != "Alumni"\
            and gr.name != "Hackers"]
        
        if role is None:
            assignable_roles_str = f"`{'`, `'.join([ar.name for ar in assignable_roles])}`"
            await ctx.send(f"Specify which role you want to add.\n**Here's a list of the available roles:**\n{assignable_roles_str}")
            return

        user = ctx.message.author
        try:
            if role in assignable_roles:
                await user.add_roles(role)
                await ctx.message.add_reaction('✅')
            else:
                raise Exception("Role not assignable")
        except Exception as e:
            print("Couldn't add role.\n" + e)
            await ctx.message.add_reaction('❌')

    @commands.command(aliases=["removerole", "rr"])
    async def removeRole(self, ctx, *, role: discord.Role = None):
        user = ctx.message.author

        if role is None:
            roles_str = [r.name for r in user.roles if r.name != "@everyone"]
            roles_str = f"`{'`, `'.join(roles_str)}`"
            # could only show the roles the bot can delete, but that's extra work I'm ot willing to do atm :)
            await ctx.send(f"Specify the role you want to remove.\n**Your roles:**\n{roles_str}")
            return 

        if role in user.roles:
            try:
                await user.remove_roles(role)
            except Exception as e:
                print(e)
                await ctx.message.add_reaction('❌')
                return
            await ctx.message.add_reaction('✅')
        else:
            print("User doesn't have specified role")

def setup(bot):
    bot.add_cog(roles(bot))