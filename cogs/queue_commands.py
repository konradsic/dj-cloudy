import datetime
import math
import random

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.colors import BASE_COLOR
from utils.run import running_nodes
from utils.buttons import PlayButtonsMenu, EmbedPaginator
from utils.base_utils import convert_to_double, get_length
from utils import logger

@logger.LoggerApplication
class QueueCommands(commands.GroupCog, name="queue"):
    def __init__(self, bot: commands.Bot, logger) -> None:
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view", description="View the queue in a nice embed")
    async def queue_view_subcommand(self, interaction: discord.Interaction):
        player = self.bot.node.get_player(interaction.guild.id)
        if player is None:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if player.queue.tracks == []:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> There are not tracks in the queue",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if len(player.queue) <= 6:
            history = player.queue.track_history
            upcoming = player.queue.upcoming_tracks
            current = player.queue.current_track
            length = get_length(
                sum([t.duration for t in player.queue.get_tracks()]))

            embed = discord.Embed(title=f"<:playlist_button:1028926036181794857> Queue (currently {len(player.queue)} {'tracks' if len(player.queue) > 1 else 'track'})", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
            embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            if history:
                history_field = [f"`{i}. ` [{t.title}]({t.uri}) [{get_length(t.duration)}]" for i,t in enumerate(history, 1)]
                history_field = "".join(e + "\n" for e in history_field)
                embed.add_field(name="Before tracks", value=history_field, inline=False)
            if current:
                embed.add_field(name="Now playing", value=f"`{len(history)+1}. ` [**{current.title}**]({current.uri}) [{get_length(current.duration)}]")
            if upcoming:
                upcoming_field = [f"`{i}. ` [{t.title}]({t.uri}) [{get_length(t.duration)}]" for i,t in enumerate(upcoming, len(history)+2)]
                upcoming_field = "".join(e + "\n" for e in upcoming_field)
                embed.add_field(name="Upcoming tracks", value=upcoming_field, inline=False)
            embed.add_field(name="Additional informations", value=f"Total queue length: `{length}`\nRepeat mode: `{player.queue.repeat.string_mode}`", inline=False)
            await interaction.response.send_message(embed=embed, view=PlayButtonsMenu(user=interaction.user))
            return
        
        history = player.queue.track_history
        upcoming = player.queue.upcoming_tracks
        current = player.queue.current_track
        length = sum([t.duration for t in player.queue.get_tracks()])
        length = get_length(length)
        fields = [
            f"**{i}.** [{t.title}]({t.uri}) `[{get_length(t.duration)}]`{' **now playing**' if t == current else ''}\n"
            for i,t in enumerate(history + [current] + upcoming, start=1)
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
            embeds.append(discord.Embed(
                title=f"<:playlist_button:1028926036181794857> Queue (currently {len(player.queue)} {'tracks' if len(player.queue) > 1 else 'track'})", 
                timestamp=datetime.datetime.utcnow(), 
                color=BASE_COLOR
            ))
            embeds[-1].set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
            embeds[-1].set_thumbnail(url=self.bot.user.display_avatar.url)
            embeds[-1].add_field(name=f"Tracks (page {i}/{len(res_fields)})", value="".join(t for t in field), inline=False)
            embeds[-1].add_field(name="Additional informations", value=f"Total queue length: `{length}`\nRepeat mode: `{player.queue.repeat.string_mode}`", inline=False)
        await interaction.response.send_message(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user))

    @app_commands.command(name="shuffle", description="Shuffle the queue")
    async def queue_shuffle_subcommand(self, interaction: discord.Interaction):
        player = self.bot.node.get_player(interaction.guild.id)
        if player is None:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if player.queue.tracks == []:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> There are not tracks in the queue",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        player.queue.shuffle()
        embed = discord.Embed(description=f"<:shuffle_button:1028926038153117727> Queue has been successfully shuffled",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="cleanup", description="Clean the queue and stop the player")
    async def queue_cleanup_command(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        elif not player.queue.tracks:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        player.queue.cleanup() # defined in music/queue.py
        await player.stop() # stop the player
        embed = discord.Embed(description=f"<:playlist_button:1028926036181794857> Queue cleaned up successfully", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove", description="Remove track with the given index from the queue")
    @app_commands.describe(index="Index of the song you want to remove")
    async def queue_remove_command(self, interaction: discord.Interaction, index: int):
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif not (1 <= index <= len(player.queue)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Index of the track is out of range",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if (index-1) == player.queue.position:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> For now you cannot remove current playing track",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        del player.queue._queue[index-1]
        if (index-1) < player.queue.position:
            player.queue.position -= 1
        
        embed = discord.Embed(description=f"<:playlist_button:1028926036181794857> Successfully removed track at position `{index}`",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        return
    
    @queue_view_subcommand.error
    @queue_shuffle_subcommand.error
    @queue_cleanup_command.error
    @queue_remove_command.error
    async def on_cog_error(self, interaction, error):
        self.logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}")
        embed = discord.Embed(description=
            f"<:x_mark:1028004871313563758> An error occured. Please contact developers for more info. Details are shown below.\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
class OtherQueueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skipto", description="Move the player to the specified position in the queue")
    @app_commands.describe(position="Position in the queue between 1 and queue length")
    async def queue_skipto_command(self, interaction: discord.Interaction, position: int):
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not (1 <= position <= len(player.queue)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Position index is out of range",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        player.queue.position = position - 2 # same as in previous command
        await player.stop() # stopping the player explained in skip command
        embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Skipping to track at position `{position}`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    
    @app_commands.command(name="skip", description="Skip to the next track if one exists")
    async def queue_skip_command(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif not player.queue.upcoming_tracks:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The `skip` command could not be executed because there is nothing to skip to",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # we are using stop function because then the advance function will be called (from the event) and next track will be played
        await player.stop()
        embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Successfully skipped to the next track", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="previous", description="Play the previous track if one exists")
    async def queue_previous(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif not player.queue.track_history:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The `previous` command could not be executed because there is nothing to play that is before this track",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # setting player index to current-2 because
        #   1) we go 1 track back
        #   2) we go one more because when stop() 
        #      is invoked we go to the next track so it would play the current track one more time

        player.queue.position -= 2 # explained up there
        await player.stop()
        embed = discord.Embed(description=f"<:previous_button:1029418191274905630> Playing previous track", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        
    @queue_skip_command.error
    @queue_skipto_command.error
    @queue_previous.error
    async def on_cog_error(self, interaction, error):
        self.logger.error(f"[/{interaction.command.name} failed] {error.__class__.__name__}: {str(error)}")
        embed = discord.Embed(description=
            f"<:x_mark:1028004871313563758> An error occured. Please contact developers for more info. Details are shown below.\n```py\ncoro: {interaction.command.callback.__name__} {interaction.command.callback}\ncommand: /{interaction.command.name}\n{error.__class__.__name__}:\n{str(error)}\n```",color=BASE_COLOR)
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("queue view", "View the queue in  a nice embed", "Music: Queue navigation")
    help_utils.register_command("queue cleanup", "Clean the queue and stop the player", "Music: Queue navigation")
    help_utils.register_command("queue shuffle", "Shuffle the queue", "Music: Queue navigation")
    help_utils.register_command("queue remove", "Remove track with the given index from the queue", "Music: Queue navigation", [("index","Index of the song you want to remove",True)])
    help_utils.register_command("previous", "Play the previous track if one exists", "Music: Queue navigation")
    help_utils.register_command("skip", "Skip to the next track if one exists", "Music: Queue navigation")
    help_utils.register_command("skipto", "Move the player to the specified position in the queue", "Music: Queue navigation", arguments=[("position", "Position in the queue between 1 and queue length", True)])

    await bot.add_cog(QueueCommands(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
    await bot.add_cog(OtherQueueCommands(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
