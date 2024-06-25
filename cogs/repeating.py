import datetime

import discord
from discord import app_commands
import wavelink
from lib.utils import help_utils
from discord.ext import commands
from lib.ui.colors import BASE_COLOR
from lib.utils.base_utils import djRole_check, quiz_check
from lib.logger import logger
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
from lib.ui import emoji

@logger.LoggerApplication
class RepeatCommands(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="repeat", description="Choose repeat mode")
    @app_commands.describe(mode="What mode do you want to choose?")
    @app_commands.choices(mode=[
        app_commands.Choice(name="No repeat", value="REPEAT_NONE"),
        app_commands.Choice(name="Repeat current track", value="REPEAT_CURRENT_TRACK"),
        app_commands.Choice(name="Repeat the whole queue", value="REPEAT_QUEUE")
    ])
    @help_utils.add("repeat", "Choose a repeat mode", "Music", {"mode": {"description": "What mode do you want to choose?", "required": False}})
    async def repeat_command(self, interaction: discord.Interaction, mode: str=""):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not mode:
            embed = ShortEmbed(f"{emoji.REPEAT} Currently, repeat mode is set to `{player.queue.repeat.string_mode}`")
            await interaction.followup.send(embed=embed)
            return
        
        if not await djRole_check(interaction, self.logger): return
        if mode not in ["REPEAT_NONE", "REPEAT_CURRENT_TRACK", "REPEAT_QUEUE"]:
            embed = ShortEmbed(description=f"{emoji.XMARK} Invalid repeat mode")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        player.queue.repeat.set_repeat(mode.upper()) # upper just in case...
        embed = ShortEmbed(description=f"{emoji.REPEAT} Repeat mode set to `{mode.upper()}`")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RepeatCommands(bot))

