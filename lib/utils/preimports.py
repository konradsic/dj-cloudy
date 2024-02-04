# preimport cogs to register loggers
from discord.ext.commands import Bot

from cogs.config_commands import ConfigCog
from cogs.eq_and_filters import EqualizersCog, FiltersCog
from cogs.events import EventHandlerCog
from cogs.play import PlayCommand
from cogs.playlists import PlaylistGroupCog
from cogs.queue_commands import QueueCommands
from cogs.seeking import SeekAndRestartCog
from cogs.spotify import SpotifyExtensionCog
from cogs.vc_handle import VC_Handler

# preinit
preinitialized_cogs = (
    EqualizersCog(Bot),
    FiltersCog(Bot),
    PlayCommand(Bot),
    PlaylistGroupCog(Bot),
    VC_Handler(Bot),
    SeekAndRestartCog(Bot),
    SpotifyExtensionCog(Bot),
    QueueCommands(Bot),
    ConfigCog(Bot),
    EventHandlerCog(Bot)
)
