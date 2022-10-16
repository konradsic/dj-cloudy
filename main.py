import discord
from discord.ext import commands
import requests, os, time
from utils import logger
import colorama
from colorama import Fore, Back, Style
import asyncio
import threading

# disabling logging
import logging
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

os.system("cls")

# setting up logging instances
logger.config["logging-path"] = "bot-logs/bot.log"
main_logger = logger.Logger("dj-cloudy-onready","main")
_ = logger.Logger("run_lavalink", "utils.run")
_ = logger.Logger("AlreadyConnectedToVoice", "utils.errors")
_ = logger.Logger("start-playback","music.core")
_ = logger.Logger("on-wavelink-node-ready","cogs.vc_handle")
_ = logger.Logger("autocomplete-play","cogs.play")

# getting token, logger and init() colorama
with open("./config/token.txt", mode="r") as f:
    TOKEN = f.read().strip("\n ")
colorama.init(autoreset=True)
main_logger.info("main", "Initializing...")

# checking up on the rate limits
r = requests.head(url="https://discord.com/api/v1")
try:
    main_logger.critical("Request-Check",f"Rate limit: {colorama.Fore.CYAN}{round(int(r.headers['Retry-After']) / 60, 2)}{colorama.Fore.RED} minutes left")
except:
    main_logger.info("Request-Check", "No Rate Limit.")

async def load_extension(ext):
    bot.current_ext_loading = ext
    bot.current_ext_idx += 1
    await bot.load_extension(ext)
    await asyncio.sleep(0.01)
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
        total = 20
        perc = (cur_idx/leng)*20
        print(f" {Back.WHITE}{'#'*round(perc)}{Back.RESET}{'.'*(total-round(perc))} Loading extension {Fore.CYAN}{cur}{Fore.RESET} [{Fore.YELLOW}{cur_idx}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {perc*5:.1f}%] {progress_running_icons[i%len(progress_running_icons)]}         ", end="\r")
        await asyncio.sleep(0.20)
        i += 1
    print(f" {Back.WHITE}{'#'*20}{Back.RESET} Loaded extensions [{Fore.YELLOW}{leng}{Fore.WHITE}/{Fore.GREEN}{leng}{Fore.RESET} {100.0}%] {progress_running_icons[i%len(progress_running_icons)]}                                                                                     ", end="\n")

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
    main_logger.info("load_extensions",f"Loading {Fore.GREEN}{bot.ext_len}{Fore.RESET} extensions...")
    thread_loader = threading.Thread(target=asyncio.run, args=(update_progressbar(),))
    thread_loader.start()
    ext_loader = threading.Thread(target=asyncio.run, args=(extload(extensions),))
    ext_loader.start()
    thread_loader.join()
    ext_loader.join()
    while not bot.part_loaded:
        pass
    main_logger.info("load_extensions", "Extensions loaded successfully, syncing with guilds...")
    for guild in list(bot.guilds):
        await bot.tree.sync(guild=guild)
    main_logger.info("load_extensions", f"Extensions synced with {len(bot.guilds)} guilds")
    bot.loaded = True

# main bot class, close() still does not work
class DJ_Cloudy(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = "$",
            intents = discord.Intents.all(),
            application_id = 1024303533685751868
        )
    
    async def on_ready(self):
        main_logger.info("dj-cloudy-onready", f"Connected to discord as `{self.user}`! Latency: {round(self.latency*1000)}ms")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
        await load_extensions()
        while not bot.loaded:
            pass
        main_logger.info("dj-cloudy-onready", f"Loading extensions done (took {(time.time()-bot.last_restart)*1000:,.0f}ms)")
        #main_logger.log("dj-cloudy-onready", "Bot is in those guilds: " + "".join(e.name + " " + str(e.owner) + "  " for e in bot.guilds))

    async def close(self):
        try:
            main_logger.info("dj-cloudy-close", "Closing gateway...")
            await super().close()
            main_logger.warn("dj-cloudy-close", "Connection closed. Consider this not a warning but a important information")
        except:
            main_logger.error("dj-cloudy-close","Closing session failed")

bot = DJ_Cloudy()
bot.loaded = False
bot.part_loaded = False
bot.last_restart = round(time.time())
bot.run(TOKEN, log_handler=None) # we do not disable discord logging