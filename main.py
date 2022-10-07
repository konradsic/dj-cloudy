import discord
from discord.ext import commands
import requests, os, time
from utils import logger
from utils.logger import LoggingType as ltype
import colorama

# disabling logging from flask
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

os.system("cls")

# logging types
INFO = ltype.INFO
WARN = ltype.WARN
ERROR = ltype.ERROR
CRITICAL = ltype.CRITICAL

# getting token, logger and init() colorama
with open("./config/token.txt", mode="r") as f:
    TOKEN = f.read().strip("\n ")
colorama.init(autoreset=True)
logging = logger.LoggerInstance(INFO, "main")

logging.log("main", "Initializing...")

# checking up on the rate limits
r = requests.head(url="https://discord.com/api/v1")
try:
    logging.log("main",f"Rate limit: {colorama.Fore.CYAN}{round(int(r.headers['Retry-After']) / 60, 2)}{colorama.Fore.RED} minutes left", CRITICAL)
except:
    logging.log("main", "No Rate Limit.")

    
# loading extensions
async def load_extensions():
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            await bot.load_extension("cogs."+cog[:-3])
            logging.log("load_extensions",f"Extension `{cog[:-3]}` loaded successfully")
    for guild in list(bot.guilds):
        await bot.tree.sync(guild=guild)
        logging.log("load_extensions", "Extensions synced with guilds")
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
        logging.log("DJ_Cloudy.on_ready", f"Connected to discord as `{self.user}`! Latency: {round(self.latency*1000)}ms")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
        await load_extensions()
        while not bot.loaded:
            pass
        logging.log("DJ_Cloudy.on_ready", f"Loading extensions done (took {(time.time()-bot.last_restart)*1000:,.0f}ms)")

    async def close(self):
        try:
            logging.log("DJ_Cloudy.close", "Closing gateway...")
            await super().close()
            logging.log("DJ_Cloudy.close", "Connection closed. Consider this not a warning but a important information", WARN)
        except:
            logging.log("DJ_Cloudy.close","Closing session failed", ERROR)

bot = DJ_Cloudy()
bot.loaded = False
bot.last_restart = round(time.time())
bot.run(TOKEN)