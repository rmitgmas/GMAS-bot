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
    activity = discord.Activity(name=f'over GMAS', type=discord.ActivityType.watching)
    await bot.change_presence(status = discord.Status.online, activity=activity)


@bot.command()
async def kill(ctx):
    if ctx.message.author.id == 253253450765172747:
        await ctx.send("Terminating...")
        exit()
    else:
        await ctx.send("You cannot kill me, I am Omega. You cannot kill me, I am SUBHUMAN!")

##Dealing With Cog Shit
#Load Cog
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('✅')
    print(f'{extension} loaded')

#Unload Cog
@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('✅')
    print(f'{extension} unloaded')
    
#Reload Cog
@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('✅')
    print(f'{extension} reloaded')

#Preload Cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f'{filename} loaded')

bot.run(token)