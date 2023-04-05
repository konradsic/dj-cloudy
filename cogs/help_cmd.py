import discord
from discord.ext import commands
from discord import app_commands
from utils import help_utils
from utils.colors import BASE_COLOR
import datetime
import random

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get helpful information about commands of the bot")
    @app_commands.describe(command="A command you want to get detailed information about")
    async def help_command(self, interaction: discord.Interaction, command: str=None):
        await interaction.response.defer(thinking=True)
        help_commands = help_utils.get_commands()
        categories = {}
        for cmd in help_commands:
            try:
                categories[cmd["category"]].append(cmd)
            except:
                categories[cmd["category"]] = [cmd]
        
        if command is None:
            embed = discord.Embed(
                title="<:commands_button:1028377812777828502> Help command - Categories", 
                description="Here, all categories with their respective commands are shown. To get detailed info about a command, use `/help <command>`\n*My command prefix is `/`*", 
                color=BASE_COLOR
            )
            embed.set_footer(text="Made by Konradoo#6824, licensed under the MIT License")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            for category_name, category_items in zip(categories.keys(), categories.values()):
                embed.add_field(name=f"{category_name} ({len(category_items)})", value="".join(
                    f"`{command['name']}` ■ "
                    for command in category_items[:-1]
                ) + f"`{category_items[-1]['name']}`", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        names_lower = [n['name'].lower() for n in help_commands]
        # check if the category exists
        if command.lower() not in names_lower:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Command does not exist. Use `/help` to view all commands",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        selected_command = {}
        # get items for category
        for cmd in help_commands:
            if command.lower() == cmd['name'].lower():
                selected_command = cmd

        command = selected_command # to make life easier
        # get the category
        embed = discord.Embed(title=f"<:commands_button:1028377812777828502> Help for command `/{command['name']}`", description="*<> - required, [] - optional*", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.set_footer(text="Made by Konradoo#6824, licensed under the MIT License")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        arguments = ""
        syntax_arguments = ""
        embed.add_field(name="Description", value=command['description'], inline=False)
        try:
            for arg in list(command['arguments'].items()):
                arguments += f"■ `{arg[0]}` - {arg[1]['description']}. Required: `{arg[1]['required']}`\n"
                syntax_arguments += f"<{arg[0]}> " if arg[1]['required'] else f"[{arg[0]}] "
            embed.add_field(name="Arguments", value=f"{arguments}", inline=False)
        except Exception as e: pass

        embed.add_field(name="Command syntax", value=f"`/{command['name']}{' ' + syntax_arguments[:-1] if syntax_arguments else ''}`", inline=False)
    
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    help_utils.register_command("help", "Get helpful information about commands of the bot", "Miscellaneous", [("category","A category/group of commands you want to view",False)])
    await bot.add_cog(HelpCommand(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])