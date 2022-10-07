import datetime
import re

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music.core import MusicPlayer
from utils import logger
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound
from utils.regexes import URL_REGEX

logging = logger.Logger().get("cogs.play")

class PlayCommand(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="play", description="Plays music")
    @app_commands.describe(query="What song to play")
    async def play_command(self, interaction: discord.Interaction, query: str):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except:
            try:
                channel = interaction.user.voice.channel
                await channel.connect(cls=MusicPlayer, self_deaf=True)
                player = self.bot.node.get_player(interaction.guild)
            except: 
                await interaction.response.send_message("You're not connected to a voice channel")
                return "failed"

        if not (re.match(URL_REGEX, query)):
            query = f"ytmsearch:{query}"

        query = query.strip("<>")
        tracks = await self.bot.node.get_tracks(cls=wavelink.Track, query=query)
        await player.add_tracks(interaction, tracks)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        PlayCommand(bot),
        guilds =[discord.Object(id=g.id) for g in bot.guilds]
    )
