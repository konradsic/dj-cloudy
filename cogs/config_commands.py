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
from utils.errors import IncorrectValueType
from utils.buttons import ResetCfgConfirmation


@logger.LoggerApplication
class ConfigCog(commands.GroupCog, name="config"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view", description="View your configuration profile or configuration for this guild")
    @app_commands.describe(profile="What profile configuration you want to view?")
    @app_commands.choices(profile=[
        app_commands.Choice(name="USER", value=1),
        app_commands.Choice(name="GUILD", value=0)
    ])
    async def config_view_command(self, interaction: discord.Interaction, profile: int = 1):
        await interaction.response.defer(ephemeral=False, thinking=True)
        if profile:
            id = interaction.user.id
        else:
            id = interaction.guild.id
        
        config = cfg.ConfigurationHandler(id=id, user=profile)
        data = config.data

        embed = discord.Embed(description="Settings for this profile: key / value\n", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
        embed.set_author(name="Your configuration profile" if profile else "This guild's configuration profile", 
                         icon_url=interaction.user.display_avatar.url if profile else interaction.guild.icon.url)
        embed.set_footer(text="https://github.com/konradsic/dj-cloudy")
        
        description = ""

        for key, value in data.items():
            # if role then transform
            val = value["value"]
            if value["type"] == "role":
                if value["value"] is not None:
                    val = interaction.guild.get_role(int(value["value"]))
                    if val is not None:
                        val = val.name
                    val = "@" + val
                else:
                    val = "null"
            
            description += f"`{key}` **:** `{str(val)}`\n"

        embed.description += description
        await interaction.followup.send(embed=embed, ephemeral=True if profile else False)

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
        
    @app_commands.command(name="reset", description="Reset given configuration profile to default values")
    @app_commands.describe(profile="Type of profile you want to reset. For guilds - required manage_guild permission")
    @app_commands.choices(profile=[
        app_commands.Choice(name="GUILD", value=0),
        app_commands.Choice(name="USER", value=1),
    ])
    async def reset_config(self, interaction: discord.Interaction, profile: int):
        await interaction.response.defer(thinking=True, ephemeral=False)
        profile = bool(profile)
        
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if (not manage_guild) and (profile == False):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> `manage_guild` permission is required in order to change this configuration profile.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        config = cfg.ConfigurationHandler(id=interaction.user.id if profile else interaction.guild.id, user=profile)
        
        embed = discord.Embed(description="Confirm you want to reset the configuration by clicking \"Yes\"", color=BASE_COLOR)
        
        await interaction.followup.send(embed=embed, view=ResetCfgConfirmation(1000, config, interaction.user), ephemeral=False)
        
    @app_commands.command(name="reset-value", description="Reset configuration value for given key")
    @app_commands.describe(profile="Type of profile you want to reset. For guilds - required manage_guild permission", key="Key you want to reset value for")
    @app_commands.choices(profile=[
        app_commands.Choice(name="GUILD", value=0),
        app_commands.Choice(name="USER", value=1),
    ])
    async def reset_value_command(self, interaction: discord.Interaction, profile: int, key: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        profile = bool(profile) 
        
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if (not manage_guild) and (profile == False):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> `manage_guild` permission is required in order to change this configuration profile.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        config = cfg.ConfigurationHandler(id=interaction.user.id if profile else interaction.guild.id, user=profile)
        foundKey = None
        for k,v in config.data.items():
            if k.lower() == key.lower():
                foundKey = k
                break
        if not foundKey:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Key `{key}` was not found.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            config.restore_default_vaule(foundKey)
            embed = discord.Embed(description=f"<:tick:1028004866662084659> Success! Set `{foundKey}` to default value", color=BASE_COLOR)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to set `{foundKey}` to default value", color=BASE_COLOR)
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot):
    help_utils.register_command("config view", "View your configuration profile or configuration for this guild", "Configuration",
        [("profile", "What profile configuration you want to view?", False)])
    help_utils.register_command("config set-user", "Set configuration for your profile", "Configuration",
        [("key", "A parameter you want to change", True),
         ("value","New value for the parameter. For roles,users etc. use thier respective ID",True)])
    help_utils.register_command("config set-guild", "Set configuration for current guild. Requires `manage_guild` permission", "Configuration",
        [("key", "A parameter you want to change", True),
         ("value","New value for the parameter. For roles,users etc. use thier respective ID",True)])
    help_utils.register_command("config reset", "Reset given configuration profile to default values", "Configuration",
        [("profile", "Type of profile you want to reset. For guilds - required manage_guild permission", True)])
    help_utils.register_command("config reset-value", "Reset configuration value for given key", "Configuration",
        [("profile", "Type of profile you want to reset. For guilds - required manage_guild permission", True),
         ("key", "Key you want to reset value for", True)])
    await bot.add_cog(ConfigCog(bot), guilds=bot.guilds)