import discord
import json
import pytz
from datetime import datetime
from discord.ext import commands

with open('config.json', 'r') as f:
    timezone = json.load(f)["Timezone"]

abbr = pytz.timezone(timezone).localize(datetime.now(), is_dst=None).tzname()
timeFormat = f'%I:%M %p, %d/%m/%y {abbr}'


class userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    ##Member Events
    #Member Join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        if serverConfig["logChannel"] is not None:
            channel = self.bot.get_channel(serverConfig["logChannel"])

            joininfo = discord.Embed(
                title = 'User Joined',
                description = serverConfig["welcome"].replace("username", f'{member.mention}'),
                colour = discord.Colour.green()
            )
        
            joininfo.set_thumbnail(url=member.avatar_url)
            joininfo.add_field(name ='Username:',value = member, inline=True)
            joininfo.add_field(name ='User ID:',value = member.id, inline=True)

            createTime = member.created_at.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(timezone))
            joininfo.add_field(name ='Created:',value = createTime.strftime(timeFormat), inline=False)

            joinTime = datetime.utcnow().replace(tzinfo=pytz.utc)
            joininfo.set_footer(text=joinTime.astimezone(pytz.timezone(timezone)).strftime(timeFormat))

            await channel.send(embed=joininfo)

            
    #Member Leave
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open('config.json', 'r') as f:
            serverConfig = json.load(f)

        if serverConfig["logChannel"] is not None:
            channel = self.bot.get_channel(serverConfig["logChannel"])
            
            leaveinfo = discord.Embed(
                title = 'User Left',
                description = serverConfig["leave"].replace("username", f'{member.mention}'),
                colour = discord.Colour.red()
            )

            leaveinfo.set_thumbnail(url=member.avatar_url)
            leaveinfo.add_field(name ='Username:',value = member, inline=True)
            leaveinfo.add_field(name ='User ID:',value = member.id, inline=True)

            joinTime = member.joined_at.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(timezone))
            leaveinfo.add_field(name ='Joined:',value = joinTime.strftime(timeFormat), inline=False)

            leaveTime = datetime.utcnow().replace(tzinfo=pytz.utc)
            leaveinfo.set_footer(text=leaveTime.astimezone(pytz.timezone(timezone)).strftime(timeFormat))

            await channel.send(embed=leaveinfo)


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


    @commands.command(aliases=['sw'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)   
    async def setwelcome(self, ctx, *, message):
        if message.count("username") == 1:
            with open('config.json', 'r') as f:
                serverConfig = json.load(f)

            serverConfig["welcome"] = message

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

    @commands.command(aliases=['info','user','ui','member','memberinfo','mi'])
    @commands.guild_only()
    async def userinfo(self, ctx, member : discord.Member):
        userinfo = discord.Embed(
            title = member.display_name,
            description = f'Info for {member}',
            colour = member.colour
        )
        if member.bot:
            userinfo.description+= ' (Bot Account)'

        if member == self.bot.user:
            userinfo.description+= f'\n - That\'s me!'

        if member == ctx.guild.owner:
            userinfo.description+= f'\n - Server Owner'

        userinfo.set_thumbnail(url=member.avatar_url)
        userinfo.add_field(name ='User ID:',value = member.id, inline=False)

        joinTime = member.joined_at.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(timezone))
        userinfo.add_field(name ='Joined:',value = joinTime.strftime(timeFormat), inline=True)

        createTime = member.created_at.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(timezone))
        userinfo.add_field(name ='Created:',value = createTime.strftime(timeFormat), inline=True)

        roles = ''
        if len(member.roles) > 1:
            for role in reversed(member.roles):
                if role == member.roles[1]:
                    roles += f'{role.name}'
                elif role.name != '@everyone':
                    roles += f'{role.name}, '  
        else:
            roles = 'None'  

        userinfo.add_field(name ='Roles:', value = roles, inline = False)
        userinfo.set_footer(text=f'Requested by {ctx.message.author}', icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=userinfo)

def setup(bot):
    bot.add_cog(userinfo(bot))