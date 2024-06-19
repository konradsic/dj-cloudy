import datetime

import discord
from discord import app_commands
from discord.ext import commands
from lib.ui.colors import BASE_COLOR
from lib.logger import logger
from lib.music import playlist
import wavelink
from lib.utils.base_utils import get_length
import math
from lib.ui.buttons import EmbedPaginator
from lib.utils.errors import CacheExpired, CacheNotFound
import time
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType

@logger.LoggerApplication
class ContextMenusCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger
        self.bot.tree.add_command(app_commands.ContextMenu(name="View Playlists", callback=self.view_playlist_menu), guilds=self.bot.guilds)
        self.bot.tree.add_command(app_commands.ContextMenu(name="View Starred Playlist", callback=self.view_starred_playlist_menu), guilds=self.bot.guilds)
        self.bot.tree.add_command(app_commands.ContextMenu(name="Copy Starred Playlist", callback=self.copy_user_playlist_menu), guilds=self.bot.guilds)
        
    async def view_playlist_menu(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(ephemeral=True, thinking=True)
        # get the user
        if user is None:
            user = interaction.user
        if user.bot:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> Bots cannot have playlists! Make sure to select a user next time",color=BASE_COLOR)
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
        embed = NormalEmbed(description="These are the user's playlists", timestamp=True, footer=FooterType.COMMANDS)
        embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
        embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def view_starred_playlist_menu(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(member.id))
        starred_playlist = handler.data['starred-playlist']
        track_data = "No tracks in their :star: songs playlist"
        tracks = []
        
        if starred_playlist:
            track_data = ""
            for i, song in enumerate(starred_playlist,1):
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
                    tracks.append(d)
        fields = [
            f"**{i+1}.** [{tracks[i]['title']}]({tracks[i]['uri']}) `[{get_length(tracks[i]['length'])}]`\n"
            for i in range(len(tracks))
        ]
        
        if track_data:
            # no tracks in the playlist
            embed = NormalEmbed(description=track_data, timestamp=True, footer=FooterType.COMMANDS)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_author(name=f"{member.name}'s starred songs", icon_url=member.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # prepare pagination
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
            embed = NormalEmbed(description="Those are the tracks in user's playlist", timestamp=True, footer=FooterType.MADE_BY)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_author(name=f"{member.name}'s starred playlist", icon_url=member.display_avatar.url)
            embed.add_field(name=f"Tracks (page {i}/{len(res_fields)})", value="".join(t for t in field), inline=False)
            embed.add_field(name="Additional informations", value=f"Playlist length: `{get_length(sum([track['length'] for track in tracks]))}`\nTotal songs: `{len(tracks)}`")
            embeds.append(embed)
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user), ephemeral=True)
        return True
            

    async def copy_user_playlist_menu(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if str(interaction.user.id) == str(member.id):
            await interaction.followup.send(ephemeral=True, embed=ShortEmbed(description="<:x_mark:1028004871313563758> You can't copy your playlist"))
            return
        handler = playlist.PlaylistHandler(key=str(member.id))
        starred = handler.data['starred-playlist']
        author_handler = playlist.PlaylistHandler(key=str(member.id))
        author_starred = handler.data['starred-playlist']
        for song in starred:
            author_handler.add_to_starred(song)
        await interaction.followup.send(embed=ShortEmbed(description=f"<:tick:1028004866662084659> Success, added {member.name}'s starred playlist to yours"),ephemeral=True)

async def setup(bot):
    await bot.add_cog(ContextMenusCog(bot))