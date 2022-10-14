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


def convert_to_double(val):
    if val < 10:
        return "0" + str(val)
    return val

def get_length(dur):
    lm, ls = divmod(dur,60)
    lh, lm = divmod(lm, 60)
    ls, lm, lh = math.floor(ls), math.floor(lm), math.floor(lh)
    if lh >= 1:
        lm = convert_to_double(lm)
    ls = convert_to_double(ls)
    return f"{str(lh) + ':' if lh != 0 else ''}{str(lm)}:{str(ls)}"

class QueueCommands(commands.GroupCog, name="queue"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="view", description="View the queue in  a nice embed")
    async def queue_view_subcommand(self, interaction: discord.Interaction):
        player = self.bot.node.get_player(interaction.guild)
        if player is None:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        if player.queue.tracks == []:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> There are not tracks in the queue",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        history = player.queue.track_history
        upcoming = player.queue.upcoming_tracks
        current = player.queue.current_track
        length = sum([t.duration for t in player.queue.get_tracks()])
        length = get_length(length)

        embed = discord.Embed(title=f"<:playlist_button:1028926036181794857> Queue (currently {len(player.queue)} {'tracks' if len(player.queue) > 1 else 'track'})", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
        embed.set_footer(text="Made by Konradoo#6938, licensed under the MIT License")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        if history:
            history_field = [f"`{i}. ` [{t.title}]({t.uri}) [{get_length(t.duration)}]" for i,t in enumerate(history, 1)]
            history_field = "".join(e + "\n" for e in history_field)
            embed.add_field(name="Before tracks", value=history_field, inline=False)
        embed.add_field(name="Now playing", value=f"`{len(history)+1}. ` [**{current.title}**]({current.uri}) [{get_length(current.duration)}]")
        if upcoming:
            upcoming_field = [f"`{i}. ` [{t.title}]({t.uri}) [{get_length(t.duration)}]" for i,t in enumerate(upcoming, len(history)+2)]
            upcoming_field = "".join(e + "\n" for e in upcoming_field)
            embed.add_field(name="Upcoming tracks", value=upcoming_field, inline=False)
        embed.add_field(name="Additional informations", value=f"Total queue length: `{length}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="Shuffle the queue")
    async def queue_shuffle_subcommand(self, interaction: discord.Interaction):
        player = self.bot.node.get_player(interaction.guild)
        if player is None:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        if player.queue.tracks == []:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> There are not tracks in the queue",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        player.queue.shuffle()
        embed = discord.Embed(description=f"<:shuffle_button:1028926038153117727> Queue has been successfully shuffled",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cleanup", description="Clean the queue and stop the player")
    async def queue_cleanup_command(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild)):
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
    
class OtherQueueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skipto", description="Move the player to the specified position in the queue")
    @app_commands.describe(position="Position in the queue between 1 and queue length")
    async def queue_moveto_command(self, interaction: discord.Interaction, position: int):
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        if not (1 <= position <= len(player.queue)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Position index is out of range",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        
        player.queue.position = position - 2 # same as in previous command
        await player.stop() # stopping the player explained in skip command
        embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Skipping to track at position `{position}`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)

    
    @app_commands.command(name="skip", description="Skip to the next track if one exists")
    async def queue_skip_command(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        elif not player.queue.upcoming_tracks:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The `skip` command could not be executed because there is nothing to skip to",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        # we are using stop function because then the advance function will be called (from the event) and next track will be played
        await player.stop()
        embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Successfully skipped to the next track", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="previous", description="Play the previous track if one exists")
    async def queue_previous(self, interaction: discord.Interaction):
        if not (player := self.bot.node.get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
        elif not player.queue.track_history:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The `previous` command could not be executed because there is nothing to play that is before this track",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        # setting player index to current-2 because
        #   1) we go 1 track back
        #   2) we go one more because when stop() 
        #      is invoked we go to the next track so it would play the current track one more time

        player.queue.position -= 2 # explained up there
        await player.stop()
        embed = discord.Embed(description=f"<:previous_button:1029418191274905630> Playing previous track", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("queue view", "View the queue in  a nice embed", "Music: Queue navigation")
    help_utils.register_command("queue cleanup", "Clean the queue and stop the player", "Music: Queue navigation")
    help_utils.register_command("queue shuffle", "Shuffle the queue", "Music: Queue navigation")
    help_utils.register_command("previous", "Play the previous track if one exists", "Music: Queue navigation")
    help_utils.register_command("skip", "Skip to the next track if one exists", "Music: Queue navigation")
    help_utils.register_command("skipto", "Move the player to the specified position in the queue", "Music: Queue navigation", arguments=[("position", "Position in the queue between 1 and queue length", True)])

    await bot.add_cog(QueueCommands(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
    await bot.add_cog(OtherQueueCommands(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
