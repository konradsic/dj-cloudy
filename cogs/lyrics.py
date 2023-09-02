import datetime
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.buttons import EmbedPaginator
from utils.colors import BASE_COLOR
from utils.regexes import URL_REGEX
from utils import logger
from music.songs import (
    GeniusAPIClient, 
    SearchResponse, 
    GeniusSong
)
from unidecode import unidecode
from utils.base_utils import quiz_check

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
    @app_commands.describe(song="Song you want lyrics for")
    async def lyrics_command(self, interaction: discord.Interaction, song: str = None):
        if not await quiz_check(self.bot, interaction, self.logger): return
        await interaction.response.defer(ephemeral=True, thinking=True)
        if song is None:
            voice = interaction.user.voice
            if not voice:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if not (player := self.bot.node.get_player(interaction.guild.id)):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            try:
                playing = player.is_playing()
                if not playing: raise Exception
            except:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot get lyrics for `noSong`: Nothing is playing and the `song` argument is also `None`",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        client: GeniusAPIClient = self.bot.genius
        title, artist = None,None
        before_song = song or "" + ""
        if not song: # we need to get current song
            title = player.queue.current_track.title
            author = player.queue.current_track.author
            artist = author[:-len("- Topic")] if author.endswith("- Topic") else author
        else:
            if not re.match(URL_REGEX, song):
                song = "ytsearch:" + song
            try:
                queried_song = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=song)
                if queried_song:
                    queried_song = queried_song[0]
                    title = queried_song.title
                    artist = queried_song.author
                else:
                    title = before_song
                    artist = "Unknown"
            except Exception as e:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No song with given name was found. Try inputing a different song",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                print(e)
                return

        try:
            title = remove_brackets(title)
            try:
                song = client.get_lyrics(unidecode(title) + " " + unidecode(artist))
            except:
                song = client.get_lyrics(unidecode(title))
            lyrics = "".join("`"+e+"`\n" if e.startswith("[") else e + "\n" for e in song.split("\n"))
            title = title + " by " + artist
        except Exception as e:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No lyrics were found. Try inputing a different song",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            print(e.__class__.__name__, str(e))
            return
        # paginator yay
        # split for 35 lines each
        lyrics = lyrics.split("\n")
        if len(lyrics) <= 35:
            lyric_groups = [lyrics]
        else:
            groups = len(lyrics)//35
            lyric_groups = []
            for i in range(groups):
                lyric_groups.append(lyrics[0:35])
                for _ in range(35):
                    del lyrics[0]
            lyric_groups.append(lyrics)
        
        embeds = []
        for i,group in enumerate(lyric_groups,1):
            embeds.append(discord.Embed(
                title = f"Displaying lyrics for {title}",
                description="".join(e + "\n" for e in group),
                color=BASE_COLOR,
                timestamp=datetime.datetime.utcnow()
            ).set_footer(text="Page {}/{}".format(i, len(lyric_groups))).set_thumbnail(url=self.bot.user.display_avatar.url))
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(embeds, 1000, interaction.user))

async def setup(bot):
    help_utils.register_command("lyrics", "Get lyrics for current playing or input song", "Music", [("song","Song you want lyrics for", False)])
    await bot.add_cog(
        LyricsCommandHandler(bot)
    )
