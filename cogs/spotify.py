import datetime
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from wavelink.ext import spotify

from music.core import MusicPlayer
from utils import emoji, help_utils, logger
from utils.base_utils import (convert_to_double, double_to_int, get_config,
                              get_length, limit_string_to, quiz_check)
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound
from utils.regexes import URL_REGEX

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

async def spotify_query_complete(
    interaction: discord.Interaction, 
    current: str
) -> t.List[app_commands.Choice[str]]:
    search_type = interaction.namespace.search_type
    query = current.strip("<>")
    counter = 0
    try:
        while True:
            counter += 1
            if counter == 101: break
            tracks = await spotify.SpotifyTrack.search(query, node=wavelink.NodePool.get_connected_node())
            if not tracks: continue
            break
        if not tracks:
            return []

        if search_type == "track":
            return [app_commands.Choice(name =
                    limit_string_to(
                        f"{number_complete[i]}{'[E] ' if track.explicit else ''}{track.title} (by {', '.join(track.artists)}) [{get_length(track.length)}]",
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
    @app_commands.describe(query="Song or album you want to play", search_type="What to search for (playlist/album/track)")
    @app_commands.autocomplete(query=spotify_query_complete)
    @app_commands.choices(search_type=[
        app_commands.Choice(name="Playlist", value="playlist"),
        app_commands.Choice(name="Album", value="album"),
        app_commands.Choice(name="Track", value="track")
    ])
    async def spotify_command(self, interaction: discord.Interaction, search_type: str, query: str):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := self.bot.node.get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            voice = interaction.user.voice
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except:
            if interaction.user.voice is None:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel
        
        query = query.strip("<>")
        track = await spotify.SpotifyTrack.search(query, node=wavelink.NodePool.get_connected_node())
        
        try:
            if search_type == "track":
                tracks = [track[0]]
            elif search_type == "album" or search_type == "playlist":
                tracks = track
        except:
            await interaction.followup.send(embed=discord.Embed(
                description=f"{emoji.XMARK.string} No tracks were found, try again", color=BASE_COLOR
            ))
        
        await player.add_tracks(interaction, tracks, spotify=True)


async def setup(bot):
    help_utils.register_command("spotify", "Play a spotify track or album", "Extensions/Plugins", [("query","Song or album you want to play",True)])
    await bot.add_cog(SpotifyExtensionCog(bot), guilds=bot.guilds)