import datetime
import math
from enum import Enum
from time import time

import discord
import utils.logger as log
import wavelink
from discord.ext import commands
from utils.buttons import PlayButtonsMenu
from utils.colors import BASE_COLOR
from utils.errors import (AlreadyConnectedToVoice, NotConnectedToVoice,
                          NoTracksFound, NoVoiceChannel, QueueIsEmpty)
from music.queue import Queue
from utils.base_utils import RepeatMode

logger = log.Logger().get("music.core")

def convert_to_double(val):
    if val < 10:
        return "0" + str(val)
    return val

def shorten_name(string):
    if len(string) > 25:
        return string[:25] + "..."
    return string

class MusicPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused_vc = False
        self.queue = Queue()
        self.bound_channel = None

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
            if lh >= 1:
                lm = convert_to_double(lm)
            ls = convert_to_double(ls)
            try: # add thumbnail
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            except: pass
            embed.add_field(name="Track title", value=f"[**{track.title}**]({track.uri})", inline=False)
            embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{lh + ':' if lh != 0 else ''}{lm}:{ls}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
        if self.is_playing():
            embed = discord.Embed(
                title = "<:play_button:1028004869019279391> Added song to the queue",
                color = BASE_COLOR,
                timestamp = datetime.datetime.utcnow()
            )
            dur = track.duration
            lm, ls = divmod(dur,60)
            lh, lm = divmod(lm, 60)
            ls, lm, lh = math.floor(ls), math.floor(lm), math.floor(lh)
            if lh >= 1:
                lm = convert_to_double(lm)
            ls = convert_to_double(ls)
            try: # add thumbnail
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            except: pass
            embed.add_field(name="Track title", value=f"[**{track.title}**]({track.uri})", inline=False)
            embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{lh + ':' if lh != 0 else ''}{lm}:{ls}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
            # calculating estimated time to play this song
            current_pos = self.position
            current_len = self.queue.current_track.duration
            to_end = current_len-current_pos
            upc_tracks = self.queue.upcoming_tracks[:-1]
            for upcoming in upc_tracks:
                to_end += upcoming.duration
            durm, durs = divmod(to_end,60)
            durh, durm = divmod(durm, 60)
            durs, durm, durh = math.floor(durs), math.floor(durm), math.floor(durh)
            if durh >= 1:
                durm = convert_to_double(durm)
            durs = convert_to_double(durs)
            embed.add_field(name="Estimated time until playback", value=f"`{durh + ':' if durh != 0 else ''}{durm}:{durs}`")
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
        await interaction.response.send_message(embed=embed, view=PlayButtonsMenu(user=interaction.user))

        if not self.is_playing():
            await self.start_playback(interaction)

    async def start_playback(self, interaction: discord.Interaction=None): # interaction used for logging info
        try:
            message = f"(guild:`{interaction.guild.name}` channel:`{interaction.user.voice.channel.name}`)"
        except:
            message = "(No additional interaction info)"
        logger.log("start-playback", f"Playing {self.queue.current_track.uri} {message}")
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            print(self.queue.current_track, self.queue.first_track, self.queue.position, len(self.queue))
            if self.queue.repeat.mode == RepeatMode.REPEAT_CURRENT_TRACK:
                logger.log("MusicPlayer.advance", f"Repeating current track (guild: {self.guild.name})")
                await self.play(self.queue.current_track)
                return
            elif self.queue.repeat.mode == RepeatMode.REPEAT_QUEUE:
                if self.queue.position == (len(self.queue)-1):
                    logger.log("MusicPlayer.advance", f"Repeating queue (guild: {self.guild.name})")
                    first = self.queue.first_track
                    await self.play(first)
                    return
            next_track = self.queue.get_next_track()
            if next_track is not None:
                await self.play(next_track)
        except QueueIsEmpty:
            return False
