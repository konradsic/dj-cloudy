import discord
from discord.ext import commands
import requests, os, time
from utils import logger
import colorama

# disabling logging from flask
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

os.system("cls")

# setting up logging instances
logging.config["logging-path"] = "./bot-logs/bot-logging.txt"
main_logger = logging.Logger(name="main")
_ = logging.Logger(name="utils.run")
_ = logging.Logger(name="utils.errors")
_ = logging.Logger(name="music.core")
_ = logging.Logger(name="music.queue")
_ = logging.Logger(name="music.playlist")

# getting token, logger and init() colorama
with open("./config/token.txt", mode="r") as f:
    TOKEN = f.read().strip("\n ")
colorama.init(autoreset=True)
main_logger.info("Initializing...")

# checking up on the rate limits
r = requests.head(url="https://discord.com/api/v1")
try:
    logging.critical("Request-Check",f"Rate limit: {colorama.Fore.CYAN}{round(int(r.headers['Retry-After']) / 60, 2)}{colorama.Fore.RED} minutes left")
except:
    logging.info("Request-Check", "No Rate Limit.")

    
# loading extensions
async def load_extensions():
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            await bot.load_extension("cogs."+cog[:-3])
            logging.info("load_extensions",f"Extension `{cog[:-3]}` loaded successfully")
    for guild in list(bot.guilds):
        await bot.tree.sync(guild=guild)
        logging.info("load_extensions", "Extensions synced with guilds")
    bot.loaded = True

# main bot class, close() still does not work
### TODO: fix close() not working
class DJ_Cloudy(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = "$",
            intents = discord.Intents.all(),
            application_id = 1024303533685751868
        )
    
    async def on_ready(self):
        logging.info("DJ_Cloudy.on_ready", f"Connected to discord as `{self.user}`! Latency: {round(self.latency*1000)}ms")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
        await load_extensions()
        while not bot.loaded:
            pass
        logging.info("DJ_Cloudy.on_ready", f"Loading extensions done (took {(time.time()-bot.last_restart)*1000:,.0f}ms)")

    async def close(self):
        try:
            logging.info("dj-cloudy-close", "Closing gateway...")
            await super().close()
            logging.warn("dj-cloudy-close", "Connection closed. Consider this not a warning but a important information")
        except:
            logging.error("dj-cloudy-close","Closing session failed")

bot = DJ_Cloudy()
bot.loaded = False
bot.last_restart = round(time.time())
bot.run(TOKEN)