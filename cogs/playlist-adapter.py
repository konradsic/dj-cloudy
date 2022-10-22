import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music import playlist
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.colors import BASE_COLOR
from utils.errors import (PlaylistCreationError, PlaylistGetError,
                          PlaylistRemoveError)

logger_instance = logger.Logger().get("cogs.playlist-adapter")

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
            return "incorrect position"
        user_data = playlist.PlaylistHandler(key=str(user.id))
        playlists = user_data.playlists
        playlist_res = "No playlists for this user. Create a playlist with `/playlist create <name>`!"
        if playlists:
            for i, p in enumerate(playlists,1):
                playlist_res += f"**{i}.** {p['name']} `#{p['id']}` *({len(p['tracks'])}) songs, duration `notImplemented`*"
        starred_playlist_data = f"{len(user_data.data['starred-playlist'])} total songs, total duration `notImplemented`"
        embed = discord.Embed(description="These are the user's playlists", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
        embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
        embed.set_footer(text="Made by Konradoo#6938")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="create", description="Create a new playlist")
    @app_commands.describe(name="Name of the playlist")
    async def playlist_create_command(self, interation: discord.Interaction, name: str):
        pass

    @app_commands.command(name="add-song", description="Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to add the song to")
    @app_commands.describe(song="Name of the song you want to add")
    async def playlist_add_song_command(self, interation: discord.Interaction, name_or_id: str, song: str):
        pass

    @app_commands.command(name="remove-song", description="Remove a song from your playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove the song from")
    @app_commands.describe(index="Index of the song you want to remove (1-playlist len)")
    async def playlist_remove_song_command(self, interation: discord.Interaction, name_or_id: str, index: int):
        pass

    @app_commands.command(name="remove-playlist", description="Remove a playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove")
    async def playlist_remove_command(self, interation: discord.Interaction, name_or_id: str):
        pass

    @app_commands.command(name="play", description="Play your playlist!")
    @app_commands.describe(name_or_id="Name of the playlist you want to play")
    @app_commands.describe(replace_queue="Wherever to replace queue with the playlist or just to append")
    async def playlist_play(self, interation: discord.Interaction, name_or_id: str, replace_queue: bool=False):
        pass

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
