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
from utils.base_utils import djRole_check

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
    PROGRESSBAR_LENGTH = 15
    perc = math.ceil(progress/end*PROGRESSBAR_LENGTH) # there will be 20 emoji progressbars
    bar = ""
    if perc in [0,1]: 
        bar += progressbar_emojis["bar_left_nofill"]
        bar += f"{progressbar_emojis['bar_mid_nofill'] * (PROGRESSBAR_LENGTH-2)}"
        bar += progressbar_emojis["bar_right_nofill"]
        return bar 
    else:
        bar += progressbar_emojis["bar_left_fill"]
    midbars = perc-2 # first and last
    # add midbars
    bar += f"{progressbar_emojis['bar_mid_fill'] * midbars}"
    if midbars < (PROGRESSBAR_LENGTH-2):
        bar += progressbar_emojis["bar_mid_halffill"]
    # add remaining bars
    bar += f"{progressbar_emojis['bar_mid_nofill'] * (PROGRESSBAR_LENGTH-2-midbars)}"
    if perc == PROGRESSBAR_LENGTH:
        bar += progressbar_emojis["bar_right_fill"]
        return bar
    bar += progressbar_emojis["bar_right_nofill"]
    return bar

async def query_complete(
    interaction: discord.Interaction, 
    current: str
) -> t.List[app_commands.Choice[str]]:
    query = current.strip("<>")
    params = interaction.namespace
    source = params.source
    
    if current == "":
        query = "scsearch:Summer hits 2022"
    elif not re.match(URL_REGEX, current):
        query = f"{source}:{current}"
    try:
        for i in range(20):
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
    @app_commands.describe(source="From what source to search. Ignored when link is pasted", query="What song to play. For spotify tracks use /spotify",
                           play_force="Required DJ permissions. Interrupts current playing track and plays this now.", put_force="Requires DJ permissions. Puts this song after currently playing track")
    @app_commands.autocomplete(query=query_complete)
    @app_commands.choices(source=[
        app_commands.Choice(name="SoundCloud Search", value="scsearch"),
        app_commands.Choice(name="YouTube search", value="ytsearch"),
        app_commands.Choice(name="Link", value="link")
    ])
    async def play_command(self, interaction: discord.Interaction, source: str, query: str, play_force: bool=False, put_force: bool=False):
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
        if not re.match(URL_REGEX, query) and source in ("ytsearch", "scsearch"):
            query = source + ":" + query
        
        counter = 0
        counter_max = 100
        
        for i in range(20):
            counter += 1
            tracks = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=query)
            
            try: 
                tracks[0]
                break
            except: pass
            
            if counter == counter_max: 
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No tracks found. Try searching for something else",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
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
        # put force and play force
        if put_force or play_force:
            await interaction.followup.send(embed=discord.Embed(
                description=f"Passed arguments `put_force={put_force}`, `play_force={play_force}`, checking DJ permissions...", 
                color=BASE_COLOR
            ))
            if not await djRole_check(interaction, self.logger): return
            if play_force and put_force:
                await interaction.followup.send(embed=discord.Embed(
                    description=":bulb: Optimization tip: `put_force` and `play_force` are both `True` although only `play_force` could be.",
                    color=BASE_COLOR
                ))
                put_force = False
        
        await player.add_tracks(interaction, [track], put_force, play_force)
            
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
        spotify = False
        try:
            author = current.author
        except:
            author = ", ".join(current.artists)
            spotify = True
        link = current.uri
        if spotify: link = "https://open.spotify.com/track/" + current.uri.split(":")[2]
        rep = player.queue.repeat.string_mode

        try: thumb = f"https://img.youtube.com/vi/{current.identifier}/maxresdefault.jpg"
        except: thumb = current.images[0]
        embed = discord.Embed(
            title="<:play_button:1028004869019279391> Currently playing track informations", 
            description="Here you can view informations about currently playing track", 
            timestamp=datetime.datetime.utcnow(), 
            color=BASE_COLOR
        )
        title = current.title
        if spotify: title = f"{'E ' if current.explicit else ''}{title}"
        embed.add_field(name="Track title", value=f"[**{title}**]({link})", inline=False)
        embed.add_field(name="Author / Artist", value=author, inline=True)
        embed.add_field(name="Data requested by", value=interaction.user.mention, inline=True)
        upcoming = player.queue.upcoming_track
        if upcoming: 
            upcoming_url = player.queue.upcoming_track.uri
            if spotify: upcoming_url = 'https://open.spotify.com/track/' + upcoming_url.split(':')[2]
            embed.add_field(name="Next up", 
                value=f"[{player.queue.upcoming_tracks[0].title}]({upcoming_url})",
                inline=False
            )
        else:
            embed.add_field(
                name="Next up",
                value="No upcoming tracks",
                inline=False
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
            color = BASE_COLOR,
            timestamp = datetime.datetime.utcnow()
        )
        embed.set_author(name="Song grabbed", icon_url=interaction.user.display_avatar.url)
        spotify = False
        try: song.author
        except:
            spotify = True
        
        try: # add thumbnail
            if spotify: embed.set_thumbnail(song.images[0])
            else: embed.set_thumbnail(url=f"https://img.youtube.com/vi/{song.identifier}/maxresdefault.jpg")
        except:
            pass
        title = song.title
        if spotify: title = f"{'E ' if song.explicit else ''}{title}"
        embed.set_footer(text="Have a nice day :D", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Song title", value=f"[{title}]({song.uri if not spotify else 'https://open.spotify.com/track/' + song.uri.split(':')[2]})", inline=False)
        if spotify: embed.add_field(name="Artist(s)", value=", ".join(song.artists))
        else: embed.add_field(name="Author", value=song.author)
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
    help_utils.register_command("play", "Plays music", "Music", [
        ("source", "From what source to search. Ignored when link is pasted", True),
        ("query","What song to play. For spotify tracks use /spotify",True),
        ("play_force", "Required DJ permissions. Interrupts current playing track and plays this now.", False),
        ("put_force", "Requires DJ permissions. Puts this song after currently playing track", False)
    ])
    help_utils.register_command("nowplaying", "Get currently playing track info in a nice embed", "Music", 
                                [("hidden", "Wherever to hide the message or not (it will be visible only to you)", False)])
    help_utils.register_command("grab", "Grab currently playing song to your Direct Messages", "Music")
    await bot.add_cog(
        PlayCommand(bot)
    )
