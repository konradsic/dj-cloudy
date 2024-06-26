import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.ui.colors import BASE_COLOR
from lib.utils.configuration import ConfigurationHandler
from lib.utils.base_utils import djRole_check, quiz_check
from lib.logger import logger
from lib.ui import emoji as emojilib
# from music.core import some-import
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType

@logger.LoggerApplication
class VolumeController(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="volume", description="Set or get current playback volume")
    @app_commands.describe(value="Value to set the volume to")
    @help_utils.add("volume", "Set or get current playback volume", "Music", arguments={"value": {"description": "Value to set the volume to", "required": False}})
    async def volume_command(self, interaction: discord.Interaction, value: int=None):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        cfg = ConfigurationHandler(id=interaction.guild.id, user=False)
        if not voice:
            embed = ShortEmbed(description=f"{emojilib.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emojilib.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emojilib.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not player.playing:
            embed = ShortEmbed(description=f"{emojilib.XMARK} Nothing is currently playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        volume = player.volume
        if value is None:
            emoji = ""
            if volume == 0: emoji = emojilib.VOLUME_NONE
            if (1 <= volume <= 60): emoji = emojilib.VOLUME_LOW
            if (61 <= volume <= 90): emoji = emojilib.VOLUME_MID
            if (91 <= volume <= 1000): emoji = emojilib.VOLUME_HIGH

            embed = ShortEmbed(description=f"{emoji} Current volume is set to `{volume}%`")
            await interaction.followup.send(embed=embed)
            return
        
        maxVolume = cfg.data["maxVolume"]["value"]
        if value is not None:
            if not (0 <= value <= maxVolume):
                embed = ShortEmbed(description=f"{emojilib.XMARK} Volume value out of range! (max. `{maxVolume}`)")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        if not await djRole_check(interaction, self.logger): return
        await player.set_volume(value)

        emoji = ""
        if value == 0: emoji = emojilib.VOLUME_NONE
        if (1 <= value <= 60): emoji = emojilib.VOLUME_LOW
        if (61 <= value <= 90): emoji = emojilib.VOLUME_MID
        if (91 <= value <= 1000): emoji = emojilib.VOLUME_HIGH
        embed = ShortEmbed(description=f"{emoji} Volume successfully set to `{value}%`")
        await interaction.followup.send(embed=embed)
        

async def setup(bot):
    await bot.add_cog(VolumeController(bot))
