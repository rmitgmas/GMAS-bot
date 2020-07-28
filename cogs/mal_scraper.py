import requests
from bs4 import BeautifulSoup
import sys
from discord.ext import commands, tasks
import discord

class mal_scraper(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    """
    Optimally the whole scraping should be a background process for ALL animes (figure out how to do that)
    and saves the scraped info that we want (score, title, links, ...) in a DB, and
    use the DB to build the embed, search the anime by name etc... so the command 
    runs faster. This is fine for now given the scope of the bot
    """

    def build_embed_from_url(self, url: str):

        result = requests.get(url)
        src = result.content
        soup = BeautifulSoup(src, "lxml")

        jp_title = soup.find("span", attrs={ "itemprop" : "name" }).contents[0]
        en_title = getattr(soup.find("span", attrs={ "class" : "title-english" }), "text", None)         
        title = en_title or jp_title

        description = soup.find("span", attrs={ "itemprop" : "description" }).text
        image = soup.find("img", attrs={ "alt" : "{}".format(jp_title)})['data-src']

        # Border element contains most of the info we need, saving this part of the
        # Html will save some time on the multiple find() calls below
        border = soup.find("td", attrs={ "class" : "borderClass", "valign" : "top" })
    
        def border_text_elem(text: str):
            return border.find("span", attrs={ "class" : "dark_text" }, text=text)

        studios_arr = ["[{}](https://myanimelist.net{})".format(a.text, a['href']) for a in border_text_elem("Studios:").parent.find_all("a")]
        studios = ", ".join(studios_arr)
        
        score = border_text_elem("Score:").find_next_sibling('span').contents[0]
        
        episodes = border_text_elem("Episodes:").parent.contents[2].strip()
        status = border_text_elem("Status:").parent.contents[2].strip()
        aired = border_text_elem("Aired:").parent.contents[2].strip()
        
        genres_arr = ["[{}](https://myanimelist.net{})".format(a.text, a['href']) for a in border_text_elem("Genres:").parent.find_all("a")]
        genres = ", ".join(genres_arr)
        
        embed = discord.Embed(title=title)
        embed.url = url
        embed.colour = 0x2f52a2
        embed.set_thumbnail(url=image)
        embed.add_field(name="Score", value=score, inline=False)
        embed.add_field(name="Episodes", value=episodes, inline=True)
        embed.add_field(name="Genres", value=genres, inline=True)
        embed.add_field(name="Studios", value=studios, inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        # "Premiered" just isn't there sometimes, gotta have some checks for it
        if border_text_elem("Premiered:"):
            premiered_link_elem = border_text_elem("Premiered:").find_next_sibling('a')
            premiered = "[{}]({})".format(premiered_link_elem.text, premiered_link_elem['href'])
            embed.add_field(name="Premiered", value=premiered, inline=True)
        embed.add_field(name="Aired", value=aired, inline=True)

        embed.description = description

        return embed

    @commands.command()
    async def anime(self, ctx, *, name):

        if not name:
            await ctx.send("No anime name provided")
            return False

        m = await ctx.send("Working on it...")
        ANIME_URL = "https://myanimelist.net/anime.php?q=" + name
        result = requests.get(ANIME_URL)
        # print("Sending request to", ANIME_URL)
        # print("Status code:", result.status_code)

        if result.status_code != 200:
            embed = discord.Embed(title="Error")
            embed.description = "Can't get a response from **MyAnimeList** (Status Code {}). The site might be under maintenance. \nTry again later or check with a @Hackers.".format(result.status_code)
            embed.colour = 0xcc0000
            await ctx.send(embed=embed)
            return

        src = result.content
        soup = BeautifulSoup(src, "lxml")

        animes = []

        for tr in soup.find_all("tr"):
            if(tr.find("strong") is not None and len(animes) < 5):
                animes.append([tr.find("strong").contents[0], tr.find('a')['href']])
        embed = discord.Embed(title='Search results for **{}**'.format(name))
        embed.colour = 0x2f52a2

        list_text = ''
        for i in range(len(animes)):
            list_text += "{}. {}\n".format(i+1, animes[i][0])

        embed.description = list_text
        embed.description += "\n**Choose an entry from the list (1 to 5)**"
        embed.set_thumbnail(url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")

        def check(m):
            return m.author == ctx.message.author and  ctx.message.channel == m.channel

        await ctx.send(embed=embed)
        await m.delete()
        reply = await self.bot.wait_for("message", check=check)
        try:
            int(reply.content)
            if int(reply.content) > 0:
                m1 = await ctx.send("Getting anime details...")
                await ctx.send(embed=self.build_embed_from_url(animes[int(reply.content)-1][1]))
                await m1.delete()
        except ValueError:
             await ctx.send("This ain't a number")
             
        return animes

  
def setup(bot):
    bot.add_cog(mal_scraper(bot))

