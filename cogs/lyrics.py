import datetime
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.ui.buttons import EmbedPaginator
from lib.ui.colors import BASE_COLOR
from lib.utils.regexes import URL_REGEX
from lib.logger import logger
from lib.music.songs import (
    GeniusAPIClient, 
    SearchResponse, 
    GeniusSong
)
from unidecode import unidecode
from lib.utils.base_utils import quiz_check
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
import traceback

def remove_brackets(string):
    replace_matcher = {
        "[": "(",
        "]": ")",
        "{": "(",
        "}": ")"
    }
    for k,v in replace_matcher.items():
        string = string.replace(k, v)
    
    string = re.sub("\(.*?\)", "", string)
    return string.strip()

@logger.LoggerApplication
class LyricsCommandHandler(commands.Cog):
    def __init__(self, bot, logger):
        self.logger = logger
        self.bot = bot

    @app_commands.command(name="lyrics", description="Get lyrics for current playing or input song")
    @app_commands.describe(song="Song you want lyrics for", raw_search="Search across genius lyrics, not parsing the title through ytsearch", hidden="Should the message be ephemeral")
    async def lyrics_command(self, interaction: discord.Interaction, song: str = None, raw_search: bool=False, hidden: bool=True):
        if not await quiz_check(self.bot, interaction, self.logger): return
        await interaction.response.defer(ephemeral=hidden, thinking=True)
        if song is None:
            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            try:
                playing = player.playing
                if not playing: raise Exception
            except:
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Cannot get lyrics for `None`: Nothing is playing and the `song` argument is also `None`")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        client: GeniusAPIClient = self.bot.genius
        title, artist = song,""
        before_song = song or "" + ""
        if not song: # we need to get current song
            title = player.queue.current_track.title
            author = player.queue.current_track.author
            artist = author[:-len("- Topic")] if author.endswith("- Topic") else author
        else:
            if not raw_search:
                if not re.match(URL_REGEX, song):
                    song = "ytsearch:" + song
                try:
                    queried_song = await self.bot.node.get_tracks(cls=wavelink.Playable, query=song)
                    if queried_song:
                        queried_song = queried_song[0]
                        title = queried_song.title
                        artist = queried_song.author
                    else:
                        title = before_song
                        artist = "Unknown"
                except Exception as e:
                    embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> No song with given name was found. Try inputing a different song")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    print(e)
                    return

        try:
            title = remove_brackets(title or "")
            genius_title, genius_author = None, None
            try:
                song = client.get_lyrics(unidecode(title) + " " + unidecode(artist))
                genius = client.get_song(unidecode(title) + " " + unidecode(artist))
            except:
                song = client.get_lyrics(unidecode(title))
                genius = client.get_song(unidecode(title))
            # print(unidecode(title))
            genius_author = genius.artist
            genius_title = genius.short_title
            lyrics = "".join("`"+e+"`\n" if e.startswith("[") else e + "\n" for e in song.split("\n"))
            title = f"{genius_title} by {genius_author} ({title if not raw_search else 'genius search'})"
        except Exception as e:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> No lyrics were found. Try entering a different song")
            await interaction.followup.send(embed=embed, ephemeral=True)
            traceback.print_exc()
            return
        # paginator yay
        # split for max. 1024 characters each
        lyrics_length = len(lyrics)
        lyrics = lyrics.split("\n")
        if lyrics_length <= 1024:
            lyric_groups = [lyrics]
        else:
            lyric_groups = [""]
            while lyrics: # del el. 0, move to lyrics_groups
                if len(lyric_groups[-1]) > 1024:
                    lyric_groups[-1].strip("\n")
                    # new
                    lyric_groups.append("")
                # add
                lyric_groups[-1] += lyrics[0] + "\n"
                del lyrics[0]
        
        embeds = []
        for i,group in enumerate(lyric_groups,1):
            embeds.append(NormalEmbed(
                title = f"Displaying lyrics for {title}",
                description=group,
                timestamp=True
            ).set_footer(text="Page {}/{}".format(i, len(lyric_groups))).set_thumbnail(url=self.bot.user.display_avatar.url))
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(embeds, 1000, interaction.user))

async def setup(bot):
    help_utils.register_command("lyrics", "Get lyrics for current playing or input song", "Music", [("song","Song you want lyrics for", False)])
    await bot.add_cog(
        LyricsCommandHandler(bot)
    )
