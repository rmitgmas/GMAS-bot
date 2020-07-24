import random
import json
import asyncio
from random import randint
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from datetime import datetime, timedelta

client = discord.Client()

# maybe only call this internally, and use it to update the json file ot avoid messign with the json in the command function (also makes it easier to set keys that don't exist on a user e.g: last_claimed)
async def update_data(users, user):
    if not str(user.id) in users:
        users[str(user.id)] = {}
        users[str(user.id)]["red orbs"] = 0
        users[str(user.id)]["level"] = 1
        users[str(user.id)]["last_claimed"] = getattr(users[str(user.id)], "last_claimed", str(datetime.now() - timedelta(days=1, minutes=1)))

async def add_red_orbs(users, user, red_orbs):

    # How many hours between redOrbs claims (save it in server config to make it changeable via a command?)
    COOLDOWN = 24
    now = datetime.now()

    try:
        users[str(user.id)]["last_claimed"]
    except KeyError:
        users[str(user.id)]["last_claimed"] = str(datetime.now() - timedelta(days=1, minutes=1))

    lc = datetime.strptime(users[str(user.id)]["last_claimed"], "%Y-%m-%d %H:%M:%S.%f")

    # Last claim was more than COOLDOWN hours ago, we proceed to add orbs and update the last_claimed value for the user
    if (now - lc) > timedelta(hours=COOLDOWN):  
        users[str(user.id)]["red orbs"] += red_orbs
        users[str(user.id)]["last_claimed"] = str(now)
        return True
    # Format the time difference string to be a bit more readable and return it to be printed to the channel
    else:
        diff = str((lc + timedelta(hours=COOLDOWN)) - now)
        diff_str = diff[:-10].replace(':', 'h ', 1) + 'min'
        print("User already claimed in the last 24h! Next claim in {}".format(diff_str))
        return diff_str

def get_red_orbs(users, user):
    if str(user.id) in users:
        return users[str(user.id)]["red orbs"]
    return 0

#<:redorb:729815039329959947>
#<:dab:592239094738714634>
#<:gasm:592239515289124874>
#<:stonks:722680072674345021>
#<:ayaya:592239431365165056>
#<:sip:669755445568733195>
#<:uwu:720136859270774834>
#<:woke:718749924010885133>