import datetime
import json
from colorama import Fore, Style, init
import os
import unicodedata

init(autoreset=True)

BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"
class LogLevels:
    DEBUG = 1
    INFO = 5
    WARN = 20
    ERROR = 50
    CRITICAL = 1000 # highest

loggers = {}

config = {
    "longest_cls_len": 0,
    "logging-path": "bot-logs/bot.log",
    "logging_level": LogLevels.INFO,
    "optimal_leng": 35
}

log_colors = {
    "DEBUG": Fore.BLUE,
    "INFO": Fore.GREEN,
    "WARN": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED
}

BYTE_CONV_RATES = {
    ("B", "B"): 1,
    ("B", "KB"): 1000,
    ("KB", "MB"): 1000,
    ("MB", "GB"): 1000,
    ("B", "MB"): 1000**2,
    ("B", "GB"): 1000**3
}

def unicode_filter(string: str):
    return str(unicodedata.normalize("NFKD", string).encode("ascii", "ignore"))

def fit_logger_cls(cls_name, length):
    if len(cls_name) <= length: return cls_name
    # split parts and compose current class name
    parts = cls_name.split(".")    
    composed = "".join(part + "." for part in parts[:-1]) + parts[-1]
    current_idx = 0
    # iterate over until it's smaller than length
    while len(composed) > length:
        parts[current_idx] = parts[current_idx][0]
        composed = "".join(part + "." for part in parts[:-1]) + parts[-1]
        current_idx += 1
    return composed

def preinit_logs():
    # config
    with open("./data/bot-config.json", mode="r") as f:
        data = json.load(f)
    if not (data.get("extraConfig", {}).get("logger.formatFilesUsingDatetime")):
        try:
            with open(config['logging-path'], 'r') as f: pass
        except:
            try:
                with open(config['logging-path'], 'w') as f: pass
            except:
                print("[CRITICAL] Directory you are trying to create the log file does not exist. Please create a directory for the log file.")

def set_level(level):
    try:
        config["logging_level"] = level
    except:
        raise ValueError("Invalid logging level")

def get_level():
    return getattr(LogLevels, config["logging_level"], None)

def get_level_from_string(level):
    return getattr(LogLevels, level, None)

def is_level_logged(level):
    if level < config["logging_level"]:
        return False
    return True

def remove_underscores(label):
    if label.startswith("__") and label.endswith("__"):
        return label[2:-2]
    return label

def weight(x):
    try:
        # get weight from file name
        components = x.strip(".log").split("-")
        weight = 10000 * int(components[2]) + 100 * int(components[1]) + int(components[0])
        return weight
    except:
        return -1

def dir_size(dir_):
    size = 0
    with os.scandir(dir_) as files:
        for entry in files:
            if entry.is_file():
                size += entry.stat().st_size
            elif entry.is_dir():
                size += dir_size(entry.path)
    return size

def convert_bytes(size, fmt, goal):
    conv = BYTE_CONV_RATES[(fmt, goal)]
    return (size / conv, goal)

def save_logs(msg):
    msg = unicode_filter(msg)
    path = config['logging-path']
    # get directory
    log_dir = path.split("/")[0]
    # get format from config
    with open("./data/bot-config.json", mode="r") as f:
        data = json.load(f)
    extras = data.get("extraConfig", {})
    limit = extras.get("logger.limitLogsTo")
    fmt = extras.get("logger.formatFilesUsingDatetime")
    if fmt:
        # open a file corresponding to the current date
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        file_format = date + ".log"
        content = ""
        try:
            with open(log_dir + "/" + file_format, mode="r") as f:
                content = f.read()
        except: pass
        with open(log_dir + "/" + file_format, mode="w") as f:
            f.write(content + msg + "\n")
    if limit:
        lmt, byte = limit
        # sort files using a custom weight for sorting
        # ! weight = 1000Y + 10M + D
        filenames = []
        for _,_,files in os.walk(log_dir):
            filenames.extend(files)
        filenames = sorted(filenames, key=lambda x: weight(x))
        # get size of files
        sizes = dir_size(log_dir)
        # check if over limit
        sizes = convert_bytes(sizes, "B", byte)
        if sizes[0] > float(int(lmt)):
            # delete files until limit is not over
            while sizes[0] > float(int(lmt)):
                os.remove(filenames[0])
                del filenames[0]
                sizes = convert_bytes(dir_size(log_dir), "B", byte)

def optimal_length(string, before, leng, err):
    if leng-err <= len(string) <= leng+err:
        return len(string)
    return before

# @decorator
def LoggerApplication(cls):
    def wrapper(*args, **kwargs):
        fullpath = remove_underscores(cls.__module__) + "." + cls.__name__
        clen = len(fullpath)
        if config["optimal_leng"] == 35:
            shorted = fit_logger_cls(fullpath, 38)
            origin_opt = optimal_length(fullpath, 35, 35, 3)
            shorted_opt = optimal_length(shorted, 35, 35, 3)
            # check if matched
            if origin_opt == clen: config["optimal_leng"] = origin_opt
            if shorted_opt == len(shorted): config["optimal_leng"] = shorted_opt
        return cls(*args, **kwargs, logger=Logger(name=fullpath))
    return wrapper

def register_cls(cls):
    clen = len(cls)
    if config["optimal_leng"] == 35:
        shorted = fit_logger_cls(cls, 38)
        origin_opt = optimal_length(cls, 35, 35, 3)
        shorted_opt = optimal_length(shorted, 35, 35, 3)
        # check if matched
        if origin_opt == clen: config["optimal_leng"] = origin_opt
        if shorted_opt == len(shorted): config["optimal_leng"] = shorted_opt


class Logger:
    """
    Logger
    ----------------------------

    Logger is a class that provides logging at the next level.
    """

    def __init__(self, name: str=None):
        self.name = "null"
        if name:
            self.name = name
            loggers[self.name] = self
        if len(self.name) > config["longest_cls_len"]:
            config["longest_cls_len"] = len(self.name)

    def get(self, logger_name: str=None):
        if not logger_name:
            raise ValueError("You must provide a logger name to get it")
        
        try:
            logger = loggers[logger_name]
        except:
            try:
                self.name = logger_name
                if len(self.name) > config["longest_cls_len"]:
                    config["longest_cls_len"] = len(self.name)
                loggers[self.name] = self
                return self
            except:
                raise ValueError("No logger found with name '{}'".format(logger_name))

        return logger

    # logging part, yay
    def _log(self, log_type, message):
        color = log_colors[log_type]
        longest_logger_name = config["optimal_leng"]
        msg = ""
        fit = fit_logger_cls(self.name, config['optimal_leng'])
        if log_type == "CRITICAL":
            msg = f"{Fore.RED}{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} {fit}{' '*(longest_logger_name+1-len(fit))}CRITICAL : {message}"
        else:
            msg = f"{Style.DIM}{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]}{Style.RESET_ALL} {Fore.CYAN}{fit}{' '*(longest_logger_name+1-len(fit))}{color}{BOLD_ON}{log_type}{BOLD_OFF}{' '*(5-len(log_type))}{Fore.WHITE}{Style.RESET_ALL} : {message}"
        if is_level_logged(get_level_from_string(log_type)):
            print(msg)
            save_logs(msg)

    def debug(self, message):
        self._log("DEBUG", message)
        
    def info(self, message):
        self._log("INFO", message)

    def warn(self, message):
        self._log("WARN", message)
    
    def error(self, message):
        self._log("ERROR", message)
    
    def critical(self, message):
        self._log("CRITICAL", message)


# print_logs: @deprecated

preinit_logs()