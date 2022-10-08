import datetime

import discord
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR


class ChangelogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="changelog", description="Display latest changes to the bot")
    async def changelog_command(self, interaction: discord.Interaction):
        fields = []
        with open("CHANGELOG.md", mode="r") as changelog_file:
            lines = changelog_file.readlines()[5:]
            for line in lines:
                line = line.strip("\n ")
                if line.startswith("##"):
                    fields.append([line[3:], ""])
                else:
                    fields[-1][1] += line + "\n"
        embed = discord.Embed(
            title="Changelog - latest changes to the bot!", 
            description="This is the changelog. It shows latest changes to the bot. 2 newest are described longer than others to prevent file being too big",
            color=BASE_COLOR,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    help_utils.register_command("changelog", "Display latest changes to the bot", "Miscellaneous")
    await bot.add_cog(ChangelogCommand(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
