from enum import Enum
import discord

AUTHENTICATED_USERS = ["958029521565679646"] # list of authenticated users (of ID's)

volume_guilds = {}
registered_nodes = []

def change_volume(guild, val):
    volume_guilds[str(guild.id)] = val

def get_volume(guild):
    try:
        return volume_guilds[str(guild.id)]
    except:
        volume_guilds[str(guild.id)] = 100
        return 100

def register_node(node_cls):
    if node_cls not in registered_nodes:
        registered_nodes.append(node_cls)

def get_nodes():
    return registered_nodes

progressbar_emojis = {
    "bar_left_nofill": "<:progressbarleftnofill:1030469955512193025>",
    "bar_left_fill": "<:progressbarleftfill:1030469953754775552>",
    "bar_mid_fill": "<:progressbarmidfullfill:1030469957592563712>",
    "bar_mid_halffill": "<:progressbarmidhalffill:1030469959232536606>",
    "bar_mid_nofill": "<:progressbarmidnofill:1030469960553746552>",
    "bar_right_nofill": "<:progressbarrightnofill:1030469964383133777>",
    "bar_right_fill": "<:progressbarrightfill:1030469962583785552>"
}

def basic_auth(name: str, string: str, user: discord.User):
    if str(user.id) not in AUTHENTICATED_USERS:
        return "hidden_" + name
    return string

class RepeatMode(Enum):
    REPEAT_NONE = 0
    REPEAT_CURRENT_TRACK = 1
    REPEAT_QUEUE = 2

class Repeat:
    def __init__(self):
        self.repeat_mode = RepeatMode.REPEAT_NONE
    
    @property
    def mode(self):
        """
        An alias to `repeat_mode`
        """
        return self.repeat_mode

    @property
    def get(self):
        """
        An alas to `repeat_mode`
        """
        return self.repeat_mode

    @property
    def string_mode(self):
        if self.repeat_mode == RepeatMode.REPEAT_NONE:
            return "REPEAT_NONE"
        elif self.repeat_mode == RepeatMode.REPEAT_CURRENT_TRACK:
            return "REPEAT_CURRENT_TRACK"
        elif self.repeat_mode == RepeatMode.REPEAT_QUEUE:
            return "REPEAT_QUEUE"

    def set_repeat(self, mode):
        if mode == "REPEAT_NONE":
            self.repeat_mode = RepeatMode.REPEAT_NONE
        elif mode == "REPEAT_CURRENT_TRACK":
            self.repeat_mode = RepeatMode.REPEAT_CURRENT_TRACK
        elif mode == "REPEAT_QUEUE":
            self.repeat_mode = RepeatMode.REPEAT_QUEUE
        return self.repeat_mode