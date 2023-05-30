import os
import json
import random
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from utils import logger

@logger.LoggerApplication
class StatusChangerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logger.Logger):
        self.logger = logger
        self.bot = bot
        
        self.statuses = {}
        self._load_statuses()
        self.bot.loop.create_task(self.presence_loop(), name="Change presence loop")
    
    def _load_statuses(self):
        path_to_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/statuses.json"))
        self.logger.debug(f"Path to statuses file: [{path_to_file}]")
        with open(path_to_file, "r") as f:
            self.statuses = json.load(f)
    
    async def get_random_status(self, ignore_status: str = None):
        # statuses as list
        listening = self.statuses.get("LISTENING")
        watching = self.statuses.get("WATCHING")
        competing = self.statuses.get("COMPETING")
        playing = self.statuses.get("PLAYING")
        
        all_statuses = [*listening, *watching, *competing, *playing]
        random_status = ignore_status
        while random_status == ignore_status: # ignore passed status
            random_status = random.choice(all_statuses)
            
        # ! tagscript -- replace tags with appropriate values
        old_status = random_status + ""
        random_status = random_status.replace("{{num_guilds}}", str(len(self.bot.guilds)))
            
        # find category and return
        if old_status in listening: return discord.ActivityType.listening, random_status, "LISTENING"
        if old_status in watching: return discord.ActivityType.watching, random_status, "WATCHING"
        if old_status in competing: return discord.ActivityType.competing, random_status, "COMPETING"
        if old_status in playing: return discord.ActivityType.playing, random_status, "PLAYING"
        
    async def presence_loop(self):
        await self.bot.wait_until_ready()
        before_status = ""
        
        while not self.bot.is_closed():
            activity_type, status, activity_name = await self.get_random_status(before_status)
            before_status = status
            await self.bot.change_presence(activity=discord.Activity(type=activity_type, name=status), status=random.choice([
                discord.Status.do_not_disturb,
                discord.Status.idle,
                discord.Status.online
            ]))
            self.logger.info(f"Changed status to [{activity_name} {status}]")
            await asyncio.sleep(random.randint(75, 180))
    
        
async def setup(bot):
    await bot.add_cog(StatusChangerCog(bot), guilds=bot.guilds)
