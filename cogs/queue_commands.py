import datetime
import math
import random

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.music.core import MusicPlayer
from lib.logger import logger
from lib.ui.colors import BASE_COLOR
from lib.ui.buttons import PlayButtonsMenu, EmbedPaginator, SkipVotingMenu
from lib.utils.base_utils import get_length, djRole_check, quiz_check
from lib.logger import logger
from lib.ui import emoji
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
 

@logger.LoggerApplication
class QueueCommands(commands.GroupCog, name="queue"):
    def __init__(self, bot: commands.Bot, logger) -> None:
        self.bot = bot
        self.logger = logger
        super().__init__()

    @app_commands.command(name="view", description="View the queue in a nice embed")
    @help_utils.add("queue view", "View the queue in a nice embed", "Music")
    async def queue_view_subcommand(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if player.queue.tracks == []:
            embed = ShortEmbed(description=f"{emoji.XMARK} There are not tracks in the queue")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if len(player.queue) <= 6:
            history = player.queue.track_history
            upcoming = player.queue.upcoming_tracks
            current = player.queue.current_track
            length = get_length(
                sum([t.length for t in player.queue.get_tracks()]))

            embed = NormalEmbed(title=f"{emoji.PLAYLIST} Queue (currently {len(player.queue)} {'tracks' if len(player.queue) > 1 else 'track'})", timestamp=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            if history:
                history_field = [f"`{i}. ` [{t.title}]({t.uri}) [{get_length(t.length)}]" for i,t in enumerate(history, 1)]
                history_field = "".join(e + "\n" for e in history_field)
                embed.add_field(name="Before tracks", value=history_field, inline=False)
            if current:
                embed.add_field(name="Now playing", value=f"`{len(history)+1}. ` [**{current.title}**]({current.uri}) [{get_length(current.length)}]")
            if upcoming:
                upcoming_field = [f"`{i}. ` [{t.title}]({t.uri}) [{get_length(t.length)}]" for i,t in enumerate(upcoming, len(history)+2)]
                upcoming_field = "".join(e + "\n" for e in upcoming_field)
                embed.add_field(name="Upcoming tracks", value=upcoming_field, inline=False)
            embed.add_field(name="Additional information", value=f"Total queue length: `{length}`\nRepeat mode: `{player.queue.repeat.string_mode}`\nShuffle mode: `{bool(player.queue.shuffle_mode_state)}`\nPlayback paused: `{'Yes' if player.paused else 'No'}`", inline=False)
            await interaction.followup.send(embed=embed, view=PlayButtonsMenu(user=interaction.user))
            return
        
        history = player.queue.track_history
        upcoming = player.queue.upcoming_tracks
        current = player.queue.current_track
        length = sum([t.length for t in player.queue.get_tracks()])
        length = get_length(length)
        fields = [
            f"{'**Now playing:** ' if t == current else ''}**{i}.** [{t.title}]({t.uri}) `[{get_length(t.length)}]`\n"
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
            embeds.append(NormalEmbed(
                title=f"{emoji.PLAYLIST} Queue (currently {len(player.queue)} {'tracks' if len(player.queue) > 1 else 'track'})", 
                timestamp=True, 
            ))
            embeds[-1].set_thumbnail(url=self.bot.user.display_avatar.url)
            embeds[-1].add_field(name=f"Tracks (page {i}/{len(res_fields)})", value="".join(t for t in field), inline=False)
            embeds[-1].add_field(name="Additional information", value=f"Total queue length: `{length}`\nRepeat mode: `{player.queue.repeat.string_mode}`\nShuffle mode: `{bool(player.queue.shuffle_mode_state)}`\nPlayback paused: `{'Yes' if player.paused else 'No'}`", inline=False)
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user))

    @app_commands.command(name="shuffle", description="Shuffle the queue or manage the queue shuffle mode")
    @app_commands.describe(shuffle_mode_state="Turn on/off shuffle mode")
    @app_commands.choices(shuffle_mode_state=[
        app_commands.Choice(name="ON", value=1),
        app_commands.Choice(name="OFF", value=-1),
        app_commands.Choice(name="TOGGLE", value=0)
    ])
    @help_utils.add("queue shuffle", "Shuffle the queue or manage the queue shuffle mode", "Music", {"shuffle_mode_state": {"description": "Turn on/off shuffle mode", "required": False}})
    async def queue_shuffle_subcommand(self, interaction: discord.Interaction, shuffle_mode_state: int=-2):
        await interaction.response.defer(thinking=True)
        # djRole check
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if player.queue.tracks == []:
            embed = ShortEmbed(description=f"{emoji.XMARK} There are not tracks in the queue")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if shuffle_mode_state not in (-1, 0, 1):
            player.queue.shuffle()
            embed = ShortEmbed(description=f"{emoji.SHUFFLE} Queue has been successfully shuffled")
            await interaction.followup.send(embed=embed)
            return
        
        # shuffle mode
        if shuffle_mode_state in (0, 1):
            player.queue.shuffle_mode_state = shuffle_mode_state
        if shuffle_mode_state == -1:
            mode = player.queue.shuffle_mode_state
            new_state = 1 if mode == 0 else 0
            player.queue.shuffle_mode_state = new_state
            
        embed = ShortEmbed(
            description=f"{emoji.SHUFFLE.string} Shuffle mode set to `{bool(player.queue.shuffle_mode_state)}`",
            color=BASE_COLOR
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="cleanup", description="Clean the queue and stop the player")
    @help_utils.add("queue cleanup", "Clean the queue and stop the player", "Music")
    async def queue_cleanup_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        # djRole check
        if not await djRole_check(interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        elif not player.queue.tracks:
            embed = ShortEmbed(description=f"{emoji.XMARK} Nothing is currently playing")
            await interaction.followup.send(embed=embed)
            return

        player.queue.cleanup() # defined in music/queue.py
        await player.stop() # stop the player
        embed = ShortEmbed(description=f"{emoji.TICK1} Queue cleaned up successfully")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="remove", description="Remove track with the given index from the queue")
    @app_commands.describe(index="Index of the song you want to remove")
    @help_utils.add("queue remove", "Remove track with the given index from the queue", "Music", {"index": {"description": "Index of the song you want to remove", "required": True}})
    async def queue_remove_command(self, interaction: discord.Interaction, index: int):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        # djRole check
        if not await djRole_check(interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        
        if not (1 <= index <= len(player.queue)):
            embed = ShortEmbed(description=f"{emoji.XMARK} Index of the track is out of range")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if (index-1) == player.queue.position:
            embed = ShortEmbed(description=f"{emoji.XMARK} For now you cannot remove current playing track")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        del player.queue._queue[index-1]
        if (index-1) < player.queue.position:
            player.queue.position -= 1
        
        embed = ShortEmbed(description=f"{emoji.TICK1} Successfully removed track at position `{index}`")
        await interaction.followup.send(embed=embed)
        return

@logger.LoggerApplication
class OtherQueueCommands(commands.Cog):
    def __init__(self, bot, logger: logger.Logger):
        self.logger = logger
        self.bot = bot

    @app_commands.command(name="skipto", description="Move the player to the specified position in the queue")
    @app_commands.describe(position="Position in the queue between 1 and queue length")
    @help_utils.add("skipto", "Move the player to the specified position in the queue", "Music", {"position": {"description": "Position in the queue between 1 and queue length", "required": True}})
    async def queue_skipto_command(self, interaction: discord.Interaction, position: int):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if not (1 <= position <= len(player.queue)):
            embed = ShortEmbed(description=f"{emoji.XMARK} Position index is out of range")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if not player.queue.repeat.string_mode == "REPEAT_CURRENT_TRACK":
            player.queue.position = position - 2
        else:
            player.queue.position = position-1
        await player.stop() # stopping the player explained in skip command
        embed = ShortEmbed(description=f"{emoji.SKIP} Skipping to track at position `{position}`")
        await interaction.followup.send(embed=embed)

    
    @app_commands.command(name="skip", description="Skip to the next track if one exists")
    @app_commands.describe(force="If repeat mode is set to `REPEAT_CURRENT_TRACK` you can force skip to the next track (normally it would play the same song again)")
    @help_utils.add("skip", "Skip to the next track track if one exists", "Music", arguments={"force": {"description": "If repeat mode is set to `REPEAT_CURRENT_TRACK` you can force skip to the next track (normally it would play the same song again)", "required": False}})
    async def queue_skip_command(self, interaction: discord.Interaction, force: bool=False):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        elif not player.queue.upcoming_tracks and (player.queue.position == len(player.queue)-1 and not player.queue.repeat.string_mode == "REPEAT_QUEUE") and not player.queue.repeat.string_mode == "REPEAT_CURRENT_TRACK":
            embed = ShortEmbed(description=f"{emoji.XMARK} The `skip` command could not be executed because there is nothing to skip to")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # we are using stop function because then the advance function will be called (from the event) and next track will be played
        if force and player.queue.repeat.string_mode == "REPEAT_CURRENT_TRACK":
            if player.queue.position != len(player.queue)-1: 
                player.queue.position += 1
                await player.stop()
            else:
                embed = ShortEmbed(description=f"{emoji.XMARK} The `skip` command could not be executed because there is nothing to skip to")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        else:
            await player.stop()
        embed = ShortEmbed(description=f"{emoji.SKIP} Successfully skipped to the next track")
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="previous", description="Play the previous track if one exists")
    @app_commands.describe(force="If repeat mode is set to `REPEAT_CURRENT_TRACK` you can force skip to the next previous (normally it would play the same song again)")
    @help_utils.add("previous", "Play the previous track if one exists", "Music", arguments={"force": {"description": "If repeat mode is set to `REPEAT_CURRENT_TRACK` you can force skip to the previous track (normally it would play the same song again)", "required": False}})
    async def queue_previous(self, interaction: discord.Interaction, force: bool=False):
        await interaction.response.defer(thinking=True)
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        elif not player.queue.track_history and (player.queue.position == 0 and not player.queue.repeat.string_mode == "REPEAT_QUEUE") and not player.queue.repeat.string_mode == "REPEAT_CURRENT_TRACK":
            embed = ShortEmbed(description=f"{emoji.XMARK} The `previous` command could not be executed because there is nothing to play that is before this track")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ! setting player index to current-2 because
        #   1) we go 1 track back
        #   2) we go one more because when stop() is invoked we go to the next track so it would play the current track one more time

        if player.queue.repeat.string_mode == "REPEAT_QUEUE" and player.queue.position == 0:
            player.queue.position = len(player.queue)-2
        elif force and player.queue.repeat.string_mode == "REPEAT_CURRENT_TRACK":
            if player.queue.position == 0:
                embed = ShortEmbed(description=f"{emoji.XMARK} The `previous` command could not be executed because there is nothing to play that is before this track")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            player.queue.position -= 1
        elif not player.queue.repeat.string_mode == "REPEAT_CURRENT_TRACK":
            player.queue.position -= 2 # explained up there
        await player.stop()
        embed = ShortEmbed(description=f"{emoji.PREVIOUS} Playing previous track")
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="voteskip", description="If you don't have DJ permissions, this will make a voting for skip")
    @help_utils.add("voteskip", "If you don't have DJ permissions, this will make a voting for skip", "Music")
    async def voteskip_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        if not await quiz_check(self.bot, interaction, self.logger): return
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if not (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):
            embed = ShortEmbed(description=f"{emoji.XMARK} The bot is not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if str(player.channel.id) != str(voice.channel.id):
            embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        elif not player.queue.upcoming_tracks:
            embed = ShortEmbed(description=f"{emoji.XMARK} The `skip` command could not be executed because there is nothing to skip to")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
    
        num_users = len([user for user in interaction.user.voice.channel.members if not user.bot])
        num_votes = math.ceil(num_users/2)
        embed = ShortEmbed(description=f"{emoji.SKIP} Voting for skip! (0/{num_votes})")
        await interaction.followup.send(embed=embed, view=SkipVotingMenu(1200, player, num_votes, interaction.user.voice.channel, True))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QueueCommands(bot))
    await bot.add_cog(OtherQueueCommands(bot))
