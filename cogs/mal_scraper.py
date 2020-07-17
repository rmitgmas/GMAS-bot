import requests
from bs4 import BeautifulSoup
import sys
from discord.ext import commands, tasks
import discord

class mal_scraper(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command()
    async def anime(self, ctx, *, name):
        m = await ctx.send("On it...")
        ANIME_URL = "https://myanimelist.net/anime.php?q=" + name
        result = requests.get(ANIME_URL)
        # print("Sending request to", DOFUS_PORTAL_URL)

        # print("Status code:", result.status_code)

        src = result.content


        soup = BeautifulSoup(src, "lxml")

        animes = []

        for tr in soup.find_all("tr"):
            if(tr.find("strong") is not None and len(animes) < 5):
                animes.append([tr.find("strong").contents[0], tr.find('a')['href']])
        embed = discord.Embed(title='Search results for **{}**'.format(name))

        list_text = ''


        for i in range(len(animes)):
            list_text += "{}. {}\n".format(i+1, animes[i][0])

        embed.description = list_text
        embed.set_thumbnail(url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")

        def check(m):
            return m.author == ctx.message.author and  ctx.message.channel == m.channel

        await m.delete()
        await ctx.send(embed=embed)
        await ctx.send("**Choose an entry from the list (1 to 5)**")
        reply = await self.bot.wait_for("message", check=check)
        try:
            int(reply.content)
            if int(reply.content) > 0:
                await ctx.send(animes[int(reply.content)-1][1])
        except:
             await ctx.send("This ain't a number")
             
        

        return animes


def setup(bot):
    bot.add_cog(mal_scraper(bot))
# return list in embed
# listen for message (number in the list)
# embed details about said anime + link
