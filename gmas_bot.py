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
import backgroundTasks

client = discord.Client()
token = open(r"token.txt", "r").read()

bot = commands.Bot(command_prefix="g!")
# bot.remove_command("help")

@bot.event
async def on_ready():
    print("My body is ready!")
    activity = discord.Activity(name=f'anime', type=discord.ActivityType.watching)
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

    has_attchmt = message.attachments and len(message.attachments)
    log_str = f"""
    Guild: **{message.guild.name}** *({message.guild.id})*
    Channel: **{channel.name}** *({channel.id})*
    User: **{message.author}** *(Server name: **{message.author.display_name}**)* - ID: {message.author.id}
    Message: {message.content}"""

    if has_attchmt:
        filenames = ", ".join([f"{a.filename} - {a.url} ({round(a.size/1000, 2)}KB)" for a in message.attachments])
        attchmt_str = f"Files attached ({len(message.attachments)}): {filenames}"
        log_str += f"\n[{attchmt_str}]"
        
    if not message.author.bot:
        print(log_str)


    if message.content == "Hi":
        await channel.send("Nice to meet you")

    # with open("bad_words.txt") as file:
    #     bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

    # for bad_word in bad_words:
    #     if message.content.lower().count(bad_word) > 0:
    #         embed = discord.Embed(title ="You said a bad word", description="I will put you in the naughty corner")
    #         await channel.send(content= None, embed = embed)
    #         await message.delete()

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if ctx.command is None:
        print("Unknown command")
        return
    command_args_arr = [i for i in ctx.command.clean_params.keys()]
    command_args = f"`{'`, `'.join(command_args_arr)}`"
    # Maybe only print certain type of arguments? https://docs.python.org/3/library/inspect.html#inspect.Parameter
    # Or don't print them this way (use command.usage property/do per command error)
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing parameter {command_args} to use the command")
    else:
        with open("config.json") as f:
            config = json.load(f)
        bot_dev_role = ctx.guild.get_role(config['botDevId'])

        # await ctx.send(f"Something went wrong! Look into it {bot_dev_role.mention}")
        print(error)

bot.run(token)