from utils.errors import (
    QueueIsEmpty
)
import random

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
    
    @property
    def tracks(self):
        return [track.title for track in self._queue]

    @property
    def first_track(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[0]

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def length(self):
        return len(self._queue)

    @property
    def upcoming_tracks(self):
        return self._queue[self.position+1:]
    
    @property
    def track_history(self):
        return self._queue[:self.position]

    def add(self, *tracks):
        self._queue.extend(tracks)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        
        self.position += 1
        if self.position > len(self._queue) -1:
            return None

        return self._queue[self.position]

    def shuffle(self):
        tracks_to_shuffle = self.track_history + self.upcoming_tracks
        random.shuffle(tracks_to_shuffle)
        # putting the current track to avoid errors with player position
        shuffled = []
        if self.track_history != []:
            shuffled.extend(tracks_to_shuffle[:len(self.track_history)])
        shuffled.append(self.current_track)
        shuffled.extend(tracks_to_shuffle[len(self.track_history):])
        self._queue = shuffled
        return self._queue

    def cleanup(self):
        if not self._queue:
            raise QueueIsEmpty
        self._queue.clear()
        self.position = 0
        return []

    def __len__(self):
        return len(self._queue)