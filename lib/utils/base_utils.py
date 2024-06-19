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
from ..logger import logger
from .configuration import ConfigurationHandler
from ..ui.colors import BASE_COLOR
from ..ui import emoji

BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"

AUTHENTICATED_USERS = ["958029521565679646"] # list of authenticated users (of ID's)

volume_guilds = {}
registered_nodes = []

logging = logger.Logger().get("utils.base_utils")

def show_figlet():
    colorama.init(autoreset=False)
    font = r"""           
     _  _           _                 _
  __| |(_)      ___| | ___  _   _  __| |_   _
 / _` || |____ / __| |/ _ \| | | |/ _` | | | |
| (_| || |____| (__| | (_) | |_| | (_| | |_| |
 \__,_|/ |     \___|_|\___/ \__,_|\__,_|\__, |
      |__/                               |___/
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
    return wavelink.Pool.get_node()

progressbar_emojis = {
    "bar_left_nofill": emoji.PROGRESSBAR_LEFT_EMPTY.mention,
    "bar_left_fill": emoji.PROGRESSBAR_LEFT_FILL.mention,
    "bar_mid_fill": emoji.PROGRESSBAR_MID_FILL.mention,
    "bar_mid_halffill": emoji.PROGRESSBAR_MID_HALF.mention,
    "bar_mid_nofill": emoji.PROGRESSBAR_MID_EMPTY.mention,
    "bar_right_nofill": emoji.PROGRESSBAR_RIGHT_EMPTY.mention,
    "bar_right_fill": emoji.PROGRESSBAR_RIGHT_FILL.mention
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
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You need to have the {role.mention} role in order to use DJ commands", color=BASE_COLOR)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return False
    except Exception as e: 
        logger.error(f"DJ Auth failed (id: {interaction.user.id}, exception {e.__class__.__name__}: {str(e)}) ")
        embed = discord.Embed(description=f"<:x_mark:1028004871313563758> Failed to check for DJ role permissions, try again", color=BASE_COLOR)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return False

async def quiz_check(
    bot: discord.ext.commands.Bot, 
    interaction: discord.Interaction, 
    logger: logger.Logger
) -> bool:
    try:
        quiz_data = await bot.quiz_cache.get(str(interaction.guild.id))
    except:
        return True
    
    if quiz_data == {}:
        return True
    
    embed = discord.Embed(description=f"{emoji.XMARK.string} You cannot use this command during the music quiz!", color=BASE_COLOR)
    logger.error(f"{interaction.user.id} caught in 4K - cheating! (commands disabled during the quiz)")
    try:
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.followup.send(embed=embed)
        
    return False
