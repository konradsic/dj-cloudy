import datetime
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils import lyrics_handler as lhandler
from utils.colors import BASE_COLOR
from utils.regexes import URL_REGEX
from utils.run import running_nodes


class LyricsCommandHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lyrics", description="Get lyrics for current playing or input song")
    @app_commands.describe(song="Song you want lyrics for")
    async def lyrics_command(self, interaction: discord.Interaction, song: str = None):
        if not (player := self.bot.node.get_player(interaction.guild)) and (song is None):
            try:
                playing = player.is_playing()
            except:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot get lyrics for `noSong`: Nothing is playing and the `song` argument is also `None`",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed)
                return

        client = lhandler.initialize_client(access_token="G_9Jh1MKwT-fy2vwUyemY641bX8B-vxg2HAcaHaLk5Mke4-tf__8h-ZAyIdtK9Wc")
        title, artist = None,None
        if not song: # we need to get current song
            title = player.queue.current_track.title
            artist = player.queue.current_track.author
        else:
            if not re.match(URL_REGEX, song):
                song = "ytmsearch:" + song
            queried_song = await running_nodes[0].get_tracks(cls=wavelink.Track, query=song)
            queried_song = queried_song[0]
            title = queried_song.title
            artist = queried_song.author
        if not title:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No lyrics were found. Try inputing a different song",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        lyrics = lhandler.get_lyrics(client, artist, title)
        # paginator yay
        # split for 35 lines each
        lyrics = lyrics.split("\n")
        for i in range(len(lyrics)):
            line = lyrics[i]
            if line.startswith(f"{title} Lyrics"):
                lyrics[i] = line[len(f"{title} Lyrics"):]
            elif line.endswith("You might also likeEmbed"):
                lyrics[i] = line[:-len("You might also likeEmbed")]
        if len(lyrics) <= 35:
            lyric_groups = [lyrics]
        else:
            groups = len(lyrics)//35
            lyric_groups = []
            for i in range(groups):
                lyric_groups.append(lyrics[0:36])
                for _ in range(35):
                    del lyrics[0]
            lyric_groups.append(lyrics)
        

async def setup(bot):
    await bot.add_cog(
        LyricsCommandHandler(bot),
        guilds =[discord.Object(id=g.id) for g in bot.guilds]
    )
