import discord
from discord.ext import commands
from utils import logger

log_instance = logger.Logger().get("utils.errors")

class UnhandledBotException(Exception):
    def __init__(self,error_name=None, string=None):
        if string:
            log_instance.error("", error_name,string)
        else:
            log_instance.error("", error_name, "Unhandled exception occured")

logger.register_func("AlreadyConnectedToVoice")
logger.register_cls("utils.errors")

# ERROR CLASSES
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

class NoVoiceChannel(UnhandledBotException): 
    def __init__(self, string=None):
        super().__init__(error_name = self.__class__.__name__, string = string or "No voice channel is available")
