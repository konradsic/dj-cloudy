import wavelink
from discord.ext import commands
import discord
from system.music.queue import Queue
import system.utils.logger as log
from system.utils.errors import (
    #NotConnectedToVoice,
    #AlreadyConnectedToVoice,
    NoTracksFound,
    QueueIsEmpty
)

logger = log.LoggerInstance(log.LoggingType.INFO,"system.music.core")

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
        await interaction.response.send_message(f"Added {tracks[0].title} to the queue.")

        if not self.is_playing():
            await self.start_playback(interaction)

    async def start_playback(self, interaction: discord.Interaction=None): # interaction used for logging info
        try:
            message = f"(guild:`{interaction.guild.name}` channel:`{interaction.user.voice.channel.name}`)"
        except:
            message = "(No additional interaction info)"
        logger.log("MusicPlayer.start_playback", f"Playing {self.queue.current_track} {message}")
        await self.play(self.queue.current_track)
        

    async def advance(self):
        try:
            if (track := self.queue.next_track) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass