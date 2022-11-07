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
from music.core import MusicPlayer

@logger.LoggerApplication
class SpotifyExtensionCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="spotify", description="Play a spotify track or album")
    @app_commands.describe(query="Song or album you want to play")
    async def spotify_command(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except:
            if interaction.user.voice is None:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel
        query = query.strip("<>")
        parts = query.split("/")
        return_first = -1
        for part in parts:
            if part.lower() == "track":
                return_first = True
            elif part.lower() == "playlist":
                return_first = False
        if return_first == -1:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> To play a Spotify track enter a valid playlist/track URL",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        results = await spotify.SpotifyTrack.search(query=query, return_first=return_first)
        if isinstance(results, list): # playlist
            await player.add_tracks(interaction, results)
            self.logger.info("Spotify search executed successfully - added playlist to queue")
            return
        await player.add_tracks(interaction, [results])
        self.logger.info("Spotify search executed successfully - added song to queue")

async def setup(bot):
    help_utils.register_command("spotify", "Play a spotify track or album", "Extensions/Plugins", [("query","Song or album you want to play",True)])
    await bot.add_cog(SpotifyExtensionCog(bot), guilds=bot.guilds)