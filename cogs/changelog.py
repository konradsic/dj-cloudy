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
            lines = changelog_file.readlines()[3:]
            for line in lines:
                line = line.strip("\n")
                if line == "": continue
                if line.startswith("##"):
                    fields.append([line[3:], ""])
                else:
                    fields[-1][1] += line + "\n"
        # small changes to the last field
        fields = fields[:5]
        embed = discord.Embed(
            title="Changelog - latest changes to the bot!", 
            description="This is the changelog. It shows latest changes to the bot. Only 5 latest changes are shown but you can view all changes [**here**](https://github.com/konradsic/dj-cloudy/blob/main/CHANGELOG.md)",
            color=BASE_COLOR,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    help_utils.register_command("changelog", "Display latest changes to the bot", "Miscellaneous")
    await bot.add_cog(ChangelogCommand(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
