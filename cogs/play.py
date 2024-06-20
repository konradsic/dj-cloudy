import datetime
import math
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.music.core import MusicPlayer
from lib.logger import logger
from lib.ui.colors import BASE_COLOR
from lib.utils.errors import NoPlayerFound, NoTracksFound, CacheExpired, CacheNotFound
from lib.utils.regexes import URL_REGEX
from lib.utils.base_utils import progressbar_emojis, get_length, limit_string_to, quiz_check
from lib.ui.buttons import PlayButtonsMenu
from lib.utils.base_utils import djRole_check
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
from lib.ui import emoji

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

SEARCH_SOURCES = [
    "ytsearch",
    "scsearch",
    "ytmsearch"
]

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
    
    if current == "":
        query = "Summer hits 2022"
    try:
        logging.debug("Trying to get results for: ", query)
        for i in range(20):
            # test for every source
            for src in [None, *SEARCH_SOURCES]:
                this_query = ""
                if not (any(query.startswith(x + ":") for x in SEARCH_SOURCES)):
                    this_query += f"{src}:" if src is not None else ""
                this_query += query
                tracks = await wavelink.Pool.fetch_tracks(this_query)
                if tracks != []:
                    break
            if not tracks: continue
            break
        
        if not tracks:
            return []
        
        logging.debug("Autocomplete: found", len(tracks), "tracks")
        return [app_commands.Choice(name =
                limit_string_to(
                    f"{number_complete[i]}{track.title} (by {track.author[:-len(' - Topic')] if track.author.endswith(' - Topic') else track.author}) [{get_length(track.length)}]",
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
    # def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger

    @app_commands.command(name="play", description="Plays music")
    @app_commands.describe(query="What song to play. For spotify tracks use /spotify",
                           play_force="Required DJ permissions. Interrupts current playing track and plays this now.", 
                           put_force="Requires DJ permissions. Puts this song after currently playing track")
    @app_commands.autocomplete(query=query_complete)
    @help_utils.add("play", "Plays music", "Music", 
                    {"query": {"description": "What song to play. For spotify tracks use /spotify", "required": True}, 
                     "play_force": {"description": "Required DJ permissions. Interrupts current playing track and plays this now.", "required": False}, 
                     "put_force": {"description": "Requires DJ permissions. Puts this song after currently playing track", "required": False}})
    async def play_command(self, interaction: discord.Interaction, query: str, play_force: bool=False, put_force: bool=False):
        await interaction.response.defer(ephemeral=False)
        if not await quiz_check(self.bot, interaction, self.logger): return
        if interaction.user.voice is None:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel
        except: 
            # already connected, get player
            player = wavelink.Pool.get_node().get_player(interaction.guild.id)
            
        query = query.strip("<>")
        for i in range(20):
            for src in [None, *SEARCH_SOURCES]:
                this_query = ""
                if not (any(query.startswith(x + ":") for x in SEARCH_SOURCES)):
                    this_query += f"{src}:" if src is not None else ""
                this_query += query
                tracks = await wavelink.Pool.fetch_tracks(this_query)
                if tracks != []:
                    break

            try: 
                tracks[0]
                break
            except: pass
            
            if i == 19: 
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> No tracks found. Try searching for something else")
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
            await interaction.followup.send(embed=ShortEmbed(
                description=f"{emoji.LOADING.mention} Passed arguments `put_force={put_force}`, `play_force={play_force}`, checking DJ permissions...", 
                color=BASE_COLOR
            ))
            if not await djRole_check(interaction, self.logger): return
            if play_force and put_force:
                await interaction.followup.send(embed=ShortEmbed(
                    description=":bulb: Optimization tip: `put_force` and `play_force` are both `True` although only `play_force` could be.",
                    color=BASE_COLOR
                ))
                put_force = False
        # self.logger.debug("Passing track to <MusicPlayer - add_tracks>, track", track)
        await player.add_tracks(interaction, [track], put_force, play_force)
            
    @app_commands.command(name="nowplaying", description="Get currently playing track info in a nice embed")
    @app_commands.describe(hidden="Whether to hide the message or not (it will be visible only to you)")
    @help_utils.add("nowplaying", "Get currently playing track info in a nice embed", "Music", {"hidden": {"description": "Whether to hide the message or not (it will be visible only to you)", "required": False}})
    async def nowplaying_command(self, interaction: discord.Interaction, hidden: bool=False):
        await interaction.response.defer(thinking=True, ephemeral=False)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        current = player.queue.current_track
        length = get_length(current.length)
        link = current.uri
        rep = player.queue.repeat.string_mode
        paused = player.paused

        thumb = current.artwork
        embed = NormalEmbed(
            title="<:play_button:1028004869019279391> Currently playing track informations", 
            description="Here you can view informations about currently playing track", 
            timestamp=True, 
        )
        title = current.title
        embed.add_field(name="Track title", value=f"[**{title}**]({link})", inline=False)
        embed.add_field(name="Author / Artist", value=current.author, inline=True)
        embed.add_field(name="Song requested by", value=player.queue.current_requested.mention, inline=True)
        upcoming = player.queue.upcoming_track
        if upcoming: 
            upcoming_url = player.queue.upcoming_track.uri
            embed.add_field(name="Next up", 
                value=f"[{player.queue.upcoming_tracks[0].title}]({upcoming_url})",
                inline=False
            )
        else:
            embed.add_field(name="Next up", value="No upcoming tracks", inline=False)
            
        embed.add_field(name="Length", value=f"{compose_progressbar(player.position, current.length)} `{get_length(player.position)}/{length}`", inline=False)    
        embed.add_field(name="Repeat mode", value=f"`{rep}`", inline=True)
        embed.add_field(name="Playback paused", value=f"`{'Yes' if paused else 'No'}`", inline=True)
        embed.set_thumbnail(url=thumb)
        embed.set_footer(text=FooterType.COMMANDS.value, icon_url=self.bot.user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=hidden, view=PlayButtonsMenu(user=interaction.user))

    @app_commands.command(name="grab", description="Grab currently playing song to your Direct Messages")
    @help_utils.add("grab", "Grab currently playing song to your Direct Messages", "Music")
    async def grab_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not player.playing:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        song = player.queue.current_track
        embed = NormalEmbed(
            color = BASE_COLOR,
            timestamp = True
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
        embed.add_field(name="length", value=f"`{get_length(song.length)}`")
        embed.add_field(name="Channel", value=f"<#{interaction.channel.id}>")
        embed.add_field(name="Guild", value=interaction.guild.name)

        try:
            await interaction.user.send(embed=embed)
            await interaction.followup.send(embed=ShortEmbed(description="<:tick:1028004866662084659> Grabbed to your DMs!"))
        except:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Failed to grab, make sure your DMs are open to everyone")
            await interaction.followup.send(embed=embed)
            return

async def setup(bot: commands.Bot) -> None:
    # help_utils.register_command("play", "Plays music", "Music", [
    #     ("query","What song to play. For spotify tracks use /spotify",True),
    #     ("play_force", "Required DJ permissions. Interrupts current playing track and plays this now.", False),
    #     ("put_force", "Requires DJ permissions. Puts this song after currently playing track", False)
    # ])
    # help_utils.register_command("nowplaying", "Get currently playing track info in a nice embed", "Music", 
    #                             [("hidden", "Wherever to hide the message or not (it will be visible only to you)", False)])
    # help_utils.register_command("grab", "Grab currently playing song to your Direct Messages", "Music")
    await bot.add_cog(PlayCommand(bot))
