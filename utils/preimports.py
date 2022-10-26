from imp import init_builtin
from cogs.eq_and_filters import EqualizersCog, FiltersCog
from cogs.play import PlayCommand
from cogs.playlist_adapter import PlaylistGroupCog
from cogs.vc_handle import VC_Handler

from discord.ext.commands import Bot

# preinit
preinitialized_cogs = (
    EqualizersCog(Bot),
    FiltersCog(Bot),
    PlayCommand(Bot),
    PlaylistGroupCog(Bot),
    VC_Handler(Bot)
)