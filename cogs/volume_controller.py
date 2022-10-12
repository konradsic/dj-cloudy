import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR

# from music.core import 

volume_guilds = {} # guildID: value

class VolumeController(commands.GroupCog, name="volume"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="get", description="Get current playback volume")
    async def volume_get_command(self, interaction: discord.Interaction):
        print(volume_guilds)
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        try:
            volume = volume_guilds[str(interaction.guild.id)]
        except:
            volume = 100

        emoji = ""
        comment = ""
        if volume == 0: emoji = "<:volume_none:1029437733631967233>"
        if (1 <= volume <= 60): emoji = "<:volume_low:1029437729265688676>"
        if (61 <= volume <= 90): emoji = "<:volume_medium:1029437731354460270>"
        if (91 <= volume <= 1000): emoji = "<:volume_high:1029437727294361691>"
        if (150 <= volume <= 250): comment = "*It starts to hurt my ears*"
        if (251 <= volume <= 600): comment = "*Ouchhh, stop it!!!*"
        if (601 <= volume <= 1000): comment = "*I am literally dying :earrape_enabled_sadge:*"

        embed = discord.Embed(description=f"{emoji} Current volume is set to `{volume}%` {comment}", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set", description="Set current playback volume to given value")
    @app_commands.describe(value="Value to set the volume to")
    async def volume_set_command(self, interaction: discord.Interaction, value: int) -> None:
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        if not (0 <= value <= 1000):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume out of range. Please select an integer between `0` and `200`. Or maybe you can go higher???",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        await player.set_volume(volume=value)
        volume_guilds[str(interaction.guild.id)] = value
        emoji = ""
        comment = ""
        if value == 0: emoji = "<:volume_none:1029437733631967233>"
        if (1 <= value <= 60): emoji = "<:volume_low:1029437729265688676>"
        if (61 <= value <= 90): emoji = "<:volume_medium:1029437731354460270>"
        if (91 <= value <= 1000): emoji = "<:volume_high:1029437727294361691>"
        if (150 <= value <= 250): comment = "*It starts to hurt my ears*"
        if (251 <= value <= 600): comment = "*Ouchhh, stop it!!!*"
        if (601 <= value <= 1000): comment = "*I am literally dying :earrape_enabled_sadge:*"
        embed = discord.Embed(description=f"{emoji} Volume successfully set to `{value}%` {comment}", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="default", description="Set the volume to the default value (100%)")
    async def volume_setdefault_command(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        await player.set_volume(100) # default value
        volume_guilds[str(interaction.guild.id)] = 100
        embed = discord.Embed(description="<:volume_high:1029437727294361691> Volume successfully set to default (`100%`)", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    help_utils.register_command("volume get", "Get current playback volume", category="Music: Base commands")
    help_utils.register_command("volume set", "Set current playback volume to given value", category="Music: Base commands", arguments=[("value", "Value to set the volume to", True)])
    help_utils.register_command("volume default", "Set the volume to the default value (100%)", category="Music: Base commands")
    await bot.add_cog(VolumeController(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
