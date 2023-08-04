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
from utils.errors import NoPlayerFound, NoTracksFound, CacheExpired, CacheNotFound
from utils.regexes import URL_REGEX
from utils.base_utils import progressbar_emojis, get_length, limit_string_to, quiz_check
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
    perc = round(progress/end*20) # there will be 20 emoji progressbars
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
    if midbars < 18:
        bar += progressbar_emojis["bar_mid_halffill"]
    # add remaining bars
    bar += f"{progressbar_emojis['bar_mid_nofill'] * (18-midbars)}"
    if perc == 20:
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
        query = "ytsearch:Summer hits 2022"
    elif not re.match(URL_REGEX, current):
        query = "ytsearch:{}".format(current)
    try:
        if query.startswith("🥇") or query.startswith("🥈") or query.startswith("🥉"):
            query = query[2:]
        while True:
            tracks = await wavelink.NodePool.get_connected_node().get_tracks(cls=wavelink.GenericTrack, query=query)
            if not tracks: continue
            break
        if not tracks:
            return []
        
        return [app_commands.Choice(name =
                limit_string_to(
                    f"{number_complete[i]}{track.title} (by {track.author[:-len(' - Topic')] if track.author.endswith(' - Topic') else track.author}) [{get_length(track.duration)}]",
                    100), value=track.uri)
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
        if not await quiz_check(self.bot, interaction, self.logger): return
        try:
            if (player := self.bot.node.get_player(interaction.guild.id)) is None:
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
        tracks = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=query)
        # Song cache saving
        track = tracks[0]
        try:
            await self.bot.song_cache_mgr.get(track.uri)
        except Exception as e:
            if isinstance(e, CacheNotFound) or isinstance(e, CacheExpired):
                await self.bot.song_cache_mgr.save(track.uri, {
                    "uri": track.uri,
                    "title": track.title,
                    "author": track.author,
                    "length": track.length,
                    "id": track.identifier
                })
        
        await player.add_tracks(interaction, [track])
        try:
            pass
        except Exception as e:
            if isinstance(e, NoTracksFound):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No tracks found. Try searching for something else",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return "failed"
            self.logger.error(f"Exception occured -- {e.__class__.__name__}: {str(e)}")
            
    @app_commands.command(name="nowplaying", description="Get currently playing track info in a nice embed")
    @app_commands.describe(hidden="Wherever to hide the message or not (it will be visible only to you)")
    async def nowplaying_command(self, interaction: discord.Interaction, hidden: bool=False):
        await interaction.response.defer(thinking=True, ephemeral=False)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        current = player.queue.current_track
        duration = get_length(current.duration)
        author = current.author
        link = current.uri
        rep = player.queue.repeat.string_mode

        thumb = f"https://img.youtube.com/vi/{current.identifier}/maxresdefault.jpg"
        embed = discord.Embed(
            title="<:play_button:1028004869019279391> Currently playing track informations", 
            description="Here you can view informations about currently playing track", 
            timestamp=datetime.datetime.utcnow(), 
            color=BASE_COLOR
        )
        embed.add_field(name="Track title", value=f"[**{current.title}**]({link})", inline=False)
        embed.add_field(name="Author / Artist", value=author, inline=True)
        embed.add_field(name="Data requested by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Next up", 
            value=f"{'No upcoming track' if not player.queue.upcoming_tracks else f'[{player.queue.upcoming_tracks[0].title}]({player.queue.upcoming_tracks[0].uri})'}"
        )
        embed.add_field(name="Duration", value=f"{compose_progressbar(player.position, current.duration)} `{get_length(player.position)}/{duration}`", inline=False)    
        embed.add_field(name="Repeat mode", value=f"`{rep}`", inline=False)
        try:
            embed.set_thumbnail(url=thumb)
        except:
            try:
                embed.set_thumbnail(url=current.images[0])
            except: pass
        embed.set_footer(text="Made by Konradoo#6938 licensed under the MIT License", icon_url=self.bot.user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=hidden, view=PlayButtonsMenu(user=interaction.user))

    @app_commands.command(name="grab", description="Grab currently playing song to your Direct Messages")
    async def grab_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
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
        try: # add thumbnail
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{song.identifier}/maxresdefault.jpg")
        except:
            try:
                embed.set_thumbnail(url=song.images[0])
            except: pass
        embed.set_footer(text="https://github.com/konradsic/dj-cloudy", icon_url=self.bot.user.display_avatar.url)
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
    help_utils.register_command("play", "Plays music", "Music", [("query","What song to play",True)])
    help_utils.register_command("nowplaying", "Get currently playing track info in a nice embed", "Music", 
                                [("hidden", "Wherever to hide the message or not (it will be visible only to you)", False)])
    help_utils.register_command("grab", "Grab currently playing song to your Direct Messages", "Music")
    await bot.add_cog(
        PlayCommand(bot),
        guilds =[discord.Object(id=g.id) for g in bot.guilds]
    )
