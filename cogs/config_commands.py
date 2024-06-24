import datetime
import random

import discord
from discord import app_commands
from discord.ext import commands
from lib.utils import configuration as cfg, help_utils as help_utils

from lib.logger import (
    logger as logger)
from lib.ui.colors import BASE_COLOR
from lib.utils.errors import IncorrectValueType
from lib.ui.buttons import ResetCfgConfirmation
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
from lib.ui import emoji
import difflib

async def config_guild_autocomplete(interaction: discord.Interaction, current: str):
    config = list(cfg.ConfigurationHandler(id=interaction.guild.id, user=False).get_default_profile_for("guild").keys())
    if current == "":
        return [app_commands.Choice(name=x, value=x) for x in config[:10]]
    
    ranking = sorted([(x, difflib.SequenceMatcher(None, x.lower(), current).quick_ratio()) for x in config], reverse=True, key=lambda x: x[1])
    # print(ranking)
    for i in range(len(ranking)):
        if ranking[i][1] < 0.7:
            ranking = ranking[:i]
            break
    # print("2", ranking)
    return [
        app_commands.Choice(name=x[0], value=x[0]) 
        for x in ranking[:20]
    ]

async def config_user_autocomplete(interaction: discord.Interaction, current: str):
    config = list(cfg.ConfigurationHandler(id=interaction.user.id, user=True).get_default_profile_for("user"))
    if current == "":
        return [app_commands.Choice(name=x, value=x) for x in config[:10]]
    
    ranking = sorted([(x, difflib.SequenceMatcher(None, x.lower(), current).quick_ratio()) for x in config], reverse=True, key=lambda x: x[1])
    # print(ranking)
    for i in range(len(ranking)):
        if ranking[i][1] < 0.7:
            ranking = ranking[:i]
            break
    # print("2", ranking)
    return [
        app_commands.Choice(name=x[0], value=x[0]) 
        for x in ranking[:20]
    ]

@logger.LoggerApplication
class ConfigCog(commands.GroupCog, name="config"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view", description="View your configuration profile or configuration for this guild")
    @app_commands.describe(profile="What profile configuration you want to view? (default: USER)")
    @app_commands.choices(profile=[
        app_commands.Choice(name="USER", value=1),
        app_commands.Choice(name="GUILD", value=0)
    ])
    @help_utils.add("config view", "View your configuration profile or configuration for this guild", category="Configuration", arguments={"profile": {"description": "What profile configuration you want to view? (default: USER)", "required": False}})
    async def config_view_command(self, interaction: discord.Interaction, profile: int = 1):
        await interaction.response.defer(ephemeral=False, thinking=True)
        if profile:
            id = interaction.user.id
        else:
            id = interaction.guild.id
        
        config = cfg.ConfigurationHandler(id=id, user=profile)
        data = config.data

        embed = NormalEmbed(description=f"{emoji.CONFIG} Settings for this profile:", timestamp=True, footer=FooterType.COMMANDS)
        embed.set_author(name="Your configuration profile" if profile else "This guild's configuration profile", 
                         icon_url=interaction.user.display_avatar.url if profile else interaction.guild.icon.url)
        
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
            
            embed.add_field(name=key, value=f"Value: `{str(val)}`", inline=False)
            # description += f"`{key}` **:** `{str(val)}`\n"

        # embed.description += description
        await interaction.followup.send(embed=embed, ephemeral=True if profile else False)

    @app_commands.command(name="set-user", description="Set configuration for your profile")
    @app_commands.describe(key="A parameter you want to change", value="New value for the parameter. For roles,users etc. use their respective ID")
    @app_commands.autocomplete(key=config_user_autocomplete)
    @help_utils.add("config set-user", "Set configuration for your profile", "Configuration",
                    {"key": {"description": "A parameter you want to change", "required": True}, "value": {"description": "New value for the parameter. For roles,users etc. use their respective ID", "required": True}})
    async def config_set_user_cmd(self, interaction: discord.Interaction, key: str, value: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        config = cfg.ConfigurationHandler(id=interaction.user.id, user=True)
        
        foundKey = None
        for k,v in config.data.items():
            if k.lower() == key.lower():
                foundKey = k
                break
        if not foundKey:
            embed = ShortEmbed(description=f"{emoji.XMARK} Key `{key}` was not found.")
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
            embed = ShortEmbed(description=f"{emoji.XMARK} Cannot convert value to `{valType}`")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return


        try:
            config.config_set(foundKey, value)
            embed = ShortEmbed(description=f"{emoji.TICK1} Successfully set `{foundKey}` to `{value}`")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        except Exception as e:
            if isinstance(e, IncorrectValueType):
                embed = ShortEmbed(description=f"{emoji.XMARK} Failed to set `{foundKey}` to `{value}`. Please try again")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            raise e

    
    @app_commands.command(name="set-guild", description="Set configuration for current guild. Requires `manage_guild` permission")
    @app_commands.describe(key="A parameter you want to change", value="New value for the parameter. For roles,users etc. use thier respective ID")
    @app_commands.autocomplete(key=config_guild_autocomplete)
    @help_utils.add("config set-guild", "Set configuration for current guild. Requires `manage_guild` permission", "Configuration",
                    {"key": {"description": "A parameter you want to change", "required": True}, "value": {"description": "New value for the parameter. For roles,users etc. use their respective ID", "required": True}})
    async def config_set_guild_cmd(self, interaction: discord.Interaction, key: str, value: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        config = cfg.ConfigurationHandler(id=interaction.guild.id, user=False)
        
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if not manage_guild:
            embed = ShortEmbed(description=f"{emoji.XMARK} `manage_guild` permission is required in order to change this configuration profile.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        foundKey = None
        for k,v in config.data.items():
            if k.lower() == key.lower():
                foundKey = k
                break
        if not foundKey:
            embed = ShortEmbed(description=f"{emoji.XMARK} Key `{key}` was not found.",color=BASE_COLOR)
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
            embed = ShortEmbed(description=f"{emoji.XMARK} Cannot convert value to `{valType}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            config.config_set(foundKey, value)
            embed = ShortEmbed(description=f"{emoji.TICK1} Successfully set `{foundKey}` to `{value}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        except Exception as e:
            if isinstance(e, IncorrectValueType):
                embed = ShortEmbed(description=f"{emoji.XMARK} Failed to set `{foundKey}` to `{value}`. Please try again",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            raise e
        
    @app_commands.command(name="reset", description="Reset given configuration profile to default values")
    @app_commands.describe(profile="Type of profile you want to reset. For guilds - required manage_guild permission")
    @app_commands.choices(profile=[
        app_commands.Choice(name="GUILD", value=0),
        app_commands.Choice(name="USER", value=1),
    ])
    @help_utils.add("config reset", "Reset given configuration profile to default values", "Configuration", {"profile": {"description": "Type of profile you want to reset. For guilds - required manage_guild permission", "required": True}})
    async def reset_config(self, interaction: discord.Interaction, profile: int):
        await interaction.response.defer(thinking=True, ephemeral=False)
        profile = bool(profile)
        
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if (not manage_guild) and (profile == False):
            embed = ShortEmbed(description=f"{emoji.XMARK} `manage_guild` permission is required in order to change this configuration profile.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        config = cfg.ConfigurationHandler(id=interaction.user.id if profile else interaction.guild.id, user=profile)
        
        embed = ShortEmbed(description="Confirm you want to reset the configuration by clicking \"Yes\"")
        
        await interaction.followup.send(embed=embed, view=ResetCfgConfirmation(1000, config, interaction.user), ephemeral=False)
        
    @app_commands.command(name="reset-value", description="Reset configuration value for given key")
    @app_commands.describe(profile="Type of profile you want to reset the key for. For guilds - required manage_guild permission", key="Key you want to reset value of")
    @app_commands.choices(profile=[
        app_commands.Choice(name="GUILD", value=0),
        app_commands.Choice(name="USER", value=1),
    ])
    @help_utils.add("config reset-value", "Reset configuration value for given key", "Configuration",
                    {"profile": {"description": "Type of profile you want to reset the key for. For guilds - required manage_guild permission", "required": True}, "key": {"description": "Key you want to reset value of", "required": True}})
    async def reset_value_command(self, interaction: discord.Interaction, profile: int, key: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        profile = bool(profile) 
        
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if (not manage_guild) and (profile == False):
            embed = ShortEmbed(description=f"{emoji.XMARK} `manage_guild` permission is required in order to change this configuration profile.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        config = cfg.ConfigurationHandler(id=interaction.user.id if profile else interaction.guild.id, user=profile)
        foundKey = None
        for k,v in config.data.items():
            if k.lower() == key.lower():
                foundKey = k
                break
        if not foundKey:
            embed = ShortEmbed(description=f"{emoji.XMARK} Key `{key}` was not found.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            config.restore_default_vaule(foundKey)
            embed = ShortEmbed(description=f"{emoji.TICK1} Success! Set `{foundKey}` to default value")
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} Failed to set `{foundKey}` to default value")
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
    
    