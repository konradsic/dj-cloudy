"""
DJ Cloudy
==========
A Discord bot that adds music functionality to your server.
:copyright: 2022-present @konradsic
"""
#######################################################################

__version__ = "1.4.0b"
__author__ = "@konradsic"
__copyright__ = "Copyright 2022-present konradsic"

import asyncio
import datetime
import getpass
import os
import platform
import threading
import time
import traceback

import colorama
import discord
import requests
import wavelink
from colorama import Fore, Style
from discord.ext import commands

from lib.logger import logger
from lib.ui.colors import BASE_COLOR
## ^ just import, not used, preimports are used to pre-define loggers for cogs and other classes.
from lib.utils import (clearscreen, get_application_id, get_bot_token,
                       get_config, get_length, hide_cursor, inittable,
                       load_logger_config, make_files, show_cursor,
                       show_figlet)
from lib.utils.cache import JSONCacheManager
from lib.utils.configuration import ConfigurationHandler
from lib.utils.garbage import GarbageCollector

clearscreen()
font = show_figlet()
inittable(__version__, __author__, platform.python_version(), discord.__version__, wavelink.__version__, __copyright__, font)

# setting up logging instances
logger.config["logging-path"] = "bot-logs/bot.log"
logger.set_level(logger.LogLevels.DEBUG) # change whenever you want (DEBUG, INFO, WARN, ERROR, CRITICAL)
logger.register_cls("main.DJ_Cloudy")
main_logger = logger.Logger("main")

# import modules using logger after setting it up
from lib.music import playlist

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
garbage = GarbageCollector(1200)

# checking up on the rate limits
r = requests.head(url="https://discord.com/api/v1")
try:
    main_logger.critical(f"Rate limit: {colorama.Fore.CYAN}{round(int(r.headers['Retry-After']) / 60, 2)}{colorama.Fore.RED} minutes left")
except:
    main_logger.info("No Rate Limit.")

# NOTE: Since 19th June 2023 this project is closed-source, checking version makes no sense
make_files()

thread_loader, ext_loader = None, None

async def load_extension(ext):
    bot.current_ext_loading = ext
    bot.current_ext_idx += 1
    await bot.load_extension(ext)

async def extload(extensions):
    for extension in extensions:
        try:
            await load_extension(extension)
        except Exception as e:
            error = "".join(traceback.format_exc())
            main_logger.critical(error)
            main_logger.critical(f"Error while loading extension {extension}, aborting...")
            bot.aborted_extload = True
            return
    bot.part_loaded = True

async def update_progressbar():
    progress_running_icons: list = ["|", "/", "-", "\\", "|", "/", "-", "\\"]
    i = 0
    while not bot.part_loaded or bot.aborted_extload:
        cur = bot.current_ext_loading or "NoExtension"
        cur_idx = bot.current_ext_idx or 0
        leng = bot.ext_len
        total = 40
        perc = (cur_idx/leng)*total
        print(f" {Fore.WHITE}{Style.BRIGHT}{'█'*round(perc)}{Fore.RESET}{Style.DIM}{'█'*(total-round(perc))}{Style.RESET_ALL} Loading extension {Fore.CYAN}{cur}{Fore.RESET} [{Fore.YELLOW}{cur_idx}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {perc*2.5:.1f}%] {progress_running_icons[i%len(progress_running_icons)]}             ", end="\r")
        await asyncio.sleep(0.15)
        i += 1
        if bot.aborted_extload:
            print()
            return
    print(f" {Fore.WHITE}{Style.BRIGHT}{'█'*40}{Fore.RESET}{Style.RESET_ALL} Loaded extensions [{Fore.YELLOW}{leng}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {100.0}%] {progress_running_icons[i%len(progress_running_icons)]}                       ")

# loading extensions
async def load_extensions():
    try:
        bot.aborted_extload = False
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
        
        while not bot.part_loaded or bot.aborted_extload:
            pass
        if bot.aborted_extload: 
            show_cursor()
            quit()
        main_logger.info("Extensions loaded successfully, syncing with guilds...")
        for guild in list(bot.guilds):
            await bot.tree.sync(guild=guild)
        main_logger.info(f"Extensions synced with {len(bot.guilds)} guilds")
        bot.loaded = True
    except:
        show_cursor()

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
        # ^ Base presence, changes in cogs.status
        await load_extensions()
        while not bot.loaded:
            pass
        # clearscreen()
        took = f'{(time.time()-bot.last_restart):,.1f}'.replace(",", " ")
        self.logger.info(f"Loading extensions done (took {took}s)")
        try: self.song_cache_mgr: JSONCacheManager = JSONCacheManager("songs.json")
        except: self.logger.error(f"Could not load manager song_cache_mgr\n{traceback.format_exc()}")
        try: self.system_vars: JSONCacheManager = JSONCacheManager("systemcache.json", expiration_time = -1)
        except: self.logger.error(f"Could not load manager system_vars\n{traceback.format_exc()}")
        try: self.quiz_cache: JSONCacheManager = JSONCacheManager("quizzes.json", expiration_time = -1)
        except: self.logger.error(f"Could not load manager quiz_cache\n{traceback.format_exc()}")
        self.logger.debug("JSON Cache managers initialized")

    async def close(self):
        garbage.close()
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
async def on_command_exception(interaction: discord.Interaction, error: Exception):
    # suppress common errors
    if str(error).endswith("AttributeError: 'Queue' object has no attribute 'loop'"):
        return
    
    # print error and send
    colorama.init(autoreset=False)
    main_logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}{Style.RESET_ALL}\n{Fore.RED}{traceback.format_exc()}")
    colorama.init(autoreset=True)
    # auto bug report
    # check if user has it enabled
    cfg = ConfigurationHandler(id=str(interaction.user.id), user=True)
    if cfg.data["experimental.autoBugReport"]["value"] == True:
        bot_config = get_config()["bot"]
        guild_id, channel_id = bot_config["support-server-id"], bot_config["auto-bug-report-channel"]
        # test data validation
        cont = True
        try:
            guild: discord.Guild = bot.get_guild(int(guild_id))
            channel = guild.get_channel(int(channel_id))
        except:
            main_logger.warn("Auto bug report: config `bot:support-server-id` or/and `bot:auto-bug-report-channel` is/are not valid")
            cont = False
        if cont:
            # report bug
            cmd_name = "/"
            if interaction.command.parent is not None:
                cmd_name += interaction.command.parent.name + " "
            name = interaction.command.name.strip("/")
            cmd_name += name
            embed = discord.Embed(color=BASE_COLOR, title="An unexpected error occurred", timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Data", value=f"```\nGuild: {interaction.guild.name} ({interaction.guild.id})\nChannel: #{interaction.channel.name} ({interaction.channel.id})\nUser: @{interaction.user.name} ({interaction.user.id})\nTime: see footer\nCommand: /{cmd_name[1:]}```")
            exc = traceback.format_exc()
            embed.description = f"**Error:**\n ```py\n{exc}```"
            await channel.send(embed=embed)
            
    embed = discord.Embed(description=
        f"<:x_mark:1028004871313563758> An unexcepted error occured while trying to execute this command. Please contact developers for more info. \nDetails:\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
    try:
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    

hide_cursor()
bot.loaded = False
bot.part_loaded = False
bot.last_restart = round(time.time())
bot.run(TOKEN, log_handler=None) # disable discord logging (log_handler=None)
