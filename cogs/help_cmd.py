import discord
from discord.ext import commands
from discord import app_commands
from lib.utils import help_utils
from lib.ui.colors import BASE_COLOR
import datetime
import random
from lib.ui.embeds import NormalEmbed, ShortEmbed, FooterType

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get helpful information about commands of the bot")
    @app_commands.describe(command="A command you want to get detailed information about")
    @help_utils.add("help", "Get helpful information about commands of the bot", "Miscellaneous", arguments={"command": {"description": "A command you want to get detailed information about", "required": False}})
    async def help_command(self, interaction: discord.Interaction, command: str=None):
        await interaction.response.defer(thinking=True)
        help_commands = help_utils.commands
        categories = help_utils.get_by_category()
        
        if command is None:
            embed = NormalEmbed(
                title=f"<:commands_button:1028377812777828502> Help: Displaying `{len(help_commands.keys())}` commands", 
                description="Here, all categories with their respective commands are shown. To get detailed info about a command, use `/help <command>`\n*My command prefix is `/`*",
                footer=FooterType.MADE_BY
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            # print(categories)
            for category_name, category_data in categories.items():
                embed.add_field(name=f"{category_name} ({len(category_data)})", value=" ■ ".join(
                    f"`{command[0]}`"
                    for command in category_data
                ), inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        names_lower = [n.lower() for n in help_commands.keys()]
        # check if the category exists
        command = command.strip("/")
        if command.lower() not in names_lower:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Command does not exist. Use `/help` to view all commands")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        selected_command = help_commands[command.lower()]
        # get the category
        embed = NormalEmbed(title=f"<:commands_button:1028377812777828502> Help for command `/{command.lower()}`", description="*<> - required, [] - optional*", timestamp=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        arguments = ""
        syntax_arguments = ""
        embed.add_field(name="Description", value=selected_command["description"], inline=False)
        embed.add_field(name="Category", value=selected_command["category"])
        try:
            for arg in list(selected_command["arguments"].items()):
                arguments += f"■ `{arg[0]}` - {arg[1]['description']}. Required: `{arg[1]['required']}`\n"
                syntax_arguments += f"<{arg[0]}> " if arg[1]["required"] else f"[{arg[0]}] "
            embed.add_field(name="Arguments", value=arguments, inline=False)
        except Exception as e: pass

        embed.add_field(name="Command syntax", value=f"`/{command.lower()}{' ' + syntax_arguments[:-1] if syntax_arguments else ''}`", inline=False)
    
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    # help_utils.register_command("help", "Get helpful information about commands of the bot", "Miscellaneous", 
    #                           [("command","A command you want to get detailed information about",False)])
    await bot.add_cog(HelpCommand(bot))