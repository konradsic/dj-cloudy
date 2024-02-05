from lib.utils.errors import (
    QueueIsEmpty
)
from enum import Enum
import random
from lib.utils.base_utils import Repeat, RepeatMode
import discord

class Queue:
    def __init__(self):
        self._queue = []
        self._requested = []
        self.position = 0
        self.repeat: Repeat = Repeat()
        self.shuffle_mode_state = 0
    
    @property
    def is_empty(self):
        return not self._queue

    @property
    def tracks(self):
        return [track.title for track in self._queue]

    @property
    def first_track(self):
        if not self._queue:
            raise QueueIsEmpty
        self.position = 0
        return self._queue[0]

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]
        
    @property
    def current_requested(self) -> discord.Member:
        if not self._requested:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._requested[self.position]

    @property
    def length(self):
        return len(self._queue)

    @property
    def upcoming_tracks(self):
        return self._queue[self.position+1:]
    
    @property
    def track_history(self):
        return self._queue[:self.position]
    
    # Fix of issue #45
    @property
    def upcoming_track(self): # ! ONE
        if self.position == len(self._queue) - 1:
            return None
        return self._queue[self.position+1]
    
    def before_track(self): # ! ONE
        if self.position == 0:
            return None
        return self._queue[self.position-1]

    def add(self, *tracks):
        self._queue.extend([t[0] for t in tracks])
        self._requested.extend([t[1] for t in tracks])

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        
        self.position += 1
        if self.repeat.mode == RepeatMode.REPEAT_CURRENT_TRACK:
            self.position -= 1 # reset back
        if self.position > len(self._queue) -1:
            if self.repeat.mode == RepeatMode.REPEAT_QUEUE:
                self.position = 0
                if self.shuffle_mode_state == True:
                    self.shuffle()

        return self._queue[self.position]

    def shuffle(self):
        before_track_requested_mapping = {}
        for track, req_by in zip(self._queue, self._requested):
            before_track_requested_mapping[track] = req_by
        
        tracks_to_shuffle = self.track_history + self.upcoming_tracks
        random.shuffle(tracks_to_shuffle)
        # putting the current track to avoid errors with player position
        shuffled = []
        if self.track_history:
            shuffled.extend(tracks_to_shuffle[:len(self.track_history)])
        shuffled.append(self.current_track)
        shuffled.extend(tracks_to_shuffle[len(self.track_history):])
        self._queue = shuffled
        # bring back requested mapping
        new_requested = []
        for track in self._queue:
            new_requested.append(before_track_requested_mapping[track])
        self._requested = new_requested
        return self._queue

    def cleanup(self):
        if not self._queue:
            raise QueueIsEmpty
        self._queue.clear()
        self._requested.clear()
        self.position = 0
        return []

    def get_tracks(self):
        return [track for track in self._queue]
    
    def get_requested(self):
        return [req for req in self._requested]

    def __len__(self):
        return len(self._queue)
