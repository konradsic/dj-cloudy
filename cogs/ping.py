import discord
from discord import app_commands
from discord.ext import commands
import datetime
from utils.colors import BASE_COLOR
from utils import help_utils

class PingCommand(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping",description="Returns latency and uptime of the bot")
    async def ping_command(self,interaction: discord.Interaction):
        embed = discord.Embed(
            color=BASE_COLOR, 
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_author(name="Pong! Here are the results", icon_url=self.bot.user.avatar)
        embed.add_field(name="<:stats_gradient:1024352560724836444> Latency", value=f"`{round(self.bot.latency*1000)}ms`")
        embed.add_field(name=":clock1: Last restart", value=f"<t:{self.bot.last_restart}:R> / <t:{self.bot.last_restart}:f>")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("ping", "Returns latency and uptime of the bot", "Miscellaneous")
    await bot.add_cog(
        PingCommand(bot),
        guilds = [discord.Object(id=g.id) for g in bot.guilds]
    )
