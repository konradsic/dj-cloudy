import datetime
import math
import re
import typing as t

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.colors import BASE_COLOR
from utils.errors import NoPlayerFound, NoTracksFound
from utils.regexes import URL_REGEX
from utils.run import running_nodes

logging = logger.Logger().get("cogs.play")

number_complete = {
    0: "🥇 ",
    1: "🥈 ",
    2: "🥉 ",
    3: "4. ",
    4: "5. ",
    5: "6. ",
    6: "7. ",
    7: "8. ",
    8: "9. ",
    9: "10. ",
}
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

async def query_complete(
    interaction: discord.Interaction, 
    current: str
) -> t.List[app_commands.Choice[str]]:
    query = current.strip("<>")
    if not re.match(URL_REGEX, current):
        query = "ytmsearch:{}".format(current)
    try:
        if query.startswith("🥇") or query.startswith("🥈") or query.startswith("🥉"):
            query = query[2:]
        tracks = await running_nodes[0].get_tracks(cls=wavelink.Track, query=query)
        if not tracks:
            return []
        return [
            app_commands.Choice(name=f"{number_complete[i]}{track.title} ({get_length(track.duration)})", value=track.uri)
            for i,track in enumerate(tracks[:10])
        ]
    except Exception as e:
        if e.__class__.__name__ == "LoadTrackError": return []
        logging.error("autocomplete-play", f"Error: {e.__class__.__name__} - {str(e)}")
        return []

class PlayCommand(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot= bot

    @app_commands.command(name="play", description="Plays music")
    @app_commands.describe(query="What song to play")
    @app_commands.autocomplete(query=query_complete)
    async def play_command(self, interaction: discord.Interaction, query: str):
        try:
            if (player := self.bot.node.get_player(interaction.guild)) is None:
                raise NoPlayerFound("There is no player connected in this guild")
        except NoPlayerFound:
            if interaction.user.voice is None:
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed)
                return
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            player.bound_channel = interaction.channel

        query = query.strip("<>")
        tracks = await self.bot.node.get_tracks(cls=wavelink.Track, query=query)
        try:
            await player.add_tracks(interaction, tracks)
        except Exception as e:
            if isinstance(e, NoTracksFound):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> No tracks found. Try searching for something else",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed)
                return "failed"

async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("play", "Plays music", "Music: Base commands", [("query","What song to play",True)])
    await bot.add_cog(
        PlayCommand(bot),
        guilds =[discord.Object(id=g.id) for g in bot.guilds]
    )
