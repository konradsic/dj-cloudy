import discord
from discord import app_commands
from discord.ext import commands
import datetime
from system.utils.colors import BASE_COLOR
from system.music.core import MusicPlayer
from system.utils import logger
import wavelink

INFO = logger.LoggingType.INFO
WARN = logger.LoggingType.WARN
ERROR = logger.LoggingType.ERROR

logs = logger.LoggerInstance(INFO, "cogs.vc_handle")


class VC_Handler(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.loop.create_task(self.start_nodes())
        self.Node = None

    async def on_player_track_error(self, player):
        await player.advance()

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        await self.on_player_track_error(player)
    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player, track, error):
        await self.on_player_track_error(player)
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player, track, treshold):
        await self.on_player_track_error(player)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                is_bot_present = False
                for bot in [m for m in before.channel.members if m.bot]:
                    if str(bot.id) == "1024303533685751868": is_bot_present = True
                if is_bot_present:
                    try:
                        player = self.node.get_player(member.guild)
                    except:
                        return False
                    await player.set_pause(True)
                    await discord.utils.get(member.guild.text_channels, id=959091972549795893).send("Paused, everybody left")
                    player.paused_vc = True
        try:
            if len([m for m in after.channel.members if not m.bot]) >= 1:
                player = self.node.get_player(member.guild)
                if player.paused_vc == True:
                    await player.set_pause(False)
                    await discord.utils.get(member.guild.text_channels, id=959091972549795893).send("Resumed playback.")
        except: pass

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node):
        logs.log("VC_Handler.on_wavelink_node_ready", f"Wavelink node `{node.identifier}` ready")
        self.node = node
        self.bot.node = node

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "password": "youshallnotpass",
            }
        }

        for node in nodes.values():
            await wavelink.NodePool.create_node(bot=self.bot, **node)
            #logs.log(INFO,"VC_Handler.start_nodes", f"Node `{node}` created")

    @app_commands.command(name="connect",description="Connects to your voice channel")
    async def connect_command(self, interaction: discord.Interaction):
        try:
            channel = interaction.user.voice.channel
            await channel.connect(cls=MusicPlayer, self_deaf=True)
            await interaction.response.send_message(f"Connected to {channel.name}")
        except Exception as e:
            await interaction.response.send_message(f"You're not connected to a channel! (or maybe {e.__class__.__name__}: {str(e)})")
            return

    @app_commands.command(name="disconnect", description="Disconnects from channel that bot is in")
    async def disconnect_command(self, interaction: discord.Interaction):
        player = self.node.get_player(interaction.guild)

        await player.disconnect()

        await interaction.response.send_message("Disconnected")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(VC_Handler(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])