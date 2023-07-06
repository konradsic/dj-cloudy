import asyncio
import datetime
import difflib
import random
import re
import time
from typing import List, Literal

import discord
import wavelink
from utils.buttons import SendAnswerUI

from utils.colors import BASE_COLOR

from .random_song import (many_songs_from_collection, song_from_artist,
                          song_from_collection)

PUNCTUATION = [".", ",", "&", "-", "'", "\"", ":", ";", "`", "?"]

def cleanup(string):
    replace_matcher = {
        "[": "(",
        "]": ")",
        "{": "(",
        "}": ")"
    }
    for k,v in replace_matcher.items():
        string = string.replace(k, v)
    
    string = re.sub("\(.*?\)", "", string)
    return string.strip()


class Round():
    def __init__(
        self,
        players: List[discord.Member],
        song: wavelink.GenericTrack,
        time: int,
        music_player: wavelink.Player,
        time_stages: List[int]
    ):
        self.players = players
        self.song = song
        self.time = time
        self.music_player = music_player
        self.time_stages = time_stages # a list of 3 elements -> 
        # first, reveal of the length with the first letter, 
        # second, reveal of two more letters, 
        # third -> reveal of the artist (no more points for the artist)
        
        # from song -> title and artist
        self.song_title: str = cleanup(self.song.title)
        self.song_artist: str = self.song.author
        
        # setups
        self.revealed_letters: List[int] = [] # indices
        self.point_for_artist: bool = True # false after third stage
        
        self.song_string: str = None
        self.artist_string: str = None 
        # ^ type: ignore [x2]
    
    def reveal_artist(self):
        self.artist_string = self.song_artist
        
    def reveal_song_letter(self):
        # if None, also length
        if not self.song_string:
            final = ""
            splitted = self.song_title.split(" ")
            for el in splitted:
                for character in el:
                    if el not in PUNCTUATION: final += "_"
                    else: final += character

                final += " "
                
            self.song_string = final

        while True:        
            random_idx = random.randint(0, len(self.song_title) - 1)
            if random_idx in self.revealed_letters: continue
            if self.song_title[random_idx] in PUNCTUATION: continue
            if self.song_title[random_idx] in [" "]: continue
            break
        
        self.revealed_letters.append(random_idx)
        # reveal
        l = list(self.song_string)
        l[random_idx] = self.song_title[random_idx]
        self.song_string = "".join(letter for letter in l)
        
    def submit_answer(self, ans, title: True):
        matcher = difflib.SequenceMatcher
        if title:
            match = matcher(None, ans.lower(), self.song_title.lower()).ratio()
        else:
            match = matcher(None, ans.lower(), self.song_artist.lower()).ratio()
        
        if match >= 0.85: # 85% or more the same
            return True
        
        return False
        

class QuizBuilder():
    def __init__(
        self,
        num_rounds: int,
        songs: list,
        players: List[discord.Member],
        round_time: int,
        player: wavelink.Player,
        round_time_stages: List[int],
        interaction: discord.Interaction,
        bot: discord.ext.commands.Bot
    ):
        self.num_round = num_rounds
        self.songs = songs
        self.players = players
        self.rounds = list([
            Round(players, self.songs[i], round_time, player, round_time_stages)
            for i in range(num_rounds)
        ])
        
        self.current_round_idx = 0
        self.player_mapping_points = {str(player.id): 0 for player in players}
        self.interaction = interaction
        self.bot = bot
        
        
    @property
    async def current_round(self):
        return self.rounds[self.current_round_idx]
        
    async def run(self):
        channel = self.interaction.channel
        
        embed = discord.Embed(description="Prepare your ears for the first round! (quiz starting...)", color=BASE_COLOR)
        embed.set_author(name="Building quiz...", icon_url=self.bot.user.avatar.url)
        
        await channel.send(embed=embed)
        
        for i in range(len(self.rounds)):
            cur_round = self.current_round
            points = await self.run_round(cur_round, i + 1)
        
    async def run_round(self, round_: Round, idx: int) -> dict[str, int]: # UserID, points
        t = round(time.time())
        end_time = t + round_.time
        stages = round_.time_stages
        round_events = {
            stages[0]: f"2x Letters reveal (<t:{t + stages[0]}:R>)",
            stages[1]: f"Second 2x letter reveal (<t:{t + stages[1]}:R>)",
            stages[2]: f"Author/Artist reveal (<t:{t + stages[2]}:R>)",
            end_time: f"Round end (<t:{t + stages[2]}:R>)"
        }
        
        embed = discord.Embed(description=f"Round #{idx} is ending in <t:{end_time}:R>")
        embed.set_author(name="Round is running!", color=BASE_COLOR, timestamp = datetime.datetime.utcnow())
        embed.add_field(name="Hints", value="No hints for now!", inline=True)
        await self.interaction.channel.send(embed=embed, view=SendAnswerUI(timeout=round_.time), interaction=self.interaction, players=round_.players, song=round_.song, start=t)
        
        
        
