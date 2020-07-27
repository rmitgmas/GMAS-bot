import discord
import random
import json
from datetime import datetime
from discord.ext import commands, tasks
import backgroundTasks

class generalChat(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    #Set general chat
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def setgeneral(self, ctx, arg : discord.TextChannel):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        serverConfig["general"] = arg.id

        with open('config.json', 'w') as f:
            json.dump(serverConfig, f, indent=4)

        await ctx.message.add_reaction('✅')

    #Remove set general chat
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def cleargeneral(self, ctx):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        serverConfig["general"] = None

        with open('config.json', 'w') as f:
            json.dump(serverConfig, f, indent=4)

        await ctx.message.add_reaction('✅')

    #Send a welcome message to general chat
    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)
            generalChannel = serverConfig["general"]
            rulesChannel = serverConfig["rules"]
            guild = self.bot.get_guild(serverConfig['guildId'])
            role = guild.get_role(serverConfig['welcomesquad'])


        if generalChannel is not None:
            with open("users.json", "r") as f:
                users = json.load(f)

            await backgroundTasks.update_data(users, member)

            with open("users.json", "w") as f:
                json.dump(users, f)

            channel = self.bot.get_channel(serverConfig["general"])

            with open('random.json', 'r') as f:
                randomised = json.load(f)
                emoji1 = random.choice(randomised["emote"])
                greeting = random.choice(randomised["greeting"]).replace("username", f'{member.mention}')

            if channel is not None:
                await channel.send(f"{greeting} {emoji1}\nWelcome to GMAS! Please be mindful of {self.bot.get_channel(rulesChannel).mention}, and enjoy your stay!\n{role.mention}")
            else:
                print("Couldn't find channel with ID {} for this server! \nTrying by name #general".format(serverConfig['general']))
                channels = self.bot.get_guild(serverConfig['guildId']).channels
                try:
                    chan = next(c for c in channels if c.name is "general")
                    await chan.send(f"{greeting} {emoji1}\nWelcome to GMAS! Please be mindful of {self.bot.get_channel(rulesChannel).mention}, and enjoy your stay!\n{role.mention}")
                except StopIteration:
                    print("No channel #general! \nNo greetings for {} :((".format(member.name))
                
            
def setup(bot):
    bot.add_cog(generalChat(bot))