import datetime

import discord
from discord import app_commands
import wavelink
from utils import help_utils
from discord.ext import commands
from utils.colors import BASE_COLOR
from utils.base_utils import djRole_check, quiz_check
from utils import logger

@logger.LoggerApplication
class RepeatCommands(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="repeat", description="Choose a repeating mode")
    @app_commands.describe(mode="What mode do you want to choose?")
    @app_commands.choices(mode=[
        app_commands.Choice(name="No repeat", value="REPEAT_NONE"),
        app_commands.Choice(name="Repeat current track", value="REPEAT_CURRENT_TRACK"),
        app_commands.Choice(name="Repeat the whole queue", value="REPEAT_QUEUE")
    ])
    async def repeat_command(self, interaction: discord.Interaction, mode: str):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        player.queue.repeat.set_repeat(mode.upper()) # upper just in case...
        embed = discord.Embed(description=f"<:repeat_button:1030534158302330912> Repeat mode set to `{mode.upper()}`", color=BASE_COLOR)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    help_utils.register_command("repeat", "Choose a repeating mode", "Music", [("mode", "What mode you want to choose?", True)])
    await bot.add_cog(RepeatCommands(bot),
                guilds=[discord.Object(id=g.id) for g in bot.guilds])
