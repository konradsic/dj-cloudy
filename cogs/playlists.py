import datetime
import re
import time
import typing as t
import math
import json

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils

from lib.music import playlist
from lib.music.core import MusicPlayer
from lib.logger import logger
from lib.utils.base_utils import get_length, limit_string_to, djRole_check, quiz_check
from lib.ui.buttons import EmbedPaginator
from lib.ui.colors import BASE_COLOR
from lib.utils.errors import (NoPlayerFound, PlaylistCreationError,
                          PlaylistGetError, PlaylistRemoveError,
                          CacheExpired, CacheNotFound)
from lib.utils.regexes import URL_REGEX
from lib.ui import emoji
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
import difflib

logger_instance = logger.Logger().get("cogs.playlists")

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

SEARCH_METHODS = [
    "spsearch",
    "ytsearch",
    "scsearch",
    "ytmsearch"
]

# autocomplete for song url
async def song_url_autocomplete(interaction: discord.Interaction, current: str) -> t.List[app_commands.Choice]:
    query = current.strip("<>")
    if current == "":
        query = "ytsearch:Best music"
    elif any(current.startswith(x) for x in SEARCH_METHODS): pass
    elif not re.match(URL_REGEX, current):
        query = f"ytsearch:{current}"
    try:
        if query.startswith("🥇") or query.startswith("🥈") or query.startswith("🥉"):
            query = query[2:]
        for i in range(20):
            tracks = await wavelink.Pool.fetch_tracks(query)
            if not tracks: continue
            break
        if not tracks:
            return []
        return [
            app_commands.Choice(
                name=limit_string_to(
                    f"{number_complete[i]}{track.title} (by {track.author[:-len(' - Topic')] if track.author.endswith(' - Topic') else track.author}) [{get_length(track.length)}]",
                    100), value=track.uri)
            for i,track in enumerate(tracks[:10])
        ]
    except Exception as e:
        logger_instance.error(f"Error: {e.__class__.__name__} - {str(e)}")
        return []

async def playlists_autocomplete(interaction: discord.Interaction, current: str) -> t.List[app_commands.Choice]:
    try:
        user = interaction.namespace.user or interaction.user
    except:
        user = interaction.user
    
    user_playlists = playlist.PlaylistHandler(str(user.id)).playlists
    if (user.id != interaction.user.id):
        # exclude private playlists
        new_playlists = []
        for playlist_ in user_playlists:
            if not playlist_["private"]: new_playlists.append(playlist_)
        user_playlists = new_playlists
    # print(user_playlists)
    if current == "":
        return [
            app_commands.Choice(name=f"{i}. {p['name']} (id:{p['id']}, {len(p['tracks'])} tracks)", value=p["id"])
            for i,p in enumerate(user_playlists[:10], start=1)
        ]
    
    result_names = sorted([(p, difflib.SequenceMatcher(None, p["name"], current).quick_ratio()) for p in user_playlists], key=lambda x: x[1])
    result_ids = sorted([(p, difflib.SequenceMatcher(None, p["id"], current).quick_ratio()) for p in user_playlists], key=lambda x: x[1])
    all_results = sorted(result_names + result_ids, key=lambda x: x[1], reverse=True)

    # eliminate results with less than 70% accuracy
    for i in range(len(all_results)):
        # print(all_results[i][1])
        if all_results[i][1] < 0.7:
            all_results = all_results[:i]
            break
    # print(3)
    all_results = list([x[0] for x in all_results])
    new_results = []
    for x in all_results:
        if x not in new_results: new_results.append(x)
    all_results = new_results # duplicates removed
    # print(4, list(all_results))
    return [
        app_commands.Choice(name=f"{i}. {p['name']} (id:{p['id']}, {len(p['tracks'])} tracks)", value=p["id"])
        for i,p in enumerate(all_results[:10], start=1)
    ]
    
async def playlist_index_autocomplete(interaction: discord.Interaction, current: str) -> t.List[app_commands.Choice]:
    user_playlists = playlist.PlaylistHandler(str(interaction.user.id)).playlists
    name = interaction.namespace.name_or_id
    found = None
    
    for idx, p in enumerate(user_playlists):
        if p["id"] == name or p["id"] == name:
            found = user_playlists[idx]
    if not found: return []
    if not 1 <= int(current) <= len(found['tracks']):
        return []
    
    track = await wavelink.Pool.fetch_tracks(found["tracks"][int(current)-1])
    track = track[0]
    return [app_commands.Choice(name=f"{current}. {track.title} by {track.author} [{get_length(track.length)}]", value=int(current))]
    
@logger.LoggerApplication
class PlaylistGroupCog(commands.GroupCog, name="playlists"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view-playlist", description="View playlist's content (you can also search for others playlists)")
    @app_commands.describe(name_or_id="Name or ID of the playlist")
    @app_commands.describe(user="User to get the playlist from")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete)
    @help_utils.add("playlists view-playlist", "View playlist's content (you can also search for others playlists)", "Playlists", {"name_or_id": {"description": "Name or ID of the playlist", "required": True}, "user": {"required": False, "description": "User to get the playlist from"}})
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
        
        starred = False
        
        if name_or_id.lower() == "starred":
            found = {"tracks":handler.data["starred-playlist"]}
            starred = True
            
        if (user.id != interaction.user.id) and (found.get("private", False) or (name_or_id == 'starred' and handler.data['starred_private'])):
            found = None
        
        if not found:
            embed = ShortEmbed(description=f"{emoji.XMARK} No playlist was found.{' The playlist you`re looking for **could be** privated by the user' if user.id != interaction.user.id else ''}")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        tracks = []
        start = time.time()
        for song in found['tracks']:
            # to prevent errors we infinite request over the track if it fails, 
            # otherwise we break out of the loop
            
            # try cache
            try:
                t = await self.bot.song_cache_mgr.get(song)
                tracks.append(t)
            except Exception as e:
                d = None
                for i in range(20):
                    d = await wavelink.Pool.fetch_tracks(song)
                    if not d:
                        self.logger.error(f"Failed to fetch song \"{song}\" (request failed)")
                        continue
                    d = d[0]
                    break
                if isinstance(e, CacheNotFound) or isinstance(e, CacheExpired):
                    await self.bot.song_cache_mgr.save(d.uri, {
                        "uri": d.uri,
                        "title": d.title,
                        "author": d.author,
                        "length": d.length,
                        "id": d.identifier
                    })
                tracks.append(await self.bot.song_cache_mgr.get(song))
                
        took_time = time.time() - start
        self.logger.info(f"Loaded {len(found['tracks'])} tracks in ~{took_time:.2f}s")
        fields = [
            f"**{i+1}.** [{tracks[i]['title']}]({tracks[i]['uri']}) `[{get_length(tracks[i]['length'])}]`\n"
            for i in range(len(tracks))
        ]
        if not fields:
            embed = NormalEmbed(description=f"ID: `{found.get('id', 'STARRED')}`\nNo tracks in the playlist\nPrivate: `{'Yes' if found.get('private') or (name_or_id == 'starred' and handler.data['starred_private'])else 'No'}`", timestamp=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_author(name=f"{user.name}'s playlist: {'STARRED' if starred else found['name']}", icon_url=user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        num_fields = math.ceil(len(fields)/6)
        if num_fields == 0:
            num_fields += 1
        per_page = 6
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
            embed = NormalEmbed(description="Those are the tracks in user's playlist", timestamp=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_author(name=f"{user.name}'s playlist: {found['name'] + '#' + found['id'] if found.get('name', '') else 'STARRED'}", icon_url=user.display_avatar.url)
            embed.add_field(name=f"Tracks (page {i}/{len(res_fields)})", value="".join(t for t in field), inline=False)
            embed.add_field(name="Additional information", value=f"Playlist length: `{get_length(sum([track['length'] for track in tracks]))}`\nTotal songs: `{len(tracks)}`\nPrivate: `{'Yes' if found.get('private') or (handler.data['starred_private'] and name_or_id.lower() == 'starred') else 'No'}`")
            embeds.append(embed)
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user), ephemeral=True)
        return True

    @app_commands.command(name="view", description="View your or user's playlists")
    @app_commands.describe(user="View this user's playlists")
    @help_utils.add("playlists view", "View your or user's playlists", "Playlists", {"user": {"description": "View this user's playlists", "required": False}})
    async def playlist_view_command(self, interaction: discord.Interaction, user: discord.Member=None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        # get the user
        if user is None:
            user = interaction.user
        if user.bot:
            embed = ShortEmbed(description=f"{emoji.XMARK} Bots cannot have playlists! Make sure to select a user next time")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        user_data = playlist.PlaylistHandler(key=str(user.id))
        playlists = user_data.playlists
        playlist_res = "No playlists for this user. Create a playlist with `/playlist create <name>`!"
        # filter out private playlists
        if (user.id != interaction.user.id):
            # exclude private playlists
            new_playlists = []
            for playlist_ in playlists:
                if not playlist_["private"]: new_playlists.append(playlist_)
            playlists = new_playlists
        
        total_tracks = 0
        start = time.time()
        if playlists:
            playlist_res = ""
            for i, p in enumerate(playlists,1):
                total_length = 0
                for track in p['tracks']:
                    # try cache
                    try:
                        t = await self.bot.song_cache_mgr.get(track)
                        total_length += t["length"]
                        total_tracks += 1
                    except Exception as e:
                        d = None
                        for i in range(20):
                            d = await wavelink.Pool.fetch_tracks(track)
                            if not d:
                                self.logger.error(f"Failed to fetch song \"{track}\" (request failed)")
                                continue
                            total_length += d[0].length
                            total_tracks += 1
                            d = d[0]
                            break
                        if isinstance(e, CacheNotFound) or isinstance(e, CacheExpired):
                            await self.bot.song_cache_mgr.save(d.uri, {
                                "uri": d.uri,
                                "title": d.title,
                                "author": d.author,
                                "length": d.length,
                                "id": d.identifier
                            })
                    
                playlist_res += f"**{i}.** {p['name']} `#{p['id']}` `[{get_length(total_length)}]` *{len(p['tracks'])} song(s)*\n"
                
        took_time = time.time() - start
        self.logger.info(f"Loaded {total_tracks} tracks in ~{took_time:.2f}s")
        
        total_tracks = 0
        starred_dur = 0
        start = time.time()
        
        for track in user_data.data['starred-playlist']:
            # try cache
            try:
                t = await self.bot.song_cache_mgr.get(track)
                starred_dur += t["length"]
            except Exception as e:
                d = None
                for i in range(20):
                    d = await wavelink.Pool.fetch_tracks(track)
                    if not d:
                        self.logger.error(f"Failed to fetch song \"{track}\" (request failed)")
                        continue
                    starred_dur += d[0].length
                    d = d[0]
                    break
                if isinstance(e, CacheNotFound) or isinstance(e, CacheExpired):
                    await self.bot.song_cache_mgr.save(d.uri, {
                        "uri": d.uri,
                        "title": d.title,
                        "author": d.author,
                        "length": d.length,
                        "id": d.identifier
                    })

        took_time = time.time() - start
        self.logger.info(f"Loaded starred playlist ({total_tracks} songs) in ~{took_time:.2f}s")
        
        starred_playlist_data = f"{len(user_data.data['starred-playlist'])} total songs, total length `{get_length(starred_dur)}`\n"
        if interaction.user.id != user.id and user_data.data['starred_private']: starred_playlist_data = "Author of this playlist has privated it"
        embed = NormalEmbed(description="These are the user's playlists", timestamp=True)
        embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
        embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="toggle-private", description="Toggle visibility of your playlist. Use 'starred' toggle visibility for your starred playlist")
    @app_commands.describe(name_or_id="Name or ID of the playlist", private="Whether the playlist should become private or not")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete)
    @help_utils.add("playlists toggle-private", "Toggle visibility of your playlist. Use 'starred' toggle visibility for your starred playlist", "Playlists", {"name_or_id": {"description": "Name or ID of the playlist",  "required": True}, "private": {"description": "Whether the playlist should become private or not", "required": True}})
    async def playlist_toggle_private_command(self, interaction: discord.Interaction, name_or_id: str, private: bool):
        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            handler = playlist.PlaylistHandler(key=str(interaction.user.id))
            handler.toggle_private_playlist(name_or_id, private)
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.LOCKED if private else emoji.UNLOCKED} Playlist security updated for **{name_or_id}**. Now this playlist is `{'private' if private else 'no longer private'}`"))
        except:
            await interaction.followup.send(embed=ShortEmbed(f"{emoji.XMARK} There was an error. Please check the spelling and try again. If the error persists, submit a bug report via the `/bug-report` command"))

    @app_commands.command(name="create", description="Create a new playlist")
    @app_commands.describe(name="Name of the playlist")
    @app_commands.describe(copy_queue="Whether to copy the queue to playlist or not", private="Whether the playlist should be private or not. Defaults to `False`")
    @help_utils.add("playlists create", "Create a new playlist", "Playlists", {"name": {"description": "Name of the playlist", "required": True}, "private": {"description": "Whether the playlist should be private or not. Defaults to `False`", "required": False}, "copy_queue": {"description": "Whether to copy the queue to playlist or not", "required": False}})
    async def playlist_create_command(self, interaction: discord.Interaction, name: str,  private: bool=False, copy_queue: bool=False):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if len(name) > 30:
            embed = ShortEmbed(description=f"{emoji.XMARK} Playlist name should be less than 30 characters!")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        limits = 25 # max playlists for user
        if handler.data['credentials'] == 1:
            limits = 100 # max playlists for moderators
        elif handler.data['credentials'] == 2:
            limits = 10**15 # "infinity", max playlists for admins
        if len(handler.playlists) >= limits:
            embed = ShortEmbed(description=f"{emoji.XMARK} A maximum of {limits} playlists can be created on your account.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if name.lower() == "starred":
            embed = ShortEmbed(description=f"{emoji.XMARK} 'starred' is a special playlist name that stands for your {emoji.STAR} songs. You can't use it for playlist creation")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            tracks = []
            if copy_queue:
                try:
                    if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)) is None:
                        raise NoPlayerFound("There is no player connected in this guild")
                except NoPlayerFound:
                    embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel, so there is no queue, so there are no songs to copy")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                if player.queue.is_empty:
                    embed = ShortEmbed(description=f"{emoji.XMARK} There are no tracks in the queue so there is nothing to copy")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                tracks = [song.uri for song in player.queue.get_tracks()]
            handler.create_playlist(name, private, tracks)
        except PlaylistCreationError:
            embed = ShortEmbed(description=f"{emoji.XMARK} Failed to create playlist, please try again")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        embed = ShortEmbed(description=f"{emoji.TICK1} Successfully created playlist **{name}**")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="add-song", description="Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to add the song to")
    @app_commands.describe(song="Song you want to add")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete, song=song_url_autocomplete)
    @help_utils.add("playlists add-song", "Add a song to your playlist. Use 'starred' when you want to add it to your starred songs playlist", "Playlists", 
                    {"name_or_id": {"description": "Name of the playlist you want to add the song to", "required": True}, "song": {"description": "Song you want to add", "required": True}})
    async def playlist_add_song_command(self, interaction: discord.Interaction, name_or_id: str, song: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        # find the playlist
        found = None
        for p in handler.playlists:
            if p['name'].lower() == name_or_id.lower() or p['id'].lower() == name_or_id.lower():
                found = p
                playlist_id = p["id"]
                playlist_name = p["name"]
                break
        if name_or_id.lower() == "starred":
            # gather starred playlist tracks
            found = {"tracks": handler.data["starred-playlist"]}
            playlist_id = None
            playlist_name = "STARRED"
        if not found:
            embed = ShortEmbed(description=f"{emoji.XMARK} Failed to get playlist with name/id `{name_or_id}`. Make sure that the name is a name of __your__ playlist")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        limits = 75 # Maximum songs in a playlist
        if handler.data['credentials'] == 1:
            limits = 500
        elif handler.data['credentials'] == 2:
            limits = 10**15 # "infinity"

        if len(found["tracks"]) >= limits:
            embed = ShortEmbed(description=f"{emoji.XMARK} Song addition exceeds your playlist's song limit (`{limits} tracks`)")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        # Fixes issue #37: no song validation
        # Fixes issue #31: no loop for search
        for _ in range(20):
            if any(song.startswith(x + ":") for x in SEARCH_METHODS) or re.match(URL_REGEX, song):
                track = await wavelink.Pool.fetch_tracks(song)
            else: 
                track = await wavelink.Pool.fetch_tracks("ytsearch:" + song)
            if not track: continue
            track = track[0]
            break
        if not track:
            embed = ShortEmbed(
                description=f"{emoji.XMARK.mention} No songs found with query `{song}`")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            handler.add_to_playlist(name_or_id.lower(), track.uri)
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} An error occured while trying to add the song. Please try again")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        await self.bot.song_cache_mgr.save(track.uri, {
            "uri": track.uri,
            "title": track.title,
            "author": track.author,
            "length": track.length,
            "id": track.identifier
        })
        
        embed = ShortEmbed(description=f"{emoji.TICK1} Successfully added [**{track.title}**]({track.uri}) to the playlist **{playlist_name}{'#' + playlist_id if playlist_id else ''}**")
        await interaction.followup.send(embed=embed)
        return


    @app_commands.command(name="remove-song", description="Remove a song from your playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove the song from")
    @app_commands.describe(index="Index of the song you want to remove (1-playlist length)")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete, index=playlist_index_autocomplete)
    @help_utils.add("playlists remove-song", "Remove a song from your playlist", "Playlists", 
                    {"name-or_id": {"description": "Name of the playlist youw ant to remove the song from", "required": True}, "index": {"description": "Index of the song you want to remove (1-playlist length)", "required": True}})
    async def playlist_remove_song_command(self, interaction: discord.Interaction, name_or_id: str, index: int):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        if index <= 0:
            embed = ShortEmbed(description=f"{emoji.XMARK} Index should be between 1 and playlist length")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            handler.remove(name_or_id, index-1)
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} An error occured while trying to remove the song. Check if index is correct and the name or ID of the playlist")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = ShortEmbed(description=f"{emoji.TICK1} Successfully removed song at position `{index}` from playlist __{name_or_id}__")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="remove-playlist", description="Remove a playlist")
    @app_commands.describe(name_or_id="Name of the playlist you want to remove")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete)
    @help_utils.add("playlists remove", "Remove a playlist", "Playlists", {"name_or_id": {"description": "Name of the playlist you want to remove", "required": True}})
    async def playlist_remove_command(self, interaction: discord.Interaction, name_or_id: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        try:
            handler.remove_playlist(name_or_id)
        except:
            embed = ShortEmbed(description=f"{emoji.XMARK} An error occured while trying to remove the playlist. Check spelling and name then try again")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = ShortEmbed(description=f"{emoji.TICK1} Successfully removed playlist **{name_or_id}**")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="play", description="Play your playlist!")
    @app_commands.describe(name_or_id="Name or ID of the playlist you want to play")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete)
    @app_commands.describe(replace_queue="Whether to replace queue with the playlist or just to extend")
    @help_utils.add("playlists play", "Play your playlist!", "Playlists", {"name_or_id": {"description": "Name or ID of the playlist you want to play", "required": True}, "replace_queue": {"description": "Whether to replace queue with the playlist or just to extend", "required": False}})
    async def playlist_play(self, interaction: discord.Interaction, name_or_id: str, replace_queue: bool=False):
        await interaction.response.defer(ephemeral=False, thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        try:
            if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
                raise NoPlayerFound("There is no player connected in this guild")

            voice = interaction.user.voice
            if not voice:
                embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        except Exception as e:
            # print(e, e.__class__.__name__)
            if interaction.user.voice is None:
                embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
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
            embed = ShortEmbed(description=f"{emoji.XMARK} No playlist with name \"{name_or_id}\" was found. Perhaps you misspelled it?")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        # adapt the playlist
        start = round(time.time())
        embed = NormalEmbed(timestamp=True, description=f"Started: <t:{start}:R>\n> {emoji.LOADING} `Status: loaded 0/{len(res['tracks'])} songs...`", title=f"{emoji.SEARCH} Fetching tracks...")
        msg: discord.WebhookMessage = await interaction.followup.send(embed=embed)
        if replace_queue:
            if not await djRole_check(interaction, self.logger): return
            # we need to replace the queue
            player.queue.cleanup()
            
            tracks = []
            for idx,song in enumerate(res['tracks']):
                # to prevent errors we infinite request over the track if it fails, 
                # otherwise we break out of the loop
                for i in range(20):
                    query = await wavelink.Pool.fetch_tracks(song)
                    if not query:
                        self.logger.debug(f"Failed to fetch song \"{song}\" (request failed)")
                        continue
                    tracks.append(query[0])
                    if (idx+1)%10 == 0:
                        embed = NormalEmbed(timestamp=True, description=f"Started: <t:{start}:R>\n> {emoji.LOADING} `Status: loaded {idx+1}/{len(res['tracks'])} songs...`", title=f"{emoji.SEARCH} Fetching tracks...")
                        await msg.edit(embed=embed)
                    break
            took_time = time.time() - start
            
            self.logger.info(f"Loaded {len(res['tracks'])} tracks in ~{took_time:.2f}s")
            player.queue.add(*zip(tracks, [interaction.user, ] * len(tracks)))
            self.logger.info(f"Playling playlist {name_or_id} at {player.guild.id} (queue replaced)")
            embed = NormalEmbed(timestamp=True, description=f"Completed\n> {emoji.LOADING} `Status: loaded {len(res['tracks'])}/{len(res['tracks'])} songs...`", title=f"{emoji.SEARCH} Fetching tracks...")
            await msg.edit(embed=embed)
            await player.play_first_track()
            return
        else:
            tracks = []
            start = round(time.time())
            for idx,song in enumerate(res['tracks']):
                # to prevent errors we infinite request over the track if it fails, 
                # otherwise we break out of the loop
                for i in range(20):
                    query = await wavelink.Pool.fetch_tracks(song)
                    if not query:
                        self.logger.debug(f"Failed to fetch song \"{song}\" (request failed)")
                        continue
                    if (idx+1)%10 == 0:
                        embed = NormalEmbed(timestamp=True, description=f"Started: <t:{start}:R>\n> {emoji.LOADING} `Status: loaded {idx+1}/{len(res['tracks'])} songs...`", title=f"{emoji.SEARCH} Fetching tracks...")
                        await msg.edit(embed=embed)
                    tracks.append(query[0])
                    break
            took_time = time.time() - start
            
            self.logger.info(f"Loaded {len(res['tracks'])} tracks in ~{took_time:.2f}s")
            embed = NormalEmbed(timestamp=True, description=f"Completed\n> {emoji.LOADING} `Status: loaded {len(res['tracks'])}/{len(res['tracks'])} songs...`", title=f"{emoji.SEARCH} Fetching tracks...")
            await msg.edit(embed=embed)
            self.logger.info(f"Playling playlist {name_or_id} at {player.guild.id} (songs added)")
            await player.add_tracks(interaction, tracks)
            return

    @app_commands.command(name="rename", description="Rename playlist to given name")
    @app_commands.describe(name_or_id="Name or ID of the playlist you want to rename")
    @app_commands.autocomplete(name_or_id=playlists_autocomplete)
    @app_commands.describe(new_name="New name of the playlist you want to rename")
    @help_utils.add("playlists rename", "Rename playlist to given name", "Playlists", 
                    {"name_or_id": {"description": "Name or ID of the playlist you want to rename", "required": True}, "new_name": {"description": "New name of the playlist you want to rename", "required": True}})
    async def rename_playlist_command(self, interaction: discord.Interaction, name_or_id: str, new_name: str):
        await interaction.response.defer(ephemeral=False, thinking=True)
        handler = playlist.PlaylistHandler(key=str(interaction.user.id))

        try:
            handler.rename_playlist(name_or_id, new_name)
            embed = ShortEmbed(description=f"{emoji.RENAME} Playlist renamed from `{name_or_id}` to `{new_name}`")
            await interaction.followup.send(embed=embed)
            return
        except Exception as e:
            self.logger.error(f"Renaming playlist error -- {e.__class__.__name__}: {str(e)}")
            embed = ShortEmbed(description=f"{emoji.XMARK} Unhandled exception occured while trying to rename playlist. Make sure that the name/id is correct.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(PlaylistGroupCog(bot))
    
    