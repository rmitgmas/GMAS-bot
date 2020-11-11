import discord
from discord.ext import commands, tasks
import json

# TODO: command to add/remove unassignable roles
# TODO: differentiate unassignable and unremovable roles?
# TODO: TBA
class roles(commands.Cog, name="Roles"):
    def __init__(self, bot):
        self.bot=bot

    def is_mod(self):
        async def predicate(ctx):
            mod_roles = ['Prez', 'Committee', 'Mods', 'Mod Helpers']
            any(role.name in mod_roles for role in ctx.author.roles)
        return commands.check(predicate)

    async def get_roles_channel(self):
        """ 
        Return the ID of the channel where roles are posted
        """
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['rolesChannelId']

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
    
    async def find_role_message(self, guild) -> discord.Message:
        """
        Finds the role message from the roles channel, and return the discord.Message instance of it
        """
        role_channel_id = await self.get_roles_channel()
        if not role_channel_id:
            # not the role channel
            return None
        channel: discord.TextChannel = guild.get_channel(role_channel_id)

        def is_bot(message):
            return message.author.bot

        role_message = False
        async for message in channel.history(limit=200).filter(is_bot):
            if "React to give yourself a role" in message.content and message.author.bot:
                # found the role message :D
                role_message = message
                break
            else:
                 return None
        
        if not role_message:
            print("Couldn't find role message")

        return role_message

    async def get_role_from_reaction(self, guild, role_message, payload) -> discord.Role:
        roles = await self.get_roles_from_role_message(guild)
        try:
            role_name = roles[str(payload.emoji)]
        except KeyError:
            print("The reaction isn't a valid role/emoji pair")
            return
        if not role_name:
            print("Emoji has no role attached")
            return None
        role: discord.Role = discord.utils.get(guild.roles, name=role_name)
        return role

    async def role_list(self, guild: discord.Guild):
        roles = guild.roles
        i = roles.index(guild.me.top_role)

        embed = discord.Embed(title="List of roles")
        display_roles = [gr for gr in roles[:i] if gr.managed is False\
            and gr.name != "@everyone"\
            and gr.name != "bots"]

        description_list = await self.get_roles_description()
        for role in reversed(display_roles):
            if role.name in description_list:
                role_description = description_list[role.name]
                embed.add_field(name=role.name, value=role_description, inline=True)
        return embed

    async def update_role_list_embed(self, guild):
        role_channel_id = await self.get_roles_channel()
        channel: discord.TextChannel = guild.get_channel(role_channel_id)
        async for message in channel.history(limit=200):
            if message.embeds and message.embeds[0].title == "List of roles":
                msg = await channel.fetch_message(message.id)
        if not message:
            print(f"Couldn't find embed role list. update manually instead")
        new_embed = await self.role_list(guild)
        await msg.edit(embed=new_embed)

    #region Commands 
    @commands.command(aliases=['printRolesDescriptions', 'prd',' printrolesdescriptions'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def print_roles_descriptions(self, ctx):
        """
        Prints the description for each roles
        """
        # loop through roles, check role-description file, print corresponding descr for each role
        print("")

    @commands.command(aliases=['printRoles', 'pr',' printroles'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def print_roles(self, ctx):
        """
        Prints the role message to self assign role, each role having a custom emoji assigned to it (set in role_const.json) 
        """
        guild: discord.Guild = ctx.guild
        # If the role message already has reaction (maybe check only on startup), assign the roles of emote ppl reacted to
        # this is useful if they reacted while the bot was down

        dup = await self.find_role_message(guild)
        if dup:
            await dup.delete()

        role_channel_id = await self.get_roles_channel()
        unassignable_roles = await self.get_unassignable_roles()
        roles_channel = guild.get_channel(role_channel_id)

        roles = guild.roles

        i = roles.index(ctx.guild.me.top_role)
        # maybe use role id and not name?
        role_names = [r.name for r in roles[:i] if r.managed == False and r.name not in unassignable_roles]

        role_emojis = []
        with open('roles/roles_const.json', 'r', encoding='utf-8') as f:
            content = json.load(f)
            role_emojis = content['role_emojis']

        m_string = "React to give yourself a role\n\n"
        emojis = []
        print(guild.emojis)
        for r in role_names:
            try:
                if role_emojis[r]:
                    if ':' in role_emojis[r]:
                        m_string += f"{role_emojis[r]} : `{r}`\n"
                    else:
                        m_string += f"{role_emojis[r]} : `{r}`\n"
                    emojis.append(role_emojis[r])
                    print(r, role_emojis[r])
            except KeyError as e:
                print(f"Role `{r}` has no emoji set")

        m: discord.Message = await roles_channel.send(m_string)

        for e in emojis:
            if ':' in e:
                await m.add_reaction(f"<:{e}>")
            else:
                await m.add_reaction(f"{e}")
 

    @commands.command(aliases=['changeRoleEmoji', 'cre',' changeroleemoji'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def change_role_emoji(self, ctx, *, text):
        texts = text.split('=')
        if(len(texts)< 2):
            await ctx.send("Syntax: role_name=emoji")
            return
        
        role_name = texts[0]
        emoji = texts[1]

        role_message =  await self.find_role_message(ctx.guild)
        with open('roles/roles_const.json', 'r+', encoding='utf-8') as f:
            content = json.load(f)

            if emoji in content['role_emojis'].values():
                await ctx.send("This emoji is already used by another role, please use a different one.")
                return
            try:
                old_emoji = content['role_emojis'][role_name]
                content['role_emojis'][role_name] = emoji
                print(old_emoji)
                print(content['role_emojis'])
            except KeyError as e:
                await ctx.send(f"Couldn't find role `{role_name}`")
                print(e)
                return
            f.seek(0)
            json.dump(content, f, indent=4, ensure_ascii=False)
            f.truncate()
            # replace the text somehow
           
            print(f"Changing {old_emoji} to {emoji} for role `{role_name}`")
            # replace based on role in that line
            new_content = role_message.content.replace(old_emoji, emoji, 1)
            await role_message.remove_reaction(old_emoji, ctx.me)
            await role_message.add_reaction(emoji)
            

            await role_message.edit(content=new_content)

    @commands.command(aliases=['src', 'setrolechannel',' setroleschannel'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_roles_channel(self, ctx, id = 0):
        """
        Sets the channel where the role message is posted and where roles can be self assigned from
        """
        with open('config.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            id_to_set = id or ctx.channel.id
            config['rolesChannelId'] = id_to_set
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        await ctx.message.add_reaction('✅')
        # TODO: Delete old role message and auto repost the role message in the new channel


    @commands.command(aliases=['rl'])
    async def rolelist(self, ctx):
        """
        Displays the list of roles with their description
        """
        embed = await self.role_list(guild=ctx.guild)
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=['srd', 'setroledescription','rd'], hidden=True, help="Set role description using g!srd `<role name>`=`<role description>`")
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_roles_description(self, ctx, *, args):
        args_list = args.split('=')
        if(len(args_list)< 2):
            await ctx.send("Please enter a description for the role, seperated by a `=`.\n**g!srd `<role name>`=`<role description>`**")
            return
        
        if args_list[0].strip() not in [r.name for r in ctx.guild.roles]:
            return
            
        with open('roles/roles_description.json', 'r+', encoding='utf-8') as f:
            roles = json.load(f)
            # TODO: check if role exists
            roles[args_list[0].strip()] = args_list[1].strip()
            f.seek(0)
            json.dump(roles, f, indent=4)
            f.truncate()

        try:
            await self.update_role_list_embed(ctx.guild)
            await ctx.message.add_reaction('✅')
        except Exception as e:
            print(f'error when updating embed: {e}')
            await ctx.message.add_reaction('❌')    
    #endregion Commands

    #region Listeners
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        roles = await self.get_roles_from_role_message(role.guild)
        print(roles)
        #TODO: edit the role message 

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        print("Role Deleted: Function not implemented")
        print(role.guild)
        roles = await self.get_roles_from_role_message(role.guild)
        #TODO: edit the role message 
     
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        roles = await self.get_roles_from_role_message(before.guild)
        print("Role Updated: Function not implemented")
        #TODO: edit the role message 

    async def get_roles_from_role_message(self, guild) -> dict:
        role_message = await self.find_role_message(guild)
        if not role_message:
            print("Can't get roles from role message")
            return

        roles = role_message.content.split('\n')
        roles = list(roles)[2:]
        def split_text(role_message):
            m = role_message.rsplit(":", 1)
            m[0] = m[0].strip()
            m[1] = m[1].replace('`', '').strip()
            return m
        roles = map(split_text, roles)
        roles = dict(roles)
        print(roles)
        return roles

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # payload member only available for add reaction
        if payload.member.bot or payload.guild_id is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(int(payload.user_id))
        if not member:
            print("Couldn't get member from reaction.")
        channel = guild.get_channel(payload.channel_id)

        role_channel_id = await self.get_roles_channel()
        role_message = await self.find_role_message(guild)

        if role_message is None:
            return

        if channel.id == role_channel_id :
            if payload.message_id == role_message.id:
                role = await self.get_role_from_reaction(guild, role_message, payload)

            unassignable_roles = await self.get_unassignable_roles()
            if role.name not in unassignable_roles:
                await member.add_roles(role)
                print(f"Added {str(role)} to user {str(member)}")
            else:
                print("Role is unassignable")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # payload member only available for add reaction
        if payload.guild_id is None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(int(payload.user_id))
        if not member:
            print("Couldn't get member from reaction.")
        if member.bot:
            return
        channel = guild.get_channel(payload.channel_id)

        role_channel_id = await self.get_roles_channel()
        role_message = await self.find_role_message(guild)

        if role_message is None:
            return

        if channel.id == role_channel_id :
            if payload.message_id == role_message.id:
                role = await self.get_role_from_reaction(guild, role_message, payload)

            unassignable_roles = await self.get_unassignable_roles()
            if role.name not in unassignable_roles:
                await member.remove_roles(role)
                print(f"Removed role {str(role)} from user {str(member)}")
            else:
                print("Role is unassignable")
    #endregion Listeners
def setup(bot):
    bot.add_cog(roles(bot))