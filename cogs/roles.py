import discord
from discord.ext import commands, tasks
import json


class roles(commands.Cog, name="Roles"):
    
    def __init__(self, bot):
        self.bot=bot

    def is_mod(self):
        async def predicate(ctx):
            mod_roles = ['Prez', 'Committee', 'Mods', 'Mod Helpers']
            any(role.name in mod_roles for role in ctx.author.roles)
        return commands.check(predicate)

    async def get_roles_channel(self):
        """ Return the ID of the channel where roles are posted
        """
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['rolesChannelId']

    async def get_roles_description(self):
        # Maybe automatically populated this file one day
        with open('roles/roles_description.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    

    @commands.command(aliases=['src', 'setrolechannel',' setroleschannel'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_roles_channel(self, ctx, id = 0):
        with open('config.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            id_to_set = id or ctx.channel.id
            config['rolesChannelId'] = id_to_set
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        await ctx.message.add_reaction('✅')

   

    @commands.command(aliases=['srd', 'setroledescription'], hidden=True)
    @commands.check_any(commands.check(is_mod), commands.check(commands.is_owner))
    async def set_roles_description(self, ctx, *, args):
        args_list = args.split('=')
        if(len(args_list)< 2):
            await ctx.send("Please enter a description for the role")
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
        await ctx.message.add_reaction('✅')


    async def role_list(self, guild: discord.Guild):
        roles = guild.roles
        i = roles.index(guild.me.top_role)

        embed = discord.Embed(title="List of roles")
        display_roles = [gr for gr in roles[:i] if gr.managed is False\
            and gr.name != "@everyone"\
            and gr.name != "bots"]

        description_list = await self.get_roles_description()
        for role in reversed(display_roles):
            role_description = description_list[role.name]
            embed.add_field(name=role.name, value=role_description, inline=True)
        return embed

    async def role_reactions(self, guild: discord.Guild):
        role_channel_id = await self.get_roles_channel()
        # could improve by check if already existing role messages exists
        # and only send messages with new roles, that way when a role changes position
        # instead of deleting all then resending all roles, we could delete up to the
        # position that changed, and start printing again from that position
        roles = guild.roles
        channel: discord.TextChannel = guild.get_channel(role_channel_id)
        i = roles.index(guild.me.top_role)
        assignable_roles = [gr for gr in roles[:i] if gr.managed is False \
            and gr.name != "@everyone"\
            and gr.name != "bots"\
            and gr.name != "Alumni"\
            and gr.name != "Hackers"]
        for role in reversed(assignable_roles):
                role_msg = await channel.send(f"**`{role.name}`**")
                await role_msg.add_reaction('✅')
   
    async def get_role_messages(self, guild):
        role_channel_id = await self.get_roles_channel()
        channel = guild.get_channel(role_channel_id)
        roles = guild.roles
        i = roles.index(guild.me.top_role)
        roles_name = [r.name for r in roles[:i] if r.managed == False]

        result = []
        async for message in channel.history(limit=200):
            no_markdown_content = message.content.replace('*', '').replace('`','')
            
            if message.author.bot and len(message.reactions) and no_markdown_content in roles_name:
                result.append(message)
        return result

    @commands.command(aliases=['rl'])
    async def rolelist(self, ctx):
        embed = await self.role_list(guild=ctx.guild) 
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=['crm', 'createrolemessages'], hidden=True)
    async def create_role_messages(self, ctx, full=''):
        if str.lower(str(full)) == 'full' or full:
            full = True
        role_channel_id = await self.get_roles_channel()
        channel = ctx.guild.get_channel(role_channel_id)

        embed = await self.role_list(guild=ctx.guild) 
        await channel.send(embed=embed)
        if full:
            await self.role_reactions(ctx.guild)
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['drm', 'deleterolemessages'], hidden=True)
    async def delete_role_messages(self, ctx):
        # this snippet could be a clear_messages function tbh (since we repeat it on_role_created)
        guild = self.bot.get_guild(ctx.guild.id)

        messages = await self.get_role_messages(guild)
        for message in messages:
            await message.delete()
        await ctx.message.add_reaction('✅')

    @commands.command(aliases=['rrm', 'resetrolemessages'], hidden=True)
    async def reset_role_messages(self, ctx):
        guild = self.bot.get_guild(ctx.guild.id)
        role_channel_id = await self.get_roles_channel()

        messages = await self.get_role_messages(guild)
        for message in messages:
            await message.delete()
        channel = guild.get_channel(role_channel_id)
        embed = await self.role_list(guild)
        await channel.send(embed=embed)
        await self.role_reactions(ctx.guild) 
        await ctx.message.add_reaction('✅')

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        guild = self.bot.get_guild(role.guild.id)
        messages = await self.get_role_messages(guild)
        for message in messages:
            await message.delete()
        await self.role_reactions(guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        role_channel_id = await self.get_roles_channel()

        guild = self.bot.get_guild(role.guild.id)
        channel = guild.get_channel(role_channel_id)
        
        async for message in channel.history(limit=200):
            no_markdown_content = message.content.replace('*', '').replace('`','')
            
            if message.author.bot and len(message.reactions) and no_markdown_content == role.name:
                await message.delete()
            
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        role_channel_id = await self.get_roles_channel()

        guild = self.bot.get_guild(before.guild.id)
        channel = guild.get_channel(role_channel_id)
        
        async for message in channel.history(limit=200):
            no_markdown_content = message.content.replace('*', '').replace('`','')

            if message.author.bot and len(message.reactions) and no_markdown_content == before.name:
                if after.managed or after.position > guild.me.top_role.position:
                    await message.delete()
                else:
                    await message.edit(content=f"**`{after.name}`**")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # payload member only available for add reaction
        if payload.member.bot or payload.guild_id is None:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        channel = guild.get_channel(payload.channel_id)

        role_channel_id = await self.get_roles_channel()

        if channel.id == role_channel_id and str(payload.emoji) == '✅':
            message = await channel.fetch_message(payload.message_id)
            role_name = message.content.replace('*', '').replace('`', '')

            role = discord.utils.get(guild.roles, name=role_name)

            if role is None:
                return

            await member.add_roles(role)
            m = await channel.send(f'**{member.mention}** assigned role {message.content}')
            await m.delete(delay=3)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot or payload.guild_id is None:
            return

        role_channel_id = await self.get_roles_channel()


        channel = guild.get_channel(payload.channel_id)
        if channel.id == role_channel_id and str(payload.emoji) == '✅':
            message = await channel.fetch_message(payload.message_id)
            role_name = message.content.replace('*', '').replace('`', '')

            role = discord.utils.get(guild.roles, name=role_name)

            if role is None:
                return

            await member.remove_roles(role)
            m = await channel.send(f'**{member.mention}** removed role {message.content}')
            await m.delete(delay=3)

    @commands.command(aliases=["addrole", "ar", "r"])
    async def role(self, ctx, *, role: discord.Role = None):

        guild_roles = ctx.guild.roles
        i = guild_roles.index(ctx.guild.me.top_role)
        assignable_roles = [gr for gr in guild_roles[:i] if gr.managed is False \
            and gr.name != "@everyone"\
            and gr.name != "bots"\
            and gr.name != "Alumni"\
            and gr.name != "Hackers"]
        
        if role is None:
            assignable_roles_str = f"`{'`, `'.join([ar.name for ar in assignable_roles])}`"
            await ctx.send(f"Specify which role you want to add.\n**Here's a list of the available roles:**\n{assignable_roles_str}")
            return

        user = ctx.message.author
        try:
            if role in assignable_roles:
                await user.add_roles(role)
                await ctx.message.add_reaction('✅')
            else:
                raise Exception("Role not assignable")
        except Exception as e:
            print("Couldn't add role.\n" + e)
            await ctx.message.add_reaction('❌')

    @commands.command(aliases=["removerole", "rr"])
    async def removeRole(self, ctx, *, role: discord.Role = None):
        user = ctx.message.author

        if role is None:
            roles_str = [r.name for r in user.roles if r.name != "@everyone"]
            roles_str = f"`{'`, `'.join(roles_str)}`"
            # could only show the roles the bot can delete, but that's extra work I'm ot willing to do atm :)
            await ctx.send(f"Specify the role you want to remove.\n**Your roles:**\n{roles_str}")
            return 

        if role in user.roles:
            try:
                await user.remove_roles(role)
            except Exception as e:
                print(e)
                await ctx.message.add_reaction('❌')
                return
            await ctx.message.add_reaction('✅')
        else:
            print("User doesn't have specified role")

def setup(bot):
    bot.add_cog(roles(bot))