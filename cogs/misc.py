import datetime

import discord
import wavelink
import time
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils.base_utils import get_nodes, basic_auth
class MiscCommands(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.content.startswith(f"<@{str(self.bot.user.id)}>") or 
            message.content.startswith(f"<@!{self.bot.user.id}>") or 
            message.content.startswith(self.bot.user.mention)):
            embed = discord.Embed(
                title="Hello! I'm DJ Cloudy",
                description="A cool bot that will make your server better by adding music functionality. Music playback at the next level. Invite now!",
                timestamp=datetime.datetime.utcnow(),
                color=BASE_COLOR
            )
            embed.set_footer(text="Made by Konradoo#6938 licensed under the MIT License", icon_url=self.bot.user.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="Why you should choose me?", value="- I am all free\n- Advanced music functions such as equalizers (coming soon)\n- Easy to use")
            embed.add_field(name="Links", value="[**Invite me!**](https://discord.com/api/oauth2/authorize?client_id=1024303533685751868&permissions=962676125504&scope=bot%20applications.commands)\n[*Join Our Discord Server*](https://discord.gg/t6qPGdHypw)\n[GitHub Project: Report bugs, see code and more](https://github.com/konradsic/dj-cloudy)")
            await message.channel.send(embed=embed)

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

    @app_commands.command(name="botinfo", description="Gathers most of informations about the bot and Wavelink nodes")
    async def botinfo_command(self,interaction: discord.Interaction):
        # gather all informations below:
        nodes = get_nodes()
        node_data = "".join(f'**Node `{node.identifier}`** at region *{node.region}*\n  - Host: `{basic_auth("node_host", node.host, interaction.user)}:{basic_auth("node_port", node.port, interaction.user)}`\n' for node in nodes)
        if node_data == "":
            node_data = "No information about connected nodes"
        players = []
        for node in nodes:
            players.extend(node.players)
        players_data = ""
        if len(players) > 10:
            players_data = f"`{len(players)}` connected to **{len(nodes)}** node(s)"
        elif len(players) == 0:
            players_data = "No players connected. Use `/connect` to connect the bot to your voice channel!"
        else:
            players_data = "".join(f"`{i}.` Player guild: **{player.guild.id}**, playing: `{player.is_playing()}`, paused: `{player.is_paused()}`" for i,player in enumerate(players,1))

        embed = discord.Embed(title="Bot informations", description="Informations gathered are below",color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Nodes data", value=node_data, inline=False)
        embed.add_field(name="Players data", value=players_data, inline=False)
        embed.add_field(name="Bot informations", value=f"Bot ID: `{self.bot.user.id}`\nLatency: `{round(self.bot.latency*1000)}ms`\nGuilds count: **{len(self.bot.guilds)}**\nCreated by: [Konradoo](https://github.com/konradsic) (bot), [ArgoMk3](https://github.com/ArgoTeam) (web)\nBot created at: <t:{round(time.mktime(self.bot.user.created_at.strptime(str(self.bot.user.created_at)[:10], '%Y-%m-%d').timetuple()))}:f>", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user} | Licensed under the MIT License")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("ping", "Returns latency and uptime of the bot", "Miscellaneous")
    help_utils.register_command("botinfo", "Gathers most of informations about the bot and Wavelink nodes", "Miscellaneous")
    await bot.add_cog(
        MiscCommands(bot),
        guilds = [discord.Object(id=g.id) for g in bot.guilds]
    )
