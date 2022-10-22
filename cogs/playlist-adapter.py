import discord
from discord.ext import commands
import wavelink

from utils.errors import PlaylistGetError, PlaylistCreationError, PlaylistRemoveError
from music import playlist
from music.core import MusicPlayer
from utils import logger
from utils import help_utils

class PlaylistGroupCog(commands.GroupCog, name="playlists"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

async def setup(bot):
    await bot.add_cog(PlaylistGroupCog(bot), guilds=bot.guilds)