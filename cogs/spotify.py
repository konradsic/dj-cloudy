import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils.regexes import URL_REGEX
from utils.errors import NoPlayerFound
from utils.base_utils import convert_to_double, double_to_int, get_config
from utils import logger
from wavelink.ext import spotify

@logger.LoggerApplication
class SpotifyExtensionCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="spotify", description="Play a spotify track or album")
    @app_commands.describe(query="Song or album you want to play")
    async def spotify_command(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        query = query.strip("<>")
        parts = query.split("/")
        for part in parts:
            if part.lower() == "track":
                return_first = True
            elif part.lower() == "playlist":
                return_first = False
        results = await spotify.SpotifyTrack.search(query=query, return_first=return_first)
        if isinstance(results, list): # playlist
            return

async def setup(bot):
    help_utils.register_command("spotify", "Play a spotify track or album", "Extensions/Plugins", [("query","Song or album you want to play",True)])
    await bot.add_cog(SpotifyExtensionCog(bot), guilds=bot.guilds)