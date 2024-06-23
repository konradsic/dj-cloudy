import datetime
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
# from wavelink.ext import spotify
from lib.ui import emoji
from lib.utils import help_utils

from lib.music.core import MusicPlayer
from lib.logger import logger
from lib.utils.base_utils import (convert_to_double, double_to_int, get_config,
                              get_length, limit_string_to, quiz_check)
from lib.ui.colors import BASE_COLOR
from lib.utils.errors import NoPlayerFound
from lib.utils.regexes import URL_REGEX
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType

logging = logger.Logger("cogs.spotify")

number_complete = {
    0: "🥇 ",
    1: "🥈 ",
    2: "🥉 ",
    3: "4. ",
    4: "5. ",
    5: "6. ",
    6: "7. ",
    7: "8. ",
    8: "9. ",
    9: "10. ",
}

# TODO: Resolve spotify errors

async def spotify_query_complete(
    interaction: discord.Interaction, 
    current: str
) -> t.List[app_commands.Choice[str]]:
    search_type = interaction.namespace.search_type
    query = current.strip("<>")
    try:
        for i in range(20):
            if not re.match(URL_REGEX, query): tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{query}")
            else: tracks = await wavelink.Pool.fetch_tracks(query)
            if not tracks: continue
            break
        # print(tracks)
        if not tracks:
            return []

        if search_type == "tracks":
            return [app_commands.Choice(name =
                    limit_string_to(
                        f"{number_complete[i]}{track.title} (by {track.author}) [{get_length(track.length)}]",
                        100), value=track.uri)
                    for i,track in enumerate(tracks[:10])
                   ]
        return [app_commands.Choice(
            name=limit_string_to(f"📁 {search_type.capitalize()} ({len(tracks)} tracks, {get_length(sum([t.length for t in tracks]))})", 100),
            value=current
        )]
            
    except Exception as e:
        if e.__class__.__name__ == "LoadTrackError": return []
        logging.error(f"Error: {e.__class__.__name__} - {str(e)}")
        return []

@logger.LoggerApplication
class SpotifyExtensionCog(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="spotify", description="Play a spotify track or playlist")
    @app_commands.describe(query="Song or album you want to play", search_type="Search for playlist/album/tracks")
    @app_commands.choices(search_type=[
        app_commands.Choice(name="Tracks", value="tracks"),
        app_commands.Choice(name="Playlist/Album", value="list")
    ])
    @app_commands.autocomplete(query=spotify_query_complete)
    @help_utils.add("spotify", "Play a spotify track or playlist", "Music", {"search_type": {"description": "Search for playlist/album/tracks", "required": True}, "query": {"description": "Song or album you want to play", "required": True}})
    async def spotify_command(self, interaction: discord.Interaction, search_type: str, query: str):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            voice = interaction.user.voice
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            if interaction.user.voice is None:
                embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel
        
        query = query.strip("<>")
        
        for i in range(20):
            if not re.match(URL_REGEX, query): tracks = await wavelink.Pool.fetch_tracks(f"spsearch:{query}")
            else: tracks = await wavelink.Pool.fetch_tracks(query)

            if tracks:
                break
            
            if i == 19:
                await interaction.followup.send(embed=ShortEmbed(
                    description=f"{emoji.XMARK.string} No tracks were found, try again", color=BASE_COLOR
                ))
                return
            
        if search_type == "track":
            tracks = [tracks[0]]
        # print(tracks.raw_data)
        await player.add_tracks(interaction, tracks, spotify=True)


async def setup(bot):
    await bot.add_cog(SpotifyExtensionCog(bot))