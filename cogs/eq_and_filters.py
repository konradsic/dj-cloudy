import datetime
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound
from utils.base_utils import filter_to_string, string_to_filter
from discord.app_commands import Choice
from utils import logger

logging = logger.Logger().get("cogs.eq_and_filters")

class FiltersCog(commands.GroupCog, name="filters"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="select", description="Select a filter to enchance your music experience")
    @app_commands.describe(filter="Filter to apply")
    @app_commands.choices(filter=[
        Choice(name="Karaoke", value="Karaoke"),
        Choice(name="Timescale", value="Timescale"),
        Choice(name="Tremolo", value="Tremolo"),
        Choice(name="Vibrato", value="Vibrato"),
        Choice(name="Rotation", value="Rotation"),
        Choice(name="Distortion", value="Rotation"),
        Choice(name="Channel Mix", value="channel_mix"),
        Choice(name="Low Pass", value="low_pass"),
    ])
    async def filters_choose_command(self, interaction: discord.Interaction, filter: str):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                    raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed"

        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't apply filters when nothing is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "not playing"
        _filter = string_to_filter(filter)
        filter_cls = wavelink.Filter(**{filter.lower(): _filter()})
        await player.set_filter(filter_cls)
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully applied filter `{filter}` to currently playing track",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        logging.info("FilterCog.choose_filter", f"Applied filter '{filter}' in guild #{interaction.guild.id}")

    @app_commands.command(name="reset", description="Reset applied filters")
    async def filters_reset_command(self, interaction: discord.Interaction):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed" 
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't reset filters when nothing is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "not playing"
        await player.set_filter(wavelink.Filter()) # empty filter for reseting
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Filters have been successfully reset",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        logging.info("FilterCog.reset_filter", f"Filters reset in guild #{interaction.guild.id}")

# class EqualizersCog(commands.GroupCog, name="equalizers"):
#     def __init__(self, bot):
#         self.bot = bot
#         super().__init__()

async def setup(bot):
    help_utils.register_command("filters choose", "Select a filter to enchance your music experience", "Music: Advanced commands", [("filter","Filter to apply",True)])
    help_utils.register_command("filters reset", "Reset applied filters", "Music: Advanced commands")
    await bot.add_cog(FiltersCog(bot), guilds=bot.guilds)