"""
DJ Cloudy
==========
A Discord bot that adds music functionality to your server.
:copyright: 2022-present @konradsic
:license: MIT License, see license files for more details.
"""
# TODO: Configuration system
#######################################################################

__version__ = "pre-1.2.0"
__author__ = "@konradsic"
__license__ = "Licensed under the MIT License"
__copyright__ = "Copyright 2022-present konradsic"

MIN_REQ_VERSION = "1.0.2"

import asyncio
import datetime
import getpass
import logging
import os
import platform
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
from utils import preimports as _  
# ^ just import, not used, preimports are used to pre-define loggers for cogs and other classes.
from utils.base_utils import (check_for_updates, clearscreen,
                              get_application_id, get_bot_token, get_length,
                              hide_cursor, inittable, load_logger_config,
                              make_files, show_cursor, show_figlet)
from utils.colors import BASE_COLOR

clearscreen()
font = show_figlet()
inittable(__version__, __author__, platform.python_version(), discord.__version__, wavelink.__version__, __copyright__, font)

# setting up logging instances
logger.config["logging-path"] = "bot-logs/bot.log"
logger.set_level(logger.LogLevels.DEBUG) # change whenever you want (DEBUG, INFO, WARN, ERROR, CRITICAL)
logger.register_cls("main.DJ_Cloudy")
main_logger = logger.Logger("main")

# import modules using logger after setting it up
from music import playlist

# getting token, logger and init() colorama
TOKEN = get_bot_token()
app_id = get_application_id()
colorama.init(autoreset=True)
# gather some info and log init message
device = platform.node()
pid = os.getpid()
path_to = os.path.abspath("./main.py")
try:
    user, effective_user = os.getlogin(), getpass.getuser()
except:
    user, effective_user = "Unknown", "Unknown"

config_logs = load_logger_config()
logger.config["logging-path"] = config_logs[1] + "/bot.log"
logger.set_level(config_logs[0])
logger.preinit_logs()

main_logger.info(f"Initializing DJ Cloudy on device [{device}], PID: {pid}")
main_logger.info(f"{path_to} started by [{user}] (effective user: {effective_user})")
main_logger.info("Loaded logger config successfully, changes were applied")

# checking up on the rate limits
r = requests.head(url="https://discord.com/api/v1")
try:
    main_logger.critical(f"Rate limit: {colorama.Fore.CYAN}{round(int(r.headers['Retry-After']) / 60, 2)}{colorama.Fore.RED} minutes left")
except:
    main_logger.info("No Rate Limit.")

check_for_updates(__version__, MIN_REQ_VERSION)
make_files()

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
        print(f" {Fore.WHITE}{Style.BRIGHT}{'█'*round(perc)}{Fore.RESET}{Style.DIM}{'█'*(total-round(perc))}{Style.RESET_ALL} Loading extension {Fore.CYAN}{cur}{Fore.RESET} [{Fore.YELLOW}{cur_idx}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {perc*2.5:.1f}%] {progress_running_icons[i%len(progress_running_icons)]}             ", end="\r")
        await asyncio.sleep(0.15)
        i += 1
    print(f" {Fore.WHITE}{Style.BRIGHT}{'█'*40}{Fore.RESET}{Style.RESET_ALL} Loaded extensions [{Fore.YELLOW}{leng}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {100.0}%] {progress_running_icons[i%len(progress_running_icons)]}                       ")

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
            application_id = app_id
        )
    
    async def on_ready(self):
        self.logger.info(f"Connected to discord as {self.user}. Latency: {round(self.latency*1000)}ms")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
        self.tree.add_command(app_commands.ContextMenu(name="View Playlists", callback=view_playlist_menu), guilds=self.guilds)
        self.tree.add_command(app_commands.ContextMenu(name="View Starred Playlist", callback=view_starred_playlist_menu), guilds=self.guilds)
        self.tree.add_command(app_commands.ContextMenu(name="Copy Starred Playlist", callback=copy_user_playlist_menu), guilds=self.guilds)
        await load_extensions()
        while not bot.loaded:
            pass
        # clearscreen()
        took = f'{(time.time()-bot.last_restart):,.1f}'.replace(",", " ")
        self.logger.info(f"Loading extensions done (took {took}s)")

    async def close(self):
        try:
            self.logger.info("Closing gateway...")
            await super().close()
            self.logger.info("Connection to Discord closed, bot shut down")
        except:
            self.logger.error("Closing session failed")
        show_cursor()

bot = DJ_Cloudy()

# error handling
@bot.tree.error
async def on_command_exception(interaction, error):
    main_logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}")
    embed = discord.Embed(description=
        f"<:x_mark:1028004871313563758> An unexcepted error occured while trying to execute this command. Please contact developers for more info. \nDetails:\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
    try:
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
# haha idk how to do it in cogs so here :

async def view_playlist_menu(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=True, thinking=True)
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
    await interaction.followup.send(embed=embed, ephemeral=True)

async def view_starred_playlist_menu(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True, thinking=True)
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
    await interaction.followup.send(embed=embed, ephemeral=True)

async def copy_user_playlist_menu(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True, thinking=True)
    if str(interaction.user.id) == str(member.id):
        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description="<:x_mark:1028004871313563758> You can't copy your playlist", color=BASE_COLOR))
        return
    handler = playlist.PlaylistHandler(key=str(member.id))
    starred = handler.data['starred-playlist']
    author_handler = playlist.PlaylistHandler(key=str(member.id))
    author_starred = handler.data['starred-playlist']
    for song in starred:
        author_handler.add_to_starred(song)
    await interaction.followup.send(embed=discord.Embed(description=f"<:tick:1028004866662084659> Success, added {member.name}'s starred playlist to yours", color=BASE_COLOR),ephemeral=True)

hide_cursor()
bot.loaded = False
bot.part_loaded = False
bot.last_restart = round(time.time())
bot.run(TOKEN, log_handler=None) # disable discord logging (log_handler=None)
