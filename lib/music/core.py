import datetime
import math
from enum import Enum
from time import time

import discord
import spotipy
import wavelink
from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials

import lib.logger.logger as log
from lib.music.queue import Queue
from lib.ui import emoji
from lib.ui.buttons import PlayButtonsMenu
from lib.ui.colors import BASE_COLOR
from lib.ui.embeds import FooterType, ShortEmbed, random_footer
from lib.utils import base_djRole_check
from lib.utils.base_utils import (RepeatMode, convert_to_double, get_config,
                                  get_length)
from lib.utils.configuration import ConfigurationHandler
from lib.utils.errors import (AlreadyConnectedToVoice, NotConnectedToVoice,
                              NoTracksFound, NoVoiceChannel, QueueIsEmpty)

logger = log.Logger().get("music.core.MusicPlayer")

cfg = get_config()["extensions"]["spotify"]

def shorten_name(string):
    if len(string) > 25:
        return string[:25] + "..."
    return string

@log.LoggerApplication
class MusicPlayer(wavelink.Player):
    def __init__(self, *args, logger: log.Logger, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger: log.Logger = logger
        self.paused_vc: bool = False
        self.queue = None # ! [new in wavelink 2.0] queue is set to wavelink's default queue, so we set it to our! [type: ignore]
        self.queue: Queue = Queue()
        self.bound_channel: discord.TextChannel = None
        # self.eq_levels: list[float] = [.0,] * 15
        self.spotipy_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=cfg["client_id"], 
            client_secret=cfg["client_secret"]
        ))

    async def teardown(self):
        try:
            await self.disconnect()
        except KeyError:
            pass

    async def add_tracks(self, interaction: discord.Interaction, tracks: list,
                         put_force: bool=False, play_force: bool=False):
                         # ^ put_force, play_force - new in 1.4.0
        tracks = list([t for t in tracks])
        if not tracks:
            raise NoTracksFound
        # check explicit settings
        config = ConfigurationHandler(str(interaction.guild.id), user=False)
        allow_explicit = config.data["allowExplicit"]["value"]
        blacklist = config.data["blacklistRules"]["value"]
        if not allow_explicit:
            indexes_to_remove = []
            offset = 0
            for i,track in enumerate(tracks):
                # search for track
                try:
                    if "spotify" in track.uri:
                        explicit = self.spotipy_client.track(track.uri)["explicit"]
                        if explicit: indexes_to_remove.append(i)
                except: pass
                
            for idx in indexes_to_remove:
                del tracks[idx-offset]
                offset += 1
            
            if indexes_to_remove:
                await interaction.followup.send(embed=ShortEmbed(f"{emoji.MINUS} `{len(indexes_to_remove)}` {'tracks have' if len(indexes_to_remove) > 1 else 'track has'} been removed due to `allowExplicit` guild setting set to `True`"))
        indexes_to_remove = set()
        for rule in blacklist:
            for i, track in enumerate(tracks):
                if rule[0] == 0: # author name contains:
                    if rule[1].lower() in track.author.lower(): indexes_to_remove.add(i)
                if rule[0] == 1: # track title contains:
                    if rule[1].lower() in track.title.lower(): indexes_to_remove.add(i)
                if rule[0] == 2: # track url contains:
                    if rule[1] == track.uri: indexes_to_remove.add(i)
        offset = 0
        for idx in indexes_to_remove:
            del tracks[idx-offset]
            offset += 1
        if indexes_to_remove:
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.MINUS} `{len(indexes_to_remove)}` {'tracks have' if len(indexes_to_remove) > 1 else 'track has'} been removed due to the blacklist. Check rules added by moderators: `/config blacklist-view`"))
        
        if not tracks: return

        if not (put_force or play_force):
            if interaction:
                self.queue.add(*zip(tracks, [interaction.user, ] * len(tracks)))
            
        if put_force or play_force:
            if len(self.queue) == 0:
                self.queue.add((tracks[0], interaction.user))
            else:
                self.queue.insert_current(tracks[0])
        
        if len(tracks) >= 2:
            total_duration = get_length(sum([t.length for t in tracks]))
            embed = discord.Embed(title=f"{emoji.PLAY} Queue extended", description=f"You extended the queue by **{len(tracks)} tracks** of duration `{total_duration}`", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text=FooterType.MADE_BY.value)
            embed.set_thumbnail(url=tracks[0].artwork)
            await interaction.followup.send(embed=embed)
            if not self.playing:
                await self.start_playback(interaction)
            return
        
        # print(tracks[0].raw_data)
        play_force_play_check = False
        track = tracks[0]
        if not self.playing or play_force:
            embed = discord.Embed(
                title=f"{emoji.PLAY} Now playing",
                color = BASE_COLOR,
                timestamp = datetime.datetime.utcnow()
            )
            dur = get_length(track.length)
            embed.set_thumbnail(url=track.artwork)
            title = track.title
            # if spotify: title = f"{'E ' if track.explicit else ''}{title}"
            embed.add_field(name="Track title", value=f"[**{title}**]({track.uri})", inline=False)
            # if spotify: embed.add_field(name="Artist(s)", value=", ".join(track.artists))
            embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{dur}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text=FooterType.COMMANDS.value)
            
            # play_force
            if play_force:
                # play NOW
                if self.playing:
                    await self.stop()
                else:
                    play_force_play_check = True # later on, we will play (len=0 or sth other error)
            
        if self.playing or put_force:
            embed = discord.Embed(
                title = f"{emoji.PLAY} Added song to the queue",
                color = BASE_COLOR,
                timestamp = datetime.datetime.utcnow()
            )
            dur = get_length(track.length)
            embed.set_thumbnail(url=track.artwork)
                
            title = track.title
            # if spotify: title = f"{'E ' if track.explicit else ''}{title}"
            embed.add_field(name="Track title", value=f"[**{title}**]({track.uri})", inline=False)
            # if spotify: embed.add_field(name="Artist(s)", value=", ".join(track.artists))
            embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{dur}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text=FooterType.LICENSED.value)
            # calculating estimated time to play this song
            current_pos = self.position
            current_len = self.queue.current_track.length
            to_end = current_len-current_pos
            upc_tracks = self.queue.upcoming_tracks[:-1]
            for upcoming in upc_tracks:
                to_end += upcoming.length
            to_end = round(to_end/1000)
            if put_force:
                print(self.queue._queue)
                to_end = round((self.queue.current_track.length-self.position)/1000)
            durm, durs = divmod(to_end,60)
            durh, durm = divmod(durm, 60)
            durs, durm, durh = math.floor(durs), math.floor(durm), math.floor(durh)
            if durh >= 1:
                durm = convert_to_double(durm)
            durs = convert_to_double(durs)
            embed.add_field(name="Estimated time until playback", value=f"`{str(durh) + ':' if int(durh) != 0 else ''}{durm}:{durs}`")
            embed.set_footer(text=FooterType.LICENSED.value)
        
        await interaction.followup.send(embed=embed, view=PlayButtonsMenu(user=interaction.user))

        if not self.playing and ((not play_force) or play_force_play_check): # bruh wacky if
            await self.start_playback(interaction)
            

    async def start_playback(self, interaction: discord.Interaction=None): # interaction used for logging info
        defaultVolume = ConfigurationHandler(interaction.user.id).data["defaultVolume"]["value"]
        maxVolume = ConfigurationHandler(interaction.guild.id, user=False).data["maxVolume"]["value"]
        volume = min(defaultVolume, maxVolume)
        try:
            message = f"(guild:`{interaction.guild.name}` channel:`{interaction.user.voice.channel.name}`)"
        except:
            message = "(No additional interaction info)"
        self.logger.info(f"Playing {self.queue.current_track.uri} {message}")
        if await base_djRole_check(interaction):
            await self.play(self.queue.current_track, volume=volume)
            return
        await self.play(self.queue.current_track)

    async def advance(self):
        self.logger.debug("Player advance called")
        try:
            self.logger.info(f"playing next track (repeat set to {self.queue.repeat.string_mode}, guild {self.guild.id})")
            next_track = self.queue.get_next_track()
            self.logger.debug(f"Next track: {next_track}")
            # announceTracks
            if self.bound_channel:
                announceTracks = ConfigurationHandler(str(self.bound_channel.guild.id), user=False).data["announceTracks"]["value"] # user=False, because guild
                if announceTracks:
                    track = next_track
                    embed = discord.Embed(
                        title=f"{emoji.PLAY} Now playing",
                        color = BASE_COLOR,
                        timestamp = datetime.datetime.utcnow()
                    )
                    dur = get_length(track.length)             
                    embed.set_thumbnail(url=track.artwork)
                    title = track.title
                    embed.add_field(name="Track title", value=f"[**{title}**]({track.uri})", inline=False)
                    embed.add_field(name="Author", value=track.author)
                    embed.add_field(name="Duration", value=f"`{dur}`")
                    embed.set_footer(text=random_footer())
                    # send
                    await self.bound_channel.send(embed=embed)

        except QueueIsEmpty:
            return False
        except IndexError:
            return False

        await self.play(next_track)

    async def play_first_track(self):
        try:
            track = self.queue.first_track
            await self.play(track)
            self.logger.info(f"Playing first track in guild {self.guild.id}")
        except Exception as e:
            self.logger.error(f"Failed to play first track in guild {self.guild.id}; caused by {e.__class__.__name__}: {str(e)}")
