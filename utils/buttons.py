import typing as t

import discord
from discord import ui
from discord.ui import View
from .base_utils import change_volume, get_volume, RepeatMode
from .run import running_nodes
from .colors import BASE_COLOR

class PlayButtonsMenu(View):
    def __init__(self, timeout: float=None, user: t.Optional[discord.Member] = None) -> None:
        super().__init__(timeout=timeout)
        self.user = user
        self.timeout = timeout

    @ui.button(label="Volume up", emoji="<:volume_high:1029437727294361691>", style=discord.ButtonStyle.gray)
    async def volume_up_button(self, interaction, button):
        if not (player := running_nodes[0].get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        volume = get_volume(interaction.guild)
        if volume == 1000:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume is currently set to the max value, can't go higher!",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await player.set_volume(volume+10)
        change_volume(interaction.guild, volume+10)
        embed = discord.Embed(description=f"<:volume_high:1029437727294361691> Volume is now higher by `10%`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Volume down", emoji="<:volume_low:1029437729265688676>", style=discord.ButtonStyle.gray)
    async def volume_low_button(self, interaction, button):
        if not (player := running_nodes[0].get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        volume = get_volume(interaction.guild)
        if volume == 0:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume is currently set to the min value, can't go lower!",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await player.set_volume(volume-10)
        change_volume(interaction.guild, volume-10)
        embed = discord.Embed(description=f"<:volume_low:1029437729265688676> Volume is now lower by `10%`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Toggle repeat", emoji="<:repeat_button:1030534158302330912>", style=discord.ButtonStyle.gray)
    async def toggle_repeat_button(self, interaction, button):
        if not (player := running_nodes[0].get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.queue.tracks:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Queue is empty, cannot set repeat mode",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        switch = { # to toggle between repeat modes
            "REPEAT_NONE": "REPEAT_CURRENT_TRACK",
            "REPEAT_CURRENT_TRACK": "REPEAT_QUEUE",
            "REPEAT_QUEUE": "REPEAT_NONE"
        }
        # set new repeat mode
        player.queue.repeat.set_repeat(switch[player.queue.repeat.string_mode])
        await interaction.response.send_message(
            embed=discord.Embed(description=f"<:repeat_button:1030534158302330912> Repeat mode updated to `{player.queue.repeat.string_mode}`",color=BASE_COLOR),
            ephemeral=True
        )