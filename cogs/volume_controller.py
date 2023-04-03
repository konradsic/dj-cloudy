import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR

# from music.core import some-import

class VolumeController(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="volume", description="Set or get current playback volume")
    @app_commands.describe(value="Value to set the volume to")
    async def volume_command(self, interaction: discord.Interaction, value: int=None):
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if value is not None:
            if not (0 <= value <= 1000):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume value out of range!",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        volume = player.volume
        if value is None:
            emoji = ""
            if volume == 0: emoji = "<:volume_none:1029437733631967233>"
            if (1 <= volume <= 60): emoji = "<:volume_low:1029437729265688676>"
            if (61 <= volume <= 90): emoji = "<:volume_medium:1029437731354460270>"
            if (91 <= volume <= 1000): emoji = "<:volume_high:1029437727294361691>"

            embed = discord.Embed(description=f"{emoji} Current volume is set to `{volume}%`", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        await player.set_volume(volume=value)

        emoji = ""
        if value == 0: emoji = "<:volume_none:1029437733631967233>"
        if (1 <= value <= 60): emoji = "<:volume_low:1029437729265688676>"
        if (61 <= value <= 90): emoji = "<:volume_medium:1029437731354460270>"
        if (91 <= value <= 1000): emoji = "<:volume_high:1029437727294361691>"
        embed = discord.Embed(description=f"{emoji} Volume successfully set to `{value}%`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @volume_command.error
    async def on_cog_error(self, interaction, error):
        self.logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}")
        embed = discord.Embed(description=
            f"<:x_mark:1028004871313563758> An error occured. Please contact developers for more info. Details are shown below.\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    help_utils.register_command("volume", "Set or get current playback volume", category="Music: Base commands", arguments=[("value", "Value to set the volume to", False)])
    await bot.add_cog(VolumeController(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
