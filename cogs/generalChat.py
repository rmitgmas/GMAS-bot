import discord
import random
import json
from datetime import datetime
from discord.ext import commands, tasks
import backgroundTasks

class generalChat(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    #Set welcome chat
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def setwelcome(self, ctx, arg : discord.TextChannel):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        serverConfig["welcome"] = arg.id

        with open('config.json', 'w') as f:
            json.dump(serverConfig, f, indent=4)

        await ctx.message.add_reaction('✅')

    #Remove set welcome chat
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def clearwelcome(self, ctx):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        serverConfig["welcome"] = None

        with open('config.json', 'w') as f:
            json.dump(serverConfig, f, indent=4)

        await ctx.message.add_reaction('✅')

    #Send a welcome message to general chat
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
       
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)
            generalChannel = serverConfig["welcome"]
            rulesChannelId = serverConfig["rules"]
            rolesChannelId = serverConfig["rolesChannelId"]
            # member.guild might just work actually
            guild: discord.Guild = self.bot.get_guild(serverConfig['guildId'])
            welcome_role = guild.get_role(serverConfig['welcomesquad'])
        if generalChannel is not None:
            with open("users.json", "r") as f:
                users = json.load(f)

            await backgroundTasks.update_data(users, member)

            with open("users.json", "w") as f:
                json.dump(users, f)

            channel = guild.system_channel
            if channel is None:
                channel = self.bot.get_channel(serverConfig["welcome"])

            with open('random.json', 'r') as f:
                randomised = json.load(f)
                emoji1 = random.choice(randomised["emote"])
                greeting = random.choice(randomised["greeting"]).replace("username", f'{member.mention}')

            if channel is None:
                print("Couldn't find channel with ID {} for this server! \nTrying by name #general".format(serverConfig['general']))
                channels = self.bot.get_guild(serverConfig['guildId']).channels
                try:
                    channel = next(c for c in channels if c.name is "welcome")
                except StopIteration:
                    print("No channel #welcome! \nNo greetings for {} :((".format(member.name))
                # could also take the guild id as the channel id, since the default channel of a guild has the same id as the guild
                if channel is None:
                    print("Couldn't find welcome channel")
                    return

            rolesChannel = self.bot.get_channel(rolesChannelId)
            rulesChannel = self.bot.get_channel(rulesChannelId)
            
            if member.bot:
                await channel.send(f"A new bot has joined the server! 🤖 Welcome {member.mention} 🤖")
            else:
                await channel.send(f"{greeting} {emoji1}\nWelcome to GMAS! Please be mindful of {rulesChannel.mention or 'the server rules'} and {rolesChannel.mention or 'the roles channel'}, and enjoy your stay!\n{welcome_role.mention}")
              
            
def setup(bot):
    bot.add_cog(generalChat(bot))