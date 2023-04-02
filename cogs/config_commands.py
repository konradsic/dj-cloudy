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

    @config_view_command.error
    async def on_cog_error(self, interaction, error):
        self.logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}")
        embed = discord.Embed(description=
            f"<:x_mark:1028004871313563758> An error occured. Please contact developers for more info. Details are shown below.\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    help_utils.register_command("config view", "View your configuration profile or configuration for this guild", "Configuration",
        [("user", "Set to true if you want to see your profile, if it's false it will show guild profile", False)])
    await bot.add_cog(ConfigCog(bot), guilds=bot.guilds)