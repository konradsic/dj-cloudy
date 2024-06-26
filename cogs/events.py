import datetime

import discord
from discord import app_commands
from discord.ext import commands
from lib.utils import base_utils, help_utils
from lib.logger import logger
from lib.ui.colors import BASE_COLOR
from lib.music import songs

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
            # sync commands with the new guild
            self.logger.info("Guild added, re-syncing tree...")
            await self.bot.tree.sync()
            self.logger.info(f"GUILD_JOIN : {guild.id} -> synced application tree")
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        await channel.send("Hi")
                        break
                    except: pass
        except Exception as e:
            self.logger.error(f"GUILD_JOIN : failed to sync with guild {guild.id}. Error - {e.__class__.__name__}: {str(e)}")
        
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            # log
            self.logger.info(f"GUILD_REMOVE : {guild.id}")
        except Exception as e:
            self.logger.error(f"GUILD_REMOVE : failed to sync with guild {guild.id}. Error - {e.__class__.__name__}: {str(e)}")
    
    
async def setup(bot):
    await bot.add_cog(EventHandlerCog(bot))
