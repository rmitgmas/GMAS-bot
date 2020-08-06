import discord
import json
from discord.ext import commands, tasks
from typing import Union
import requests
import os

class league(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.group()    
    async def league(self, ctx):
        if ctx.invoked_subcommand is None:
            print('Invalid git command passed...')

    # Getting a username
    @league.command(aliases=['username', 'summonername', 'n'])
    async def name(self, ctx, *, member : discord.Member=None):
        if member is None:
            member = ctx.author

        id_key = str(member.id)

        with open("league.json", 'r', encoding='utf-8') as f:
            league_users = json.load(f)

        if id_key not in league_users:
            await ctx.send("You didn't set your username.\nUse `g!league setname <username>` to set your league username")
        else:
            await ctx.send(f"`{league_users[id_key]['name']}`")

    @name.error
    async def name_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'{error}')


    # Setting username
    @league.command(aliases=['setusername', 'setsummonername', 'sn'])
    async def setname(self, ctx, *, name):

        id_key = str(ctx.author.id)

        with open("league.json", 'r+') as f:
            league_users = json.load(f)

        if id_key not in league_users:
            league_users[id_key] = {}
        
        league_users[id_key]['name'] = name

        print(league_users)
        try:
            with open("league.json", "w") as f:
                json.dump(league_users, f, indent = 4)

            await ctx.send(f"Username set to: `{name}`")
        except:
            ctx.message.add_reaction('❌')

    @league.command(aliases=['serverusernames', 'serversummonernames', 'servn', 'servnames'])
    async def servernames(self, ctx):
        with open("league.json", 'r', encoding='utf-8') as f:
            league_users = json.load(f)
        
        embed = discord.Embed(title=f"{ctx.guild.name} list of League of Legends usernames")
        embed.description = "*(Server name  -  League username)*\n\n"

        # Only keep ones with name
        league_usernames = [lu for lu in league_users if league_users[lu]['name']]
        
        if not len(league_usernames):
            embed.description += "*No username set for this server*"
        else:
            for u in league_usernames:
                guild_name = ctx.guild.get_member(int(u)).display_name
                print(guild_name)
                league_name = league_users[u]['name']
                print(league_name)
                embed.description += f"**{guild_name}** - **{league_name}**\n"

        embed.set_thumbnail(url="https://i.imgur.com/vgERB5I.png")

        embed.set_footer(text=f"Showing {len(league_users)} users")

        await ctx.send(embed=embed)


    # streamline it, separate in smaller functions, save some league variables, 
    # generalize the checks for when member argument, no member argument, id exists or not in json file
    @league.command()
    async def profile(self, ctx, *, member: Union[discord.Member, str] = None):
        if member is None:
            member = ctx.author

        # either have a check for if the user ment to check for a string or make an alt function (g!sprofile)
        # this is because, if the guild has a member with the same username, it'll consider the member arg to
        # be an actual discord.Member. So we need a way to search a league username directly, even if it exists in the guild
        name = ""
        if isinstance(member, discord.Member):
            with open("league.json", 'r', encoding='utf-8') as f:
                league_users = json.load(f)
            id_key = str(member.id)
            if id_key in league_users:
                name = league_users[id_key]["name"]
            else:
                await ctx.send("No league username set for this user")
                return
        else:
            name = member
           

        async with ctx.typing():
            os.environ['RIOT_API_KEY'] = "Your API key here"
            headers = {"X-Riot-Token": os.environ.get('RIOT_API_KEY')}
            
            # Summoner
            url = f"https://oc1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}"
            r = requests.get(url, headers=headers)
            ud = r.json()
            # League
            url = f"https://oc1.api.riotgames.com/lol/league/v4/entries/by-summoner/{ud['id']}"
            r = requests.get(url, headers=headers)
            league = r.json()

            if r.status_code == 404:
                ctx.send(f"Username **{name}** doesn't seem to exist. Make sure you spelt it right and that it's an OCE account.")
                return

            if r.status_code == 403:
                ctx.send(f"Regenerate the API key <!@102054983381311488>")
                return

            # Create embed
            embed = discord.Embed(title=f"{name}'s Profile | Level {ud['summonerLevel']}")

            embed.url = f"https://oce.op.gg/summoner/userName={name}"
            embed.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/10.15.1/img/profileicon/{ud['profileIconId']}.png")

            queueType = {
                "RANKED_SOLO_5x5": "Ranked Solo/Duo",
                "RANKED_FLEX_SR": "Ranked Flex"
            }

            for l in league:
                embed.add_field(name=queueType[l['queueType']], value=f"{l['tier'].capitalize()} {l['rank']} ({l['leaguePoints']} LP)")
            if not len(league):
                embed.description = "No ranks available for this user"

            await ctx.send(embed=embed)
            
            return


def setup(bot):
    bot.add_cog(league(bot))