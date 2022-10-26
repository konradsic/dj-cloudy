import datetime
from utils.base_utils import BOLD_ON, BOLD_OFF

from colorama import Fore, Style, init
init(autoreset=True)

loggers = {}

config = {
    "longest_cls_len": 0,
    "logging-path": "bot-logs/bot.log"
}

log_colors = {
    "DEBUG": Fore.BLUE,
    "INFO": Fore.GREEN,
    "WARN": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED
}

def remove_underscores(label):
    if label.startswith("__") and label.endswith("__"):
        return label[2:-2]
    return label

def LoggerApplication(cls):
    def wrapper(*args, **kwargs):
        fullpath = remove_underscores(cls.__module__) + "." + cls.__name__
        clen = len(fullpath)
        if clen > config["longest_cls_len"]:
            config["longest_cls_len"] = clen
        return cls(*args, **kwargs, logger=Logger(name=fullpath))
    return wrapper

def register_cls(cls):
    leng = len(cls)
    if leng > config["longest_cls_len"]:
        config["longest_cls_len"] = leng


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
        longest_logger_name = config["longest_cls_len"]
        msg = ""
        if log_type == "CRITICAL":
            msg = f"{Fore.RED}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} {self.name}{' '*(longest_logger_name+1-len(self.name))}CRITICAL : {message}"
        else:
            msg = f"{Style.DIM}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]}{Style.RESET_ALL} {Fore.CYAN}{self.name}{' '*(longest_logger_name+1-len(self.name))}{color}{BOLD_ON}{log_type}{BOLD_OFF}{' '*(5-len(log_type))}{Fore.WHITE}{Style.RESET_ALL} : {message}"
        print(msg)

        with open(config["logging-path"], mode="r+") as _: pass
        with open(config["logging-path"], mode="r") as content_reader:
            content = content_reader.read()
        with open(config["logging-path"], mode="w") as writer:
            writer.write(content+msg+"\n")
        return True

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