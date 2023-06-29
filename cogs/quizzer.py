import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from music.quiz import Round, get_random_song
from utils import help_utils, logger
from utils.colors import BASE_COLOR


@logger.LoggerApplication
class MusicQuizCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger
        
    @app_commands.command(name="randomsong", description="Get random song [BETA/TEST]")
    async def randomsong_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        song = await get_random_song()

        music_round = Round([], song, 120, wavelink.Player, [15, 60, 110])
        music_round.reveal_song_letter()
        await interaction.followup.send(song.title + "\n`" + music_round.song_string + "`")

async def setup(bot):
    await bot.add_cog(MusicQuizCog(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
