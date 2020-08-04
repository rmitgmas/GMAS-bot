import discord
import json
import pytz
from datetime import datetime
from discord.ext import commands

with open('config.json', 'r') as f:
    timezone = json.load(f)["Timezone"]

abbr = pytz.timezone(timezone).localize(datetime.now(), is_dst=None).tzname()
timeFormat = f'%I:%M %p, %d/%m/%Y {abbr}'

class userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    # The action takes either 'leave' 'join' or 'command' depending where it's called from 
    def build_user_info_embed(self, member: discord.Member, action: str, ctx=None):        
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)
        
        if action is 'command':
            desc = f'Info for {member}'
            if member.bot:
                desc += ' (Bot Account)'
            if member == self.bot.user:
                desc += f'\n - That\'s me!'
            if member == self.bot.get_guild(serverConfig['guildId']).owner:
                desc += f'\n - Server Owner'

            footer = f'Requested by {ctx.message.author}'
            icon_url = ctx.message.author.avatar_url
            title = member.display_name
            colour = member.colour

        elif action is 'leave' or 'join':
            desc = serverConfig[action].replace("username", f'{member.mention}')
            footer = datetime.utcnow().replace(tzinfo=pytz.utc) 
            title = "User Left" if action is 'leave' else "User Joined" 
            colour = discord.Colour.red() if action is 'leave' else discord.Colour.green()
            
        embed = discord.Embed(
            title = title,
            description = desc,
            colour = colour
        )

        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name ='Username:',value = member, inline=True)
        embed.add_field(name ='User ID:',value = member.id, inline=True)

        joinTime = member.joined_at.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(timezone))
        embed.add_field(name ='Joined:',value = joinTime.strftime(timeFormat), inline=True)

        createTime = member.created_at.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(timezone))
        embed.add_field(name ='Created:',value = createTime.strftime(timeFormat), inline=True)

        if icon_url is not None:
            embed.set_footer(text=footer, icon_url=icon_url)
        else:
            embed.set_footer(text=footer)
        return embed


    ##Member Events
    #Member Join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        if serverConfig["logChannel"] is not None:
            channel = self.bot.get_channel(serverConfig["logChannel"])        
            embed = self.build_user_info_embed(member, 'join')
            await channel.send(embed=embed)
        else:
            print(f"User {member} joined")

            
    #Member Leave
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        if serverConfig["logChannel"] is not None:
            channel = self.bot.get_channel(serverConfig["logChannel"])
            embed = self.build_user_info_embed(member, 'leave')
            await channel.send(embed=embed)

        else:
            print(f"User {member} left")


    @commands.command(aliases=['info','user','ui','member','memberinfo','mi'])
    @commands.guild_only()
    async def userinfo(self, ctx, *, member : discord.Member=None):
        # No specific user provided, we check the msg sender's profile
        if member is None:
            member = ctx.author
        embed = self.build_user_info_embed(member, 'command', ctx)
        await ctx.send(embed=embed)

    # Handles the error for userinfo command, to handle when the parameter member is wrong (cf: https://stackoverflow.com/questions/49478189/discord-py-discord-notfound-exception)
    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'{error}')
            

    #Set channel for user log
    @commands.command(aliases=['sul'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def setuserlog(self, ctx, arg : discord.TextChannel):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        serverConfig["logChannel"] = arg.id

        with open('config.json', 'w') as f:
            json.dump(serverConfig, f, indent=4)

        await ctx.message.add_reaction('✅')


    #leave and join could be put in one function with "join" or "leave" as a param for the JSON, and call that function in the @commands 
    @commands.command(aliases=['sj'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def setjoin(self, ctx, *, message):
        if message.count("username") == 1:
            with open('config.json', 'r') as f:
                serverConfig = json.load(f)

            serverConfig["join"] = message

            with open('config.json', 'w') as f:
                json.dump(serverConfig, f, indent=4)

            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['sl'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def setleave(self, ctx, *, message):
        if message.count("username") == 1:
            with open('config.json', 'r') as f:
                serverConfig = json.load(f)

            serverConfig["leave"] = message

            with open('config.json', 'w') as f:
                json.dump(serverConfig, f, indent=4)

            await ctx.message.add_reaction('✅')

    #Clear channel for user log
    @commands.command(aliases=['cul'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def clearuserlog(self, ctx):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        serverConfig["logChannel"] = None

        with open('config.json', 'w') as f:
            json.dump(serverConfig, f, indent=4)

        await ctx.message.add_reaction('✅')

    

def setup(bot):
    bot.add_cog(userinfo(bot))