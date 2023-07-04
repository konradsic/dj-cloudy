import datetime
import time

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from utils import help_utils, logger, get_length
from utils.colors import BASE_COLOR
from utils import djRole_check
from music.quiz import random_song
import difflib
from traceback import format_exc
import colorama
from utils import emoji
from utils.buttons import QuizButtonsUI

logging = logger.Logger(__name__)

def diff(a, b) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()

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
            sorted_artists = difflist(current, artists)
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
    @app_commands.describe(rounds="Number of rounds", song_collection="What collection of songs you want to select. Use `artist:` to search for artists")
    @app_commands.autocomplete(song_collection=song_collection_autocomplete)
    async def quiz_start_command(self, interaction: discord.Interaction, rounds: int, song_collection: str):
        await interaction.response.defer(thinking=True)
        # djRole check
        if not await djRole_check(interaction, self.logger): return
        
        category, string = song_collection.split(":")
        songs = []
        if category == "artist":
            songs = await random_song.many_songs_from_artist(string, limit=rounds)
            genres = f"`[🧑‍🎤]` {string}'s songs"
        if category == "top":
            songs = await random_song.many_songs_from_collection(num=rounds, top_num=int(string), from_best=True)
            genres = f"`[📂]` Songs from top {string} artist(s) [(check here)](https://www.billboard.com/charts/artist-100/)"
            
        if not songs:
            embed = discord.Embed(description=f"{emoji.XMARK.string} No songs were found with given criteria. Try again", color=BASE_COLOR)
            await interaction.followup.send(embed=embed)
            return
        
        starting_in = round(time.time()) + 30
        
        quiz_embed = discord.Embed(description=f"Music quiz starting in <t:{starting_in}:R>. Click the button below to join.", color=BASE_COLOR)
        quiz_embed.set_author(name="Music Quiz!", url=self.bot.user.avatar.url)
        quiz_embed.add_field(name="Songs in the quiz", value=genres)
        quiz_embed.add_field(name="Rounds", value=f"{rounds} (estimated time: `{get_length(65 * rounds * 1000)}`)")
        # ^ we multiply estimated time by 1000 because of get_length is suited for wavelink.Playable track duration that is in milliseconds
        
        await interaction.followup.send(embed=quiz_embed, view=QuizButtonsUI(timeout=60))



async def setup(bot):
    await bot.add_cog(MusicQuizCog(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
