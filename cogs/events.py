import datetime

import discord
from discord import app_commands
from discord.ext import commands
from utils import help_utils, logger, base_utils
from utils.colors import BASE_COLOR
from music import songs

@logger.LoggerApplication
class EventHandlerCog(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        
        cfg = base_utils.get_config()
        genius_token = cfg.get("lyrics").get("genius-auth-token")
        if genius_token is None:
            self.logger.error("Failed to authenticate with genius: loading token failed")
            return
        
        self.bot.genius = songs.GeniusAPIClient(genius_token)
        self.logger.info("Created GeniusAPIClient and bound to `self.bot`")
        
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            # change presence
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
            # sync commands with the new guild
            await self.bot.tree.sync(guild=guild)
            self.logger.info(f"GUILD_JOIN : {guild.id} -> synced, changed presence")
        except Exception as e:
            self.logger.error(f"GUILD_JOIN : failed to sync with guild {guild.id}. Error - {e.__class__.__name__}: {str(e)}")
        
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            # change presence
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"music in {len(self.guilds)} guilds | /help"))
            # log
            self.logger.info(f"GUILD_REMOVE : {guild.id} -> changed presence")
        except Exception as e:
            self.logger.error(f"GUILD_REMOVE : failed to sync with guild {guild.id}. Error - {e.__class__.__name__}: {str(e)}")
    
    
async def setup(bot):
    await bot.add_cog(EventHandlerCog(bot),
                guilds=[discord.Object(g.id) for g in bot.guilds])
