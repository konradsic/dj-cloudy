import discord
from discord.ext import commands
from utils import logger

ERROR = logger.LoggingType.ERROR

log_instance = logger.LoggerInstance(ERROR, "system.utils.errors")

class UnhandledBotException(Exception):
    def __init__(self,error_name=None, string=None):
        if string:
            log_instance.log(error_name,string)
        else:
            log_instance.log(error_name, "Unhandled exception occured")
    

# ERROR CLASSES
class TestException(UnhandledBotException): pass
class NotConnectedToVoice(UnhandledBotException):
    def __init__(self, string=None):
        super().__init__(error_name= self.__class__.__name__, string=string or "The bot/user is not connected to a voice channel")

class AlreadyConnectedToVoice(UnhandledBotException): 
    def __init__(self, string=None):
        super().__init__(error_name = self.__class__.__name__, string = string or "The bot is already connected to a voice channel")
class QueueIsEmpty(UnhandledBotException): 
    def __init__(self, string=None):
        super().__init__(error_name = self.__class__.__name__, string = string or "The queue is empty")
class NoTracksFound(UnhandledBotException): 
    def __init__(self, string=None):
        super().__init__(error_name = self.__class__.__name__, string = string or "No tracks were found")

class NoPlayerFound(UnhandledBotException): 
    def __init__(self, string=None):
        super().__init__(error_name = self.__class__.__name__, string = string or "No players available for this guild")
