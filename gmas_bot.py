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

#Dealing With Cog Shit
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

@bot.event
async def on_message(message):

        channel = message.channel

        if message.author == client.user:
            return

        messageToRecord = message.content
        messageAuthor = message.author

        #outputFile = open(r"output.txt","a")
        #outputFile.write(str(message.content) + ": sent by: " + str(message.author) + "\n")

        log_str = ""
        log_str += f"\nGuild: **{message.guild.name}** *({message.guild.id})*"
        log_str += f"\nChannel: **{channel.name}** *({channel.id})*"
        log_str += f"\nUser: **{message.author}** *(Server name: **{message.author.nick}**)* - ID: {message.author.id}"
        log_str += f"\nMessage: {message.content}"
        if message.attachments and len(message.attachments):
            str_ = f"Files attached ({len(message.attachments)}): "
            filenames = ", ".join([f"{a.filename} ({round(a.size/1000, 2)}KB)" for a in message.attachments])
            str_ += f"{filenames}"
            log_str += f"[{str_}]"

        if not message.author.bot:
            print(log_str)

        if message.content == "Hello there":
            await channel.send("General Kenobi")

        if message.content == "Hi":
            await channel.send("Nice to meet you")

        with open("bad_words.txt") as file:
            bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

        for bad_word in bad_words:
            if message.content.lower().count(bad_word) > 0:
                embed = discord.Embed(title ="You said a bad word", description="I will put you in the naughty corner")
                await channel.send(content= None, embed = embed)
                await message.delete()

        await bot.process_commands(message)

bot.run(token)