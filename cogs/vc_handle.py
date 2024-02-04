import asyncio
import datetime
import sys

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from wavelink.ext import spotify
from lib.utils import help_utils

from lib.music.core import MusicPlayer
from lib.logger import logger
from lib.utils.base_utils import get_config, djRole_check, quiz_check
from lib.ui.colors import BASE_COLOR
from lib.utils.configuration import ConfigurationHandler
from lib.utils.errors import NoPlayerFound
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType

logging = logger.Logger().get("cogs.vc_handle")

@logger.LoggerApplication
class VC_Handler(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger
        try:
            self.bot.loop.create_task(self.start_nodes())
        except:
            pass # preinitialized cog -- commands.Bot does not have a loop attr 
        self.node = None
        self._load_spotify_config()

    def _load_spotify_config(self) -> None:
        config = get_config()
        spotify_conf = config["extensions"]["spotify"]
        client, token = spotify_conf["client_id"], spotify_conf["client_secret"]
        self.spotify_config = {"client": client, "token": token}

    async def on_player_track_error(self, player, *, additional_info: dict):
        guild = additional_info.get('guild').id
        track = additional_info.get('track').title
        info = additional_info.get('info')
        self.logger.debug(f"Track {track} {info} #{guild} (calling player advance, queue position: {player.queue.position})")
        if not (info == None or info == "REPLACED"):
            await player.advance()
        
    
    @commands.Cog.listener()
    async def on_wavelink_track_event(self, payload):
        await self.on_player_track_error(payload.player, additional_info={
            "track": payload.track,
            "guild": payload.player.guild,
            "info": payload.reason,
        })
        
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload):
        await self.on_player_track_error(payload.player, additional_info={
            "track": payload.track,
            "guild": payload.player.guild,
            "info": payload.reason,
        })

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        config = ConfigurationHandler(id=member.guild.id, user=False)
        if not member.bot and ((after.channel is None) or (after.channel != before.channel)):
            if before.channel is not None:
                if not [m for m in before.channel.members if not m.bot]:
                    is_bot_present = False
                    # check if bot in vc
                    for m in list([m for m in before.channel.members if m.bot]):  
                        if str(m.id) == str(self.bot.user.id):
                            is_bot_present = True

                    if is_bot_present:
                        cont = True
                        try:
                            player = wavelink.NodePool.get_connected_node().get_player(member.guild.id)
                        except:
                            cont = False
                        if not player.paused_vc and cont:
                            await player.pause()
                            disconnect_after = config.data["inactiveTimeout"]["value"]
                            if player.channel is not None:
                                embed = ShortEmbed(description=f"<:pause_gradient_button:1028219593082286090> Playback paused because everybody left. Disconnecting in `{disconnect_after}min`")
                                await player.bound_channel.send(embed=embed)
                            player.paused_vc = True
                            # use inactiveTimeout config value to check if users are disconnected after time passes
                            # wait
                            await asyncio.sleep(disconnect_after*60)
                            # get channel
                            for channel in member.guild.voice_channels:
                                if str(channel.id) == str(before.channel.id):
                                    # check
                                    if not [m for m in before.channel.members if not m.bot]:
                                        await player.teardown()
                                        embed = ShortEmbed(description=f"<:channel_button:1028004864556531824> Disconnected due to inactivity. Start a new party using `/connect` or `/play`!")
                                        await player.bound_channel.send(embed=embed)
                            
        try:
            if len(list([m for m in member.voice.channel.members if not m.bot])) >= 1:
                player = wavelink.NodePool.get_connected_node().get_player(int(member.guild.id))
                if player is None: return
                if player.paused_vc == True:
                    await player.resume()
                    if player.bound_channel is not None:
                        embed = ShortEmbed(description=f"<:play_button:1028004869019279391> Resuming playback...")
                        await player.bound_channel.send(embed=embed)
                    player.paused_vc = False
        except Exception as e: self.logger.debug(f"{e.__class__.__name__}, {str(e)}, {member}")

        # check if bot has been disconnected:
        if str(member.id) == str(self.bot.user.id):
            try:
                if before.channel is None:
                    return
                player = self.node.get_player(member.guild.id)
                await player.disconnect()
                del player
                self.logger.info("Destroyed player at guild " + str(member.guild.id))
            except Exception as e:
                self.logger.error(f"on_voice_state_update:: {e.__class__.__name__}: {str(e)}")
        
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node):
        self.logger.info(f"Wavelink node `{node.id}` ready")
        self.node = node
        self.bot.node = node

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        config = get_config()
        try:
            nodes_data = config["lavalink"]["nodes"]
        except:
            self.logger.critical("Failed to load lavalink nodes data, aborting...")
            sys.exit(0)
        spotify_config = self.spotify_config
        nodes = []
        for node in nodes_data.items():
            node_id, data = node
            nodes.append(wavelink.Node(id=node_id, uri=data["uri"], password=data["password"], secure=data["secure"], use_http=True))
        try:
            await wavelink.NodePool.connect(client=self.bot, nodes=nodes, spotify=spotify.SpotifyClient(client_id=spotify_config["client"], client_secret=spotify_config["token"]))
        except:
            await wavelink.NodePool.connect(client=self.bot, nodes=nodes, spotify=spotify.SpotifyClient(client_id=spotify_config["client"], client_secret=spotify_config["token"]))
            

    @app_commands.command(name="connect",description="Connects to your voice channel")
    async def connect_command(self, interaction: discord.Interaction):
        try:
            channel = interaction.user.voice.channel
            player = await channel.connect(cls=MusicPlayer, self_deaf=True)
            embed = ShortEmbed(description=f"<:channel_button:1028004864556531824> Connected to <#{channel.id}>")
            await interaction.response.send_message(embed=embed, ephemeral=False)
            player.bound_channel = interaction.channel
        except Exception as e:
            if str(e) == "Already connected to a voice channel.": # handle that
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is already connected to a voice channel")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            elif isinstance(e, AttributeError):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            self.logger.error(f"Exception occured while connecting -- {e.__class__.__name__} - {str(e)}")
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> {e.__class__.__name__}: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return # ^ we did not defer, so we kinda set our own little error handler
            

    @app_commands.command(name="disconnect", description="Disconnects from channel that bot is in")
    async def disconnect_command(self, interaction: discord.Interaction):
        if not await djRole_check(interaction, self.logger): return
        if not await quiz_check(self.bot, interaction, self.logger): return
        await interaction.response.defer(thinking=True)
        voice = interaction.user.voice
        if not voice:
            embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            player = self.node.get_player(interaction.guild.id)
            if not player: raise NoPlayerFound
            if str(player.channel.id) != str(voice.channel.id):
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            await player.teardown()
            del player
        except Exception as e:
            if isinstance(e, NoPlayerFound):
                print(e.__class__.__name__ + ": " + str(e))
                embed = ShortEmbed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            raise e

        embed = ShortEmbed(description=f"<:channel_button:1028004864556531824> Disconnected")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("connect", "Connects to your voice channel", "Music")
    help_utils.register_command("disconnect", "Disconnects from channel that bot is in", "Music")
    await bot.add_cog(VC_Handler(bot))
