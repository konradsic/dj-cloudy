import json
import time
from utils.errors import (
    DefaultProfileNotFound,
    KeyDoesNotExist,
    IncorrectValueType,
    UserNotFound,
)

class ConfigurationHandler:
    def __init__(self, id: str, user: bool=True):
        self.id = id
        self.is_user = user
        self._load()

    def _load(self):
        # create FILE settings.json if not exists
        try:
            with open("data/settings.json", mode="r") as f:
                _ = json.load(f)
        except:
            with open("data/settings.json", mode="w") as f:
                profile = {"users": {}, "guilds": {}}

        profile = self.get_default_profile_for("user" if self.is_user else "guild")

        with open("data/settings.json", mode="r") as f:
            content = json.load(f)
        
        try:
            self.data = content["users" if self.is_user else "guilds"][self.id]
        except:
            self.data = profile
        self.save()

    def save(self):
        with open("data/settings.json", mode="r") as f:
            content = json.load(f)
        
        type = "users" if self.is_user else "guilds"
        content[type][self.id] = self.data
        with open("data/settings.json", mode="w") as f:
            json.dump(content, f)

    def get_default_profile_for(self, what: str):
        if what == "user":
            with open("data/default-user.json", mode="r") as f:
                default_user = json.load(f)
                return default_user
        elif what == "guild":
            with open("data/default-guild.json", mode="r") as f:
                default_guild = json.load(f)
                return default_guild
        else:
            raise DefaultProfileNotFound(f"Profile \"{what}\" was not found. Available profiles are in data folder, named <default-*.json>")

    def config_set(self, key, value):
        pass

    def update_profile(self):
        pass

    def restore_default_vaule(self, key):
        pass

    def reset_to_default(self):
        # in addition to self.restore_default_value this function resets EVERYTHING to default
        pass