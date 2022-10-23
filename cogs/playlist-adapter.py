from cgitb import handler
import datetime
import typing as t
import re

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music import playlist
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.colors import BASE_COLOR
from utils.errors import (NoPlayerFound, PlaylistCreationError, PlaylistGetError,
                          PlaylistRemoveError)
from utils.regexes import URL_REGEX
from utils.run import running_nodes
from utils.base_utils import get_length

logger_instance = logger.Logger().get("cogs.playlist-adapter")

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

# autocomplete for song url
async def song_url_autocomplete(interaction: discord.Interaction, current: str) -> t.List[app_commands.Choice]:
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
        logger_instance.error("", "song_autocomplete", f"Error: {e.__class__.__name__} - {str(e)}")
        return []

@logger.class_logger
class PlaylistGroupCog(commands.GroupCog, name="playlists"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="view", description="View your or user's playlists")
    @app_commands.describe(user="View this user's playlists")
    async def playlist_view_command(self, interaction: discord.Interaction, user: discord.Member=None):
        # get the user
        if user is None:
            user = interaction.user
        if user.bot:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Bots cannot have playlists! Make sure to select a user next time",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        user_data = playlist.PlaylistHandler(key=str(user.id))
        playlists = user_data.playlists
        playlist_res = "No playlists for this user. Create a playlist with `/playlist create <name>`!"
        if playlists:
            playlist_res = ""
            for i, p in enumerate(playlists,1):
                total_duration = 0
                for track in p['tracks']:
                    d = await self.bot.node.get_tracks(cls=wavelink.Track, query=track)
                    total_duration += d[0].length
                playlist_res += f"**{i}.** {p['name']} `#{p['id']}` `[{get_length(total_duration)}]` *{len(p['tracks'])} song(s)*"
        starred_dur = 0
        for t in user_data.data['starred-playlist']:
            d = await self.bot.node.get_tracks(cls=wavelink.Track, query=t)
            starred_dur += d[0].length
        starred_playlist_data = f"{len(user_data.data['starred-playlist'])} total songs, total duration `{get_length(starred_dur)}`\n"
        embed = discord.Embed(description="These are the user's playlists", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
        embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
        embed.set_footer(text="Made by Konradoo#6938")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="create", description="Create a new playlist")
    @app_commands.describe(name="Name of the playlist")
    async def playlist_create_command(self, interaction: discord.Interaction, name: str):
        if len(name) > 30:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Playlist name should be less that 30 characters!",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        limits = 25 # max playlists for user
        if handler.data['credentials'] == 1:
            limits = 100 # max playlists for moderators
        elif handler.data['credentials'] == 2:
            limits = 10**15 # "infinity", max playlists for admins
        if len(handler.playlists) >= limits:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Playlist creation exceeds your current limits. Only moderators, admins and devs have higher limits. Contact us for more info",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            handler.create_playlist(name)
        except PlaylistCreationError:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to create playlist, please try again",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully created playlist **{name}**",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add-song", description="Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to add the song to")
    @app_commands.describe(song="Name of the song you want to add")
    @app_commands.autocomplete(song=song_url_autocomplete)
    async def playlist_add_song_command(self, interaction: discord.Interaction, name_or_id: str, song: str):
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        # find the playlist
        found = None
        for p in handler.playlists:
            if p['name'] == name_or_id or p['id'] == name_or_id:
                found = p
                break
        if not found:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to get playlist with name/id `{name_or_id}`. Make sure that the name is a name of __your__ playlist",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        limits = 75 # Maximum songs in a playlist
        if handler.data['credentials'] == 1:
            limits = 500
        elif handler.data['credentials'] == 2:
            limits = 10**15 # "infinity"
        if len(handler.playlists) >= limits:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Song addition exceeds your playlist's song limit. Higher limits are available for moderators and admins",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            handler.add_to_playlist(name_or_id, song)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> An error occured while trying to add the song. Please try again",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully added [**song**]({song}) to the playlist",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-song", description="Remove a song from your playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove the song from")
    @app_commands.describe(index="Index of the song you want to remove (1-playlist len)")
    async def playlist_remove_song_command(self, interaction: discord.Interaction, name_or_id: str, index: int):
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        if index <= 0:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Index should be between 1 and playlist length",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            handler.remove(name_or_id, index-1)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> An error occured while trying to remove the song. Check if index is correct and the name or ID of the playlist",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully removed song at position `{index}` from playlist __{name_or_id}__",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-playlist", description="Remove a playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove")
    async def playlist_remove_command(self, interaction: discord.Interaction, name_or_id: str):
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        try:
            handler.remove_playlist(name_or_id)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> An error occured while trying to remove the playlist. Check spelling and name then try again",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully removed playlist **{name_or_id}**",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Play your playlist!")
    @app_commands.describe(name_or_id="Name of the playlist you want to play")
    @app_commands.describe(replace_queue="Wherever to replace queue with the playlist or just to append")
    async def playlist_play(self, interaction: discord.Interaction, name_or_id: str, replace_queue: bool=False):
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            if interaction.user.voice is None:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel
        # get tracks
        res = []
        for play in handler.playlists:
            if play['name'] == name_or_id or play['id'] == name_or_id:
                res = play

        # adapt the playlist
        if replace_queue:
            # we need to replace the queue
            player.queue.cleanup()
            tracks = [list(await self.bot.node.get_tracks(cls=wavelink.Track, query=song))[0] for song in res['tracks']]
            player.queue.add(*tracks)
            await player.play_first_track()
            return
        else:
            tracks = [list(await self.bot.node.get_tracks(cls=wavelink.Track, query=song))[0] for song in res['tracks']]
            await player.add_tracks(interaction, tracks)
            return

async def setup(bot):
    help_utils.register_command("playlists view", "View your or user's playlists", "Music: Playlist management", [("user", "View this user's playlists", False)])
    help_utils.register_command("playlists create", "Create a new playlist", "Music: Playlist management", [("name", "Name of the playlist", True)])
    help_utils.register_command("playlists add-song", 
        "Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist", "Music: Playlist management", 
        [("name_or_id", "Name of the playlist you want to add the song to", True),("song", "Name of the song you want to add",True)])
    help_utils.register_command("playlists remove-song", "Remove a song from your playlist", "Music: Playlist management", 
        [("name_or_id", "Name of the playlist you want to remove the song from", True),("index", "Index of the song you want to remove (1-playlist len)", True)])
    help_utils.register_command("playlists play", "Play your playlist!", "Music: Playlist management", 
        [("name_or_id", "Name of the playlist you want to play", True), ("replace_queue", "Wherever to replace the queue with the playlist or just append", False)])
    help_utils.register_command("playlists remove-playlist", "Remove a playlist", "Music: Playlist management", [("name_or_id", "Name of the playlist you want to remove", True)])
    await bot.add_cog(PlaylistGroupCog(bot), guilds=bot.guilds)
