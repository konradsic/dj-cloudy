import datetime
import random

import discord
from discord import app_commands
from discord.ext import commands

from utils import (
    help_utils as help_utils, 
    logger as logger,
    configuration as cfg)
from utils.colors import BASE_COLOR


@logger.LoggerApplication
class ConfigCog(commands.GroupCog, name="config"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view", description="View your configuration profile or configuration for this guild")
    @app_commands.describe(user="Set to true if you want to see your profile, if it's false it will show guild profile")
    async def config_view_command(self, interaction: discord.Interaction, user: bool=True):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if user:
            id = interaction.user.id
        else:
            id = interaction.guild.id
        
        config = cfg.ConfigurationHandler(id=id, user=user)
        data = config.data

        embed = discord.Embed(description="Settings for this profile: key / value\n", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Your configuration profile" if user else "This guild's configuration profile", 
                         icon_url=interaction.user.display_avatar.url if user else interaction.guild.icon.url)
        embed.set_footer(text="https://github.com/konradsic/dj-cloudy")
        
        description = ""

        for key, value in data.items():
            # if role then transform
            val = value["value"]
            if value["type"] == "role":
                val = interaction.guild.get_role(value["value"])
                if val is not None:
                    val = val.name
            description += f"`{key}` {val}\n"

        embed.description += description
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="set-user", description="Set configuration for your profile")
    @app_commands.describe(key="A parameter you want to change", value="New value for the parameter. For roles,users etc. use thier respective ID")
    async def config_set_user_cmd(self, interaction: discord.Interaction, key: str, value: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

    
    @app_commands.command(name="set-user", description="Set configuration for current guild. Requires ManageGuild permission")
    @app_commands.describe(key="A parameter you want to change", value="New value for the parameter. For roles,users etc. use thier respective ID")
    async def config_set_guild_cmd(self, interaction: discord.Interaction, key: str, value: str):
        await interaction.response.defer(thinking=True, ephemeral=False)

async def setup(bot):
    help_utils.register_command("config view", "View your configuration profile or configuration for this guild", "Configuration",
        [("user", "Set to true if you want to see your profile, if it's false it will show guild profile", False)])
    await bot.add_cog(ConfigCog(bot), guilds=bot.guilds)