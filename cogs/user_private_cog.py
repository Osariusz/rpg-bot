from datetime import datetime
import re
from typing import Optional
import discord
from discord.ext import commands
import random
from db.message_thread import add_message_thread_channel, remove_message_thread_channel
from db.statistics import StatisticChangeORM, StatisticORM, StatisticsShowInfoSortTypeBehaviour, UserORM, add_end_turn, delete_end_turn_by_day, end_turn_with_max_adjustment, get_statistic_data, get_statistics, get_turn_dates, get_user_name_by_discord_id, get_user_statistic_data, get_users, save_to_db, update_user_country, update_user_discord_id
from globe.globe_dedicated_channel import GlobeDedicatedChannelORM, add_globe_dedicated_channel, remove_globe_dedicated_channel, get_all_globe_dedicated_channels

ALL_PERMISSIONS = discord.PermissionOverwrite.from_pair(discord.Permissions.all(), discord.Permissions.none())

class UserPrivateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command()
    async def mystatistics(self, ctx: discord.commands.context.ApplicationContext):
        """
        Retrieves your aggregated statistics.
        For each statistic, displays its current total value and, if applicable, the max value (as 'na turę').
        """

        server_id = ctx.guild_id
        user_name = get_user_name_by_discord_id(ctx.author.id)

        if(user_name == None):
            await ctx.respond(f"**You do not exist**", ephemeral=True)
            return

        # Retrieve the aggregated statistic data for this user
        data = get_user_statistic_data(server_id, user_name)
        
        # Build output lines, mimicking your existing formatting:
        # e.g., "(None) bulwa: 13 (na turę: 17)"
        if data:
            result = "\n".join([
                f"{row[0]}: {row[1]}" + (f" (na turę: {row[3]})" if len(row) > 3 else "")
                for row in data
            ])
        else:
            result = "No statistic data found."

        await ctx.respond(f"**{user_name} Statistics:**\n{result}", ephemeral=True)

def setup(bot):
    bot.add_cog(UserPrivateCog(bot))