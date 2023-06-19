import datetime

import discord
from discord import app_commands
from discord.ext import commands
from utils import help_utils
from utils.colors import BASE_COLOR
from utils import logger
from music import playlist
import wavelink
from utils.base_utils import get_length
import math
from utils.buttons import EmbedPaginator

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
        handler = playlist.PlaylistHandler(key=str(user.id))
        playlist_res = "This user does not have any custom playlists"
        if handler.playlists:
            playlist_res = ""
            for i, p in enumerate(handler.playlists,1):
                total_duration = 0
                for track in p['tracks']:
                    while True:
                        d = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=track)
                        if not d: continue
                        d = d[0]
                        total_duration += d.length
                        break
                playlist_res += f"**{i}.** {p['name']} `#{p['id']}` `[{get_length(total_duration)}]` *{len(p['tracks'])} song(s)*\n"
        starred_dur = 0
        for t in handler.data['starred-playlist']:
            while True:
                d = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=t)
                if not d: continue
                d = d[0]
                starred_dur += d.length
                break
        starred_playlist_data = f"{len(handler.data['starred-playlist'])} total songs, total duration `{get_length(starred_dur)}`\n"
        embed = discord.Embed(description="These are the user's playlists", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.add_field(name="Starred songs", value=starred_playlist_data, inline=False)
        embed.add_field(name="Custom playlists", value=playlist_res, inline=False)
        embed.set_footer(text="Made by Konradoo#6938")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=f"{user.name}'s playlists", icon_url=user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def view_starred_playlist_menu(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True, thinking=True)
        handler = playlist.PlaylistHandler(key=str(member.id))
        starred_playlist = handler.data['starred-playlist']
        track_data = "No tracks in their :star: songs playlist"
        tracks = []
        total_duration = 0
        if starred_playlist:
            track_data = ""
            for i, song in enumerate(starred_playlist,1):
                while True:
                    cls_song = await self.bot.node.get_tracks(cls=wavelink.GenericTrack, query=song)
                    if not cls_song: continue
                    cls_song = cls_song[0]
                    total_duration += cls_song.duration
                    tracks.append(cls_song)
                    break
                
        fields = [
            f"**{i+1}.** [{tracks[i].title}]({tracks[i].uri}) `[{get_length(tracks[i].length)}]`\n"
            for i in range(len(tracks))
        ]
        
        if track_data:
            # no tracks in the playlist
            embed = discord.Embed(description=track_data, timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
            embed.set_footer(text="Made by Konradoo#6938")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_author(name=f"{member.name}'s starred songs", icon_url=member.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # prepare pagination
        found = {"tracks": starred_playlist}
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
            embed = discord.Embed(description="Those are the tracks in user's playlist", color=BASE_COLOR, timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text="Made by Konradoo#6938")
            embed.set_author(name=f"{member.name}'s playlist: {found['name'] + '#' + found['id'] if found.get('name', '') else 'STARRED'}", icon_url=member.display_avatar.url)
            embed.add_field(name=f"Tracks (page {i}/{len(res_fields)})", value="".join(t for t in field), inline=False)
            embed.add_field(name="Additional informations", value=f"Playlist length: `{get_length(sum([track.length for track in tracks]))}`\nTotal songs: `{len(tracks)}`")
            embeds.append(embed)
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user), ephemeral=True)
        return True
            

    async def copy_user_playlist_menu(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if str(interaction.user.id) == str(member.id):
            await interaction.followup.send(ephemeral=True, embed=discord.Embed(description="<:x_mark:1028004871313563758> You can't copy your playlist", color=BASE_COLOR))
            return
        handler = playlist.PlaylistHandler(key=str(member.id))
        starred = handler.data['starred-playlist']
        author_handler = playlist.PlaylistHandler(key=str(member.id))
        author_starred = handler.data['starred-playlist']
        for song in starred:
            author_handler.add_to_starred(song)
        await interaction.followup.send(embed=discord.Embed(description=f"<:tick:1028004866662084659> Success, added {member.name}'s starred playlist to yours", color=BASE_COLOR),ephemeral=True)

async def setup(bot):
    await bot.add_cog(ContextMenusCog(bot), guilds=bot.guilds)