import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from lib.logger import logger
from lib.ui.colors import BASE_COLOR
from lib.ui.embeds import FooterType, NormalEmbed, ShortEmbed
from lib.utils import help_utils
from lib.utils.base_utils import djRole_check, quiz_check
from lib.utils.errors import NoPlayerFound
from lib.ui import emoji


@logger.LoggerApplication
class PlayPauseCommands(commands.Cog):
    def __init__(self,bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="pause", description="Pauses currently playing track")
    @help_utils.add("pause", "Pauses currently playing track", "Music")
    async def pause_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")

            voice = interaction.user.voice
            if not voice:
                embed = discord.Embed(description=f"{emoji.XMARK} You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed"

        if player.paused:
            embed = ShortEmbed(description=f"{emoji.PAUSE} The player is already paused")
            await interaction.followup.send(embed=embed)
            return "alr paused"
        
        await player.pause(True)
        embed = ShortEmbed(description=f"{emoji.PAUSE} Playback paused")
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="resume", description="Resumes paused playback")
    @help_utils.add("resume", "Resumes paused playback", "Music")
    async def resume_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "failed"

        if not player.paused:
            embed = ShortEmbed(description=f"{emoji.PLAY} The player is already resumed")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "alr resumed"
        
        await player.pause(False)
        embed = ShortEmbed(description=f"{emoji.PLAY} Playback resumed")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayPauseCommands(bot))