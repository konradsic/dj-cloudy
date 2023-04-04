import discord
from discord import app_commands
from discord.ext import commands
import datetime
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound
from utils import help_utils

class PlayPauseCommands(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="pause", description="Pauses current playing track")
    async def pause_command(self, interaction: discord.Interaction):
        try:
            if (player := self.bot.node.get_player(interaction.guild.id)) is None:
                    raise NoPlayerFound("There is no player connected in this guild")
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "failed"

        if player.is_paused():
            embed = discord.Embed(description=f"<:pause_gradient_button:1028219593082286090> The player is already paused",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "alr paused"
        
        await player.set_pause(True)
        embed = discord.Embed(description=f"<:pause_gradient_button:1028219593082286090> Playback paused",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="resume", description="Resumes paused playback")
    async def resume_command(self, interaction: discord.Interaction):
        try:
            if (player := self.bot.node.get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "failed"

        if not player.is_paused():
            embed = discord.Embed(description=f"<:play_button:1028004869019279391> The player is already resumed",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "alr resumed"
        
        await player.set_pause(False)
        embed = discord.Embed(description=f"<:play_button:1028004869019279391> Playback resumed",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("pause", "Pauses current playing track", "Music: Base commands")
    help_utils.register_command("resume", "Resumes paused playback", "Music: Base commands")
    await bot.add_cog(
        PlayPauseCommands(bot),
        guilds = [discord.Object(id=g.id) for g in bot.guilds]
    )