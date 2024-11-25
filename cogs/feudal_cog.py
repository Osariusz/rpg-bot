from typing import Optional
import discord
from discord.ext import commands
import random

ALL_PERMISSIONS = discord.PermissionOverwrite.from_pair(discord.Permissions.all(), discord.Permissions.none())

class FeudalCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        else:
            await ctx.respond("You need administrator permissions to use commands in this cog.")

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
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: ALL_PERMISSIONS,
            }
            category = await guild.create_category(name=f"{role_name} Zone", overwrites=category_overwrites)

            public_channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=True, send_messages=False
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

def setup(bot):
    bot.add_cog(FeudalCog(bot))