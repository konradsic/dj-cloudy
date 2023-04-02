import datetime
import re
import time
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from music import playlist
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.base_utils import get_length, limit_string_to
from utils.buttons import EmbedPaginator
from utils.colors import BASE_COLOR
from utils.errors import (NoPlayerFound, PlaylistCreationError,
                          PlaylistGetError, PlaylistRemoveError)
from utils.regexes import URL_REGEX
from utils.run import running_nodes

logger_instance = logger.Logger().get("cogs.playlist_adapter")

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
        query = "ytmsearch:Best music"
    elif not re.match(URL_REGEX, current):
        query = "ytmsearch:{}".format(current)
    try:
        if query.startswith("🥇") or query.startswith("🥈") or query.startswith("🥉"):
            query = query[2:]
        tracks = await running_nodes[0].get_tracks(cls=wavelink.Track, query=query)
        if not tracks:
            return []
        return [
            app_commands.Choice(
                name=limit_string_to(
                    f"{number_complete[i]}{track.title} (by {track.author[:-len(' - Topic')] if track.author.endswith(' - Topic') else track.author}) [{get_length(track.duration)}]",
                    100), value=track.uri)
            for i,track in enumerate(tracks[:10])
        ]
    except Exception as e:
        if e.__class__.__name__ == "LoadTrackError": return []
        logger_instance.error(f"Error: {e.__class__.__name__} - {str(e)}")
        return []

@logger.LoggerApplication
class PlaylistGroupCog(commands.GroupCog, name="playlists"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view-playlist", description="View playlist's content (for your playlist or anybody else)")
    @app_commands.describe(name_or_id="Name or id of the playlist")
    @app_commands.describe(user="(optional) User to get the playlist from")
    async def view_playlist_of_user_command(self, interaction: discord.Interaction, name_or_id: str, user: t.Union[discord.Member, None]=None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not user:
            user = interaction.user
        handler = playlist.PlaylistHandler(key=str(user.id))
        # get the playlist
        found = None
        for play in handler.playlists:
            if play['name'].lower() == name_or_id.lower() or play['id'].lower() == name_or_id.lower():
                found = play
                break
        
        if not found:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No playlist was found",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        tracks = []
        start = time.time()
        for song in found['tracks']:
            # to prevent errors we infinite request over the track if it fails, 
            # otherwise we break out of the loop
            while True:
                query = await self.bot.node.get_tracks(cls=wavelink.Track, query=song)
                if not query:
                    self.logger.error(f"Failed to fetch song \"{song}\" (request failed)")
                    continue
                tracks.append(query[0])
                break
        took_time = time.time() - start
        self.logger.info(f"Loaded {len(found['tracks'])} tracks in ~{took_time:.2f}s")
        fields = [
            f"**{i+1}.** [{tracks[i].title}]({tracks[i].uri}) `[{get_length(tracks[i].length)}]`\n"
            for i in range(len(tracks))
        ]
        num_fields = len(fields)//6
        if len(fields)%num_fields != 0:
            num_fields += 1
        per_page = len(fields)//(num_fields-1)
        res_fields = []
        for _ in range(num_fields):
            res_fields.append([])
            for _ in range(per_page):
                try:
                    res_fields[-1].append(fields[0])
                    del fields[0]
                except:
                    break
        embeds = []
        for i, field in enumerate(res_fields, start=1):
            embed = discord.Embed(description="Those are the tracks in user's playlist", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text="Made by Konradoo#6938")
            embed.set_author(name=f"{user.name}'s playlist: {found['name']}#{found['id']}", icon_url=user.display_avatar.url)
            embed.add_field(name=f"Tracks (page {i}/{len(res_fields)})", value="".join(t for t in field), inline=False)
            embed.add_field(name="Additional informations", value=f"Playlist length: `{get_length(sum([track.length for track in tracks]))}`\nTotal songs: `{len(tracks)}`")
            embeds.append(embed)
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user), ephemeral=True)
        return True

    @app_commands.command(name="view", description="View your or user's playlists")
    @app_commands.describe(user="View this user's playlists")
    async def playlist_view_command(self, interaction: discord.Interaction, user: discord.Member=None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        # get the user
        if user is None:
            user = interaction.user
        if user.bot:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Bots cannot have playlists! Make sure to select a user next time",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        user_data = playlist.PlaylistHandler(key=str(user.id))
        playlists = user_data.playlists
        playlist_res = "No playlists for this user. Create a playlist with `/playlist create <name>`!"
        
        total_tracks = 0
        start = time.time()
        if playlists:
            playlist_res = ""
            for i, p in enumerate(playlists,1):
                total_duration = 0
                for track in p['tracks']:
                    while True:
                        d = await self.bot.node.get_tracks(cls=wavelink.Track, query=track)
                        if not d:
                            self.logger.error(f"Failed to fetch song \"{track}\" (request failed)")
                            continue
                        total_duration += d[0].length
                        total_tracks += 1
                        break
                playlist_res += f"**{i}.** {p['name']} `#{p['id']}` `[{get_length(total_duration)}]` *{len(p['tracks'])} song(s)*\n"
                
        took_time = time.time() - start
        self.logger.info(f"Loaded {total_tracks} tracks in ~{took_time:.2f}s")
        
        total_tracks = 0
        starred_dur = 0
        start = time.time()
        
        for t in user_data.data['starred-playlist']:
            while True:
                d = await self.bot.node.get_tracks(cls=wavelink.Track, query=t)
                if not d:
                    self.logger.error(f"Failed to fetch song \"{t}\" (request failed)")
                    continue
                starred_dur += d[0].length
                total_tracks += 1
                break
        took_time = time.time() - start
        self.logger.info(f"Loaded starred playlist ({total_tracks} songs) in ~{took_time:.2f}s")
        
        starred_playlist_data = f"{len(user_data.data['starred-playlist'])} total songs, total duration `{get_length(starred_dur)}`\n"
        embed = discord.Embed(description="These are the user's playlists", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
        embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
        embed.set_footer(text="Made by Konradoo#6938")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="create", description="Create a new playlist")
    @app_commands.describe(name="Name of the playlist")
    @app_commands.describe(copy_queue="Wherever to copy the queue to playlist or not")
    async def playlist_create_command(self, interaction: discord.Interaction, name: str, copy_queue: bool=False):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if len(name) > 30:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Playlist name should be less that 30 characters!",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        limits = 25 # max playlists for user
        if handler.data['credentials'] == 1:
            limits = 100 # max playlists for moderators
        elif handler.data['credentials'] == 2:
            limits = 10**15 # "infinity", max playlists for admins
        if len(handler.playlists) >= limits:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Playlist creation exceeds your current limits. Only moderators, admins and devs have higher limits. Contact us for more info",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if name.lower() == "starred":
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> 'starred' is a special playlist name that stands for your :star: songs. You can't use it for playlist creation",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            tracks = []
            if copy_queue:
                try:
                    if (player := self.bot.node.get_player(interaction.guild)) is None:
                        raise NoPlayerFound("There is no player connected in this guild")
                except NoPlayerFound:
                    embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel -> no queue -> no songs to copy",color=BASE_COLOR)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                if player.queue.is_empty:
                    embed = discord.Embed(description=f"<:x_mark:1028004871313563758> There are not tracks in the queue so there is nothing to copy",color=BASE_COLOR)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                tracks = [song.uri for song in player.queue.get_tracks()]
            handler.create_playlist(name, tracks)
        except PlaylistCreationError:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to create playlist, please try again",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully created playlist **{name}**",color=BASE_COLOR)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="add-song", description="Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to add the song to")
    @app_commands.describe(song="Name of the song you want to add")
    @app_commands.autocomplete(song=song_url_autocomplete)
    async def playlist_add_song_command(self, interaction: discord.Interaction, name_or_id: str, song: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        # find the playlist
        found = None
        starred = False
        for p in handler.playlists:
            if p['name'].lower() == name_or_id.lower() or p['id'].lower() == name_or_id.lower():
                found = p
                break
        if name_or_id.lower() == "starred":
            found = 'starred'
            starred = True
        if not found and not starred:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to get playlist with name/id `{name_or_id}`. Make sure that the name is a name of __your__ playlist",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        limits = 75 # Maximum songs in a playlist
        if handler.data['credentials'] == 1:
            limits = 500
        elif handler.data['credentials'] == 2:
            limits = 10**15 # "infinity"
        if not starred:
            if len(handler.playlists[found]) >= limits:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Song addition exceeds your playlist's song limit. Higher limits are available for moderators and admins",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            try:
                handler.add_to_playlist(name_or_id, song)
            except:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> An error occured while trying to add the song. Please try again",color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully added [**song**]({song}) to the playlist",color=BASE_COLOR)
            await interaction.followup.send(embed=embed)
            return
        added = handler.add_to_starred(song)
        if not added:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> This song was already in the playlist so it has been removed.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed)
            return
        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully added [**song**]({song}) to the starred playlist",color=BASE_COLOR)
        await interaction.followup.send(embed=embed)
        return

    @app_commands.command(name="remove-song", description="Remove a song from your playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove the song from")
    @app_commands.describe(index="Index of the song you want to remove (1-playlist len)")
    async def playlist_remove_song_command(self, interaction: discord.Interaction, name_or_id: str, index: int):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        if index <= 0:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Index should be between 1 and playlist length",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            handler.remove(name_or_id, index-1)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> An error occured while trying to remove the song. Check if index is correct and the name or ID of the playlist",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully removed song at position `{index}` from playlist __{name_or_id}__",color=BASE_COLOR)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="remove-playlist", description="Remove a playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove")
    async def playlist_remove_command(self, interaction: discord.Interaction, name_or_id: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        try:
            handler.remove_playlist(name_or_id)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> An error occured while trying to remove the playlist. Check spelling and name then try again",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(description=f"<:tick:1028004866662084659> Successfully removed playlist **{name_or_id}**",color=BASE_COLOR)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="play", description="Play your playlist!")
    @app_commands.describe(name_or_id="Name of the playlist you want to play")
    @app_commands.describe(replace_queue="Wherever to replace queue with the playlist or just to append")
    async def playlist_play(self, interaction: discord.Interaction, name_or_id: str, replace_queue: bool=False):
        await interaction.response.defer(ephemeral=False, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
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
        # get tracks
        res = {}
        for play in handler.playlists:
            if play['name'].lower() == name_or_id.lower() or play['id'].lower() == name_or_id.lower():
                res = play
        if name_or_id.lower() == "starred":
            res = handler.data['starred-playlist']
            res = {'tracks': res}
        self.logger.debug(res)
        if not res:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No playlist with name \"{name_or_id}\" was found. Perhaps you misspelled it?",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        # adapt the playlist
        if replace_queue:
            # we need to replace the queue
            player.queue.cleanup()
            
            tracks = []
            start = time.time()
            for song in res['tracks']:
                # to prevent errors we infinite request over the track if it fails, 
                # otherwise we break out of the loop
                while True:
                    query = await self.bot.node.get_tracks(cls=wavelink.Track, query=song)
                    if not query:
                        self.logger.debug(f"Failed to fetch song \"{song}\" (request failed)")
                        continue
                    tracks.append(query[0])
                    break
            took_time = time.time() - start
            
            self.logger.info(f"Loaded {len(res['tracks'])} tracks in ~{took_time:.2f}s")
            player.queue.add(*tracks)
            self.logger.info(f"Playling playlist {name_or_id} at {player.guild.id} (queue replaced)")
            await player.play_first_track()
            return
        else:
            tracks = []
            start = time.time()
            for song in res['tracks']:
                # to prevent errors we infinite request over the track if it fails, 
                # otherwise we break out of the loop
                while True:
                    query = await self.bot.node.get_tracks(cls=wavelink.Track, query=song)
                    if not query:
                        self.logger.debug(f"Failed to fetch song \"{song}\" (request failed)")
                        continue
                    tracks.append(query[0])
                    break
            took_time = time.time() - start
            
            self.logger.info(f"Loaded {len(res['tracks'])} tracks in ~{took_time:.2f}s")
            
            self.logger.info(f"Playling playlist {name_or_id} at {player.guild.id} (songs added)")
            await player.add_tracks(interaction, tracks)
            return

    @app_commands.command(name="rename", description="Rename playlist to given name")
    @app_commands.describe(name_or_id="Name or ID of playlist you want to rename")
    @app_commands.describe(new_name="New name of the playlist you want to rename")
    async def rename_playlist_command(self, interaction: discord.Interaction, name_or_id: str, new_name: str):
        await interaction.response.defer(ephemeral=False, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))

        try:
            res = handler.rename_playlist(name_or_id, new_name)
            embed = discord.Embed(description=f"<:tick:1028004866662084659> Playlist renamed from `{name_or_id}` to `{new_name}`",color=BASE_COLOR)
            await interaction.followup.send(embed=embed)
            return
        except Exception as e:
            self.logger.error(f"Renaming playlist error -- {e.__class__.__name__}: {str(e)}")
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Unhandled exception occured while trying to rename playlist. Make sure that the name/id is correct.",color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

    @playlist_view_command.error
    @view_playlist_of_user_command.error
    @rename_playlist_command.error
    @playlist_remove_song_command.error
    @playlist_remove_command.error
    @playlist_play.error
    @playlist_add_song_command.error
    @playlist_create_command.error
    async def on_cog_error(self, interaction, error):
        self.logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}")
        embed = discord.Embed(description=
            f"<:x_mark:1028004871313563758> An error occured. Please contact developers for more info. Details are shown below.\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    help_utils.register_command("playlists view", "View your or user's playlists", "Music: Playlist management", [("user", "View this user's playlists", False)])
    help_utils.register_command("playlists create", "Create a new playlist", "Music: Playlist management", [("name", "Name of the playlist", True),("copy_queue","Wherever to copy the queue to playlist or not",False)])
    help_utils.register_command("playlists add-song", 
        "Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist", "Music: Playlist management", 
        [("name_or_id", "Name of the playlist you want to add the song to", True),("song", "Name of the song you want to add",True)])
    help_utils.register_command("playlists remove-song", "Remove a song from your playlist", "Music: Playlist management", 
        [("name_or_id", "Name of the playlist you want to remove the song from", True),("index", "Index of the song you want to remove (1-playlist len)", True)])
    help_utils.register_command("playlists play", "Play your playlist!", "Music: Playlist management", 
        [("name_or_id", "Name of the playlist you want to play", True), ("replace_queue", "Wherever to replace the queue with the playlist or just append", False)])
    help_utils.register_command("playlists remove-playlist", "Remove a playlist", "Music: Playlist management", [("name_or_id", "Name of the playlist you want to remove", True)])
    help_utils.register_command("playlists view-playlist", "View playlist's content (for your playlist or anybody else)", "Music: Playlist management", [("name_or_id", "Name of the playlist", True),("user","(optional) User to get the playlist from",False)])
    help_utils.register_command("playlists rename", "Rename playlist to given name", "Music: Playlist management", 
        [("name_or_id", "Name or ID of playlist you want to rename", True), ("new_name","New name of the playlist you want to rename",True)])
    await bot.add_cog(PlaylistGroupCog(bot), guilds=bot.guilds)