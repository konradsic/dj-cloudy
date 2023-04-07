import json
import time
from utils.errors import (
    DefaultProfileNotFound,
    KeyDoesNotExist,
    IncorrectValueType,
    UserNotFound,
    AuthFailed
)

def get_class_from_value(value):
    valType = str(type(value))
    valType = valType[len("<class '"):][:-2]
    return str(valType)  #string

class ConfigurationHandler:
    def __init__(self, id: str, user: bool=True):
        self.id = id
        self.is_user = user
        self._load()
        self.update_profile()

    def _load(self):
        # create FILE settings.json if not exists
        try:
            with open("data/settings.json", mode="r") as f:
                _ = json.load(f)
        except:
            with open("data/settings.json", mode="w") as f:
                profile = {"users": {}, "guilds": {}}
                json.dump(profile,f)

        profile = self.get_default_profile_for("user" if self.is_user else "guild")

        with open("data/settings.json", mode="r") as f:
            content = json.load(f)
        
        try:
            self.data = content["users" if self.is_user else "guilds"][str(self.id)]
        except:
            self.data = profile
        try:
            self.save()
        except:
            with open("data/settings.json", mode="w") as f:
                json.dump({"users": {}, "guilds": {}},f)
            self.save()

    def save(self):
        with open("data/settings.json", mode="r") as f:
            content = json.load(f)
        
        type = "users" if self.is_user else "guilds"
        content[type][str(self.id)] = self.data
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
        try:
            current = self.data[key]
        except:
            raise KeyDoesNotExist(f"Key \"{key}\" does not exist")
        valType = get_class_from_value(value)
        if valType == "discord.role.Role":
            valType = "role"
            value = str(value.id)
        if valType not in ["int", "str", "bool", "role"]:
            raise IncorrectValueType(f"{valType} is not a correct value type")
        if valType != current["type"]:
            raise IncorrectValueType(f"{valType} does not match type for key {key} (expected {current['type']})")

        # correct data type - lets overwrite data
        self.data[key]["value"] = value
        self.save()
        return self.data[key] # new value
        

    def update_profile(self):
        typeProfile = "user" if self.is_user else "guild"
        fileName = f"data/default-{typeProfile}.json"
        with open(fileName, mode="r") as f:
            data = json.load(f)

        # iterate over elements, add missing
        for key,val in data.items():
            try:
                _key = self.data[key]
            except KeyError:
                self.data[key] = val

        # save
        self.save()
        return True # profile updated with new values!

    def restore_default_vaule(self, key):
        # restore default of given value
        typeProfile = "user" if self.is_user else "guild"
        fileName = f"default-{typeProfile}.json"
        with open(fileName, mode="r") as f:
            data = json.load(f)
        
        try:
            self.data[key] = data[key]
        except KeyError:
            raise KeyDoesNotExist(f"Attempted to reset value for \"{key}\" but it does not exist")
        return True
        

    def reset_to_default(self, sure: bool=False):
        # in addition to self.restore_default_value this function resets EVERYTHING to default
        if not sure:
            raise AuthFailed("To reset profile please confirm you want to do that by setting `sure` to True")

        typeProfile = "user" if self.is_user else "guild"
        fileName = f"default-{typeProfile}.json"
        with open(fileName, mode="r") as f:
            data = json.load(f)
        
        self.data = data
        self.save()
        return True