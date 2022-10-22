import datetime
from utils.base_utils import BOLD_ON, BOLD_OFF

from colorama import Fore, Style, init
init(autoreset=True)

loggers = {}

config = {
    "longest_func_len": 0,
    "longest_cls_len": 0,
    "logging-path": "bot-logs/test.txt"
}

log_colors = {
    "DEBUG": Fore.BLUE,
    "INFO": Fore.GREEN,
    "WARN": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED
}

def class_logger(cls):
    def wrapper(*args, **kwargs):
        clen = len(cls.__module__ + "." + cls.__name__)
        if clen > config["longest_cls_len"]:
            config["longest_cls_len"] = clen
        functions = dir(cls)
        for e in functions:
            if not (e.startswith("__") and e.endswith("__")):
                leng = len(e)
                if leng > config["longest_func_len"]:
                    config["longest_func_len"] = leng
        return cls(*args, **kwargs)
    return wrapper

def register_cls(cls):
    leng = len(cls)
    if leng > config["longest_cls_len"]:
        config["longest_cls_len"] = leng

def register_func(func):
    leng = len(func)
    if leng > config["longest_func_len"]:
        config["longest_func_len"] = leng


class Logger:
    """
    Logger
    ----------------------------

    Logger is a class that provides logging at the next level.
    """

    def __init__(self, name: str=None, *, func_len: int=0, cls_len: int=0):
        self.name = "null"
        if name:
            self.name = name
            loggers[self.name] = self
        self.flen = func_len or 1
        self.clen = (cls_len + len(self.name)) or 1

    def get(self, logger_name: str=None):
        if not logger_name:
            raise ValueError("You must provide a logger name to get it")
        
        try:
            logger = loggers[logger_name]
            self.name = logger.name
        except:
            raise ValueError("No logger found with name '{}'".format(logger_name))

        return logger

    # logging part, yay
    def _log(self, log_type, base, func, message):
        if len(func) > config["longest_func_len"]:
            config["longest_func_len"] = len(func)
        color = log_colors[log_type]
        len_process = config["longest_func_len"]
        longest_logger_name = config["longest_cls_len"]
        if self.flen > len_process:
            len_process = self.flen
        if self.clen > longest_logger_name:
            longest_logger_name = self.clen
        msg = ""
        clsfmt = f"{self.name}{'.' + base if base else ''}"
        if log_type == "CRITICAL":
            msg = f"{Fore.RED}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} [{func}{' '*(len_process-len(func))}] {clsfmt}{' '*(longest_logger_name+1-len(clsfmt))} CRITICAL - {message}"
        else:
            msg = f"{Style.DIM}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]}{Style.RESET_ALL} [{Fore.MAGENTA}{func}{' '*(len_process-len(func))}{Fore.WHITE}] {Fore.CYAN}{clsfmt}{' '*(longest_logger_name+1-len(clsfmt))} {color}{BOLD_ON}{log_type}{BOLD_OFF}{' '*(5-len(log_type))}{Fore.WHITE}{Style.RESET_ALL} - {message}"
        print(msg)

        with open(config["logging-path"], mode="r+") as _: pass
        with open(config["logging-path"], mode="r") as content_reader:
            content = content_reader.read()
        with open(config["logging-path"], mode="w") as writer:
            writer.write(content+msg+"\n")
        return True

    def debug(self, base, func, message):
        self._log("DEBUG", base, func, message)
        
    def info(self, base, func, message):
        self._log("INFO", base, func, message)

    def warn(self, base, func, message):
        self._log("WARN", base, func, message)
    
    def error(self, base, func, message):
        self._log("ERROR", base, func, message)
    
    def critical(self, base, func, message):
        self._log("CRITICAL", base, func, message)

#message = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} [{process_name}{' '*(len_process-len(process_name))}] {self.name}{Fore.WHITE}{' '*(longest_logger_name-len(self.name))} CRITICAL -- {message}"

def print_logs(history):
    """
    print_logs
    ------------
    Prints out logging file to given moment

    Parameters
    -------
    `history`:int - length of the history
    """

    with open(config["logging-path"], mode="r") as file:
        lines = file.readlines()[-history:]
        for line in lines:
            print(line.strip("\n"))