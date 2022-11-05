import datetime
import math
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound, NoTracksFound
from utils.regexes import URL_REGEX
from utils.run import running_nodes
from utils.base_utils import progressbar_emojis, get_length
from utils.buttons import PlayButtonsMenu

logging = logger.Logger().get("cogs.play")

number_complete = {
    0: "🥇 ",
    1: "🥈 ",
    2: "🥉 ",
    3: "4. ",
    4: "5. ",
    5: "6. ",
    6: "7. ",
    7: "8. ",
    8: "9. ",
    9: "10. ",
}

def compose_progressbar(progress, end):
    perc = round(progress/end*12) # there will be 20 emoji progressbars
    full = 12
    bar = ""
    if perc in [0,1]: 
        bar += progressbar_emojis["bar_left_nofill"]
        bar += f"{progressbar_emojis['bar_mid_nofill'] * 10}"
        bar += progressbar_emojis["bar_right_nofill"]
        return bar # its just... short bar now
    else:
        bar += progressbar_emojis["bar_left_fill"]
    midbars = perc-2 # first and last
    # add midbars
    bar += f"{progressbar_emojis['bar_mid_fill'] * midbars}"
    if midbars < 10:
        bar += progressbar_emojis["bar_mid_halffill"]
    # add reamining bars
    bar += f"{progressbar_emojis['bar_mid_nofill'] * (10-midbars)}"
    if perc == 12:
        bar += progressbar_emojis["bar_right_fill"]
        return bar
    bar += progressbar_emojis["bar_right_nofill"]
    return bar

async def query_complete(
    interaction: discord.Interaction, 
    current: str
) -> t.List[app_commands.Choice[str]]:
    query = current.strip("<>")
    if current == "":
        query = "ytmsearch:Summer hits 2022"
    elif not re.match(URL_REGEX, current):
        query = "ytmsearch:{}".format(current)
    try:
        if query.startswith("🥇") or query.startswith("🥈") or query.startswith("🥉"):
            query = query[2:]
        tracks = await running_nodes[0].get_tracks(cls=wavelink.Track, query=query)
        if not tracks:
            return []
        return [
            app_commands.Choice(name=f"{number_complete[i]}{track.title} (by {track.author[:-len(' - Topic')] if track.author.endswith(' - Topic') else track.author}) [{get_length(track.duration)}]", value=track.uri)
            for i,track in enumerate(tracks[:10])
        ]
    except Exception as e:
        if e.__class__.__name__ == "LoadTrackError": return []
        logging.error(f"Error: {e.__class__.__name__} - {str(e)}")
        return []

@logger.LoggerApplication
class PlayCommand(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="play", description="Plays music")
    @app_commands.describe(query="What song to play")
    @app_commands.autocomplete(query=query_complete)
    async def play_command(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=False)
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except:
            if interaction.user.voice is None:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel

        query = query.strip("<>")
        tracks = await self.bot.node.get_tracks(cls=wavelink.Track, query=query)
        await player.add_tracks(interaction, [tracks[0]])
        try:
            pass
        except Exception as e:
            if isinstance(e, NoTracksFound):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No tracks found. Try searching for something else",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return "failed"
            self.logger.error(f"Exception occured -- {e.__class__.__name__}: {str(e)}")

    @app_commands.command(name="nowplaying", description="Get currently playing track info in a nice embed")
    @app_commands.describe(hidden="Wherever to hide the message or not (it will be visible only to you)")
    async def nowplaying_command(self, interaction: discord.Interaction, hidden: bool=False):
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        current = player.queue.current_track
        duration = get_length(current.duration)
        author = current.author
        link = current.uri
        thumb = f"https://img.youtube.com/vi/{current.identifier}/maxresdefault.jpg"
        embed = discord.Embed(
            title="Currently playing track informations", 
            description="Here you can view informations about currently playing track", 
            timestamp=datetime.datetime.utcnow(), 
            color=BASE_COLOR
        )
        embed.add_field(name="Track title", value=f"[**{current.title}**]({link})", inline=False)
        embed.add_field(name="Author / Artist", value=author, inline=True)
        embed.add_field(name="Requested by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Next up", 
            value=f"{'No upcoming track' if not player.queue.upcoming_tracks else f'[{player.queue.upcoming_tracks[0].title}]({player.queue.upcoming_tracks[0].uri})'}"
        )
        embed.add_field(name="Duration", value=f"{compose_progressbar(player.position, current.duration)} `{get_length(player.position)}/{duration}`", inline=False)    
        embed.set_thumbnail(url=thumb)
        embed.set_footer(text="Made by Konradoo#6938 licensed under the MIT License", icon_url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=hidden, view=PlayButtonsMenu(user=interaction.user))

    @app_commands.command(name="grab", description="Grab currently playing song to your Direct Messages")
    async def grab_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        song = player.queue.current_track
        embed = discord.Embed(
            description="You wanted it, you got it!",
            color = BASE_COLOR,
            timestamp = datetime.datetime.utcnow()
        )
        embed.set_author(name="Song grabbed", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="https://github.com/konradsic/dj-cloudy")
        embed.add_field(name="Song title", value=f"[{song.title}]({song.uri})", inline=False)
        embed.add_field(name="Author / Artist", value=song.author)
        embed.add_field(name="Duration", value=f"`{get_length(song.duration)}`")
        embed.add_field(name="Channel", value=f"<#{interaction.channel.id}>")
        embed.add_field(name="Guild", value=interaction.guild.name)

        try:
            await interaction.user.send(embed=embed)
            await interaction.followup.send(embed=discord.Embed(description="<:tick:1028004866662084659> Grabbed to your DMs!", color=BASE_COLOR))
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to grab, make sure your DMs are open to everyone",color=BASE_COLOR)
            await interaction.followup.send(embed=embed)
            return

async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("play", "Plays music", "Music: Base commands", [("query","What song to play",True)])
    help_utils.register_command("nowplaying", "Get currently playing track info in a nice embed", "Music: Base commands", 
                                [("hidden", "Wherever to hide the message or not (it will be visible only to you)", False)])
    help_utils.register_command("grab", "Grab currently playing song to your Direct Messages", "Music: Base commands")
    await bot.add_cog(
        PlayCommand(bot),
        guilds =[discord.Object(id=g.id) for g in bot.guilds]
    )
