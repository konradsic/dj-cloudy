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
    @app_commands.describe(category="A category/group of commands you want to view")
    async def help_command(self, interaction: discord.Interaction, category: str=None):
        help_commands = help_utils.get_commands()
        categories = {}
        for command in help_commands:
            try:
                categories[command["category"]].append(command)
            except:
                categories[command["category"]] = [command]
        
        if category is None:
            embed = discord.Embed(
                title="<:commands_button:1028377812777828502> Help command - Categories", 
                description="Here you can view all categories and some best commands that belong to these categories (only 3 are shown but there are more!). Use `/help [categroy]` to view a specific category with detailed description", 
                color=BASE_COLOR
            )
            embed.set_footer(text="Made by Konradoo#6824, licensed under the MIT License")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            for category_name, category_items in zip(categories.keys(), categories.values()):
                embed.add_field(name=f"{category_name} - {len(category_items)}", value=f'Example: `{random.choice(category_items)["name"]}`', inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        categories_lower = [c.lower() for c in categories.keys()]
        # check if the category exists
        if category.lower() not in categories_lower:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Category does not exist. Use `/help` to view all categories",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        selected_category = {}
        # get items for category
        for ctg in categories.items():
            if category.lower() == ctg[0].lower():
                selected_category = ctg[1]

        # get the category
        embed = discord.Embed(title=f"<:commands_button:1028377812777828502> Help for category {category}", description="*<> - required, [] - optional*", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.set_footer(text="Made by Konradoo#6824, licensed under the MIT License")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        for command in selected_category:
            arguments = ""
            syntax_arguments = ""
            try:
                for arg in list(command['arguments'].items()):
                    arguments += f"- `{arg[0]}` - {arg[1]['description']}. Required: `{arg[1]['required']}`\n"
                    syntax_arguments += f"<{arg[0]}> " if arg[1]['required'] else f"[{arg[0]}] "
                embed.add_field(name=command["name"], value=f"{command['description']}\nSyntax: `/{command['name']} {syntax_arguments[:-1]}`\n**Arguments:**\n{arguments}", inline=False)
            except Exception as e:
                embed.add_field(name=command["name"], value=f"{command['description']}\nSyntax: `/{command['name']}`", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    help_utils.register_command("help", "Get helpful information about commands of the bot", "Miscellaneous", [("category","A category/group of commands you want to view",False)])
    await bot.add_cog(HelpCommand(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])