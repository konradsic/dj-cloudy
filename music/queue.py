from utils.errors import (
    QueueIsEmpty
)

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
    
    @property
    def first_track(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[0]

    @property
    def next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        
        self.position += 1
        if self.position >= len(self._queue) -1:
            return None

        return self._queue[self.position]
    
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
