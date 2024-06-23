import datetime
import time

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from lib.logger import logger
from lib.music.quiz import QuizBuilder
from lib.utils import help_utils

from lib.utils import get_length
from lib.ui.colors import BASE_COLOR
from lib.utils import djRole_check
from lib.music.quiz import random_song
import difflib
from traceback import format_exc
import colorama
from lib.ui import emoji
from lib.music.core import MusicPlayer
from lib.ui.buttons import QuizButtonsUI, QuizResponseModal
import asyncio
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType

logging = logger.Logger(__name__)

def diff(a, b) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).quick_ratio()

def difflist(current: str, targets: list) -> list:
    return sorted(targets, key=lambda x: diff(current, x), reverse=True)

async def song_collection_autocomplete(
    interaction: discord.Interaction, 
    current: str
):
    try:
        artists = await random_song.get_top100_artists()
        pre_collections = [
            100,
            50,
            25,
            10,
            5
        ]
        
        # easier :D
        if current.startswith("artist:"):
            splitted = current.split(":", 1)[1]
            if not splitted: splitted = ""
            sorted_artists = difflist(splitted, artists)
            return [
                app_commands.Choice(name=f"{i}. [🧑‍🎤] {artist}", value=f"artist:{artist}")
                for i, artist in enumerate(sorted_artists[:10], start=1)
            ]
            
        try:
            current = int(current)
            if current > 100: current = 100
            if current < 1: current = 1
        except:
            return [
                app_commands.Choice(name=f"{i}. [📂] Songs from top {num} artist(s)", value=f"top:{num}")
                for i, num in enumerate(pre_collections, start=1)
            ]
        
        return [app_commands.Choice(name=f"[📂] Songs from top {current} artist(s)", value=f"top:{current}")]
        
    except Exception as e:
        colorama.init(autoreset=False)
        logging.error(f"[song_collection_autocomplete] Exception while trying to autocomplete:\n\t{e.__class__.__name__}: {str(e)}\n{colorama.Fore.RED}{format_exc()}{colorama.Style.RESET_ALL}")
        colorama.init(autoreset=True)
        return [
            app_commands.Choice(name=f"{i}. [📂] Songs from top {num} artist(s)", value=f"top:{num}")
            for i, num in enumerate(pre_collections, start=1)
        ]

@logger.LoggerApplication
class MusicQuizCog(commands.GroupCog, name="quiz"):
    def __init__(self, bot: commands.Bot, logger: logger.Logger):
        self.bot: commands.Bot = bot
        self.logger = logger
        super().__init__()
        
    @app_commands.command(name="start", description="Start a music quiz. Requires DJ permissions")
    @app_commands.describe(rounds="Number of rounds")
    @help_utils.add("quiz start", "Start a music quiz. Required DJ permissions", "Music quiz", {"rounds": {"description": "Number of rounds", "required": True}})
    async def quiz_start_command(self, interaction: discord.Interaction, rounds: int):
        await interaction.response.defer(thinking=True)
        # djRole check
        if not await djRole_check(interaction, self.logger): return
        
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"{emoji.XMARK} You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if (player := wavelink.Pool.get_node().get_player(interaction.guild.id)):    
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"{emoji.XMARK} The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
        try:
            self.bot.quizzes[str(interaction.guild.id)]
            embed = ShortEmbed(description=f"{emoji.XMARK.string} Another quiz is already running!")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        except: pass

        songs = await random_song.random_songs_new(rounds)
        genres = f"`[📂]` Top 100 songs of 2022"
            
        if not songs:
            embed = ShortEmbed(description=f"{emoji.XMARK.string} No songs were found with given criteria. Try again")
            await interaction.followup.send(embed=embed)
            return
        
        starting_in = round(time.time()) + 30
        
        quiz_embed = NormalEmbed(description=f"Music quiz starting in <t:{starting_in}:R>. Click the button below to join.")
        quiz_embed.set_author(name="Music Quiz!", icon_url=self.bot.user.avatar.url)
        quiz_embed.add_field(name="Songs in the quiz", value=genres)
        quiz_embed.add_field(name="Rounds", value=f"{rounds} (estimated time: `{get_length(65 * rounds * 1000)}`)")
        # ^ we multiply estimated time by 1000 because of get_length is suited for wavelink.Playable track length that is in milliseconds
        try:
            self.bot.quizzes[str(interaction.guild.id)] = []
        except:
            self.bot.quizzes = {str(interaction.guild.id): []}
        
        try:
            channel = interaction.user.voice.channel
            await channel.connect(cls=MusicPlayer, self_deaf=True)
        except: pass
        
        await interaction.followup.send(embed=quiz_embed, view=QuizButtonsUI(timeout=30, bot=self.bot))
        
        await asyncio.sleep(30)
        
        players = self.bot.quizzes[str(interaction.guild.id)]
        music_player = wavelink.Pool.get_node().get_player(interaction.guild.id)
        try: music_player.queue.cleanup() # emptying the queue for sure
        except: pass
        
        game = QuizBuilder(rounds, songs, players, 60, music_player, [20, 40, 50], interaction, self.bot)
        try:
            self.bot.quiz_obj[str(interaction.guild.id)] = game
        except:
            self.bot.quiz_obj = {}
            self.bot.quiz_obj[str(interaction.guild.id)] = game
        
        # NOTE: passing "interaction" lets the QuizBuilder run itself without code here
        await game.run() # game loop - run rounds
        
    @app_commands.command(name="end", description="Forces stop of the music quiz. Requires DJ permissions")
    @help_utils.add("quiz end", "Forces stop of the music quiz. Required DJ permissions", "Music quiz")
    async def quiz_end_command(self, interaction: discord.Interaction):
        if not await djRole_check(interaction, self.logger): return
        game = self.bot.quiz_obj[str(interaction.guild.id)]
        print(game)
        await game.stop()
        del self.bot.quiz_obj[str(interaction.guild.id)]
        await interaction.response.send_message(embed=ShortEmbed(description=f"{emoji.TICK.string} Success!"), ephemeral=True)



async def setup(bot):
    await bot.add_cog(MusicQuizCog(bot))
