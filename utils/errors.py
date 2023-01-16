import discord
from discord.ext import commands
from utils import logger

# we will think about it later
loggers = [
    logger.Logger().get("utils.errors.NotConnectedToVoice"),
    logger.Logger().get("utils.errors.AlreadyConnectedToVoice"),
    logger.Logger().get("utils.errors.QueueIsEmpty"),
    logger.Logger().get("utils.errors.NoTracksFound"),
    logger.Logger().get("utils.errors.NoPlayerFound"),
    logger.Logger().get("utils.errors.NoVoiceChannel"),
    logger.Logger().get("utils.errors.NoPlaylistFound"),
    logger.Logger().get("utils.errors.PlaylistCreationError"),
    logger.Logger().get("utils.errors.PlaylistGetError"),
    logger.Logger().get("utils.errors.PlaylistRemoveError"),
    logger.Logger().get("utils.errors.NoPlaylistFound")
]

class UnhandledBotException(Exception):
    def __init__(self, logger: logger.Logger, string: str=None):
        if string:
            logger.error(string)
        else:
            logger.error("Unhandled exception occured")

# ERROR CLASSES
class NotConnectedToVoice(UnhandledBotException):
    def __init__(self, string=None, *, logger: logger.Logger=loggers[0]):
        super().__init__(logger=logger, string=string or "The bot/user is not connected to a voice channel")

class AlreadyConnectedToVoice(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[1]):
        super().__init__(logger=logger, string = string or "The bot is already connected to a voice channel")

class QueueIsEmpty(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[2]):
        super().__init__(logger=logger, string = string or "The queue is empty")

class NoTracksFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[3]):
        super().__init__(logger=logger, string = string or "No tracks were found")

class NoPlayerFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[4]):
        super().__init__(logger=logger, string = string or "No players available for this guild")

class NoVoiceChannel(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[5]):
        super().__init__(logger=logger, string = string or "No voice channel is available")

class NoPlaylistFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[6]):
        super().__init__(logger=logger, string = string or "No playlist with given name was found")

class PlaylistCreationError(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[7]):
        super().__init__(logger=logger, sstring = string or "Creating playlist {null} failed")

class PlaylistGetError(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[8]):
        super().__init__(logger=logger, string = string or "Failed to get playlist (no further info)")

class PlaylistRemoveError(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[9]):
        super().__init__(logger=logger, string = string or "Failed to delete playlist/song of playlist {null}")

class NoPlaylistFound(UnhandledBotException): 
    def __init__(self, string=None, *, logger: logger.Logger=loggers[10]):
        super().__init__(logger=logger, string = string or "Playlist not found")