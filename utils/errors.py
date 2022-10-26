import discord
from discord.ext import commands
from utils import logger

class UnhandledBotException(Exception):
    def __init__(self, logger: logger.Logger, string: str=None):
        if string:
            logger.error(string)
        else:
            logger.error("Unhandled exception occured")

# ERROR CLASSES
@logger.LoggerApplication
class NotConnectedToVoice(UnhandledBotException):
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string=string or "The bot/user is not connected to a voice channel")

@logger.LoggerApplication
class AlreadyConnectedToVoice(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "The bot is already connected to a voice channel")

@logger.LoggerApplication
class QueueIsEmpty(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "The queue is empty")

@logger.LoggerApplication
class NoTracksFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "No tracks were found")

@logger.LoggerApplication
class NoPlayerFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "No players available for this guild")

@logger.LoggerApplication
class NoVoiceChannel(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "No voice channel is available")

@logger.LoggerApplication
class NoPlaylistFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "No playlist with given name was found")

@logger.LoggerApplication
class PlaylistCreationError(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, sstring = string or "Creating playlist {null} failed")

@logger.LoggerApplication
class PlaylistGetError(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "Failed to get playlist (no further info)")

@logger.LoggerApplication
class PlaylistRemoveError(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger):
        super().__init__(logger=logger, string = string or "Failed to delete playlist/song of playlist {null}")