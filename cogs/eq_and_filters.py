import datetime
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound
from utils.base_utils import (
    filter_to_string, string_to_filter,
    AEQ_HZ_BANDS
)
from discord.app_commands import Choice
from utils import logger

logging = logger.Logger().get("cogs.eq_and_filters")

@logger.class_logger
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
        logging.info("FilterCog", "choose_filter", f"Applied filter '{filter}' in guild #{interaction.guild.id}")

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
        logging.info("FilterCog", "reset_filter", f"Filters reset in guild #{interaction.guild.id}")

@logger.class_logger
class EqualizersCog(commands.GroupCog, name="equalizers"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="choose", description="Choose an equalizer to apply it to the currently playing track")
    @app_commands.describe(equalizer="Equalizer to apply")
    @app_commands.choices(equalizer=[
        Choice(name="piano", value="piano"),
        Choice(name="metal", value="metal"),
        Choice(name="flat", value="flat"),
        Choice(name="boost", value="boost"),
    ])
    async def equalizer_choose_command(self, interaction: discord.Interaction, equalizer: str):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed" 
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't apply equalizers when no song is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "not playing"
        _eq = getattr(wavelink.Equalizer, equalizer, None)
        if _eq is None:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:x_mark:1028004871313563758> Something went wrong, please try again",color=BASE_COLOR), ephemeral=True)
            return "failed"
        filter = wavelink.Filter(equalizer=_eq())
        await player.set_filter(filter)
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully applied equalizer `{equalizer}` to currently playing track",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        logging.info("EqualizersCog", "choose_equalizer", f"Applied eq '{equalizer}' in guild #{interaction.guild.id}")

    @app_commands.command(name="advanced", description="Advanced, 15-band equalizer allows you to change values as you want. Have fun!")
    @app_commands.describe(band="A hertz band you want to apply the gain on")
    @app_commands.describe(gain="A float-like gain (-10 to 10)")
    @app_commands.choices(band=[
        Choice(name=str(gain_value), value=gain_value) for gain_value in AEQ_HZ_BANDS
    ])
    async def equalizer_advanced_command(self, interaction: discord.Interaction, band: int, gain: float):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed" 
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't apply equalizers when no song is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "not playing"
        
        if gain < -2.5:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Gain must be between -2.5 and -10.0",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed"
        elif gain > 10:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Gain must be between -2.5 and -10.0",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed"

        band_idx = AEQ_HZ_BANDS.index(band)
        player.eq_levels[band_idx] = gain/10
        eq = wavelink.Filter(equalizer=wavelink.Equalizer(name="AEQ_ADVANCED_EQUALIZER", bands=[(i,g) for i,g in enumerate(player.eq_levels)]))
        await player.set_filter(eq)
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Equalizer adjusted to a custom preset.", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reset", description="Reset applied equalizers. Similiar to /filters reset")
    async def eq_reset_command(self, interaction: discord.Interaction):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed" 
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't reset equalizers when nothing is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "not playing"
        await player.set_filter(wavelink.Filter()) # empty filter for reseting
        player.eq_levels = [0.] * 15
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Equalizers have been successfully reset",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        logging.info("EqualizersCog", "reset_filter", f"Filters reset in guild #{interaction.guild.id}")

async def setup(bot):
    help_utils.register_command("filters choose", "Select a filter to enchance your music experience", "Music: Advanced commands", [("filter","Filter to apply",True)])
    help_utils.register_command("filters reset", "Reset applied filters", "Music: Advanced commands")
    help_utils.register_command("equalizers choose", "Choose an equalizer to apply it to the currently playing track", "Music: Advanced commands", [("equalizer","Equalizer to apply",True)])
    help_utils.register_command("equalizers advanced", "Advanced, 15-band equalizer allows you to change values as you want. Have fun!", "Music: Advanced commands", [("band", "A hertz band you want to apply the gain on", True),("gain", "A float-like gain",True)])
    help_utils.register_command("equalizers reset", "Reset applied equalizers", "Music: Advanced commands")
    await bot.add_cog(FiltersCog(bot), guilds=bot.guilds)
    await bot.add_cog(EqualizersCog(bot), guilds=bot.guilds)