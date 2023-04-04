import datetime
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils import lyrics_handler as lhandler
from utils.base_utils import get_lyrics_token
from utils.buttons import EmbedPaginator
from utils.colors import BASE_COLOR
from utils.regexes import URL_REGEX
from utils import logger

@logger.LoggerApplication
class LyricsCommandHandler(commands.Cog):
    def __init__(self, bot, logger):
        self.logger = logger
        self.bot = bot

    @app_commands.command(name="lyrics", description="Get lyrics for current playing or input song")
    @app_commands.describe(song="Song you want lyrics for")
    async def lyrics_command(self, interaction: discord.Interaction, song: str = None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not (player := self.bot.node.get_player(interaction.guild.id)) and (song is None):
            try:
                playing = player.is_playing()
            except:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot get lyrics for `noSong`: Nothing is playing and the `song` argument is also `None`",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        client = lhandler.initialize_client(access_token=get_lyrics_token())
        title, artist = None,None
        if not song: # we need to get current song
            title = player.queue.current_track.title
            artist = player.queue.current_track.author.strip("- Topic")
        else:
            if not re.match(URL_REGEX, song):
                song = "ytmsearch:" + song
            try:
                queried_song = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=song)
                queried_song = queried_song[0]
                title = queried_song.title
                artist = queried_song.author
            except:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No song with given name was found. Try inputing a different song",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        try:
            song = lhandler.get_lyrics(client, artist, title)
            lyrics = song[0]
            title = song[1]
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No lyrics were found. Try inputing a different song",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        # paginator yay
        # split for 35 lines each
        lyrics = lyrics.split("\n")
        for i in range(len(lyrics)):
            line = lyrics[i]
            if line.startswith(f"{title} Lyrics"):
                lyrics[i] = line[len(f"{title} Lyrics"):]
            elif line.endswith("You might also likeEmbed"):
                lyrics[i] = line[:-len("You might also likeEmbed")]
            # after removing
            if line.endswith("Embed"):
                lyrics[i] = line[:-len("Embed")]
            # just realised that it can also start with that sht
            if line.startswith("You might also like"):
                lyrics[i] = line[len("You might also like"):]
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
    help_utils.register_command("lyrics", "Get lyrics for current playing or input song", "Miscellaneous", [("song","Song you want lyrics for", False)])
    await bot.add_cog(
        LyricsCommandHandler(bot),
        guilds =[discord.Object(id=g.id) for g in bot.guilds]
    )
