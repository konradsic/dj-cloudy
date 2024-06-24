"""
Why lib.ui.conflicted_ui?
Due to circular imports, which occur when two or more modules depend on each other directly or indirectly, creating a loop. 
This dependency loop can cause issues when the interpreter tries to load these modules because 
Python's import system works by executing the code in a module when it is imported for the first time.

Here's an example:
file: lib.music.core
`from lib.ui.buttons import PlayButtonsMenu`
but in lib.ui.buttons
`from lib.music.core import MusicPlayer`

This issue can be solved by creating a separate file like this which won't cause circular imports 
i.e. (PlayButtonsMenu don't require MusicPlayer, but SearchResultsButtons do, but they aren't imported by lib.music.core which solves the issue)
"""
import re
import traceback
import typing as t

import discord
import wavelink
from discord import ui
from discord.ui import View
from unidecode import unidecode

from ..music.core import MusicPlayer
from ..music.songs import GeniusAPIClient
from . import emoji
from .buttons import EmbedPaginator
from .embeds import NormalEmbed, ShortEmbed
from .colors import BASE_COLOR
from ..music import playlist


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

class SearchResultsButtons(View):
    def __init__(self, timeout: float=None, tracks: list[wavelink.Playable]=[], bot: discord.ext.commands.Bot=None, original_query: str="") -> None:
        super().__init__(timeout=timeout)
        self.timeout = timeout
        self.tracks = tracks
        self.bot = bot
        self.ogquery = original_query
        
        if len(self.tracks) > 1:
            self.children[1].disabled = True
            self.children[2].disabled = True

    @ui.button(label="Add to queue", emoji=str(emoji.PLUS), style=discord.ButtonStyle.gray)
    async def add_to_queue(self, interaction: discord.Interaction, button):
        await interaction.response.defer(thinking=True)
        voice = interaction.user.voice
        if interaction.user.voice is None:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel
        except: 
            # already connected, get player
            player = wavelink.Pool.get_node().get_player(interaction.guild.id)
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        
        await player.add_tracks(interaction, self.tracks)
        
    @ui.button(emoji=str(emoji.SEARCH), label="Search for lyrics")
    async def search_lyrics(self, interaction: discord.Interaction, button):
        await interaction.response.defer(thinking=True)
        og = self.ogquery
        song = self.tracks[0].title
        artist = self.tracks[0].author
        client: GeniusAPIClient = self.bot.genius
        title, artist = song,""
        before_song = song or "" + ""
        try:
            title = remove_brackets(title or "")
            genius_title, genius_author = None, None
            try:
                song = client.get_lyrics(unidecode(og))
                genius = client.get_song(unidecode(og))
            except:
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
            title = f"{genius_title} by {genius_author}"
        except Exception as e:
            embed = ShortEmbed(description=f"{emoji.XMARK} No lyrics were found. Try entering a different song")
            await interaction.followup.send(embed=embed, ephemeral=True)
            traceback.print_exc()
            return

        # paginator yay
        # split for max. 1024 characters each
        lyrics_length = len(lyrics)
        lyrics = lyrics.split("\n")
        if lyrics_length <= 1024:
            lyric_groups = ["\n".join(lyrics)]
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
        
    @ui.button(emoji=str(emoji.STAR), style=discord.ButtonStyle.gray)
    async def star_button(self, interaction: discord.Interaction, button):
        await interaction.response.defer(thinking=True)

        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        resp = handler.add_to_starred(self.tracks[0].uri)
        if resp:
            await interaction.followup.send(ephemeral=True,embed=discord.Embed(description=f"{emoji.TICK1} Added **{self.tracks[0].title}** to your {emoji.STAR} playlist", color=BASE_COLOR))
            return
        await interaction.followup.send(ephemeral=True,embed=discord.Embed(description=f"{emoji.TICK1} Un-starred **{self.tracks[0].title}**", color=BASE_COLOR))
        
