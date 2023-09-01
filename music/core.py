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
from utils.base_utils import convert_to_double, get_length
from music.queue import Queue
from utils.base_utils import RepeatMode
from utils.configuration import ConfigurationHandler

logger = log.Logger().get("music.core.MusicPlayer")

def shorten_name(string):
    if len(string) > 25:
        return string[:25] + "..."
    return string

@log.LoggerApplication
class MusicPlayer(wavelink.Player):
    def __init__(self, *args, logger: log.Logger, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.paused_vc = False
        # ! [new in wavelink 2.0] queue is set to wavelink's default queue, so we set it to our!
        self.queue = None 
        self.queue = Queue()
        self.bound_channel = None
        self.eq_levels = [.0,] * 15
        self.shuffle_mode_state = 0

    async def teardown(self):
        try:
            await self.disconnect()
        except KeyError:
            pass

    async def add_tracks(self, interaction: discord.Interaction, tracks: list,
                         put_force: bool=False, play_force: bool=False, *, spotify: bool=False):
                         # ^ put_force, play_force - new in 1.4.0
        if not tracks:
            raise NoTracksFound

        if not (put_force or play_force):
            self.queue.add(*tracks)
            
        if put_force or play_force:
            current = self.queue.position
            copy = self.queue._queue.copy()
            new_queue = copy.insert(current+1, tracks[0])
            self.queue._queue = new_queue
            
        if len(tracks) >= 2:
            total_duration = get_length(sum([t.duration for t in tracks]))
            embed = discord.Embed(title="<:play_button:1028004869019279391> Queue extended", description=f"You extended the queue by **{len(tracks)} tracks** of duration `{total_duration}`", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
            await interaction.followup.send(embed=embed)
            if not self.is_playing():
                await self.start_playback(interaction)
            return
        
        track = tracks[0]
        if not self.is_playing() or play_force:
            embed = discord.Embed(
                title="<:play_button:1028004869019279391> Now playing",
                color = BASE_COLOR,
                timestamp = datetime.datetime.utcnow()
            )
            dur = get_length(track.duration)
            try: # add thumbnail
                if spotify: embed.set_thumbnail(url=track.images[0])
                else: embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            except:
                try:
                    embed.set_thumbnail(url=track.images[0])
                except: pass
            title = track.title
            if spotify: title = f"{'E ' if track.explicit else ''}{title}"
            embed.add_field(name="Track title", value=f"[**{title}**]({track.uri if not spotify else 'https://open.spotify.com/track/' + track.uri.split(':')[2]})", inline=False)
            if spotify: embed.add_field(name="Artist(s)", value=", ".join(track.artists))
            else: embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{dur}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
            
            # play_force
            if play_force:
                # play NOW
                await self.stop()
            
        if self.is_playing() or put_force:
            embed = discord.Embed(
                title = "<:play_button:1028004869019279391> Added song to the queue",
                color = BASE_COLOR,
                timestamp = datetime.datetime.utcnow()
            )
            dur = get_length(track.duration)
            
            try: # add thumbnail
                if spotify: embed.set_thumbnail(url=track.images[0])
                else: embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
            except:
                try:
                    embed.set_thumbnail(url=track.images[0])
                except: pass
                
            title = track.title
            if spotify: title = f"{'E ' if track.explicit else ''}{title}"
            embed.add_field(name="Track title", value=f"[**{title}**]({track.uri if not spotify else 'https://open.spotify.com/track/' + track.uri.split(':')[2]})", inline=False)
            if spotify: embed.add_field(name="Artist(s)", value=", ".join(track.artists))
            else: embed.add_field(name="Author", value=track.author)
            embed.add_field(name="Duration", value=f"`{dur}`")
            embed.add_field(name="Requested by", value=interaction.user.mention)
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
            # calculating estimated time to play this song
            current_pos = self.position
            current_len = self.queue.current_track.duration
            to_end = current_len-current_pos
            upc_tracks = self.queue.upcoming_tracks[:-1]
            for upcoming in upc_tracks:
                to_end += upcoming.duration
            to_end = round(to_end/1000)
            if put_force:
                print(self.queue._queue)
                to_end = round((self.queue.current_track.duration-self.position)/1000)
            durm, durs = divmod(to_end,60)
            durh, durm = divmod(durm, 60)
            durs, durm, durh = math.floor(durs), math.floor(durm), math.floor(durh)
            if durh >= 1:
                durm = convert_to_double(durm)
            durs = convert_to_double(durs)
            embed.add_field(name="Estimated time until playback", value=f"`{str(durh) + ':' if int(durh) != 0 else ''}{durm}:{durs}`")
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
        
        await interaction.followup.send(embed=embed, view=PlayButtonsMenu(user=interaction.user))

        if not self.is_playing() and not play_force:
            await self.start_playback(interaction)
            

    async def start_playback(self, interaction: discord.Interaction=None): # interaction used for logging info
        try:
            message = f"(guild:`{interaction.guild.name}` channel:`{interaction.user.voice.channel.name}`)"
        except:
            message = "(No additional interaction info)"
        self.logger.info(f"Playing {self.queue.current_track.uri} {message}")
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
                        title="<:play_button:1028004869019279391> Now playing",
                        color = BASE_COLOR,
                        timestamp = datetime.datetime.utcnow()
                    )
                    dur = get_length(track.duration)
                    spotify = False
                    try: track.author # one of params that are not in wavelink.ext.spotify.SpotifyTrack class
                    except: spotify = True
                    
                    try: # add thumbnail
                        if spotify: embed.set_thumbnail(url=track.images[0])
                        else: embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg")
                    except:
                        try:
                            embed.set_thumbnail(url=track.images[0])
                        except: pass
                    title = track.title
                    if spotify: title = f"{'E ' if track.explicit else ''}{title}"
                    embed.add_field(name="Track title", value=f"[**{title}**]({track.uri if not spotify else 'https://open.spotify.com/track/' + track.uri.split(':')[2]})", inline=False)
                    if spotify: embed.add_field(name="Artist(s)", value=", ".join(track.artists))
                    else: embed.add_field(name="Author", value=track.author)
                    embed.add_field(name="Duration", value=f"`{dur}`")
                    embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
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
