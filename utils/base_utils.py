import math
import os
import platform
from enum import Enum

import discord
import wavelink
import pyfiglet
import colorama
import json
import requests
import uuid
from . import logger

BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"

AUTHENTICATED_USERS = ["958029521565679646"] # list of authenticated users (of ID's)
AEQ_HZ_BANDS = (20, 40, 63, 100, 150, 250, 400, 450, 630, 1000, 1600, 2500, 4000, 10000, 16000)

volume_guilds = {}
registered_nodes = []

logging = logger.Logger().get("utils.base_utils")

def show_figlet(text, color1="#E50AF5", color2="#2CFBF7"):
    colorama.init(autoreset=False)
    font = pyfiglet.Figlet(font="larry3d", direction="left-to-right", justify=True, width=400).renderText(text)
    print(colorama.Fore.CYAN + BOLD_ON + font + BOLD_OFF)
    colorama.init(autoreset=True)
    return font

def inittable(bot_version, authors, python_version, dpy_version, wavelink_version, copy, font_info):
    fontlen = len(font_info.splitlines()[2])
    print("=*"*(fontlen//2))
    contents = [("Version", bot_version),("Authors", authors),("Python", python_version),("discord.py", dpy_version),("Wavelink", wavelink_version), ("Copyright", copy)]
    longest_content = len(max(contents, key=lambda con: len(con[0]))[0])
    padding = (fontlen//2)-longest_content
    for content in contents:
        print(f"{' '*padding}{' '*(longest_content-len(content[0]))}{content[0]} : {content[1]}")

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

def convert_to_double(val):
    if val < 10:
        return "0" + str(val)
    return val

def get_length(dur):
    lm, ls = divmod(dur,60)
    lh, lm = divmod(lm, 60)
    ls, lm, lh = math.floor(ls), math.floor(lm), math.floor(lh)
    if lh >= 1:
        lm = convert_to_double(lm)
    ls = convert_to_double(ls)
    return f"{str(lh) + ':' if lh != 0 else ''}{str(lm)}:{str(ls)}"

def double_to_int(value):
    value = str(value)
    if value.startswith("0") and len(value) >= 2:
        return int(value[1:])
    return int(value)

filters = {
    wavelink.Karaoke: "Karaoke",
    wavelink.Timescale: "Timescale",
    wavelink.Tremolo: "Tremolo",
    wavelink.Vibrato: "Vibrato",
    wavelink.Rotation: "Rotation",
    wavelink.Distortion: "Distortion",
    wavelink.ChannelMix: "channel_mix",
    wavelink.LowPass: "low_pass"
}

def filter_to_string(cls):
    try:
        return filters[cls]
    except KeyError:
        return False

def string_to_filter(string):
    _filters = list(filters.items())
    for k,v in _filters:
        if v == string:
            return k
    return False

def hide_cursor():
    print('\033[?25l', end="")

def show_cursor():
    print('\033[?25h', end="")

def clearscreen():
    _platform = platform.system().lower()
    if _platform == "windows":
        os.system("cls")
    elif _platform == "linux":
        os.system("clear")

def get_config():
    with open("data/bot-config.json", mode="r") as f:
        config = json.load(f)

    return config

def get_bot_token():
    return get_config()["bot"]["token"]

def get_lyrics_token():
    return get_config()["lyrics"]["genius-auth-token"]

def get_application_id():
    return int(get_config()["bot"]["application_id"])

hex_encoder = {
    0: "0", 1: "1", 2: "2", 3: "3", 4: "4",
    5: "5", 6: "6", 7: "7" ,8: "8", 9: "9",
    10: "A", 11: "B", 12: "C", 13: "D", 14: "E", 15: "F",
}

def int_to_hex(integer):
    res = ""
    while integer > 16:
        new_int, mod = divmod(integer,16)
        res += str(hex_encoder[mod])
        integer = new_int
    return res.lower()

def getid(label_to_encode):
    generated = str(uuid.uuid5(uuid.NAMESPACE_URL, label_to_encode))
    # remove hyphens and not-numeral characters
    res = ""
    for g in generated:
        if g.isdigit():
            res += str(g)

    res = int_to_hex(int(res))
    if len(res) < 15:
        res = ('0' * (15-len(res))) + res
    res = res[:15]
    return res

def get_latest_github_release():
    req = requests.get("https://raw.githubusercontent.com/konradsic/dj-cloudy/main/main.py").text.split("\n")
    for line in req:
        if line.startswith("__version__"):
            return line.split("=")[-1].strip(" \"")

def is_update_required():
    """
    Fetch latest release file from github and check if an necessary update is needed.
    """
    req = requests.get("https://raw.githubusercontent.com/konradsic/dj-cloudy/main/main.py").text.split("\n")
    for line in req:
        if line.startswith("REQUIRED_UPDATE"):
            required = line.split("=")[-1].strip(" \"")
            if required == "True":
                return True
            return False
    return False

def check_for_updates(current_version):
    logging.info("Checking for updates...")
    latest = get_latest_github_release()
    if str(latest) != str(current_version):
        logging.warn(f"You are using version {current_version} however version {latest} is available. Visit https://github.com/konradsic/dj-cloudy to download the latest version")
        if is_update_required():
            logging.critical(f"Version {current_version} is deprecated - you need to download version {latest} from the link above to use this bot. Your current version may not handle latest required standarts for the bot to work - thats why you need to update it")
            exit()
    else:
        logging.info(f"You are using the latest version -- {latest}")


def make_files():
    files = ["data/playlists.json", "data/settings.json"]
    for file in files:
        try:
            with open(file, 'r') as f:
                pass
        except:
            with open(file, 'w') as f:
                f.write("{}")
    return True

def load_logger_config():
    try:
        config = get_config()["logger"]
        level, file = config["level"], config["save_file"]
        level = logger.get_level_from_string(level)
        if level is None:
            logging.warn("Incorrect logging level was passed in config file, using default value (INFO)")
            return logger.LogLevels.INFO, file
        return level, file
    except:
        logging.error("Error while parsing logger config, using default config")
        return logger.LogLevels.INFO, "./bot-logs/bot.log"