import discord
from discord.ext import commands
from discord import app_commands
from utils import help_utils
from utils.colors import BASE_COLOR
import datetime

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get helpful information about commands of the bot")
    async def help_command(self, interaction: discord.Interaction):
        help_commands = help_utils.get_commands()
        categories = {}
        for command in help_commands:
            try:
                categories[command["category"]].append(command)
            except:
                categories[command["category"]] = [command]
        embed = discord.Embed(title="<:commands_button:1028377812777828502> Here you go! There are my commands", description="*<> - required, [] - optional*", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.set_footer(text="Made by Konradoo#6824, licensed under the MIT License")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        for category in categories:
            result = ""
            for command in categories[category]:
                try:
                    arguments = ""
                    for arg in command['arguments']:
                        arguments += f"<{arg}> " if command['arguments'][arg]['required'] else f"[{arg}] "
                    current = f"`/{command['name']} {arguments[:-1]}` - {command['description']}\n"
                except:
                    current = f"`/{command['name']}` - {command['description']}\n"
                result += current
            embed.add_field(name=f"{category} - {len(categories[category])}",value=result, inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    help_utils.register_command("help", "Get helpful information about commands of the bot", "Miscellaneous")
    await bot.add_cog(HelpCommand(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])