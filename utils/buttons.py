import typing as t

import discord
from discord import ui
from discord.ui import View

from music import playlist
import wavelink

from .base_utils import RepeatMode
from .colors import BASE_COLOR
from .configuration import ConfigurationHandler as Config

class PlayButtonsMenu(View):
    def __init__(self, timeout: float=None, user: t.Optional[discord.Member] = None) -> None:
        super().__init__(timeout=timeout)
        self.user = user
        self.timeout = timeout

    @ui.button(emoji="<:volume_high:1029437727294361691>", style=discord.ButtonStyle.gray)
    async def volume_up_button(self, interaction, button):
        if not (player := wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        volume = player.volume
        if volume+10 >= 1000:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume is currently set to the max value, can't go higher!",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await player.set_volume(volume+10)
        embed = discord.Embed(description=f"<:volume_high:1029437727294361691> Volume is now higher by `10%`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(emoji="<:volume_low:1029437729265688676>", style=discord.ButtonStyle.gray)
    async def volume_low_button(self, interaction, button):
        if not (player := wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)):
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if not player.is_playing():
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Nothing is currently playing",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        volume = player.volume
        if volume == 0:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Volume is currently set to the min value, can't go lower!",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await player.set_volume(volume-10)
        embed = discord.Embed(description=f"<:volume_low:1029437729265688676> Volume is now lower by `10%`", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(emoji="<:repeat_button:1030534158302330912>", style=discord.ButtonStyle.gray)
    async def toggle_repeat_button(self, interaction, button):
        if not (player := wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)):
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
        if not (player := wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)):
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
        if not (player := wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)):
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
        
class ResetCfgConfirmation(View):
    def __init__(self, timeout: float, cfg: Config, user: t.Optional[discord.Member]=None) -> None:
        super().__init__(timeout=timeout)
        self.user = user
        self.config = cfg
        
    async def confirm(self, interaction: discord.Interaction, confirmed: bool):
        self.children[0].disabled = True
        self.children[1].disabled = True
        
        embed = discord.Embed(description="Success! ",color=BASE_COLOR)

        if confirmed: message = "Configuration has been reset"
        else: message = "Cancelled, nothing changed"
        embed.description += message
        
        try:
            if confirmed:
                self.config.reset_to_default(True)
        except Exception as e:
            print(e.__class__.__name__, str(e))
        await interaction.response.edit_message(embed=embed,view=self)
        
    @ui.button(label="Yes", style=discord.ButtonStyle.grey)
    async def confirm_button(self, interaction: discord.Interaction, button):
        await self.confirm(interaction, True)
        
    @ui.button(label="No", style=discord.ButtonStyle.blurple)
    async def cancel_button(self, interaction: discord.Interaction, button):
        await self.confirm(interaction, False)
        
class SkipVotingMenu(View): # player: type: Any (due to circular imports)
    def __init__(self, timeout: float, player, num_votes: int, vc: discord.VoiceChannel, forward_track: bool = True) -> None:
        super().__init__(timeout=timeout)
        self.player = player
        self.vc = vc
        self.num_votes = num_votes
        self.current_votes = 1
        self.forward_track = forward_track
        self.voted_members = []
        
    def add_vote(self, user: discord.Member):
        if user.bot: return # no bots pls!
        if (user not in self.vc.members) and (user not in self.vc.voted_members):
            return
        
        self.voted_members.append(user)
        self.current_votes += 1
        
    @ui.button(label="Skip!", style=discord.ButtonStyle.blurple)
    async def skip_button(self, interaction: discord.Interaction, button):
        self.add_vote(interaction.user)
        
        if self.current_votes < self.num_votes:
            embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Voting for skip! ({self.current_votes}/{self.num_votes})", color=BASE_COLOR)
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        # voting success!
        if self.current_votes >= self.num_votes:
            if not self.forward_track: # previous
                self.player.queue.position -= 2 
                # ^ explained in cogs.queue_commands.OtherQueueCommands.queue_previous func
            await self.player.stop() # chain-calls player advance 
            
            embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Skipped! (action approved by channel users)", color=BASE_COLOR)
            self.children[0].disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
