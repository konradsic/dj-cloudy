import datetime
import random

import discord
from discord import app_commands
from discord.ext import commands

from utils import (
    help_utils as help_utils, 
    logger as logger,
    configuration as cfg)
from utils.colors import BASE_COLOR
from utils.errors import (
    IncorrectValueType
)


@logger.LoggerApplication
class ConfigCog(commands.GroupCog, name="config"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view", description="View your configuration profile or configuration for this guild")
    @app_commands.describe(user="Set to true if you want to see your profile, if it's false it will show guild profile")
    async def config_view_command(self, interaction: discord.Interaction, user: bool=True):
        await interaction.response.defer(ephemeral=False, thinking=True)
        if user:
            id = interaction.user.id
        else:
            id = interaction.guild.id
        
        config = cfg.ConfigurationHandler(id=id, user=user)
        data = config.data

        embed = discord.Embed(description="Settings for this profile: key / value\n", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Your configuration profile" if user else "This guild's configuration profile", 
                         icon_url=interaction.user.display_avatar.url if user else interaction.guild.icon.url)
        embed.set_footer(text="https://github.com/konradsic/dj-cloudy")
        
        description = ""

        for key, value in data.items():
            # if role then transform
            val = value["value"]
            if value["type"] == "role":
                val = interaction.guild.get_role(int(value["value"]))
                if val is not None:
                    val = val.name
            
            description += f"`{key}` **:** `{str(val)}`\n"

        embed.description += description
        await interaction.followup.send(embed=embed, ephemeral=True if user else False)

    @app_commands.command(name="set-user", description="Set configuration for your profile")
    @app_commands.describe(key="A parameter you want to change", value="New value for the parameter. For roles,users etc. use thier respective ID")
    async def config_set_user_cmd(self, interaction: discord.Interaction, key: str, value: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        config = cfg.ConfigurationHandler(id=interaction.user.id, user=True)
        
        foundKey = None
        for k,v in config.data.items():
            if k.lower() == key.lower():
                foundKey = k
                break
        if not foundKey:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Key `{key}` was not found.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # change value type depends on correct type
        valType = config.data[foundKey]["type"]
        try:
            if valType == "role":
                value = interaction.guild.get_role(int(value))
            elif valType == "int":
                value = int(value)
            elif valType == "bool":
                
                try:
                    if (int(value) <= 0): 
                        value = False
                except: pass
                if (str(value).lower() == "false"):
                    value = False
                else: 
                    value = True
        except Exception as e:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot convert value to `{valType}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            config.config_set(foundKey, value)
            embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully set `{foundKey}` to `{value}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        except Exception as e:
            if isinstance(e, IncorrectValueType):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to set `{foundKey}` to `{value}`. Please try again",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            raise e

    
    @app_commands.command(name="set-guild", description="Set configuration for current guild. Requires `manage_guild` permission")
    @app_commands.describe(key="A parameter you want to change", value="New value for the parameter. For roles,users etc. use thier respective ID")
    async def config_set_guild_cmd(self, interaction: discord.Interaction, key: str, value: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        config = cfg.ConfigurationHandler(id=interaction.guild.id, user=False)
        
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if not manage_guild:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> `manage_guild` permission is required in order to change this configuration profile.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        foundKey = None
        for k,v in config.data.items():
            if k.lower() == key.lower():
                foundKey = k
                break
        if not foundKey:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Key `{key}` was not found.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # change value type depends on correct type
        valType = config.data[foundKey]["type"]
        try:
            if valType == "role":
                value = interaction.guild.get_role(int(value))
            elif valType == "int":
                value = int(value)
            elif valType == "bool":
                
                try:
                    if (int(value) <= 0): 
                        value = False
                except: pass
                if (str(value).lower() == "false"):
                    value = False
                else: 
                    value = True
        except Exception as e:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot convert value to `{valType}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            config.config_set(foundKey, value)
            embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully set `{foundKey}` to `{value}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        except Exception as e:
            if isinstance(e, IncorrectValueType):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to set `{foundKey}` to `{value}`. Please try again",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            raise e

async def setup(bot):
    help_utils.register_command("config view", "View your configuration profile or configuration for this guild", "Configuration",
        [("user", "Set to true if you want to see your profile, if it's false it will show guild profile", False)])
    await bot.add_cog(ConfigCog(bot), guilds=bot.guilds)