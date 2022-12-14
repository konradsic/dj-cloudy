import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils.regexes import URL_REGEX
from utils.errors import NoPlayerFound
from utils.base_utils import convert_to_double, double_to_int
from utils import logger

@logger.LoggerApplication
class SeekAndRestartCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="restart", description="Restart current playing track (similiar to seek position:0)")
    async def restart_command(self, interaction: discord.Interaction):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "failed"

        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't restart when nothing is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "not playing"

        await player.seek(0) # restart
        embed = discord.Embed(description=f"<:seek_button:1030534160844062790> Track successfully restarted",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="seek", description="Seek the player to given position")
    @app_commands.describe(position="Position you want for player to seek ([h:]m:s). If none is provided it will seek forward by 15s")
    async def seek_command(self, interaction: discord.Interaction, position: str=None):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                    raise NoPlayerFound("There is no player connected in this guild")
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "failed"

        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't seek when nothing is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "not playing"

        # check if user inputted correct position
        if position is None:
            if player.position+15 > player.queue.current_track.length:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't seek out of bounds",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return "cannot seek forward"
            await player.seek(int((player.position+15)*1000))
            embed = discord.Embed(description="<:seek_button:1030534160844062790> Seeked forward by `15 seconds`", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "15s forward success!"
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
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Invalid player position, use format [h:]m:s e.g `2:15` or `1:39:56`",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "incorrect position"

        seek_pos = ((h*3600)+(m*60)+s)*1000
        if not (0 <= int(seek_pos/1000) <= int(player.queue.current_track.length)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot seek: position out of bounds",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "incorrect position"
        try:
            await player.seek(seek_pos)
            embed = discord.Embed(description=f"<:seek_button:1030534160844062790> Successfully seeked to position `{str(h) + ':' if h != 0 else ''}{convert_to_double(m) if h >= 1 else m}:{convert_to_double(s)}`", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "success!"
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to seek, please try again",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "seek failed"

async def setup(bot):
    help_utils.register_command("seek", "Seek the player to given position", "Music: Advanced commands", [("position","Position you want for player to seek ([h:]m:s). If none is provided it will seek forward by 15s",False)])
    help_utils.register_command("restart", "Restart current playing track (replay)", "Music: Advanced commands")
    await bot.add_cog(SeekAndRestartCog(bot),
                guilds=[discord.Object(id=g.id) for g in bot.guilds])