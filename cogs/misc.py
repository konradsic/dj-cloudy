import datetime
import difflib
import time

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from lib.ui import emoji
from lib.ui.colors import BASE_COLOR
from lib.ui.embeds import FooterType, NormalEmbed, ShortEmbed
from lib.utils import help_utils
from lib.utils.base_utils import basic_auth, get_nodes, get_config
# from lib.utils.help_utils import get_commands


async def command_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    current = current.strip("/")
    matcher = difflib.SequenceMatcher
    commands = [cmd for cmd in help_utils.commands.keys()]
    #print("command autocomplete matching star")
    matches: list[tuple] = [] # (cmd, match)
    for i, command in enumerate(commands):
        #print(f"{i}/{len(commands)}...\t", end="\r")
        result = matcher(None, current.lower(), command.lower()).quick_ratio()
        matches.append((command, result))
    # cap at 10
    matches = sorted(matches, reverse=True, key=lambda x: x[1])[:5]
    #print(matches)
    return [
        app_commands.Choice(name=f"{f'{i}.' if i > 1 else '🏆'} /{match[0]}", value=match[0])
        for i, match in enumerate(matches, start=1)
    ]

class MiscCommands(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.content.startswith(f"<@{str(self.bot.user.id)}>") or 
            message.content.startswith(f"<@!{self.bot.user.id}>") or 
            message.content.startswith(self.bot.user.mention)):
            embed = NormalEmbed(
                title="Hello! I'm DJ Cloudy",
                description="A cool bot that will make your server better by adding music functionality. Music playback at the next level. Invite now!",
                timestamp=True,
            )
            embed.set_footer(text=FooterType.MADE_BY.value, icon_url=self.bot.user.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(name="Why you should choose me?", value="- I am all free\n- Advanced music functions such as equalizers\n- Playlist system so you can save your favourite songs\n- Easy to use")
            embed.add_field(name="Links", value="[**Invite me!**](https://dsc.gg/dj-cloudy)\n[*Join Our Discord Server*](https://discord.gg/t6qPGdHypw)\n[GitHub Project: Report bugs, see code and more](https://github.com/konradsic/dj-cloudy)")
            await message.channel.send(embed=embed)

    @app_commands.command(name="ping",description="Returns latency and uptime of the bot")
    @help_utils.add("ping", "Returns latency and uptime of the bot", "Miscellaneous")
    async def ping_command(self,interaction: discord.Interaction):
        embed = NormalEmbed(timestamp=True, footer=FooterType.COMMANDS)
        embed.set_author(name="Pong! Here are the results", icon_url=self.bot.user.avatar)
        embed.add_field(name="<:stats_gradient:1024352560724836444> Latency", value=f"`{round(self.bot.latency*1000)}ms`")
        embed.add_field(name=":clock1: Last restart", value=f"<t:{self.bot.last_restart}:R> / <t:{self.bot.last_restart}:f>")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Gathers some information about the bot and Wavelink nodes")
    @help_utils.add("botinfo", "Gathers some information about the bot and Wavelink nodes", "Miscellaneous")
    async def botinfo_command(self,interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        # gather all informations below:
        nodes = [get_nodes()]
        node_data = "".join(f'**Node `{node.identifier}`** with status `{node.status.name}`\n  - Host: URI `{basic_auth("uri", node.uri, interaction.user)}`\n' for node in nodes)
        if node_data == "":
            node_data = "No information about connected nodes"
        players = []
        for node in nodes:
            players.extend(node.players)
        print(players)
        actual_players = []
        for p in players:
            actual_players.append(wavelink.Pool.get_node().get_player(int(p)))
            
        players = actual_players
        players_data = ""
        if len(players) > 10:
            players_data = f"`{len(players)}` connected to **{len(nodes)}** node(s)"
        elif len(players) == 0:
            players_data = "No players connected. Use `/connect` to connect the bot to your voice channel!"
        else:
            players_data = "".join(f"`{i}.` Player guild: **{player.guild.id}**, playing: `{player.playing}`, paused: `{player.paused}`" for i,player in enumerate(players, start=1))

        embed = NormalEmbed(title="Bot informations", description="Informations gathered are below",timestamp=True, footer=FooterType.GH_LINK)
        embed.add_field(name="Nodes data", value=node_data, inline=False)
        embed.add_field(name="Players data", value=players_data, inline=False)
        embed.add_field(name="Bot informations", 
            value=f"Bot ID: `{self.bot.user.id}`\nLatency: `{round(self.bot.latency*1000)}ms`\nGuilds count: **{len(self.bot.guilds)}**\nBot created at: <t:{round(time.mktime(self.bot.user.created_at.strptime(str(self.bot.user.created_at)[:10], '%Y-%m-%d').timetuple()))}:f>", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    @app_commands.command(name="credits", description="Display credits")
    @help_utils.add("credits", "Display credits", "Miscellaneous")
    async def credits_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        embed = NormalEmbed(description="A list of people who are very proud to be a part of the DJ Cloudy team.",
                            timestamp=True)
        embed.set_author(name="Credits", icon_url=self.bot.user.avatar.url)
        embed.set_footer(text="Thanks to all people from our team <3")
        
        DEVELOPERS = [958029521565679646]
        SPONSORS = [508661400089002004]
        # TESTERS = [997874629379117086, 958029521565679646]
        TESTERS = [997874629379117086]
        
        devlen = len(DEVELOPERS)
        sponsorlen = len(SPONSORS)
        testlen = len(TESTERS)
        
        string_devs = "\n".join(f"<@{dev}>" for dev in DEVELOPERS)
        string_sponsors = "\n".join(f"<@{sponsor}>" for sponsor in SPONSORS)
        string_testers = "\n".join(f"<@{tester}>" for tester in TESTERS)
        
        dev_text_singular     = "*This person codes the bot*"
        dev_text_plural       = "*These people code the bot*"
        sponsor_text_singular = "*This person sponsors the DJ Cloudy project*"
        sponsor_text_plural   = "*These people sponsor the DJ Cloudy project*"
        tester_text_singular  = "*This person test the bot to ensure everything is running smoothly*"
        tester_text_plural    = "*These people test the bot to ensure everything is running smoothly*"
        
        embed.add_field(name=f"{emoji.DEVELOPER.string} Developer{'s' if len(DEVELOPERS) > 1 else ''}", value=f"\n{dev_text_singular if devlen == 1 else dev_text_plural}\n{string_devs}", inline=False)
        embed.add_field(name=f"{emoji.SPONSOR.string} Sponsor{'s' if len(SPONSORS) > 1 else ''}", value=f"\n{sponsor_text_singular if sponsorlen == 1 else sponsor_text_plural}\nNo sponsors for now!", inline=False)
        embed.add_field(name=f"{emoji.TESTER.string} Tester{'s' if len(TESTERS) > 1 else ''}", value=f"\n{tester_text_singular if testlen == 1 else tester_text_plural}\n{string_testers}", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)
        
    @app_commands.command(name="bug-report", description="Report bugs")
    @app_commands.describe(command="When using which command the bug occurred?", description="Description of the bug")
    @app_commands.autocomplete(command=command_autocomplete)
    @help_utils.add("bug-report", "Report bugs", "Miscellaneous", {"command": {"description": "When using which command the bug occurred?", "required": True}, "description": {"description": "Description of the bug", "required": True}})
    async def bugreport_command(self, interaction: discord.Interaction, command: str, description: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed = NormalEmbed(timestamp=True, footer=FooterType.NONE, description=f"**Description of the bug:**\n```{description}```", title="Recieved a bug report via /bug-report command")
        embed.add_field(name="Command", value=f"```/{command}```", inline=False)
        embed.add_field(name="Submitted by", value=f"<@{interaction.user.id}>\n```@{interaction.user.name} ({interaction.user.id})```", inline=False)
        cfg = get_config()["bot"]
        guild: discord.Guild = self.bot.get_guild(int(cfg["support-server-id"]))
        channel = guild.get_channel(int(cfg["auto-bug-report-channel"]))
        await channel.send(embed=embed)
        
        await interaction.followup.send("Submitted your bug! There is a chance it will be fixed")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MiscCommands(bot))
