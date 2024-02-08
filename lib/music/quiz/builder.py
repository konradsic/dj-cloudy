import asyncio
import datetime
import difflib
import random
import re
import time
from typing import List, Literal

import discord
import wavelink
from lib.ui.buttons import SendAnswerUI

from lib.ui.colors import BASE_COLOR

from .random_song import (many_songs_from_collection, song_from_artist,
                          song_from_collection)
from lib.ui import emoji

PUNCTUATION = [".", ",", "&", "-", "'", "\"", ":", ";", "`", "?", "/"]

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
        self.song_artist: str = self.song.artists[0]
        
        # setups
        self.revealed_letters: List[int] = [] # indices
        self.point_for_artist: bool = True # false after third stage
        
        self.song_string: str = None
        self.artist_string: str = "" 
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
            match = matcher(None, ans.lower(), self.song_title.lower()).quick_ratio()
        else:
            match = matcher(None, ans.lower(), self.song_artist.lower()).quick_ratio()
        
        if match >= 0.85: # 85% or more the same
            return True
        
        return False

def get_round_embed(hint, next_event, end_time, icon_url, round_num):
    embed = discord.Embed(description=f"Round #{round_num} is ending in <t:{end_time}:R>", color=BASE_COLOR, timestamp = datetime.datetime.utcnow())
    embed.set_author(name="Round is running!", icon_url=icon_url)
    embed.add_field(name="Hints", value=hint, inline=False)
    embed.add_field(name="Next event", value=next_event, inline=True)
    return embed


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
        self.player = player
        self.player.queue.add(*zip(self.songs, [interaction.user, ] * len(self.songs)))
        self.is_stopped = False
        
        
    @property
    def current_round(self):
        return self.rounds[self.current_round_idx]
        
    async def run(self):
        channel = self.interaction.channel
        
        embed = discord.Embed(description="Prepare your ears for the first round! (quiz starting...)", color=BASE_COLOR)
        embed.set_author(name="Building quiz...", icon_url=self.bot.user.avatar.url)
        
        await channel.send(embed=embed)
        
        for i in range(len(self.rounds)):
            cur_round = self.current_round
            await self.run_round(cur_round, i + 1)
            if self.is_stopped: return
            # round results
            embed = discord.Embed(description="Lets look at the results (next round starting soon)", timestamp=datetime.datetime.utcnow(), color=BASE_COLOR)
            embed.set_author(name="Round ended!", icon_url=self.bot.user.avatar.url)
            _cache = self.player_mapping_points
            embed.add_field(name="Ranking", value="\n".join(f"{i}. <@{player}> `{points} pts.`" for (i, player), points in sorted(zip(enumerate(_cache.keys()), _cache.values()), key=lambda x: x[1], reverse=True)), inline=False)
            embed.add_field(name="Song", value=f"The song was...\n`{cur_round.song_title}, by: {cur_round.song_artist}`", inline=False)
            await self.interaction.channel.send(embed=embed)
            
            await asyncio.sleep(5)
            self.current_round_idx += 1
        
        # send ranking embed
        embed = discord.Embed(color=BASE_COLOR, timestamp=datetime.datetime.utcnow(), title="Quiz ranking", description="Top 5 places")
        ranks = sorted(zip(_cache.keys(), _cache.values()), key=lambda x: x[1], reverse=True)
        embed.add_field(name="🏆 The winner", value=f"<@{ranks[0][0]}> : `{ranks[0][1]} pts.`", inline=False)
        if len(ranks) == 2:
            embed.add_field(name="Podium", value=f"🥈 <@{ranks[1][0]}> : `{ranks[1][1]} pts.`", inline=False)
        if len(ranks) == 3:
            embed.add_field(name="Podium", value=f"🥈 <@{ranks[1][0]}> : `{ranks[1][1]} pts.`\n🥉 <@{ranks[2][0]}> : `{ranks[2][1]} pts.`", inline=False)
        
        if len(ranks) == 4:
            embed.add_field(name="Honourable mention", value=f"4th <@{ranks[3][0]}> : `{ranks[3][1]} pts.`", inline=False)
        if len(ranks) >= 5:
            embed.add_field(name="Honourable mentions", value=f"4th <@{ranks[3][0]}> : `{ranks[3][1]} pts.`\n5th <@{ranks[4][0]}> : `{ranks[4][1]} pts.`", inline=False)
        
        await self.interaction.channel.send(embed=embed)
        
        # cleanup
        await self.bot.quiz_cache.remove(str(self.interaction.guild.id))
        del self.bot.quizzes[str(self.interaction.guild.id)]
        
    async def run_round(self, round_: Round, idx: int):
        t = round(time.time())
        end_time = t + round_.time
        pdict = {
            str(player.id): 0 for player in self.players
        }
        pdict["round_start"] = t
        pdict["title"] = round_.song_title
        pdict["artist"] = round_.song_artist
        
        await self.bot.quiz_cache.save(str(self.interaction.guild.id), pdict)
        stages = round_.time_stages
        round_events = {
            stages[0]: f"2x Letters reveal (<t:{t + stages[0]}:R>)",
            stages[1]: f"Second 2x letter reveal (<t:{t + stages[1]}:R>)",
            stages[2]: f"Author/Artist reveal (<t:{t + stages[2]}:R>)",
            end_time: f"Round end (<t:{end_time}:R>)"
        }
        
        embed = get_round_embed("No hint for now!", round_events[stages[0]], end_time, self.bot.user.avatar.url, idx)
        try:
            if idx == 1:
                await self.player.start_playback(self.interaction)
            else:
                await self.player.stop()
            await self.player.seek(60 * 1000)
        except: pass
        
        ui = SendAnswerUI(timeout=round_.time, interaction=self.interaction, quiz=self)
        msg = await self.interaction.channel.send(embed=embed, view=ui)
        
        _stages2 = [*round_.time_stages, end_time]
        before_time = 0
        
        for k,v in list(round_events.items())[:-1]:
            if self.is_stopped: return
            await asyncio.sleep(k-before_time)
            before_time = k
            if k == stages[0] or k == stages[1]:
                round_.reveal_song_letter()
                round_.reveal_song_letter()
                # ^ two times as promised
            if k == stages[2]:
                round_.reveal_artist()
            
            embed = get_round_embed(f"`{round_.song_string}, by: {round_.artist_string or 'Not revealed yet!'}`", round_events[_stages2[_stages2.index(k) + 1]], end_time, self.bot.user.avatar.url, idx)
            ui.timeout = round_.time - k
            await msg.edit(embed=embed, view=ui)

        await asyncio.sleep(round_.time-before_time)
        if self.is_stopped:
            return
        _cache = await self.bot.quiz_cache.get(str(self.interaction.guild.id))
        _cache = list(_cache.items())[:-4]
        for k,v in _cache:
            self.player_mapping_points[k] += v
        
        return
    
    async def stop(self):
        # wipe up cache and bot.quizzes
        await self.bot.quiz_cache.remove(str(self.interaction.guild.id))
        del self.bot.quizzes[str(self.interaction.guild.id)]
        
        self.is_stopped = True # returns from run_round -> and then run
        
        await self.interaction.channel.send(embed=discord.Embed(
            description=f"{emoji.TICK.string} Quiz ended! [forced]",
            color=BASE_COLOR
        ))
    