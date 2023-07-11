import difflib
import time
import typing as t

import discord
import wavelink
from discord import ui
from discord.ui import Modal, View

from music import playlist

from . import emoji
from .base_utils import RepeatMode
from .cache import JSONCacheManager
from .colors import BASE_COLOR
from .configuration import ConfigurationHandler as Config
from traceback import format_tb


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
        self.current_votes = 0
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
        
        if self.current_votes < self.num_votes:
            return
    
        # voting success!
        if not self.forward_track: # previous
            self.player.queue.position -= 2 
            # ^ explained in cogs.queue_commands.OtherQueueCommands.queue_previous func
        await self.player.stop() # chain-calls player advance 
        
        embed = discord.Embed(description=f"<:skip_button:1029418193321725952> Skipped! (action approved by channel users)", color=BASE_COLOR)
        self.children[0].disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

class QuizButtonsUI(View):
    def __init__(self, timeout: float, bot: discord.Client):
        super().__init__(timeout=timeout)
        self.bot = bot
        #self.players = self.bot.quizzes[str(interaction.guild.id)]
        
    @ui.button(label="Join quiz", style=discord.ButtonStyle.blurple)
    async def join_quiz_btn(self, interaction: discord.Interaction, button):
        try:
            if interaction.user in self.bot.quizzes[str(interaction.guild.id)]:
                await interaction.response.send_message(embed=discord.Embed(
                    description=f"{emoji.XMARK.string} Already joined the quiz, please wait for the start",
                    color=BASE_COLOR
                ), ephemeral=True)
                return
            
            # NOTE: vc checks - user needs to be in the vc to join
            player = wavelink.NodePool.get_connected_node().get_player(interaction.guild.id)
            if not interaction.user.voice:
                await interaction.response.send_message(embed=discord.Embed(
                    description=f"{emoji.XMARK.string} You need to be in a voice channel ({player.channel.mention}) to join the quiz",
                    color=BASE_COLOR
                ), ephemeral=True)
                return
                
            if interaction.user.voice.channel != player.channel:
                await interaction.response.send_message(embed=discord.Embed(
                    description=f"{emoji.XMARK.string} You need to be in the same channel that the bot is in to join the quiz. Please switch to {player.channel.mention}"
                ), ephemeral=True)
                return
            
            self.bot.quizzes[str(interaction.guild.id)].append(interaction.user)
            await interaction.response.send_message(embed=discord.Embed(
                description=f"{emoji.TICK.string} Successfully joined the quiz",
                color=BASE_COLOR
            ), ephemeral=True)
        except Exception as e:
            print(e.__class__.__name__, str(e))

class QuizResponseModal(Modal, title="What is the song and author?"):
    song_title = ui.TextInput(label="Song title", required=True, placeholder="What is the title of the currently playing song")
    song_author = ui.TextInput(label="Song author", required=False, placeholder="What is the author of the currently playing song")

    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            points = 0
            mgr = JSONCacheManager("quizzes.json", expiration_time = -1)
            _old = await mgr.get(str(interaction.guild.id))
            started = _old["round_start"]
            players = list(_old.keys())
            if str(interaction.user.id) not in players:
                await interaction.followup.send("You are not in the players list!", ephemeral=True)
                return
            round_time = 60
            # NOTE: points - 200 (time), 500 (title) and 300 (author) - max 1000
            artist = _old["artist"]
            title = _old["title"]
            
            # comparison
            matcher = difflib.SequenceMatcher
            match_title = matcher(None, str(self.song_title).lower(), str(title).lower()).real_quick_ratio()
            match_artist = matcher(None, str(self.song_author).lower(), str(artist).lower()).real_quick_ratio()
            
            # points if good
            if match_title == 1.0: # ~~more than 80% similarity
                points += 500
            if match_artist == 1.0:
                points += 300
            if points:
                points += round(200 * (1 - round(time.time() - started) / (round_time)))
                
            if not (points == 0):
                await interaction.followup.send(f"Submitted! Your score: {round(points)} points", ephemeral=True)
                _old[str(interaction.user.id)] = points
                await mgr.save(str(interaction.guild.id), _old)
                return
            await interaction.followup.send("Submitted! Although you didn't get any points :(", ephemeral=True)   
        except Exception as e:
            print(e.__class__.__name__, str(e), format_tb())
                 
        

class SendAnswerUI(View):
    def __init__(self, timeout: float, interaction: discord.Interaction, quiz) -> None:
        super().__init__(timeout=timeout)
        self.timeout = timeout
        self.quiz = quiz
        
    @ui.button(label="Click to answer!", style=discord.ButtonStyle.blurple)
    async def answer_button(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(QuizResponseModal())
