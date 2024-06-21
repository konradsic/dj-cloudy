# easily set up DJ Cloudy
import argparse
import os
import colorama
from colorama import Fore, Back, Style
import requests
import shutil
import json

LAVALINK_GITHUB_DOWNLOAD = "https://github.com/lavalink-devs/Lavalink/releases/download/4.0.6/Lavalink.jar"
LAVASRC_PLUGIN_GITHUB_DOWNLOAD = "https://github.com/topi314/LavaSrc/releases/download/4.1.1/lavasrc-plugin-4.1.1.jar"
YOUTUBE_PLUGIN_GITHUB_DOWNLOAD = "https://github.com/lavalink-devs/youtube-source/releases/download/1.3.0/youtube-plugin-1.3.0.jar"
font = r"""           
     _  _           _                 _
  __| |(_)      ___| | ___  _   _  __| |_   _
 / _` || |____ / __| |/ _ \| | | |/ _` | | | |
| (_| || |____| (__| | (_) | |_| | (_| | |_| |
 \__,_|/ |     \___|_|\___/ \__,_|\__,_|\__, |
      |__/                               |___/
"""

parser = argparse.ArgumentParser(prog="DJ Cloudy Setup", description="Easily set up DJ Cloudy to run on your local machine/server", epilog="Licensed under the MIT license, made with <3 by @konradsic")
parser.add_argument("-s", "--settings", action="store_true", help="Modify basic settings", default=False)
parser.add_argument("-u", "--update", action="store_true", help="Update Python dependencies, install Lavalink and plugins", default=False)
parser.add_argument("-n", "--nokeyboard", action="store_true", help="If passed, installation (NOT configuration) will not require pressing 'Enter'")
args = parser.parse_args()
kbd = args.nokeyboard

def download_file(url, path):
    print(Style.RESET_ALL + "Downloading...")
    r = requests.get(url)
    total_size = int(r.headers.get('content-length', 1))/(10 * 1024) # avoid zero-division errors
    
    with open(path, 'wb') as f:
        counter = 0
        for chunk in r.iter_content(chunk_size=10 * 1024):
            progress = counter/total_size
            print(f"Writing... {round(progress*100, 2)}% [{Fore.MAGENTA}{'#' * round(progress*30)}{Fore.WHITE}{Style.DIM}{'.' * (30-round(progress*30))}{Style.RESET_ALL}]", end="\r")
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
            counter += 1
    print(f"Writing... 100.00% [{Fore.MAGENTA}{'#' * 30}{Style.RESET_ALL}]", end="\n")
    return path

def flatten_dict(d: dict, sep='.') -> dict:
    flat_dict = {}
    stack = [((), d)]

    while stack:
        path, current = stack.pop()
        for k, v in current.items():
            new_path = path + (k,)
            if isinstance(v, dict):
                stack.append((new_path, v))
            else:
                flat_dict[sep.join(new_path)] = v

    return flat_dict

def unflatten_dict(d, sep='.'):
    result_dict = {}
    for key, value in d.items():
        parts = key.split(sep)
        d = result_dict
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return result_dict

colorama.init(autoreset=False)
print(Fore.CYAN + font)
colorama.init(autoreset=True)
print(Style.RESET_ALL + "Welcome to DJ Cloudy configuration. Here you can quickly install all required packages and configure everything necessary.\nPlease follow instructions that the program will give you to ensure that DJ Cloudy will be installed correctly.\nType required things and press 'Enter' after a prompt to continue the installation process")

def install_lavalink():
    print(Style.RESET_ALL + Back.MAGENTA + "[Installing Lavalink and plugins]")
    print(f"Install Lavalink v4.0.6 from {Style.BRIGHT}{Fore.MAGENTA}`{LAVALINK_GITHUB_DOWNLOAD}`{Style.RESET_ALL} [Y/Skip] ", end="")
    if not kbd: skip = input(Style.DIM).lower() in ["s", "skip"]
    if kbd: skip = False
    if not skip: # install lavalink
        download_file(LAVALINK_GITHUB_DOWNLOAD, "./Lavalink.jar")
    else:
        print(Style.RESET_ALL + "Skipping, assuming the file is already installed (because it's eseential for the bot to run correctly). If it's not please re-run this file")
    
    print(f"\nAttempting to create folder {Fore.MAGENTA}`plugins`{Fore.WHITE}...")
    try:
        os.mkdir("plugins")
        print("Folder created successfully")
    except:
        print("Folder already exists")
        
    print()
    print(f"Install LavaSrc plugin v4.1.1 from {Style.BRIGHT}{Fore.MAGENTA}`{LAVASRC_PLUGIN_GITHUB_DOWNLOAD}`{Style.RESET_ALL} [Y/Skip] ", end="")
    if not kbd: skip = input(Style.DIM).lower() in ["s", "skip"]
    if kbd: skip = False
    if not skip: # install lavalink
        download_file(LAVASRC_PLUGIN_GITHUB_DOWNLOAD, "./plugins/lavasrc-plugin-4.1.1.jar")
    else:
        print(Style.RESET_ALL + "Skipping, assuming the file is already installed (because it's eseential for the bot to run correctly). If it's not please re-run this file")
    
    print()
    print(Style.RESET_ALL + f"Install YouTube essential plugin v1.3.0 from {Style.BRIGHT}{Fore.MAGENTA}`{YOUTUBE_PLUGIN_GITHUB_DOWNLOAD}`{Style.RESET_ALL} [Y/Skip] ", end="")
    if not kbd: skip = input(Style.DIM).lower() in ["s", "skip"]
    if kbd: skip = False
    if not skip: # install lavalink
        download_file(YOUTUBE_PLUGIN_GITHUB_DOWNLOAD, "./plugins/youtube-plugin-1.3.0.jar")
    else:
        print(Style.RESET_ALL + "Skipping, assuming the file is already installed (because it's eseential for the bot to run correctly). If it's not please re-run this file")


def configure_lavalink():
    print(Style.RESET_ALL + "\n\n" + Back.YELLOW + "[Configure Lavalink]")
    print(f"Settings will be written to file {Fore.YELLOW}`./config/application.yml`{Fore.WHITE}. Remember that it's a basic configuration, essential to run DJ Cloudy")
    print(f"Most settings here are copied from bot configuration, you can enter other values if you want")
    print("If there is a value in [square brackets] it's a default value. Press 'Enter' to accept it or type your own value to overwrite it")
        
    with open("./config/application.example.yml", "r") as f:
        lavalink_conf = f.read()
        
    config = {
        "Lavalink server address": ["lavalink.nodes.MAIN.uri", "127.0.0.1", True],
        "Lavalink server port": ["lavalink.nodes.MAIN.uri", "2333", True],
        "Lavalink server password": ["lavalink.nodes.MAIN.password", "youshallnotpass", True],
        "Spotify client ID": ["extensions.spotify.client_id", "SPOTIFY CLIENT ID HERE", True],
        "Spotify client secret": ["extensions.spotify.client_secret", "SPOTIFY CLIENT SECRET HERE", True],
    }
    
    with open("./data/bot-config.json", "r") as f:
        bot_config = flatten_dict(json.load(f))
    
    for prompt, [jsonpath, key, accept_default] in config.items():
        default = bot_config[jsonpath]
        if jsonpath == "lavalink.nodes.MAIN.uri":
            addr, port = default.split("/")[-1].split(":")
            if "port" in prompt: # port
                default = port
            if "address" in prompt: # addr
                default = addr
        print(Style.RESET_ALL + f"{prompt} {Fore.GREEN}{'[' + default + ']' if accept_default else ''}{Fore.WHITE}: ", end="")
        data = input(Style.DIM)
        if data == "" and accept_default: data = default
        
        lavalink_conf = lavalink_conf.replace(key, data)
        
    with open("./config/application.yml", "w") as f:
        f.write(lavalink_conf)        
    
    print(Style.RESET_ALL + Style.BRIGHT + "\n\nConfiguration complete! To run the bot, open two terminal instances. In the first one run `java -jar Lavalink.jar`. It will start the Lavalink server, which is very importnat. To run the bot, in the second instance run `py launcher.py` or `python3 launcher.py` depending on your operating system and Python installation")

def update_deps():
    print(Style.RESET_ALL + Back.BLUE + "[Updating dependencies]")
    print("Update packages from `requirements.txt` [Y/Skip] ", end="")
    if not kbd: skip = input(Style.DIM).lower() in ["s", "skip"]
    if kbd: skip = False
    if not skip: os.system("pip install -r requirements.txt")

def configure_bot():
    print(Style.RESET_ALL + "\n\n" + Back.GREEN + "[Configure Bot]")
    print(f"Settings will be written to {Fore.GREEN}`./data/bot-config.json`{Fore.WHITE}. Note that this file contains more options to configure, this is {Style.BRIGHT}basic configuration{Style.RESET_ALL}")
    
    config_values = {
        "Discord bot token": "bot.token",
        "Discord application ID": "bot.application_id",
        "Support server ID": "bot.support-server-id",
        "Auto bug report channel": "bot.auto-bug-report-channel",
        "Genius API Token (for working lyrics)": "lyrics.genius-auth-token",
        "Spotify client ID": "extensions.spotify.client_id",
        "Spotify client secret": "extensions.spotify.client_secret",
        "Lavalink server URI (default: http://127.0.0.1:2333)": ["lavalink.nodes.MAIN.uri", "http://127.0.0.1:2333"],
        "Lavalink server password (default: youshallnotpass, this is the only password that works on local hosted lavalink servers)": ["lavalink.nodes.MAIN.password", "youshallnotpass"]
    }
    
    with open("./data/config.example.json", mode="r") as f:
        example_data = json.load(f)
        
    # flatten
    example_data = flatten_dict(example_data)
    # print(example_data)
    
    for display, path in config_values.items():
        print(f"{Style.RESET_ALL}[config] {display}: ", end="")
        value = input(Style.DIM)
        if isinstance(path, list):
            actual_path = path[0]
            default = path[1]
            if not value:
                value = default
        else:
            actual_path = path
             
        example_data[actual_path] = value
        
    print("\nSaving results...")
    with open("./data/bot-config.json", mode="w") as f:
        json.dump(unflatten_dict(example_data), f, indent=4)
    print("Basic bot configuration complete!")

if args.settings:
    configure_bot()
    configure_lavalink()
    
if args.update:
    update_deps()
    install_lavalink()
    
if not args.update and not args.settings:
    update_deps()
    install_lavalink()
    configure_bot()
    configure_lavalink()

