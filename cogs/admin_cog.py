from datetime import datetime
from typing import Optional
import discord
from discord.ext import commands
import random
from db.message_thread import add_message_thread_channel, remove_message_thread_channel
from db.statistics import StatisticChangeORM, StatisticORM, StatisticsShowInfoSortTypeBehaviour, UserORM, get_statistic_sum, get_statistics, get_users, save_to_db, update_user_country
from globe.globe_dedicated_channel import GlobeDedicatedChannelORM, add_globe_dedicated_channel, remove_globe_dedicated_channel, get_all_globe_dedicated_channels

ALL_PERMISSIONS = discord.PermissionOverwrite.from_pair(discord.Permissions.all(), discord.Permissions.none())

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        else:
            await ctx.respond("You need administrator permissions to use commands in this cog.")

    ### Feudalization Commands

    async def create_roles(self, guild: discord.Guild, role_list: list[str]) -> None:
        if not role_list:
            raise Exception("Please provide a comma-separated list of role names.")

        for role_name in role_list:
            random_color: discord.Color = discord.Color.from_rgb(
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            )
            try:
                await guild.create_role(name=role_name, color=random_color)
            except discord.Forbidden:
                raise Exception(f"Permission error: Could not create role '{role_name}'.")
            except discord.HTTPException as e:
                raise Exception(f"HTTP error while creating role '{role_name}': {e}.")

    async def create_role_based_structure(self,
        guild: discord.Guild, 
        role_names: list[str]
    ) -> None:
        for role_name in role_names:
            role: Optional[discord.Role] = discord.utils.get(guild.roles, name=role_name)
            if not role:
                raise ValueError(f"Role with name '{role_name}' not found.")

            category_overwrites = {
                guild.default_role: discord.PermissionOverwrite(),
                role: ALL_PERMISSIONS,
            }
            category = await guild.create_category(name=f"{role_name} Zone", overwrites=category_overwrites)

            public_channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False
                ),
                role: ALL_PERMISSIONS
            }
            await category.create_text_channel(
                name=f"{role_name}-public", overwrites=public_channel_overwrites
            )

            private_channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: ALL_PERMISSIONS,
            }
            await category.create_text_channel(
                name=f"{role_name}-private", overwrites=private_channel_overwrites
            )

    @discord.slash_command()
    async def feudalize(self, ctx: discord.commands.context.ApplicationContext, role_names: str):
        role_list: list[str] = [name.strip() for name in role_names.split(",") if name.strip()]
        await self.create_roles(ctx.guild, role_list)
        await self.create_role_based_structure(ctx.guild, role_list)
        await ctx.respond('Feudalized!')

    ### Message thread commands

    @discord.slash_command()
    async def add_message_thread_channel(self, ctx: discord.commands.context.ApplicationContext, channel_id:str = None):
        if(channel_id == None):
            channel_id = ctx.channel_id
        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if(channel.guild.id != ctx.guild_id):
            await ctx.respond("Please use this command on the guild of this channel")
            return
        channel_id = int(channel_id)
        try:
            add_message_thread_channel(channel_id)
        except IndexError:
            await ctx.respond(f"Channel {channel_id} is already thread channel")
            return

        self.bot.refresh_message_thread_channels()
        await ctx.respond(f"Channel {channel_id} added to thread channels")

    @discord.slash_command()
    async def remove_message_thread_channel(self, ctx: discord.commands.context.ApplicationContext, channel_id:str = None):
        if(channel_id == None):
            channel_id = ctx.channel_id
        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if(channel.guild.id != ctx.guild_id):
            await ctx.respond("Please use this command on the guild of this channel!")
            return
        channel_id = int(channel_id)
        try:
            remove_message_thread_channel(channel_id)
        except IndexError:
            await ctx.respond(f"Channel {channel_id} is not thread channel")
            return

        self.bot.refresh_message_thread_channels()
        await ctx.respond(f"Channel {channel_id} removed from thread channels")


    ### Globe commands

    @discord.slash_command()
    async def globe_dedicate_channel(self, ctx: discord.commands.context.ApplicationContext, channel_id:str = None):
        if(channel_id == None):
            channel_id = ctx.channel_id
        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if(channel.guild.id != ctx.guild_id):
            await ctx.respond("Please use this command on the guild of this channel")
            return
        channel_id = int(channel_id)
        try:
            add_globe_dedicated_channel(channel_id)
        except IndexError:
            await ctx.respond(f"Channel {channel_id} is already globe dedicated channel")
            return

        self.bot.refresh_map_channels()
        await ctx.respond(f"Channel {channel_id} added to globe dedicated channels")

    @discord.slash_command()
    async def globe_undedicate_channel(self, ctx: discord.commands.context.ApplicationContext, channel_id:str = None):
        if(channel_id == None):
            channel_id = ctx.channel_id
        channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
        if(channel.guild.id != ctx.guild_id):
            await ctx.respond("Please use this command on the guild of this channel!")
            return
        channel_id = int(channel_id)
        try:
            remove_globe_dedicated_channel(channel_id)
        except IndexError:
            await ctx.respond(f"Channel {channel_id} is not globe dedicated channel")
            return

        self.bot.refresh_map_channels()
        await ctx.respond(f"Channel {channel_id} removed from globe dedicated channels")

    @discord.slash_command()
    async def print_globe_dedicated_channels(self, ctx: discord.commands.context.ApplicationContext):
        all_channels_ids: list[GlobeDedicatedChannelORM] = get_all_globe_dedicated_channels()
        output_channels_names: list[str] = []
        for channelORM in all_channels_ids:
            channel_id = channelORM.id
            try:
                channel: discord.TextChannel = await self.bot.fetch_channel(channel_id)
                if(channel.guild.id == ctx.guild_id):
                    output_channels_names.append(f"{channel.name} ({channel.id})")
            except Exception as e:
                print(e)

        response: str = "\n".join(output_channels_names)
        if(response == ''):
            response = "No channels"
        await ctx.respond(response)

    ### Statistic Commands
    @discord.slash_command()
    async def add_new_user(self, ctx: discord.commands.context.ApplicationContext, name: str, country: str = None):
        save_to_db(UserORM(name=name, server_id=ctx.guild_id, country=country))
        await ctx.respond(f"Added user {name}")

    @discord.slash_command()
    async def update_user_country(self, ctx: discord.commands.context.ApplicationContext, name: str, country: str = None):
        update_user_country(name, country)
        await ctx.respond(f"Changed user {name}")

    @discord.slash_command()
    async def add_new_statistic(self, ctx: discord.commands.context.ApplicationContext, name: str, type: str, sort_behavior: int = 0, max_name: str = ""):
        if(max_name == ""):
            max_name = None
        save_to_db(StatisticORM(name=name, type=type, max_name=max_name, server_id=ctx.guild_id, sort_behavior=sort_behavior))
        await ctx.respond(f"Added statistic {name}")
        
    def user_autocomplete(ctx : discord.AutocompleteContext):
        print(ctx.interaction.guild_id)
        return [user.name for user in get_users(ctx.interaction.guild_id)]
    
    def statistic_autocomplete(ctx : discord.AutocompleteContext):
        return [user.name for user in get_statistics(ctx.interaction.guild_id)]

    @discord.slash_command()
    async def statistic_change(self, 
                                   ctx: discord.commands.context.ApplicationContext, 
                                   user_name: discord.Option(str, autocomplete=user_autocomplete), 
                                   statistic: discord.Option(str, autocomplete=statistic_autocomplete), 
                                   value: discord.Option(int, description="Amount to modify statistic, can be negative"),
                                   comment: discord.Option(str) = ""
                                   ):
        save_to_db(StatisticChangeORM(
            user_name=user_name, 
            statistic=statistic, 
            value=value,
            date=datetime.now(),
            comment=comment,
            server_id=ctx.guild_id
        ))
        await ctx.respond(f"Added statistic change for {user_name}")

    @discord.slash_command()
    async def statistic(self, 
                                   ctx: discord.commands.context.ApplicationContext, 
                                   statistic: discord.Option(str, autocomplete=statistic_autocomplete), 
                                   ):
        result = "\n".join([f"({row[2]}) {row[0]}: {row[1]}" for row in get_statistic_sum(ctx.interaction.guild_id, statistic)])
        await ctx.respond(f"# {statistic}\n{result}")
    


def setup(bot):
    bot.add_cog(AdminCog(bot))