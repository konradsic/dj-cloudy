from dis import dis
import typing as t

import discord
from discord import ui
from discord.ui import View
from .base_utils import change_volume, get_volume, RepeatMode
from .run import running_nodes
from .colors import BASE_COLOR
from music import playlist

class PlayButtonsMenu(View):
    def __init__(self, timeout: float=None, user: t.Optional[discord.Member] = None) -> None:
        super().__init__(timeout=timeout)
        self.user = user
        self.timeout = timeout

    @ui.button(emoji="<:volume_high:1029437727294361691>", style=discord.ButtonStyle.gray)
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
        if volume+10 >= 1000:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume is currently set to the max value, can't go higher!",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await player.set_volume(volume+10)
        change_volume(interaction.guild, volume+10)
        embed = discord.Embed(description=f"<:volume_high:1029437727294361691> Volume is now higher by `10%`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(emoji="<:volume_low:1029437729265688676>", style=discord.ButtonStyle.gray)
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

    @ui.button(emoji="<:repeat_button:1030534158302330912>", style=discord.ButtonStyle.gray)
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

    @ui.button(emoji="<:seek_button:1030534160844062790>", style=discord.ButtonStyle.gray)
    async def restart_playback_button(self, interaction: discord.Interaction, button):
        if not (player := running_nodes[0].get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Cannot seek: nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await player.seek(0) # restart
        embed = discord.Embed(description=f"<:seek_button:1030534160844062790> Track successfully restarted",color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return True

    @ui.button(emoji="<:star_button:1033999611238551562>", style=discord.ButtonStyle.gray)
    async def add_to_starred_button(self, interaction: discord.Interaction, button):
        if not (player := running_nodes[0].get_player(interaction.guild)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        handler = playlist.PlaylistHandler(key=str(interaction.user.id))
        resp = handler.add_to_starred(player.queue.current_track.uri)
        if resp:
            await interaction.response.send_message(ephemeral=True,embed=discord.Embed(description="<:tick:1028004866662084659> Added current playing song to your :star: playlist", color=BASE_COLOR))
            return
        await interaction.response.send_message(ephemeral=True,embed=discord.Embed(description="<:tick:1028004866662084659> Un-starred current playing song", color=BASE_COLOR))

class EmbedPaginator(View):
    def __init__(self, pages:list, timeout:float, user: t.Optional[discord.Member]=None) -> None:
        super().__init__(timeout=timeout)
        self.current_page = 0
        self.pages = pages
        self.user = user
        self.length = len(self.pages)-1

    async def update(self, page:int):
        self.current_page = page
        if page == 0:
            self.children[0].disabled = True
            self.children[-1].disabled = False
        elif page == self.length:
            self.children[0].disabled = False
            self.children[-1].disabled = True
        else:
            for i in self.children: i.disabled = False

    async def get_page(self, page):
        return [page]

    async def show_page(self, page:int, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user.id):
            await interaction.response.send_message("Thats not yours!", ephemeral=True)
            return
        await self.update(page)
        embeds = await self.get_page(self.pages[page])

        await interaction.response.edit_message(
            embeds=embeds,
            view=self
        )
    
    @ui.button(label="◄", style=discord.ButtonStyle.blurple)
    async def backwards_button(self, interaction: discord.Interaction, button):
        await self.show_page(self.current_page-1, interaction)
    
    @ui.button(label="►", style=discord.ButtonStyle.blurple)
    async def forward_button(self, interaction: discord.Interaction, button):
        await self.show_page(self.current_page+1, interaction)