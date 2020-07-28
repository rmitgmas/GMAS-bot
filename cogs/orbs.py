import discord
import random
import json
from discord.ext import commands, tasks
import backgroundTasks

class orbs(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    #Get user profile
    @commands.command()
    async def profile(self, ctx):
        with open("users.json", "r") as f:
            users = json.load(f)

        await backgroundTasks.update_data(users, ctx.author)

        numberOfRedOrbs = backgroundTasks.get_red_orbs(users, ctx.message.author)
        name = str(ctx.message.author)
        embed = discord.Embed(title=name +'s profile')
        embed.add_field(name="Number of Red Orbs", value=str(numberOfRedOrbs) + "<:redorb:729815039329959947>")
            
        await ctx.send(content= None, embed = embed)

    #Add orbs
    @commands.command(aliases=['ro', 'redorb'])
    async def redOrb(self, ctx):
        with open("users.json", "r") as f:
            users = json.load(f)

        await backgroundTasks.update_data(users, ctx.message.author)

        numberOfRedOrbs = backgroundTasks.randint(500,1000)
        added = await backgroundTasks.add_red_orbs(users, ctx.message.author, numberOfRedOrbs)
        if added is True:
            await ctx.send("You have gained {} red orbs <:redorb:729815039329959947>.".format(numberOfRedOrbs))
        else:
            await ctx.send("Can't get your orbs yet! Your next orbs will be ready in **{}**.".format(added))

        with open("users.json", "w") as f:
            json.dump(users, f, indent = 4)


    @commands.command(aliases=['lb', 'board', 'ladder', 'ranking'])
    async def leaderboard(self, ctx):
        with open("users.json", "r") as f:
            users = json.load(f)

        def myfunc(n):
            return n[1]["red orbs"]

        sorted_users = sorted(users.items(), key=myfunc, reverse=True)

        best_player = self.bot.get_user(int(sorted_users[0][0]))
        embed = discord.Embed(title=f"{ctx.guild.name} Red Orb leaderboard")
        
        if best_player is not None:
            embed.set_thumbnail(url=best_player.avatar_url)
        
        embed.description = ""
        
        for i, u in enumerate(sorted_users[0:10]):
            user_info = self.bot.get_user(int(u[0]))
            print(user_info)
            ro = u[1]["red orbs"]
            if user_info is not None:
                embed.description += f"**{i+1}. {user_info}** - **{ro}** <:redorb:729815039329959947>\n"
        
            if embed.description is "":
                embed.description = "No member with any Red Orbs..."
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(orbs(bot))