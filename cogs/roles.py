from dataclasses import replace
import string
from typing import List
import discord
from discord.ext import commands
import json
from datetime import datetime
import psycopg2
import os
# TODO: command to add/remove unassignable roles
# TODO: differentiate unassignable and unremovable roles?
# TODO: save role message in memory (and in a json in case bot goes down) and always use this reference. 
# update it on message_edit() for that specific message id (that way we dont have to fetch for the role
# message on every update)
class roles(commands.Cog, name="Roles"): 

    
    def __init__(self, bot: discord.Client):
        self.host = os.getenv("HOST")
        self.database = os.getenv("DATABASE")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

        self.bot=bot
        self.role_categories: dict = self.get_roles_categories()
        # print(self.role_categories)
        self.roles = self.get_roles()
        # print(self.roles)
        self.roles_channel_id = self.get_roles_channel()

        
    def log(self, message: string):
        # print("Uncomment if we want to log roles activity")
        with open("logs/roleActivity.txt", "a+", encoding="utf-8") as f:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{time}] {message}\n")
        print(f"{message}")

    def is_mod():
        async def predicate(ctx):
            # Save this once to avoid fetching it everytime. only refetch if changes are made to role
            mod_role = discord.utils.get(ctx.guild.roles, name="Mods")
            has_role = ctx.author.top_role.position >= mod_role.position
            # print(f"{mod_role.position} - your Id: {ctx.author.top_role.position}")
            if has_role == False:
               await ctx.send(content="You do not have persmission to use this command")
            return has_role
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


    def get_roles(self):
        """ 
        Returns the ID of the channel where roles are posted
        """
        try:
            conn = psycopg2.connect(host=self.host,
            database=self.database,
            user=self.user,
            password=self.password)

            cur = conn.cursor()

            cur.execute('SELECT name, emoji, category, assignable, channels, description FROM roles')
            query = cur.fetchall()
            # print(query)
            res = {}
            for r in query:
                # print(r)
                res[r[0]] = {"name": r[0], "emoji": r[1], "category": r[2], "assignable": r[3], "channels": r[4], "description": r[5]}
            
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                res = None
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
            return res
        
        
        # with open('roles/roles_const.json', 'r', encoding='utf-8') as f:
        #     content = json.load(f)
        #     if 'role_emojis' in content:
        #         return content['role_emojis']
        #     else:
        #         return None 
    
    def get_roles_categories(self):
        """ 
        Returns roles categories object stored in the roles config .json file
        """
        try:
            conn = psycopg2.connect(host=self.host,
            database=self.database,
            user=self.user,
            password=self.password)

            cur = conn.cursor()

            cur.execute('SELECT name, roles, message_id FROM role_categories')
            query = cur.fetchall()
            res = {}
            for r in query:
                res[r[0]] = {"name": r[0], "roles": r[1], "message_id": r[2]}

        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                res = None
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
            return res
        # with open('roles/roles_const.json', 'r', encoding='utf-8') as f:
        #     content = json.load(f)
        #     if 'roles_categories' in content:
        #         return content['roles_categories']
        #     else:
        #         return None    
    
    def update_role(self, role):
        try:
            conn = psycopg2.connect(host=self.host,
            database=self.database,
            user=self.user,
            password=self.password)

            cur = conn.cursor()

            emoji = f"\'{role['emoji']}\'" or "NULL"
            category = f"\'{role['category']}\'" or "NULL"
            channels = f"\'{{{', '.join(str(r) for r in role['channels'])}}}\'" if role['channels'] else "NULL"
            assignable = f"\'{role['assignable']}\'"

            sgl_qt = '\''
            description = f"\'{role['description'].replace(sgl_qt, sgl_qt + sgl_qt)}\'" or "NULL"

            update_query=f"UPDATE roles SET emoji={emoji}, category={category}, channels={channels}, assignable={assignable}, description={description} WHERE name=\'{role['name']}\'"
            cur.execute(update_query)
            conn.commit()      
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def create_role(self, role):
        try:
            conn = psycopg2.connect(host=self.host,
            database=self.database,
            user=self.user,
            password=self.password)

            cur = conn.cursor()

            emoji = f"\'{role['emoji']}\'" or "NULL"
            category = f"\'{role['category']}\'" or "NULL"
            channels = f"\'{{{', '.join(str(r) for r in role['channels'])}}}\'" if role['channels'] else "NULL"
            assignable = f"\'{role['assignable']}\'"

            sgl_qt = '\''
            description = f"\'{role['description'].replace(sgl_qt, sgl_qt + sgl_qt)}\'" or "NULL"

            insert_query=f"INSERT INTO roles (name, emoji, category, channels, assignable, description) VALUE(\'{role['name']}\', {emoji}, {category}, {channels}, {assignable}, {description})"
            cur.execute(insert_query)
            conn.commit()      
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def delete_role(self, role):
        try:
            conn = psycopg2.connect(host=self.host,
            database=self.database,
            user=self.user,
            password=self.password)

            cur = conn.cursor()

            insert_query=f"DELETE FROM roles WHERE name = {role['name']}"
            cur.execute(insert_query)
            conn.commit()      
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    def update_category(self, category):
        try:
            conn = psycopg2.connect(host=self.host,
            database=self.database,
            user=self.user,
            password=self.password)

            cur = conn.cursor()

            message_id = f"\'{category['message_id']}\'" or "NULL"
            roles = f"\'{{{', '.join(str(r) for r in category['roles'])}}}\'" if category['roles'] else "NULL"

            update_query=f"UPDATE role_categories SET message_id={message_id}, roles={roles} WHERE name=\'{category['name']}\'"
            cur.execute(update_query)
            conn.commit()      
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')


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

    async def set_role_message_reactions(self, channel: discord.TextChannel, category, clearReactions = False, message: discord.Message = None) -> discord.Message:
        role_emojis = self.roles
        _message = message
        if _message is None:
            _message: discord.Message = await channel.fetch_message(category["message_id"])
        
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
                    print(f"clearing {str(reaction.emoji)} from {category['roles']}")
                    await _message.clear_reaction(str(reaction.emoji))
        # return the message to edit its content when possible
        return _message

    #region Commands
    @commands.command(aliases=['src', 'setrolechannel',' setroleschannel'], hidden=True)
    @commands.check_any(is_mod(), commands.is_owner())
    async def set_roles_channel(self, ctx: commands.Context, id = 0):
        """
        Sets the channel where the role message is posted and where roles can be self assigned from
        """
        channel_id = id or ctx.channel.id
        self.update_roles_channel(channel_id)
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['cl'], hidden=True)
    @commands.check_any(is_mod(), commands.is_owner())
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
    @commands.check_any(is_mod(), commands.is_owner())
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

            old_message_id = self.role_categories[category_name]["message_id"]
            if old_message_id == message_id:
                return

            self.role_categories[category_name]["message_id"] = message_id
            category = self.role_categories[category_name]
            
            self.update_category(self.role_categories[category_name])
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
    @commands.check_any(is_mod(), commands.is_owner())
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
        emoji = temp[0]
        if role_name in self.roles:
            old_emoji = self.roles[role_name]["emoji"]

            self.roles[role_name]["emoji"] = str(emoji)
            self.update_role(self.roles[role_name])


            roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())
            category_name = self.roles[role_name]["category"]
            category = self.role_categories[category_name]

            m = await self.set_role_message_reactions(channel=roles_channel, category=category, clearReactions=True)

            # Updating message content
            try:
                await m.edit(content=m.content.replace(old_emoji, str(emoji)))
            except:
                print("can't edit someone else's message")
        else:
            self.roles[role_name] = {
                "name": role_name,
                "emoji": emoji,
                "assignable": True,
                "category": category,
                "channels": [],
                "description": "League but everyone is OP so is balanced"
            }
            # TODO: ADD RECORD< NOT UPDATE
            self.create_role(self.roles[role_name])
            if category:
                self.role_categories[category]["roles"].append(role_name)
                self.update_category(self.role_categories[category_name])
                m = await self.set_role_message_reactions(channel=roles_channel, category=category, clearReactions=True)


        await ctx.message.add_reaction('✅')


    # TODO 1.Change emoji command => update .json and edit role message too. -- DONE (editing msg content partially)
    # 2. Add new Role => create command and update .json + msg 
    # 3. Delete role => same thing  -- 
    # --- EDIT ROLE COMMAND: takes emoji=, description=, category=, channel=, ... arguments and edits the date in the json file accordingly.
    # some extra logic will be handled when the category or the emoji are changing (updating the self assign msgs)

    @commands.command(aliases=['setrolecategory'], hidden=True)
    @commands.check_any(is_mod(), commands.is_owner())
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
                old_category = self.roles[role_name]["category"]
                # clear old category
                if role_name in self.role_categories[old_category]["roles"]:
                    self.role_categories[old_category]["roles"].remove(role_name)


            self.roles[role_name]["category"] = category
            self.role_categories[category]["roles"].append(role_name)
            self.update_role(self.roles[role_name])
            self.update_category(self.role_categories[category])

            roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())
            if old_category:
                m = await self.set_role_message_reactions(channel=roles_channel, category=self.role_categories[old_category], clearReactions=True)
            m2 = await self.set_role_message_reactions(channel=roles_channel, category=self.role_categories[category], clearReactions=True)

        await ctx.message.add_reaction('✅')

    @commands.command(aliases=['editrole'])
    @commands.check_any(is_mod(), commands.is_owner())
    async def role_info(self, ctx: commands.Context, *, command):
        """
        
        """
        # process_command(command)
        print()
    @commands.command(aliases=['roleinfo'], hidden=True)
    @commands.check_any(is_mod(), commands.is_owner())
    async def role_info(self, ctx: commands.Context, *, role_name):
        """
        Get the setting for a specific role. These are settings for the self-assign channel, not Discord settings
        """
        if role_name not in self.roles:
            print(f"Role {role_name} not found")
            return

        role = self.roles[role_name]
        embed = discord.Embed(title=f"{role_name} details")

        embed.add_field(name="Emoji", value=role["emoji"])
        embed.add_field(name="Category", value=role["category"])
        embed.add_field(name="Self-assignable", value=role["assignable"])
        embed.add_field(name="Description", value=role["description"])
        # TODO: better implement channel (command to update it, check disocrd channel behing certain roles)
        embed.add_field(name="Channels", value=", ".join(map(lambda c: f"<#{c}>", role["channels"])))
        await ctx.channel.send(embed=embed)



    @commands.command(aliases=['activaterole'])
    @commands.check_any(is_mod(), commands.is_owner())
    async def set_role_active(self, ctx: commands.Context, *, role_name):
        # To be redone
        """
        Sets a specific Role as assignable
        """
        
        if role_name not in self.roles:
            print(f"Role {role_name} couldn't be found")
            return

        roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())

        self.roles[role_name]["assignable"] = True
        category = self.roles[role_name]["category"]

        self.update_role(self.roles[role_name])
        await self.set_role_message_reactions(roles_channel, self.role_categories[category], clearReactions=True)
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['deactivaterole'])
    @commands.check_any(is_mod(), commands.is_owner())
    async def set_role_inactive(self, ctx: commands.Context, *, role_name):
        # To be redone
        """
        Sets a specific Role as unassignable
        """
        
        if role_name not in self.roles:
            print(f"Role {role_name} couldn't be found")
            return

        roles_channel: discord.TextChannel = ctx.guild.get_channel(self.get_roles_channel())

        self.roles[role_name]["assignable"] = False
        category = self.roles[role_name]["category"]

        self.update_role(self.roles[role_name])
        await self.set_role_message_reactions(roles_channel, self.role_categories[category], clearReactions=True)
        await ctx.message.add_reaction('✅')


    @commands.command(aliases=['initroles', 'initroleassign', 'i'], hidden=True)
    @commands.check_any(is_mod(), commands.is_owner())
    async def init_role_messages_reactions(self, ctx: commands.Context):
        """
        Adds all the reactions for all the role assignment messages. clears all unreated reactions
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
                    
            # TODO: DELETE RECORD, NOT UPDATE
            self.delete_role(assignable_roles[role.name])
            self.update_category(roles_categories[category])

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
                    
                    # TODO: DELETE RECORD, NOT UPDATE
                    # maybe pass role object AND a role name, then only update the 
                    # before record in the DB, changing the name to the after one
                    self.delete_role(assignable_roles[before.name])

                    self.create_role(assignable_roles[after.name])
                    self.update_category(roles_categories)

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
            if payload.message_id == category["message_id"]:
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
            if payload.message_id == category["message_id"]:
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