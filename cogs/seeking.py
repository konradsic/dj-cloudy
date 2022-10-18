import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils.regexes import URL_REGEX
from utils.errors import NoPlayerFound

class SeekAndRestartCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="restart", description="Restart current playing track (similiar to seek position:0)")
    async def restart_command(self, interaction: discord.Interaction):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                    raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "failed"

        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Can't restart when nothing is playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "not playing"

        await player.seek(0) # restart
        embed = discord.Embed(description=f"<:seek_button:1030534160844062790> Track successfully restarted",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    help_utils.register_command("restart", "Restart current playing track (similiar to seek position:0)", "Music: Advanced commands")
    await bot.add_cog(SeekAndRestartCog(bot),
                guilds=[discord.Object(id=g.id) for g in bot.guilds])