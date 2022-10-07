import datetime
from time import time
import math
import discord
import utils.logger as log
import wavelink
from discord.ext import commands
from utils.colors import BASE_COLOR
from utils.errors import (  # NotConnectedToVoice,; AlreadyConnectedToVoice,
    NoTracksFound, QueueIsEmpty)

from music.queue import Queue

logger = log.Logger().get("music.core")

class MusicPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused_vc = False
        self.queue = Queue()

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, interaction: discord.Interaction, tracks: list):
        if not tracks:
            raise NoTracksFound

        self.queue.add(tracks[0])
        track = tracks[0]
        if not self.is_playing():
            embed = discord.Embed(
                title="<:play_button:1028004869019279391> Now playing",
                color = BASE_COLOR,
                timestamp = datetime.datetime.utcnow()
            )
            dur = track.duration
            lm, ls = divmod(dur,60)
            lh, lm = divmod(lm, 60)
            ls, lm, lh = math.floor(ls), math.floor(lm), math.floor(lh)
            try: # add thumbnail
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            except: pass
            embed.add_field(name="Track title", value=track.title)
            embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{lh + ':' if lh != 0 else ''}{lm}:{ls}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

        if not self.is_playing():
            await self.start_playback(interaction)

    async def start_playback(self, interaction: discord.Interaction=None): # interaction used for logging info
        try:
            message = f"(guild:`{interaction.guild.name}` channel:`{interaction.user.voice.channel.name}`)"
        except:
            message = "(No additional interaction info)"
        logger.log("start-playback", f"Playing {self.queue.current_track} {message}")
        await self.play(self.queue.current_track)
        

    async def advance(self):
        try:
            if (track := self.queue.next_track) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass
