import discord
from discord import app_commands
from discord.ext import commands
from lib.logger import logger
import json
from lib.ui import emoji
from lib.utils.base_utils import get_config

OWNER_ID = int(get_config()["bot"]["owner"])

async def ban_user(user: int):
    try: 
        with open("./data/banned.json", mode="r") as f:
            contents = json.load(f)
    except:
        with open("./data/banned.json", "w") as f:
            json.dump({"guilds": [], "users": []}, f)
            contents = {"guilds": [], "users": []}
        
    contents["users"].append(str(user))
    with open("./data/banned.json", mode="w") as f:
        json.dump(contents, f)

@logger.LoggerApplication
class BanCommands(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger
        
    @app_commands.command(name="ban-user", description="Only for owner of the bot, fully ban a user from using DJ Cloudy")
    @app_commands.describe(id="ID of user to ban")
    async def ban_user_globally_command(self, interaction: discord.Interaction, id: str):
        await interaction.response.defer(thinking=True)
        if interaction.user.id != OWNER_ID:
            await interaction.followup.send(f"{emoji.XMARK} Insufficient permissions, cannot execute command")
            return
        
        await ban_user(id)
        await interaction.followup.send(f"{emoji.TICK1} User banned")

async def setup(bot):
    await bot.add_cog(BanCommands(bot), guilds=[discord.Object(int(id)) for id in get_config()["bot"]["emoji-guilds"]])

