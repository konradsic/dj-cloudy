import datetime

import discord
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.ui.colors import BASE_COLOR
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
import requests

class ChangelogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="changelog", description="Display latest changes to the bot")
    @help_utils.add(name="changelog", description="Display latest changes to the bot", category="Miscellaneous")
    async def changelog_command(self, interaction: discord.Interaction):
        fields = []
        version_info = ""
        latest_version = requests.get("https://raw.githubusercontent.com/konradsic/dj-cloudy/main/CHANGELOG.md").text.split("\n")[3].strip("# ")
        version_info += f"Latest version: `{latest_version}`\n"
        if any(x in latest_version for x in ["a", "b", "pre", "rc"]):
            version_info += "*Not a stable release*\n"
        
        with open("CHANGELOG.md", mode="r") as changelog_file:
            lines = changelog_file.readlines()[3:]
            for line in lines:
                line = line.strip("\n")
                if line == "": continue
                if line.startswith("##") and len(line.split(" ")[0]) == 2:
                    fields.append([line[3:], ""])
                else:
                    fields[-1][1] += line + "\n"
        # small changes to the last field
        fields = [fields[0]]
        current_version = fields[0][0]
        if latest_version == current_version:
            version_info += "This bot is using the latest release"
        else:
            version_info += "This bot **does not** use the latest release available."
        embed = NormalEmbed(
            title="Changelog - latest changes to the bot!", 
            description="This is the changelog. It shows latest changes to the bot. Only latest changes are shown but you can view all of them [**here**](https://github.com/konradsic/dj-cloudy/blob/main/CHANGELOG.md)\n",
            timestamp=True,
            footer=FooterType.GH_LINK
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.description += f"## {fields[0][0]}\n{fields[0][1]}"
        embed.add_field(name="Version info", value=version_info, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChangelogCommand(bot))

