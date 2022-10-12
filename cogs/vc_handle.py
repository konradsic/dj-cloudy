import datetime

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from music.core import MusicPlayer
from utils import help_utils, logger
from utils.colors import BASE_COLOR
from utils.run import running_nodes

logging = logger.Logger().get("cogs.vc_handle")

class VC_Handler(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.loop.create_task(self.start_nodes())
        self.node = None

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
                    if player.channel is not None:
                        embed = discord.Embed(description=f"<:pause_gradient_button:1028219593082286090> Playback paused because everybody left",color=BASE_COLOR)
                        await player.bound_channel.send(embed=embed)
                    player.paused_vc = True
        try:
            if len([m for m in after.channel.members if not m.bot]) >= 1:
                player = self.node.get_player(member.guild)
                if player is None: return
                if player.paused_vc == True:
                    await player.set_pause(False)
                    if player.bound_channel is not None:
                        embed = discord.Embed(description=f"<:play_button:1028004869019279391> Resuming playback...",color=BASE_COLOR)
                        await player.bound_channel.send(embed=embed)
                    player.paused_vc = False
        except: pass

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node):
        logging.info("on-wavelink-node-ready", f"Wavelink node `{node.identifier}` ready")
        self.node = node
        self.bot.node = node
        running_nodes.append(node)

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
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            embed = discord.Embed(description=f"<:channel_button:1028004864556531824> Connected to <#{channel.id}>", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            player.bound_channel = interaction.channel
        except Exception as e:
            logging.log("connect-command", f"Debug errors: {e.__class__.__name__} - {str(e)}")
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return
            

    @app_commands.command(name="disconnect", description="Disconnects from channel that bot is in")
    async def disconnect_command(self, interaction: discord.Interaction):
        try:
            player = self.node.get_player(interaction.guild)

            await player.disconnect()
            embed = discord.Embed(description=f"<:channel_button:1028004864556531824> Disconnected", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed)
            return


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("connect", "Connects to your voice channel", "Music: Base commands")
    help_utils.register_command("disconnect", "Disconnects from channel that bot is in", "Music: Base commands")
    await bot.add_cog(VC_Handler(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
