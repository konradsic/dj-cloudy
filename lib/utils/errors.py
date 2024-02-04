import discord
from discord.ext import commands
from ..logger import logger

class DJCloudyException(Exception):
    def __init__(self, logger: logger.Logger, string: str=None):
        if string:
            logger.error(string)
        else:
            logger.error("Unhandled exception occured")

# ERROR CLASSES
# NOTE: Player errors
class NotConnectedToVoice(DJCloudyException):
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NotConnectedToVoice")):
        super().__init__(logger=logger, string=string or "The bot/user is not connected to a voice channel")

class AlreadyConnectedToVoice(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.AlreadyConnectedToVoice"),):
        super().__init__(logger=logger, string = string or "The bot is already connected to a voice channel")

class NoVoiceChannel(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoVoiceChannel")):
        super().__init__(logger=logger, string = string or "No voice channel is available")

# NOTE: Queue/Track errors
class QueueIsEmpty(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.QueueIsEmpty")):
        super().__init__(logger=logger, string = string or "The queue is empty")

class NoTracksFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoTracksFound")):
        super().__init__(logger=logger, string = string or "No tracks were found")

class NoPlayerFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoPlayerFound")):
        super().__init__(logger=logger, string = string or "No players available for this guild")

class NoPreviousTrack(DJCloudyException):
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoPreviousTrack")):
        super().__init__(logger=logger, string = string or "No previous track in the queue")
        
class NoUpcomingTracks(DJCloudyException):
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoUpcomingTracks")):
        super().__init__(logger=logger, string = string or "No upcoming tracks in the queue")

# NOTE: Playlist errors
class NoPlaylistFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoPlaylistFound")):
        super().__init__(logger=logger, string = string or "No playlist with given name was found")

class PlaylistCreationError(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.PlaylistCreationError")):
        super().__init__(logger=logger, sstring = string or "Creating playlist {null} failed")

class PlaylistGetError(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.PlaylistGetError")):
        super().__init__(logger=logger, string = string or "Failed to get playlist (no further info)")

class PlaylistRemoveError(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.PlaylistRemoveError")):
        super().__init__(logger=logger, string = string or "Failed to delete playlist/song of playlist {null}")

class NoPlaylistFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.NoPlaylistFound")):
        super().__init__(logger=logger, string = string or "Playlist not found")


# NOTE: Configuration errors
class DefaultProfileNotFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.DefaultProfileNotFound")):
        super().__init__(logger=logger, string = string or "Default profile for given value was not found (check data folder for default profiles)")

class KeyDoesNotExist(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.KeyDoesNotExist")):
        super().__init__(logger=logger, string = string or "Configuration key does not exist.")

class IncorrectValueType(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.IncorrectValueType")):
        super().__init__(logger=logger, string = string or "Incorrect value type")

class UserNotFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.UserNotFound")):
        super().__init__(logger=logger, string = string or "Configuration for given user was not found")

class AuthFailed(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.AuthFailed")):
        super().__init__(logger=logger, string = string or "Authentication failed, aborting...")


# NOTE: Cache errors        
class CacheExpired(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.CacheExpired")):
        super().__init__(logger=logger, string = string or "Cache entry has expired")
        
class CacheNotFound(DJCloudyException): 
    def __init__(self, string=None, *, logger: logger.Logger=logger.Logger().get("utils.errors.CacheNotFound")):
        super().__init__(logger=logger, string = string or "Cache entry was not found")