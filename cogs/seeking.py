import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.ui.colors import BASE_COLOR
from lib.utils.regexes import URL_REGEX
from lib.utils.errors import NoPlayerFound
from lib.utils.base_utils import convert_to_double, double_to_int, djRole_check, quiz_check
from lib.logger import logger
from lib.utils.configuration import ConfigurationHandler
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
from lib.ui import emoji

@logger.LoggerApplication
class SeekAndRestartCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="restart", description="Restart current playing track (similiar to seek position: 0:00)")
    @help_utils.add("restart", "Restart current playing track (similiar to seek position: 0:00)", "Music")
    async def restart_command(self, interaction: discord.Interaction):
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

        if not player.playing:
            embed = ShortEmbed(description=f"{emoji.XMARK} Can't restart when nothing is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"

        await player.seek(0) # restart
        embed = ShortEmbed(description=f"{emoji.SEEK} Track successfully restarted")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="seek", description="Seek the player to given position")
    @app_commands.describe(position="Position you want for player to seek ([h:]m:s). If none is provided it will seek forwards/backwards by configured amount of seconds")
    @help_utils.add("seek", "Seek the player to given position", "Music", {"position": {"description": "Position you want for player to seek ([h:]m:s). If none is provided it will seek forward by 15s", "required": False}})
    async def seek_command(self, interaction: discord.Interaction, position: str=None):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        cfg = ConfigurationHandler(interaction.user.id, user=True)
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

        if not player.playing:
            embed = ShortEmbed(description=f"{emoji.XMARK} Can't seek when nothing is playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "not playing"

        # check if user inputted correct position
        if position is None:
            seekForward = cfg.data["seekForward"]["value"]
            seeklength = cfg.data["defaultSeekAmount"]["value"]
            if seekForward:
                if player.position/1000+seeklength > player.queue.current_track.length/1000:
                    embed = ShortEmbed(description=f"{emoji.XMARK} Can't seek out of bounds")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                await player.seek(int(round(player.position/1000+seeklength)*1000))
            else:
                if player.position/1000-seeklength < 0:
                    embed = ShortEmbed(description=f"{emoji.XMARK} Can't seek out of bounds")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                await player.seek(int(round(player.position/1000-seeklength)*1000))
            embed = ShortEmbed(description=f"{emoji.SEEK} Seeking {'forward' if seekForward else 'backwards'} by `{seeklength} seconds`")
            await interaction.followup.send(embed=embed)
            return "relative seek success!"
        h,m,s = 0,0,0
        try:
            pos = position.split(":")
            if len(pos) == 3: # hours
                h = double_to_int(pos[0])
                m = double_to_int(pos[1])
                s = double_to_int(pos[2])
            elif len(pos) == 2:
                m = double_to_int(pos[0])
                s = double_to_int(pos[1])
            else:
                raise ValueError("Incorrect position format")
        except Exception as e:
            self.logger.error(f"Failed to get position parameters caused by {e.__class__.__name__}: {str(e)}")
            embed = ShortEmbed(description=f"{emoji.XMARK} Invalid player position, use format [h:]m:s e.g `2:15` or `1:39:56`")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "incorrect position"

        seek_pos = ((h*3600)+(m*60)+s)*1000
        if not (0 <= int(seek_pos/1000) <= int(player.queue.current_track.length)):
            embed = ShortEmbed(description=f"{emoji.XMARK} Cannot seek: position out of bounds")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "incorrect position"
        try:
            await player.seek(seek_pos)
            embed = ShortEmbed(description=f"{emoji.SEEK} Successfully seeked to position `{str(h) + ':' if h != 0 else ''}{convert_to_double(m) if h >= 1 else m}:{convert_to_double(s)}`")
            await interaction.followup.send(embed=embed)
            return "success!"
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} Failed to seek, please try again")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return "seek failed"

async def setup(bot):
    await bot.add_cog(SeekAndRestartCog(bot))