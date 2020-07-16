import random
import asyncio
from random import randint
import json
import os
import discord
import backgroundTasks
from discord.ext import commands, tasks
from discord import Game
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from discord.voice_client import VoiceClient
from backgroundTasks import *

client = discord.Client()
token = open(r"token.txt", "r").read()

bot = commands.Bot(command_prefix="g!")
bot.remove_command("help")

@bot.event
async def on_ready():
    print("My body is ready!")
    game = discord.Game("Moderating GMAS")
    await bot.change_presence(status = discord.Status.online, activity=game)

@bot.event
async def on_member_join(member):
    with open("users.json", "r") as f:
        users = json.load(f)

    await update_data(users, member)

    with open("users.json", "w") as f:
        json.dump(users, f)

@bot.event
async def on_message(message):

    channel = message.channel

    if message.author == client.user:
        return

    messageToRecord = message.content
    messageAuthor = message.author

    #outputFile = open(r"output.txt","a")
    #outputFile.write(str(message.content) + ": sent by: " + str(message.author) + "\n")

    print(message.content)
    print(message.author)

    if message.content == "Hello there":
        await channel.send("General Kenobi")

    if message.content == "Hi":
        await channel.send("Nice to meet you")

    with open("bad_words.txt") as file:
        bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

    for bad_word in bad_words:
        if message.content.count(bad_word) > 0:
            embed = discord.Embed(title ="You said a bad word", description="I will put you in the naughty corner")
            await channel.send(content= None, embed = embed)

    await bot.process_commands(message)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title ="GMAS bot command list", description="Here are my commands!")
    embed.add_field(name="sample command", value="sample text")
    await ctx.send(content= None, embed = embed)

@bot.command()
async def profile(ctx):
        with open("users.json", "r") as f:
            users = json.load(f)
        await update_data(users, ctx.author)
        numberOfRedOrbs = get_red_orbs(users, ctx.message.author)
        name = str(ctx.message.author)
        embed = discord.Embed(title=name +'s profile')
        embed.add_field(name="Number of Red Orbs", value=str(numberOfRedOrbs) + "<:redorb:729815039329959947>")
        await ctx.send(content= None, embed = embed)

@bot.command()
async def ping(ctx):
    ping = round(bot.latency * 1000)
    await ctx.send(str(ping) + "ms")

@bot.command()
async def test(ctx, msg):
    print(str(msg))
    await ctx.send(str(msg))

@bot.command()
async def redOrb(ctx):
    with open("users.json", "r") as f:
        users = json.load(f)

    await update_data(users, ctx.message.author)
    numberOfRedOrbs = randint(500,1000)
    await add_red_orbs(users, ctx.message.author, numberOfRedOrbs)
    await ctx.send("You have gained {} red orbs".format(numberOfRedOrbs))

    with open("users.json", "w") as f:
        json.dump(users, f)

@bot.command()
async def kill(ctx):
    if ctx.message.author.id == 253253450765172747:
        await ctx.send("Terminating...")
        exit()
    else:
        await ctx.send("You cannot kill me, I am Omega. You cannot kill me, I am SUBHUMAN!")

class Main_Commands():
    def __init__(self, bot):
        self.bot = bot


bot.run(token)

