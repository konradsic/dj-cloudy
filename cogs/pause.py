import discord
from discord import app_commands
from discord.ext import commands
import datetime
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound
from utils import help_utils
from utils.base_utils import djRole_check, quiz_check
from utils import logger

@logger.LoggerApplication
class PlayPauseCommands(commands.Cog):
    def __init__(self,bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="pause", description="Pauses current playing track")
    async def pause_command(self, interaction: discord.Interaction):
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := self.bot.node.get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")

            voice = interaction.user.voice
            if not voice:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "failed"

        if player.is_paused():
            embed = discord.Embed(description=f"<:pause_gradient_button:1028219593082286090> The player is already paused",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return "alr paused"
        
        await player.pause()
        embed = discord.Embed(description=f"<:pause_gradient_button:1028219593082286090> Playback paused",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="resume", description="Resumes paused playback")
    async def resume_command(self, interaction: discord.Interaction):
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := self.bot.node.get_player(interaction.guild.id)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
            voice = interaction.user.voice
            if not voice:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            if str(player.channel.id) != str(voice.channel.id):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "failed"

        if not player.is_paused():
            embed = discord.Embed(description=f"<:play_button:1028004869019279391> The player is already resumed",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return "alr resumed"
        
        await player.resume()
        embed = discord.Embed(description=f"<:play_button:1028004869019279391> Playback resumed",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("pause", "Pauses current playing track", "Music")
    help_utils.register_command("resume", "Resumes paused playback", "Music")
    await bot.add_cog(
        PlayPauseCommands(bot),
        guilds = [discord.Object(id=g.id) for g in bot.guilds]
    )