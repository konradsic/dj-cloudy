## TODO:  1. Adapt playlist system it to the bot
##        2. Make some /commands and relase 0.9.0 

import json
from utils.base_utils import getid, AUTHENTICATED_USERS
from utils.errors import (
    PlaylistGetError,
    PlaylistCreationError,
    PlaylistRemoveError
)

class PlaylistHandler:
    def __init__(self, key: str):
        self.key = key
        self._load()
        if str(key) in AUTHENTICATED_USERS:
            self.set_credentials(2)

    @property
    def playlists(self):
        return self.data["playlists"]

    def _load(self):
        with open("data/playlists.json", mode="r") as f:
            data = json.load(f)
        try:
            self.data = data[self.key]
        except KeyError:
            data[self.key] = {"credentials": 0, "playlists": [], "starred-playlist": []}
            with open("data/playlists.json", mode="w") as f:
                json.dump(data, f)
            with open("data/playlists.json", mode="r") as f:
                self.data = json.load(f)[self.key]
        return self.data["playlists"]

    def set_credentials(self, credentials: int):
        """
        Set credentials for a playlist user
        
        Credential types
        ---
        `0`: none
        `1`: moderator
        `2`: admin
        """
        self.data["credentials"] = credentials
        with open("data/playlists.json", mode="r") as f:
            content = json.load(f)
        content[self.key] = self.data
        with open("data/playlists.json", mode="w") as f:
            json.dump(content, f)

    def create_playlist(self, name, tracks=[]):
        try:
            self.data["playlists"].append({"name": name, "id": getid(name), "tracks": tracks})
            with open("data/playlists.json", mode="r") as f:
                content = json.load(f)
            content[self.key] = self.data
            with open("data/playlists.json", mode="w") as f:
                json.dump(content,f)
            return self.data["playlists"]
        except:
            raise PlaylistCreationError(f"Failed to create playlist {name}/tracks:{tracks}")

    def add_to_playlist(self, playlist_name: str, song_url: str):
        try:
            # find playlist
            for i,playlist in enumerate(self.data["playlists"]):
                if playlist["name"] == playlist_name or playlist["id"] == playlist_name:
                    self.data["playlists"][i]['tracks'].append(song_url)
        except: 
            # in case of an error we will raise PlaylistGetError
            raise PlaylistCreationError(f"Failed to add items to playlist {playlist_name}/song:{song_url}")
        if playlist_name.lower() == "starred":
            self.data['starred-playlist'].append(song_url)

        with open("data/playlists.json", mode="r") as f:
            content = json.load(f)
        content[self.key] = self.data
        with open("data/playlists.json", mode="w") as f:
            json.dump(content, f)
        return self.data["playlists"][i]

    def get_playlist(self, name_or_id: str):
        try:
            for playlist in self.data["playlists"]:
                if playlist["name"] == name_or_id or playlist["id"] == name_or_id:
                    return playlist
        except: 
            # in case of an error we will raise PlaylistGetError
            raise PlaylistGetError(f"Failed to get playlist #{name_or_id}")

    def add_to_starred(self, song_url: str):
        self.data["starred-playlist"].append(song_url)
        with open("data/playlists.json", mode="r") as f:
            content = json.load(f)
        content[self.key] = self.data
        with open("data/playlists.json", mode="w") as f:
            json.dump(content, f)
        return self.data["starred-playlist"]

    def remove(self, playlist_name_or_id: str, track_pos: int):
        try:
            for i,playlist in enumerate(self.data["playlists"]):
                if playlist["name"] == playlist_name_or_id or playlist["id"] == playlist_name_or_id:
                    del self.data["playlists"][i]["tracks"][track_pos]
                    with open("data/playlists.json", mode="r") as f:
                        content = json.load(f)
                    content[self.key] = self.data
                    with open("data/playlists.json", mode="w") as f:
                        json.dump(content, f)
                    return playlist
            if playlist_name_or_id.lower() == "starred":
                del self.data['starred-playlist'][track_pos]
                with open("data/playlists.json", mode="r") as f:
                    content = json.load(f)
                content[self.key] = self.data
                with open("data/playlists.json", mode="w") as f:
                    json.dump(content, f)
                return self.data['starred-playlist']
        except:
            # raise PlaylistRemoveError
            raise PlaylistRemoveError(f"Failed to remove element {track_pos}, playlist #{playlist_name_or_id}")

        raise PlaylistRemoveError(f"No data found for name/id:{playlist_name_or_id}, pos:{track_pos}")

    def remove_playlist(self, playlist_name_or_id: str):
        try:
            # remove playlist
            for i,playlist in enumerate(self.data["playlists"]):
                if playlist["name"] == playlist_name_or_id or playlist["id"] == playlist_name_or_id:
                    del self.data["playlists"][i]
                    with open("data/playlists.json", mode="r") as f:
                        content = json.load(f)
                    content[self.key] = self.data
                    with open("data/playlists.json", mode="w") as f:
                        json.dump(content, f)
                    return self.data["playlists"]
        except:
            raise PlaylistRemoveError(f"Failed to remove playlist #{playlist_name_or_id}")

        raise PlaylistRemoveError(f"No data found for playlist {playlist_name_or_id}")

    def __getitem__(self, item):
        return self.data["playlists"][item]

    def __str__(self):
        return f"<class PlaylistHandler userID={self.key} playlists={self.playlists}>"

    def __len__(self):
        return len(self.data["playlists"])

# other utility functions for playlists
async def get_playlists_for_user(user_id: str):
    try:
        user = PlaylistHandler(key=user_id)
        return user.playlists
    except:
        raise PlaylistGetError(f"Failed to get playlists for user {user_id}")

async def get_user(user_id: int):
    try:
        return PlaylistHandler(key=user_id)
    except: 
        raise PlaylistGetError(f"Failed to get user {user_id}")