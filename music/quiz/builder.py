from random_song import song_from_artist, song_from_collection
from typing import List, Literal
import discord
import wavelink
import asyncio
import random
import re

PUNCTUATION = [".", ",", "&", "-", "'", "\"", ":", ";", "`", "?"]

def cleanup(string):
    # TODO: removal of brackets, etc.
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
        
        # set ups
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
        

class QuizBuilder():
    pass
