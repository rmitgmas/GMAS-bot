import string
from typing import List
import discord
from discord.ext import commands
import json

# TODO: command to add/remove unassignable roles
# TODO: differentiate unassignable and unremovable roles?
# TODO: save role message in memory (and in a json in case bot goes down) and always use this reference. 
# update it on message_edit() for that specific message id (that way we dont have to fetch for the role
# message on every update)
class roles(commands.Cog, name="Roles"): 

    def __init__(self, bot: discord.Client):
        self.bot=bot
        self.role_categories: dict = self.get_roles_categories()
        self.roles = self.get_roles()
        self.channel_id = self.get_roles_channel()

        
    def log(self, message: string):
        print("Uncomment if we want to log roles activity")
        # with open("logs/roleActivity.txt", "a+", encoding="utf-8") as f:
        #     time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #     f.write(f"[{time}] {message}\n")
        # print(f"{message}")

    def is_mod(self):
        async def predicate(ctx):
            mod_roles = ['Prez', 'Committee', 'Mods', 'Mod Helpers']
            any(role.name in mod_roles for role in ctx.author.roles)
        return commands.check(predicate)

    def get_roles_channel(self):
        """ 
        Return the ID of the channel where roles are posted
        """
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['rolesChannelId']
    
    def update_roles_channel(self, channel_id: int = None):
        if channel_id is not None and type(channel_id) == int:
            with open('config.json', 'r+', encoding='utf-8') as f:
                content = json.load(f)    
                content['rolesChannelId'] = channel_id
                f.seek(0)
                json.dump(content, f, indent=4, ensure_ascii=False)
                f.truncate()
            self.roles_channel_id = channel_id


    # move somehwere more global
    async def get_guild(self):
        """ 
        Return the ID of the guild
        """
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['guildId']

    async def get_roles_description(self):
        # Maybe automatically populated this file one day
        with open('roles/roles_description.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def get_unassignable_roles(self):
        """ 
        Returns the ID of the channel where roles are posted
        """
        with open('roles/roles_const.json', 'r', encoding='utf-8') as f:
            content = json.load(f)
            return content['unassignable_roles']

    def get_roles(self):
        """ 
        Returns the ID of the channel where roles are posted
        """
        with open('roles/roles_const.json', 'r', encoding='utf-8') as f:
            content = json.load(f)
            if 'role_emojis' in content:
                return content['role_emojis']
            else:
                return None 
    
    def get_roles_categories(self):
        """ 
        Returns roles categories object stored in the roles config .json file
        """
        with open('roles/roles_const.json', 'r', encoding='utf-8') as f:
            content = json.load(f)
            if 'roles_categories' in content:
                return content['roles_categories']
            else:
                return None 
    
    async def find_role_message(self, guild) -> discord.Message:
        """
        Finds the role message from the roles channel, and return the discord.Message instance of it
        """
        role_channel_id = self.get_roles_channel()
        if not role_channel_id:
            # not the role channel
            return None
        channel: discord.TextChannel = guild.get_channel(role_channel_id)

        def is_bot(message):
            return message.author.bot

        role_message = False
        async for message in channel.history(limit=200).filter(is_bot):
            if "React to give yourself a role:" in message.content and message.author.bot:
                # found the role message :D
                role_message = message
                break
            else:
                 return None
        
        if not role_message:
            print("Couldn't find role message")

        return role_message
    
    
    def update_assignable_roles(self, roles):
        if roles is not None:
            with open('roles/roles_const.json', 'r+', encoding='utf-8') as f:
                content = json.load(f)              
                content['role_emojis'] = roles
                f.seek(0)
                json.dump(content, f, indent=4, ensure_ascii=False)
                f.truncate()
            self.roles = roles

    def update_roles_categories(self, roles_categories):
        if roles_categories is not None:
            with open('roles/roles_const.json', 'r+', encoding='utf-8') as f:
                content = json.load(f)              
                content['roles_categories'] = roles_categories
                f.seek(0)
                json.dump(content, f, indent=4, ensure_ascii=False)
                f.truncate()
            self.role_categories = roles_categories

            
    async def get_role_from_reaction(self, guild, role_message, payload) -> discord.Role:
        # why from name and note from json file directly?
        roles = await self.get_roles_from_role_message(guild)
        try:
            role_name = roles[str(payload.emoji)]
        except KeyError:
            print("The reaction isn't a valid role/emoji pair")
            raise
        if not role_name:
            print("Emoji has no role attached")
            return None
        role: discord.Role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            print(f"Role `{role_name}` couldn't be found to be added/removed, check the name in roles_const.json")
        return role

    async def role_list(self, guild: discord.Guild):
        roles = guild.roles
        i = roles.index(guild.me.top_role)

        embed = discord.Embed(title="List of roles")
        display_roles = [r for r in roles[:i] if r.managed is False\
            and r.name != "@everyone"\
            and r.name != "bots"]

        for role in reversed(display_roles):
            if role.name in self.roles:
                print(f"{role.name}")
                role_description = self.roles[role.name]["description"]
                if self.roles[role.name]["assignable"]:
                    embed.add_field(name=role.name, value=role_description or "N/A", inline=True)
        return embed

    async def update_role_list_embed(self, guild):
        role_channel_id = self.get_roles_channel()
        channel: discord.TextChannel = guild.get_channel(role_channel_id)
        async for message in channel.history(limit=200):
            if message.embeds and message.embeds[0].title == "List of roles":
                msg = await channel.fetch_message(message.id)
        if not message:
            print(f"Couldn't find embed role list. update manually instead")
        new_embed = await self.role_list(guild)
        await msg.edit(embed=new_embed)

    async def set_role_message_reactions(self, channel: discord.TextChannel, category, clearReactions = False, message: discord.Message = None) -> discord.Message:
        role_emojis = self.roles
        _message = message
        if _message is None:
            _message: discord.Message = await channel.fetch_message(category["messageId"])
        
        emoji_list = []
        for role in category["roles"]:
            if role in role_emojis and role_emojis[role]["emoji"]:
                if role_emojis[role]["assignable"]:
                    try:
                        emoji_list.append(str(role_emojis[role]["emoji"]))
                        await _message.add_reaction(role_emojis[role]["emoji"])
                    except:
                        print(f"Couldnt add reaction for {role}")
                        continue
        if clearReactions:
            for reaction in _message.reactions:
                if str(reaction.emoji) not in emoji_list:
                    await _message.clear_reaction(str(reaction.emoji))
        # return the message to edit its content when possible
        return _message

    @commands.command(aliases=['src', 'setrolechannel',' setroleschannel'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_roles_channel(self, ctx: commands.Context, id = 0):
        """
        Sets the channel where the role message is posted and where roles can be self assigned from
        """
        channel_id = id or ctx.channel.id
        self.update_roles_channel(channel_id)
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['cl'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def list_categories(self, ctx: commands.Context):
        """
        Lists all the roles categories and the list of roles in each category
        """
        res = "**__Role Categories:__**\n─────────────────\n"
        for category in self.role_categories.items():
            temp = f"**`{category[0]}`: ** {', '.join(category[1]['roles'])}"
            res += f"{temp}\n"
        await ctx.channel.send(content=res)
        await ctx.message.delete()

    @commands.command(aliases=['rl'])
    async def list_roles(self, ctx: commands.Context):
        # To be redone/
        """
        Displays the list of roles with their description
        """
        embed = await self.role_list(guild=ctx.guild)
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()


    @commands.command(aliases=['setrolemessage', 'setrolemsg'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_role_message(self, ctx: commands.Context, *, args):
        """
        Sets the message use for role assignment for a specific category. **g!setrolemsg `<CATEGORY_NAME>`=`<MESSAGE_ID>`**
        """
        clear_old_message = False
        args_list: List[str] = args.split('=')
        if(len(args_list) < 2):
            await ctx.send("Please enter message ID for the role category, seperated by a `=`.\n**g!setrolemsg `<CATEGORY_NAME>`=`<MESSAGE_ID>`**")
            return

        temp = args_list[1].split(" ")
        if len(temp) > 1:
            if temp[1].lower() == "clear":
                clear_old_message = True

        channel: discord.TextChannel = ctx.guild.get_channel(self.roles_channel_id)

        category_name: string = args_list[0]
        message_id = temp[0]

        try:
            message_id = int(message_id)
        except:
            print("Message ID isn't a number")

        # checking if the message actually exists
        try:
            role_message = await channel.fetch_message(message_id) 
        except:
            print(f"Couldn't fetch message {message_id} in {channel.mention}")
            return

        if category_name in self.role_categories:

            old_message_id = self.role_categories[category_name]["messageId"]
            if old_message_id == message_id:
                return

            self.role_categories[category_name]["messageId"] = message_id
            category = self.role_categories[category_name]
            
            self.update_roles_categories(self.role_categories)
            # channel can be None because we provide the message directly, so channel wont be used
            await self.set_role_message_reactions(None, category, message=role_message, clearReactions=True)

            try:
                # problem here if they changed the channel id before running this command
                # other approach is to include the channel id as an argument of this command so they can run it
                # without changing the rolesChannelId before this seperately (running this will then update the 
                # rolesChannelId) for now we just wont cleanup the old message if it's in a different channel
                if clear_old_message:
                    old_message: discord.Message = await channel.fetch_message(old_message_id)
                    await old_message.clear_reactions()
            except Exception as e:
                print(e)
                print(f"Couldn't fetch old message {old_message_id} in {channel.mention} ({channel.name})")
                return
        else: 
            print(f"Can't find category {category_name} in roles categories")
            
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['setemoji'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def change_role_emoji(self, ctx: commands.Context, *, args):
        """
        Change the emoji used to assign a specific role. **g!setEmoji `<ROLE_NAME>`=`<EMOJI>`**
        """
        args_list = args.split('=')
        if(len(args_list) < 2):
            await ctx.send("Please enter an emoji for the role, seperated by a `=`.\n**g!setEmoji `<role name>`=`<role emoji>`**")
            return

        temp = args_list[1].split(" ")
        category = ""
        if len(temp) > 1:
            if temp[1].lower() in self.role_categories:
                category = temp[1].lower()

        role_name = args_list[0]
        emoji = args_list[1]
        if role_name in self.roles:
            old_emoji = self.roles[role_name]["emoji"]

            self.roles[role_name]["emoji"] = str(emoji)
            self.update_assignable_roles(self.roles)
           
            roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())
            category_name = self.roles[role_name]["category"]
            category = self.role_categories[category_name]
            print("here")

            m = await self.set_role_message_reactions(channel=roles_channel, category=category, clearReactions=True)

            # Updating message content
            try:
                await m.edit(content=m.content.replace(old_emoji, str(emoji)))
            except:
                print("can't edit someone else's message")
        else:
            self.roles[role_name] = {
                "emoji": emoji,
                "assignable": True,
                "category": category,
                "channels": [],
                "description": "League but everyone is OP so is balanced"
            }
            self.update_assignable_roles(self.roles)
            if category:
                print("here")
                self.role_categories[category]["roles"].append(role_name)
                self.update_roles_categories(self.role_categories)
                m = await self.set_role_message_reactions(channel=roles_channel, category=category, clearReactions=True)


        await ctx.message.add_reaction('✅')


    # TODO 1.Change emoji command => update .json and edit role message too. -- DONE (editing msg content partially)
    # 2. Add new Role => create command and update .json + msg 
    # 3. Delete role => same thing  -- 


    @commands.command(aliases=['setrolecategory'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_role_category(self, ctx: commands.Context, *, args):
        """
        Change the category of a certain role. **g!setEmoji `<ROLE_NAME>`=`<CATEGORY>`**
        """
        args_list = args.split('=')
        if(len(args_list) < 2):
            await ctx.send("Please enter an emoji for the role, seperated by a `=`.\n**g!setEmoji `<role name>`=`<role emoji>`**")
            return

        role_name = args_list[0]
        category = args_list[1]
        
        if role_name in self.roles:
            if category in self.role_categories:
                self.roles[role_name]["category"] = category
                self.role_categories[category]["roles"].append(role_name)
                self.update_assignable_roles(self.roles)
                self.update_roles_categories(self.role_categories)


    @commands.command(aliases=['activaterole'])
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_role_active(self, ctx: commands.Context, *, role):
        # To be redone
        """
        Sets a specific Role as assignable
        """
        
        if role not in self.roles:
            print(f"Role {role} couldn't be found")
            return

        roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())

        self.roles[role]["assignable"] = True
        category = self.roles[role]["category"]

        self.update_assignable_roles(self.roles)
        await self.set_role_message_reactions(roles_channel, self.role_categories[category], clearReactions=True)
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['deactivaterole'])
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_role_inactive(self, ctx: commands.Context, *, role):
        # To be redone
        """
        Sets a specific Role as unassignable
        """
        
        if role not in self.roles:
            print(f"Role {role} couldn't be found")
            return

        roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())

        self.roles[role]["assignable"] = False
        category = self.roles[role]["category"]

        self.update_assignable_roles(self.roles)
        await self.set_role_message_reactions(roles_channel, self.role_categories[category], clearReactions=True)
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['initroles', 'initroleassign'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_role_messages_reactions(self, ctx: commands.Context):
        """
        Sets all the reactions for all the role assignment messages
        """
        role_emojis = self.roles
        # not using ctx here because this might just become a funciton run on startup or reccuringly, so no ctx will be provided
        guildId = await self.get_guild()
        guild: discord.Guild = self.bot.get_guild(guildId)
        channel: discord.TextChannel = guild.get_channel(self.get_roles_channel())
        if not channel:
            print("not roles channel found")
            return

        for category in self.role_categories.items():
            key = category[0]
            category_obj = category[1]
            await self.set_role_message_reactions(channel, category_obj, clearReactions = True)

        await ctx.message.add_reaction('✅')

    #endregion Commands

    #region Listeners
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        roles = await self.get_roles_from_role_message(role.guild)
        with open("logs/roleActivity.txt", "a+", encoding="utf-8") as f:
                f.write(f"Role {role} create\n")
        print(roles)
        #TODO: edit the role message 


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        assignable_roles = self.roles
        roles_categories = self.role_categories

        if role.name in assignable_roles:
            roleEmoji = assignable_roles.pop(role.name)

            category = roleEmoji["category"]
            roles_categories[category]["roles"] = [r for r in roles_categories[category]["roles"] if r != role.name]
                    
            self.update_assignable_roles(assignable_roles)
            self.update_roles_categories(roles_categories)

            # TODO: Sync discord message using roleEmoji

        self.log(f"Role {role} deleted")
        # roles = await self.get_roles_from_role_message(role.guild)
     
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        # roles = await self.get_roles_from_role_message(before.guild)

        if before.name != after.name:
            assignable_roles = self.roles
            roles_categories = self.role_categories

            if before.name in assignable_roles:
                roleEmoji = assignable_roles.pop(before.name)
                if roleEmoji is not None:
                    assignable_roles[after.name] = roleEmoji

                    category = roleEmoji["category"]
                    roles_categories[category]["roles"] =  [r.replace(before.name, after.name) for r in roles_categories[category]["roles"]]
                    # message doesnt need to be edited as the role itself is mentionned (@Role) in the message, meaning it'll be updated automatically
                    self.update_assignable_roles(assignable_roles)
                    self.update_roles_categories(roles_categories)

                    # TODO: Sync discord message usiong roleEmojui

        print(before)
        print(after)

        # ====== LOGGIN ======
        changes = ""
        for s in before.__slots__:
            if s == "tags":
                continue
            prop_before = getattr(before,s)
            prop_after = getattr(after, s)
            if prop_before != prop_after:
                if s == "_colour":
                    prop_before = hex(int(prop_before)).replace("0x", "#")
                    prop_after = hex(int(prop_after)).replace("0x", "#")
                    
                changes += f"\n\t* {s}: {prop_before} -> {prop_after}"
                
        try:
            self.log(f"Role {before} updated: {after}{changes}")
        except Exception as e:
            self.log(f"Role {before}: something changed, but couldn't log. Error: {e}")
        
        #TODO: edit the role message? 

    async def get_roles_from_role_message(self, guild) -> dict:
        role_message = await self.find_role_message(guild)
        if not role_message:
            print("Can't get roles from role message")
            return

        roles = [r for r in role_message.content.split('\n') if ' :' in r]
        print(roles)
        # roles = list(roles)[2:]
        def split_text(role_message):
            m = role_message.rsplit(":", 1)
            m[0] = m[0].strip()
            m[1] = m[1].replace('`', '').strip()
            return m
        roles = map(split_text, roles)
        roles = dict(roles)
        # print(roles)
        return roles

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # payload member only available for add reaction
        if payload.member.bot or payload.guild_id is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member: discord.Member = guild.get_member(int(payload.user_id))
        if not member:
            print("Couldn't get member from reaction.")
        if member.bot:
            return
        # channel = guild.get_channel(payload.channel_id)
        role_emojis = self.roles

        # role_channel_id = await self.get_roles_channel()        

        for category in self.role_categories.values():
            if payload.message_id == category["messageId"]:
                role = next(filter(lambda x: (x[1]["emoji"] == str(payload.emoji)), role_emojis.items()), None)
                # print(role)
                if role and role[1]["assignable"]:
                    try:
                        r = discord.utils.get(guild.roles, name=role[0])
                        await member.add_roles(r)
                        # TODO move logging to seperate file
                        self.log(f"Added {str(role[0])} to user {str(member)}")
                    except:
                        print(f"Role {role[0]} not found in discord server.")

                else:
                    print("Role is unassignable")
   
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # payload member only available for add reaction
        
        if payload.guild_id is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member: discord.Member = guild.get_member(int(payload.user_id))
        if not member:
            print("Couldn't get member from reaction.")
        if member.bot:
            return
        # channel = guild.get_channel(payload.channel_id)
        role_emojis = self.roles

        # role_channel_id = await self.get_roles_channel()
        for category in self.role_categories.values():
            if payload.message_id == category["messageId"]:
                role = next(filter(lambda x: (x[1]["emoji"] == str(payload.emoji)), role_emojis.items()), None)
                # print(role)
                if role and role[1]["assignable"]:
                    try:
                        r = discord.utils.get(guild.roles, name=role[0])
                        await member.remove_roles(r)
                        # TODO move logging to seperate file
                        self.log(f"Removed {str(role[0])} from user {str(member)}")
                    except:
                        print(f"Role {role[0]} not found in discord server.")


def setup(bot):
    bot.add_cog(roles(bot))