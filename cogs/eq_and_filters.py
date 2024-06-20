import datetime
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.ui.colors import BASE_COLOR
from lib.utils.errors import NoPlayerFound
from lib.utils.base_utils import djRole_check
from lib.utils import filters_and_eqs
from discord.app_commands import Choice
from lib.logger import logger
from lib.utils.base_utils import quiz_check
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType

@logger.LoggerApplication
class FiltersCog(commands.GroupCog, name="filters"):
    def __init__(self, bot: discord.ext.commands.Bot, logger):
        self.bot: discord.ext.commands.Bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="select", description="Select a filter to enhance your music experience")
    @app_commands.describe(filter="Filter to apply")
    @app_commands.choices(filter=[
        Choice(name="Karaoke", value="karaoke"),
        Choice(name="Timescale", value="timescale"),
        Choice(name="Tremolo", value="tremolo"),
        Choice(name="Vibrato", value="vibrato"),
        Choice(name="Rotation", value="rotation"),
        Choice(name="Distortion", value="distortion"),
        Choice(name="Channel Mix", value="channel_mix"),
        Choice(name="Low Pass", value="low_pass"),
    ])
    @help_utils.add("filters choose", "Select a filter to enhance your music experience", "Filters and equalizers", {"filter": {"description": "Filter to apply", "required": True}})
    async def filters_choose_command(self, interaction: discord.Interaction, filter: str):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")

            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed"

        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Can't apply filters when nothing is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"
        
        # set filter
        if filter not in filters_and_eqs.FILTERS:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Invalid filter")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        await filters_and_eqs.set_filter(player, filter)
        
        embed = ShortEmbed(description=f"<:tick:1028004866662084659> Successfully applied filter `{filter}` to currently playing track")
        await interaction.followup.send(embed=embed)
        self.logger.info(f"Applied filter '{filter}' in guild #{interaction.guild.id}")

    @app_commands.command(name="reset", description="Reset applied filters")
    @help_utils.add("filters reset", "Reset applied filters", "Filters and equalizers")
    async def filters_reset_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")

            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed" 
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Can't reset filters when nothing is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"
        
        await player.set_filters(wavelink.Filters(), seek=True) # empty for no filter modifications
        embed = ShortEmbed(description=f"<:tick:1028004866662084659> Filters successfully reset")
        await interaction.followup.send(embed=embed)
        self.logger.info(f"Filters reset in guild #{interaction.guild.id}")
        
    @app_commands.command(name="list", description="List all filters and check if they are applied")
    @help_utils.add("filters list", "List all filters and check if they are applied", "Filters and equalizers")
    async def filters_list_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")

            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed" 
        
        filters: wavelink.Filters = player.filters
        embed = NormalEmbed(timestamp=True)
        embed.set_author(name="Listing all filters", icon_url=self.bot.user.display_avatar.url)
        
        for filter in filters_and_eqs.FILTERS:
            cur = getattr(filters, filter)
            # print("comparing", cur.__dict__, getattr(wavelink, cur.__class__.__name__).__dict__)
            embed.add_field(name=cur.__class__.__name__, value="Applied: `Yes`" if cur.__dict__ != {"_payload": {}} else "Applied: `No`", inline=True)
            
        await interaction.followup.send(embed=embed)
            

@logger.LoggerApplication
class EqualizersCog(commands.GroupCog, name="equalizers"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="choose", description="Choose an equalizer to apply it to the currently playing track")
    @app_commands.describe(equalizer="Equalizer to apply")
    @app_commands.choices(equalizer=[
        Choice(name="Piano", value="piano"),
        Choice(name="Metal", value="metal"),
        Choice(name="Bass boost", value="bassboost"),
        Choice(name="Bass boost++ (⚠)", value="bassboost++"),
    ])
    @help_utils.add("equalizers choose", "Choose an equalizer to apply it to the currently playing track", "Filters and equalizers", {"equalizer": {"description": "Equalizer to apply", "required": True}})
    async def equalizer_choose_command(self, interaction: discord.Interaction, equalizer: str):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return

        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            
            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed" 
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Can't apply equalizers when no song is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"
        
        eq = await filters_and_eqs.set_equalizer(player, equalizer)
        if not eq:
            await interaction.followup.send(embed=ShortEmbed(description=f"<:x_mark:1028004871313563758> Invalid equalizer preset"), ephemeral=True)
            return "failed"
        
        embed = ShortEmbed(description=f"<:tick:1028004866662084659> Successfully applied equalizer `{equalizer}` to currently playing track")
        await interaction.followup.send(embed=embed)
        self.logger.info(f"Applied eq '{equalizer}' in guild #{interaction.guild.id}")

    @app_commands.command(name="advanced", description="Advanced, 15-band equalizer allows you to change values as you want. Have fun!")
    @app_commands.describe(band="A hertz band you want to apply the gain on")
    @app_commands.describe(gain="A number from -2.5 to 10 [dB]")
    @app_commands.choices(band=[
        Choice(name=str(band_hz) + " Hz", value=band_hz) for band_hz in filters_and_eqs.EQ_HZ_BANDS
    ])
    @help_utils.add("equalizers advanced", "Advanced, 15-band equalizer allows you to change values as you want. Have fun!", "Filters and equalizers", 
                    {"band": {"description": "A hertz band you want to apply the gain on", "required": True}, "gain": {"required": False, "description": "A number from -2.5 to 10 [dB]"}})
    async def equalizer_advanced_command(self, interaction: discord.Interaction, band: int, gain: float):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            
            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed" 
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Can't apply equalizers when no song is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"
        
        if gain < -2.5:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Gain must be between `-2.5` and `10.0`")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed"
        elif gain > 10:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Gain must be between `-2.5` and `10.0`")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed"

        filters: wavelink.Filters = player.filters
        idx = filters_and_eqs.EQ_HZ_BANDS.index(band)
        payload = filters.equalizer.payload
        payload[idx]["gain"] = gain/10
        # convert payload to a list and apply it
        payload = [{"band": x["band"], "gain": x["gain"]} for x in payload.values()]
        filters.equalizer.set(bands=payload)
        await player.set_filters(filters)
        embed = ShortEmbed(description=f"<:tick:1028004866662084659> Equalizer adjusted to a custom preset.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="reset", description="Resets applied equalizers. Similiar to /filters reset")
    @help_utils.add("equalizers reset", "Resets applied equalizers. Similiar to /filters reset", "Filters and equalizers")
    async def eq_reset_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            
            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed" 
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Can't reset equalizers when nothing is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"
        
        filters: wavelink.Filters = player.filters
        filters.equalizer.set([{"band": x, "gain": 0.0} for x in range(15)])
        await player.set_filter(filters) # empty filter for reseting
        embed = ShortEmbed(description=f"<:tick:1028004866662084659> Equalizers have been successfully reset")
        await interaction.followup.send(embed=embed)
        self.logger.info(f"Filters reset in guild #{interaction.guild.id}")
        
    @app_commands.command(name="list", description="List equalizer bands and their gains, look for applied presets")
    @help_utils.add("equalizers list", "List equalizer bands and their gains, look for applied presets", "Filters and equalizers")
    async def equalizers_list_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            
            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed" 
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Can't reset equalizers when nothing is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"
        
        filters: wavelink.Filters = player.filters
        payload = list([x["gain"] for x in filters.equalizer.payload.values()])
        # print(payload)
        embed = NormalEmbed(timestamp=True, footer=FooterType.LICENSED)
        embed.set_author(name="Listing equalizer bands", icon_url=self.bot.user.display_avatar.url)
        
        for i, gain in enumerate(payload, start=1):
            embed.add_field(name=f"Band #{i}: {filters_and_eqs.EQ_HZ_BANDS[i-1]}Hz", value=f"Gain: `{'+' if gain>0 else ''}{gain*10}`")
            
        # look for patterns, convert EQ_PRESETS to a list of gains like payload
        all_eqs = filters_and_eqs.EQ_PRESETS
        preset = ""
        
        for name, bands in all_eqs.items():
            bands = list([x["gain"] for x in bands])
            if bands == payload:
                preset = name
                break
            
        embed.add_field(name="Found preset", value=f"Note that if you change any band after applying a preset it's applied bands are no longer a preset\nPreset: `{'None found' if not preset else preset}`", inline=False)
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    # help_utils.register_command("filters choose", "Select a filter to enchance your music experience", "Playback modifiers", [("filter","Filter to apply",True)])
    # help_utils.register_command("filters reset", "Reset applied filters", "Playback modifiers")
    # help_utils.register_command("equalizers choose", "Choose an equalizer to apply it to the currently playing track", "Playback modifiers", [("equalizer","Equalizer to apply",True)])
    # help_utils.register_command("equalizers advanced", "Advanced, 15-band equalizer allows you to change values as you want. Have fun!", "Playback modifiers", [("band", "A hertz band you want to apply the gain on", True),("gain", "A float-like gain",True)])
    # help_utils.register_command("equalizers reset", "Reset applied equalizers", "Playback modifiers")
    await bot.add_cog(FiltersCog(bot), guilds=bot.guilds)
    await bot.add_cog(EqualizersCog(bot))