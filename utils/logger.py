import datetime

from colorama import Fore, Style, init
init(autoreset=True)

loggers = {}

config = {
    "longest_process_len": 0,
    "logging-path": "bot-logs/test.txt"
}

class Logger:
    """
    Logger
    ----------------------------

    Logger is a class that provides logging at the next level.
    """

    def __init__(self, longest_process_name: str="None", name: str=None):
        if len(longest_process_name) > config["longest_process_len"]:
            config["longest_process_len"] = len(longest_process_name)
        if name:
            self.name = name
            loggers[self.name] = self

    def get(self, logger_name: str=None):
        if not logger_name:
            raise ValueError("You must provide a logger name to get it")
        
        try:
            logger = loggers[logger_name]
            self.name = logger.name
        except:
            raise ValueError("No logger found with name '{}'".format(logger_name))

        return logger

    def log(self, process_name, message: str=None):
        """
        Prints in debugging format. 
        ----------------------------------------------------------------
        Use info(), warn(), error() or critical() if you want to log any other type
        
        Parameters:
        ------------
        `process_name`: str - name of the process
        `message`: str - message you want to log

        """
        longest_logger_name = longest_logger_name = len(max(list(loggers.keys()), key=lambda x: len(x)))

        color = Fore.BLUE
        len_process = config["longest_process_len"]
        
        message = f"{Style.DIM}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} {Style.RESET_ALL}[{Fore.MAGENTA}{process_name}{Fore.WHITE}{' '*(len_process-len(process_name))}] {Fore.CYAN}{self.name}{Fore.WHITE}{' '*(longest_logger_name-len(self.name))} {Style.BRIGHT}{color}\033[1mDEBUG\033[0m{Style.RESET_ALL}{Fore.WHITE} -- {message}"

        print(message)

        with open(config["logging-path"], mode="r") as f:
            content = f.read()
        with open(config["logging-path"], mode="w") as file:
            file.write(content + message + "\n")

    def info(self, process_name, message: str=None):
        """
        Prints in informative context
        ----------------------------------------------------------------
        
        Parameters:
        ------------
        `process_name`: str - name of the process
        `message`: str - message you want to log

        """
        longest_logger_name = len(max(list(loggers.keys()), key=lambda x: len(x)))
        color = Fore.GREEN
        len_process = config["longest_process_len"]
        
        message = f"{Style.DIM}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} {Style.RESET_ALL}[{Fore.MAGENTA}{process_name}{Fore.WHITE}{' '*(len_process-len(process_name))}] {Fore.CYAN}{self.name}{Fore.WHITE}{' '*(longest_logger_name-len(self.name))} {Style.BRIGHT}{color}\033[1mINFO\033[0m{Style.RESET_ALL}{Fore.WHITE}  -- {message}"

        print(message)

        with open(config["logging-path"], mode="r") as f:
            content = f.read()
        with open(config["logging-path"], mode="w") as f:
            f.write(content + message + "\n")

    def warn(self, process_name, message: str=None):
        """
        Prints a warning 
        ----------------------------------------------------------------
        
        Parameters:
        ------------
        `process_name`: str - name of the process
        `message`: str - message you want to log

        """
        longest_logger_name = len(max(list(loggers.keys()), key=lambda x: len(x)))

        color = Fore.YELLOW
        len_process = config["longest_process_len"]
        
        message = f"{Style.DIM}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} {Style.RESET_ALL}[{Fore.MAGENTA}{process_name}{Fore.WHITE}{' '*(len_process-len(process_name))}] {Fore.CYAN}{self.name}{Fore.WHITE}{' '*(longest_logger_name-len(self.name))} {Style.BRIGHT}{color}\033[1mWARN\033[0m{Style.RESET_ALL}{Fore.WHITE}  -- {message}"

        print(message)

        with open(config["logging-path"], mode='r') as f:
            content = f.read()
        with open(config["logging-path"], mode="w") as f:
            f.write(content + message + "\n")

    def error(self, process_name, message: str=None):
        """
        Prints an error 
        ----------------------------------------------------------------
        
        Parameters:
        ------------
        `process_name`: str - name of the process
        `message`: str - message you want to log

        """
        longest_logger_name = len(max(list(loggers.keys()), key=lambda x: len(x)))

        color = Fore.RED
        len_process = config["longest_process_len"]
        
        message = f"{Style.DIM}{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} {Style.RESET_ALL}[{Fore.MAGENTA}{process_name}{Fore.WHITE}{' '*(len_process-len(process_name))}] {Fore.CYAN}{self.name}{Fore.WHITE}{' '*(longest_logger_name-len(self.name))} {Style.BRIGHT}{color}\033[1mERROR\033[0m{Style.RESET_ALL}{Fore.WHITE} -- {message}"

        print(message)

        with open(config["logging-path"], mode="r") as f:
            content = f.read()
        with open(config["logging-path"], mode="w") as f:
            f.write(content + message + "\n")

    def critical(self, process_name, message: str=None):
        """
        CRITICAL ERROR!
        ----------------------------------------------------------------
        
        Parameters:
        ------------
        `process_name`: str - name of the process
        `message`: str - message you want to log

        """
        longest_logger_name = len(max(list(loggers.keys()), key=lambda x: len(x)))

        len_process = config["longest_process_len"]
        
        message = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]} [{process_name}{' '*(len_process-len(process_name))}] {self.name}{Fore.WHITE}{' '*(longest_logger_name-len(self.name))} CRITICAL -- {message}"

        print(message)

        with open(config["logging-path"], mode="r") as f:
            content = f.read()
        with open(config["logging-path"], mode="w") as f:
            f.write(content + message + "\n")

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