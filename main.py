"""
DJ Cloudy
==========
A Discord bot that adds music functionality to your server.
:copyright: 2022-present @konradsic, @ArgoMk3
:license: MIT License, see license files for more details.
"""
## TODO: Fix bugs and test everything, add logger v3 and more
#######################################################################

__version__ = "0.9.1"
__author__ = "@konradsic"
__license__ = "Licensed under the MIT License"
__copyright__ = "Copyright 2022-present konradsic"

import asyncio
import datetime
import logging
import os
import threading
import time

import colorama
import discord
import requests
import wavelink
from colorama import Back, Fore, Style
from discord import app_commands
from discord.ext import commands

from utils import logger
from utils.base_utils import (clearscreen, get_bot_token, get_length,
                              hide_cursor, inittable, show_cursor, show_figlet)
from utils.colors import BASE_COLOR
from utils import preimports

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

clearscreen()
font = show_figlet("DJ Cloudy")
inittable(__version__, __author__, discord.__version__, wavelink.__version__, __copyright__, font)

# setting up logging instances
logger.config["logging-path"] = "bot-logs/bot.log"
# logger.register_cls("main.DJ_Cloudy")
# logger.register_func("load_extensions")
# main_logger = logger.Logger("main")
# _ = (logger.Logger(name="utils.run"),
#      logger.Logger(name="utils.errors"),
#      logger.Logger(name="music.core"),
#      logger.Logger(name="cogs.vc_handle"),
#      logger.Logger(name="cogs.play"),
#      logger.Logger(name="cogs.eq_and_filters"),
#      logger.Logger(name="cogs.playlist_adapter"))
logger.register_cls("main.DJ_Cloudy")
main_logger = logger.Logger("main")

# import modules using logger after setting it up
from music import playlist

# getting token, logger and init() colorama
TOKEN = get_bot_token()
colorama.init(autoreset=True)
main_logger.info("Initializing...")

# checking up on the rate limits
r = requests.head(url="https://discord.com/api/v1")
try:
    main_logger.critical(f"Rate limit: {colorama.Fore.CYAN}{round(int(r.headers['Retry-After']) / 60, 2)}{colorama.Fore.RED} minutes left")
except:
    main_logger.info("No Rate Limit.")

async def load_extension(ext):
    bot.current_ext_loading = ext
    bot.current_ext_idx += 1
    await bot.load_extension(ext)
async def extload(extensions):
    for extension in extensions:
        await load_extension(extension)
    bot.part_loaded = True

async def update_progressbar():
    progress_running_icons: list = ["|", "/", "-", "\\", "|", "/", "-", "\\"]
    i = 0
    while not bot.part_loaded:
        cur = bot.current_ext_loading or "NoExtension"
        cur_idx = bot.current_ext_idx or 0
        leng = bot.ext_len
        total = 40
        perc = (cur_idx/leng)*total
        print(f" {Fore.WHITE}{Style.BRIGHT}{'█'*round(perc)}{Fore.RESET}{Style.DIM}{'█'*(total-round(perc))}{Style.RESET_ALL} Loading extension {Fore.CYAN}{cur}{Fore.RESET} [{Fore.YELLOW}{cur_idx}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {perc*2.5:.1f}%] {progress_running_icons[i%len(progress_running_icons)]}         ", end="\r")
        await asyncio.sleep(0.25)
        i += 1
    print(f" {Fore.WHITE}{Style.BRIGHT}{'█'*40}{Fore.RESET}{Style.RESET_ALL} Loaded extensions [{Fore.YELLOW}{leng}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {100.0}%] {progress_running_icons[i%len(progress_running_icons)]}                                                                                     ", end="\n")

# loading extensions
async def load_extensions():
    extensions = []
    bot.ext_len = 0
    bot.current_ext_loading = None
    bot.current_ext_idx = 0
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            extensions.append("cogs." + cog[:-3])
    bot.ext_len = len(extensions)
    main_logger.info(f"Loading {Fore.GREEN}{bot.ext_len}{Fore.RESET} extensions...")
    thread_loader = threading.Thread(target=asyncio.run, args=(update_progressbar(),))
    thread_loader.start()
    ext_loader = threading.Thread(target=asyncio.run, args=(extload(extensions),))
    ext_loader.start()
    thread_loader.join()
    ext_loader.join()
    while not bot.part_loaded:
        pass
    main_logger.info("Extensions loaded successfully, syncing with guilds...")
    for guild in list(bot.guilds):
        await bot.tree.sync(guild=guild)
    main_logger.info(f"Extensions synced with {len(bot.guilds)} guilds")
    bot.loaded = True

@logger.LoggerApplication
class DJ_Cloudy(commands.Bot):
    def __init__(self, logger: logger.Logger):
        self.logger = logger
        super().__init__(
            command_prefix = "dj$",
            intents = discord.Intents.all(),
            application_id = 1024303533685751868
        )
    
    async def on_ready(self):
        self.logger.info(f"Connected to discord as `{self.user}`! Latency: {round(self.latency*1000)}ms")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
        self.tree.add_command(app_commands.ContextMenu(name="View Playlists", callback=view_playlist_menu), guilds=self.guilds)
        self.tree.add_command(app_commands.ContextMenu(name="View Starred Playlist", callback=view_starred_playlist_menu), guilds=self.guilds)
        self.tree.add_command(app_commands.ContextMenu(name="Copy Starred Playlist", callback=copy_user_playlist_menu), guilds=self.guilds)
        await load_extensions()
        while not bot.loaded:
            pass
        # clearscreen()
        self.logger.info(f"Loading extensions done (took {(time.time()-bot.last_restart)*1000:,.0f}ms)")

    async def close(self):
        try:
            self.logger.info("Closing gateway...")
            await super().close()
            self.logger.info("Connection to Discord closed, bot shut down")
        except:
            self.logger.error("Closing session failed")
        show_cursor()

bot = DJ_Cloudy()

# haha idk how to do it in cogs so here :)

async def view_playlist_menu(interaction: discord.Interaction, user: discord.Member):
    handler = playlist.PlaylistHandler(key=str(user.id))
    playlist_res = "This user does not have any custom playlists"
    if handler.playlists:
        playlist_res = ""
        for i, p in enumerate(handler.playlists,1):
            total_duration = 0
            for track in p['tracks']:
                d = await bot.node.get_tracks(cls=wavelink.Track, query=track)
                total_duration += d[0].length
            playlist_res += f"**{i}.** {p['name']} `#{p['id']}` `[{get_length(total_duration)}]` *{len(p['tracks'])} song(s)*\n"
    starred_dur = 0
    for t in handler.data['starred-playlist']:
        d = await bot.node.get_tracks(cls=wavelink.Track, query=t)
        starred_dur += d[0].length
    starred_playlist_data = f"{len(handler.data['starred-playlist'])} total songs, total duration `{get_length(starred_dur)}`\n"
    embed = discord.Embed(description="These are the user's playlists", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
    embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
    embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
    embed.set_footer(text="Made by Konradoo#6938")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def view_starred_playlist_menu(interaction: discord.Interaction, member: discord.Member):
    handler = playlist.PlaylistHandler(key=str(member.id))
    starred_playlist = handler.data['starred-playlist']
    track_data = "No tracks in their :star: songs playlist"
    total_duration = 0
    if starred_playlist:
        track_data = ""
        for i, song in enumerate(starred_playlist,1):
            cls_song = await bot.node.get_tracks(cls=wavelink.Track, query=song)
            cls_song = cls_song[0]
            total_duration += cls_song.duration
            track_data += f'**{i}.** [{cls_song.title}]({cls_song.uri}) `[{get_length(cls_song.duration)}]`\n'
    embed = discord.Embed(description="These are the user's starred/liked songs", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
    embed.set_footer(text="Made by Konradoo#6938")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_author(name=f"{member.name}'s starred songs", icon_url=member.display_avatar.url)
    embed.add_field(name="Tracks", value=track_data, inline=False)
    embed.add_field(name="Additional info", value=f"Total duration: `{get_length(total_duration)}`\nTotal tracks: **{len(starred_playlist)}**")
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def copy_user_playlist_menu(interaction: discord.Interaction, member: discord.Member):
    if str(interaction.user.id) == str(member.id):
        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description="<:x_mark:1028004871313563758> You can't copy your playlist", color=BASE_COLOR))
        return
    handler = playlist.PlaylistHandler(key=str(member.id))
    starred = handler.data['starred-playlist']
    author_handler = playlist.PlaylistHandler(key=str(member.id))
    author_starred = handler.data['starred-playlist']
    for song in starred:
        author_handler.add_to_starred(song)
    await interaction.response.send_message(embed=discord.Embed(description=f"<:tick:1028004866662084659> Success, added {member.name}'s starred playlist to yours", color=BASE_COLOR),ephemeral=True)

hide_cursor()
bot.loaded = False
bot.part_loaded = False
bot.last_restart = round(time.time())
bot.run(TOKEN, log_handler=None) # we disable discord logging
