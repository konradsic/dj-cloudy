import datetime

import discord
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils import logger
from music.quiz import get_random_song

@logger.LoggerApplication
class MusicQuizCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger
        
    @app_commands.command(name="randomsong", description="Get random song [BETA/TEST]")
    async def randomsong_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        song = await get_random_song()

        await interaction.followup.send(f"{song.title}, {song.author}")

async def setup(bot):
    await bot.add_cog(MusicQuizCog(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
