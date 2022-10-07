from colorama import init, Fore, Style
from enum import Enum
import datetime as dt

init(autoreset=False)

class LoggingType(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3
    CRITICAL = 4

class LoggerInstance:
    """
    Represents a logging instance.

    Parameters
    ================
        default_logging_type : LoggingType - If `log_type` of `LoggerInstance.log` is `None` then it's bound to this variable
        caller : str - default caller for this instance.
    """
    def __init__(self, default_logging_type, caller):
        date = dt.datetime.utcnow().strftime("%y-%m-%d")
        with open(f"bot-logs/{date}.log", mode="w") as _:
            pass
        self.date = date
        self.default_type = default_logging_type
        self.caller = caller

    @property
    def get_caller(self): return self.caller 
    
    def set_caller(self, caller):
        self.caller = caller

    def set_logging_type(self, logging_type):
        self.default_type = logging_type

    def log(self, log_function : str, log_message: str, log_type: str=None):
        log_type = log_type or self.default_type
        caller = self.caller
        if not log_type:
            log_type = self.default_type

        date = dt.datetime.utcnow().strftime("%y-%m-%d %H:%M:%S.%f")[:-3]
        if log_type == LoggingType.INFO:
            clr = Fore.GREEN
            msg = "INFO"
        if log_type == LoggingType.WARN:
            clr = Fore.YELLOW
            msg = "WARN"
        if log_type == LoggingType.ERROR:
            clr = Fore.RED
            msg = "ERROR"
        if log_type == LoggingType.CRITICAL:
            formatted = f"{Fore.RED}CRITICAL {date} [{log_function}] {caller} -- {log_message}"
            formatted_without_colors = f"CRITICAL {date} [{log_function}] {caller} -- {log_message}"
            print(formatted)
            with open(f"bot-logs/{self.date}.log", mode="r") as f:
                content = f.read()
            with open(f"bot-logs/{self.date}.log", mode="w") as f:
                f.write(content + formatted_without_colors + "\n")
            return
        formatted = f"{Style.DIM}{Fore.WHITE}{date} [{Style.RESET_ALL}{Fore.MAGENTA}{log_function} {clr}{msg}{Fore.WHITE}{Style.DIM}]{Style.RESET_ALL} {Fore.CYAN}{caller}{Fore.WHITE} {Style.DIM}--{Style.RESET_ALL} {log_message}"
        formatted_without_colors = f"{date} [{log_function} {msg}] {caller} -- {log_message}"
        print(formatted)
        with open(f"bot-logs/{self.date}.log", mode="r") as f:
            content = f.read()
        with open(f"bot-logs/{self.date}.log", mode="w") as f:
            f.write(content + formatted_without_colors + "\n")
