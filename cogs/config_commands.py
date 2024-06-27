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

async def config_double_autocomplete(interaction: discord.Interaction, current: str):
    profile = interaction.namespace.profile
    config = cfg.ConfigurationHandler(id=interaction.guild.id, user=profile).get_default_profile_for("user" if profile else "guild")
    try: del config["trackBlacklistRules"]
    except: pass
    config = list(config.keys())
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

async def config_guild_autocomplete(interaction: discord.Interaction, current: str):
    config = cfg.ConfigurationHandler(id=interaction.guild.id, user=False).get_default_profile_for("guild")
    del config["trackBlacklistRules"]
    config = list(config.keys())
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
        if profile == 0:
            del data["blacklistRules"]

        embed = NormalEmbed(description=f"{emoji.CONFIG} Settings for this profile:", timestamp=True, footer=FooterType.COMMANDS)
        embed.set_author(name="Your configuration profile" if profile else "This guild's configuration profile", 
                         icon_url=interaction.user.display_avatar.url if profile else interaction.guild.icon.url)

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

        if key in ["defaultVolume"]:
            if not (0 <= value <= 1000):
                await interaction.followup.send(embed=ShortEmbed(f"{emoji.XMARK} Volume values must be between `0` and `1000`"))
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
        if key.lower() == "blacklistrules":
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.XMARK} To set `blacklistRules` please use `/config blacklist-add` command"))
            return
        
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
    @app_commands.autocomplete(key=config_double_autocomplete)
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
        
    @app_commands.command(name="blacklist-add", description="Add a rule to the blacklist")
    @app_commands.describe(rule="Rule type you want to add", content="Content of the rule")
    @app_commands.choices(rule=[
        app_commands.Choice(name="Author's name contains", value=0),
        app_commands.Choice(name="Track title contains", value=1),
        app_commands.Choice(name="Track URI is equal to", value=2)
    ])
    @help_utils.add("config blacklist-add", "Add a rule to the blacklist", "Configuration", 
                    {"rule": {"description": "Rule type you want to add", "required": True}, "content": {"description": "Content of the rule", "required": True}})
    async def trackblacklist_add_command(self, interaction: discord.Interaction, rule: int, content: str):
        await interaction.response.defer(thinking=True, ephemeral=False)
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if (not manage_guild):
            embed = ShortEmbed(description=f"{emoji.XMARK} `manage_guild` permission is required in order to change this configuration profile.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if not (0 <= rule <= 2):
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.XMARK} Invalid rule type. Please use one of the choices given while completing the command."))
            return
        
        config = cfg.ConfigurationHandler(str(interaction.guild.id), user=False)
        blacklist = config.data["blacklistRules"]["value"]
        if len(blacklist) == 10:
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.XMARK} Maximum `10` blacklist rules can be added"))
            return
        
        transform = {
            0: "Author's name contains",
            1: "Track title contains",
            2: "Track link is equal to"
        }
        config.blacklist_add(rule, content)
        await interaction.followup.send(embed=ShortEmbed(f"{emoji.TICK1} Created rule: Exclude track when `{transform[rule]}` {content}"))
        
    
    @app_commands.command(name="blacklist-view", description="View the blacklist for current guild")
    @help_utils.add("config blacklist-view", "View the blacklist for current guild", "Configuration")
    async def trackblacklist_view_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        embed = NormalEmbed(True, description="")
        embed.set_author(name="Blacklist rules", icon_url=interaction.guild.icon.url)
        
        config = cfg.ConfigurationHandler(str(interaction.guild.id), False)
        blacklist = config.data["blacklistRules"]["value"]
        if blacklist == []:
            embed.description = "No blacklist rules in this guild. Create one using `/config blacklist-add`"
        
        transform = {
            0: "Author's name contains",
            1: "Track title contains",
            2: "Track link is equal to"
        }
        for i, (rule, content) in enumerate(blacklist, start=1):
            embed.add_field(name=f"Rule #{i}", value=f"Exclude track when `{transform[rule]}` {content}", inline=False)
            
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="blacklist-remove", description="Remove a rule from the blacklist")
    @app_commands.describe(ruleindex="Index of the rule to remove")
    @help_utils.add("config blacklist-remove", "Remove a rule from the blacklist", "Configuration", {"ruleindex": {"description": "Index of the rule to remove", "required": True}})
    async def trackblacklist_remove_command(self, interaction: discord.Interaction, ruleindex: int):
        await interaction.response.defer(thinking=True, ephemeral=False)
        perms = interaction.user.resolved_permissions
        manage_guild = perms.manage_guild
        if (not manage_guild):
            embed = ShortEmbed(description=f"{emoji.XMARK} `manage_guild` permission is required in order to change this configuration profile.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        config = cfg.ConfigurationHandler(str(interaction.guild.id), False)
        blacklist = config.data["blacklistRules"]["value"]
        if not (1 <= ruleindex <= len(blacklist)):
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.XMARK} Rule index `{ruleindex}` out of range"))
            return
        
        original = config.data["blacklistRules"]["value"][ruleindex-1]
        rule = {
            0: "Author's name contains",
            1: "Track title contains",
            2: "Track link is equal to"
        }[original[0]]
        config.blacklsit_remove(ruleindex-1)
        await interaction.followup.send(embed=ShortEmbed(f"{emoji.TICK1} Successfully remoed **Rule #{ruleindex}: ** Exclude track when `{rule}` {original[1]}"))

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
    
    