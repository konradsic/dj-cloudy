import math
import os
import platform
from enum import Enum

import discord
import wavelink
import colorama
import json
import requests
import uuid
from . import logger
from .configuration import ConfigurationHandler
from .colors import BASE_COLOR

BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"

AUTHENTICATED_USERS = ["958029521565679646"] # list of authenticated users (of ID's)
AEQ_HZ_BANDS = (20, 40, 63, 100, 150, 250, 400, 450, 630, 1000, 1600, 2500, 4000, 10000, 16000)

volume_guilds = {}
registered_nodes = []

logging = logger.Logger().get("utils.base_utils")

def show_figlet():
    colorama.init(autoreset=False)
    font = r"""
 ____     _____      ____    ___                       __              
/\  _`\  /\___ \    /\  _`\ /\_ \                     /\ \             
\ \ \/\ \\/__/\ \   \ \ \/\_\//\ \     ___   __  __   \_\ \  __  __    
 \ \ \ \ \  _\ \ \   \ \ \/_/_\ \ \   / __`\/\ \/\ \  /'_` \/\ \/\ \   
  \ \ \_\ \/\ \_\ \   \ \ \L\ \\_\ \_/\ \L\ \ \ \_\ \/\ \L\ \ \ \_\ \  
   \ \____/\ \____/    \ \____//\____\ \____/\ \____/\ \___,_\/`____ \ 
    \/___/  \/___/      \/___/ \/____/\/___/  \/___/  \/__,_ /`/___/> \
                                                                /\___/
                                                                \/__/
    """
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

def limit_string_to(string: str, limit: int) -> str:
    # we add [...] if its larger than limit-4 
    # (4 for safety reasons)
    if len(string) >= limit-1:
        string = string[:(limit-4)] + "..."
    return string

def get_nodes():
    return wavelink.NodePool.get_connected_node()

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
    dur = round(dur/1000)
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

def is_update_required(current_version, min_version):
    """
    (new) Check if version is higher or equal to min_version, else throw error
    """
    current_version = tuple(current_version.split("-")[1].split(".")) # tuple
    min_version = tuple(min_version.split("."))        # tuple
    
    # from highest to lowest
    if current_version[0] < min_version[0]:
        return True
    if current_version[1] < min_version[1]:
        return True
    if current_version[2] < min_version[2]:
        return True
    # for example, current = (1,0,5) min = (1,0,0) 
    # first - equal so continue, second - equal so continue, third - larger so no update required
    # second example - current = (1,0,0) min = (1,0,5)
    # on third it will return True, so update is required
    return False

def check_for_updates(current_version, min_version):
    logging.info("Checking for updates...")
    latest = get_latest_github_release()
    if str(latest) != str(current_version):
        logging.warn(f"You are using version {current_version} however version {latest} is available. Visit https://github.com/konradsic/dj-cloudy to download the latest version")
        if is_update_required(current_version, min_version):
            logging.critical(f"Version {current_version} may not handle latest support for liblaries, audio or other features so it's marked as deprecated. Please upgrade your version atleast to v.{min_version}")
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
        level, file = config["level"], config["logs_directory"]
        level = logger.get_level_from_string(level)
        if level is None:
            logging.warn("Incorrect logging level was passed in config file, using default value (INFO)")
            return logger.LogLevels.INFO, file
        return level, file
    except:
        logging.error("Error while parsing logger config, using default config")
        return logger.LogLevels.INFO, "bot-logs"
    
async def djRole_check(interaction: discord.Interaction, logger: logger.Logger):
    djRole = ConfigurationHandler(id=str(interaction.guild.id), user=False).data.get("djRole")["value"]
    if not djRole: return True # no role - no reqs
    
    djRole = str(djRole) # to make sure this is a string
    user_role_ids = [str(role.id) for role in interaction.user.roles]
    if djRole in user_role_ids:
        return True
    # ^ if True returned - check passed
    # failed auth interaction response
    try:
        user_vc_len = len(interaction.user.voice.channel.members)
        if not (user_vc_len == 2):
            role = interaction.guild.get_role(int(djRole))
            logger.error(f"DJ Auth failed (id: {interaction.user.id}, required role {role}) ")
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You need to have the {role.mention} in order to use DJ commands", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
    except Exception as e: 
        logger.error(f"DJ Auth failed (id: {interaction.user.id}, exception {e.__class__.__name__}: {str(e)}) ")
        embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to check for DJ role permissions, try again", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
