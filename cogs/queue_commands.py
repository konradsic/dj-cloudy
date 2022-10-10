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
        


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("queue view", "View the queue in  a nice embed", "Music: Queue navigation")
    help_utils.register_command("queue shuffle", "Shuffle the queue", "Music: Queue navigation")
    await bot.add_cog(QueueCommands(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
