import datetime
import sys

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from wavelink.ext import spotify

from music.core import MusicPlayer
from utils import help_utils, logger
from utils.base_utils import get_config
from utils.colors import BASE_COLOR

logging = logger.Logger().get("cogs.vc_handle")

@logger.LoggerApplication
class VC_Handler(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logger.Logger) -> None:
        self.bot = bot
        self.logger = logger
        try:
            self.bot.loop.create_task(self.start_nodes())
        except:
            pass # preinitialized cog -- commands.Bot does not a loop attr 
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
        if not (info == None):
            self.logger.debug(f"Track {track} {info} #{guild} (calling player advance)")
            await player.advance()
        

    # ! We use on_wavelink_track_end as it also handles on_wavelink_track_end
    
    # @commands.Cog.listener()
    # async def on_wavelink_track_end(self, payload):
    #     await self.on_player_track_error(payload.player, additional_info={
    #         "track": payload.track,
    #         "guild": payload.player.guild,
    #         "info": payload.reason
    #     })
    
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
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                is_bot_present = False
                for bot in [m for m in before.channel.members if m.bot]:
                    if str(bot.id) == "1024303533685751868": is_bot_present = True
                if is_bot_present:
                    try:
                        player = self.node.get_player(member.guild.id)
                    except:
                        return False
                    await player.set_pause(True)
                    if player.channel is not None:
                        embed = discord.Embed(description=f"<:pause_gradient_button:1028219593082286090> Playback paused because everybody left",color=BASE_COLOR)
                        await player.bound_channel.send(embed=embed)
                    player.paused_vc = True
        try:
            if len([m for m in after.channel.members if not m.bot]) >= 1:
                player = self.node.get_player(member.guild.id)
                if player is None: return
                if player.paused_vc == True:
                    await player.set_pause(False)
                    if player.bound_channel is not None:
                        embed = discord.Embed(description=f"<:play_button:1028004869019279391> Resuming playback...",color=BASE_COLOR)
                        await player.bound_channel.send(embed=embed)
                    player.paused_vc = False
        except: pass

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
                self.logger.error(f"at on_voice_state_update - {e.__class__.__name__}: {str(e)}")
        
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
            embed = discord.Embed(description=f"<:channel_button:1028004864556531824> Connected to <#{channel.id}>", color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=False)
            player.bound_channel = interaction.channel
        except Exception as e:
            if str(e) == "Already connected to a voice channel.": # handle that
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is already connected to a voice channel",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            elif isinstance(e, AttributeError):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            self.logger.error(f"Exception occured while connecting -- {e.__class__.__name__} - {str(e)}")
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> {e.__class__.__name__}: {str(e)}",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            

    @app_commands.command(name="disconnect", description="Disconnects from channel that bot is in")
    async def disconnect_command(self, interaction: discord.Interaction):
        voice = interaction.user.voice
        if not voice:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> You are not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            player = self.node.get_player(interaction.guild.id)
            if str(player.channel.id) != str(voice.channel.id):
                embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The voice channel you're in is not the one that bot is in. Please switch to {player.channel.mention}",
                    color=BASE_COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            await player.teardown()
            del player
        except:
            embed = discord.Embed(description=f"<:x_mark:1028004871313563758> The bot is not connected to a voice channel",color=BASE_COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(description=f"<:channel_button:1028004864556531824> Disconnected", color=BASE_COLOR)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    help_utils.register_command("connect", "Connects to your voice channel", "Music: Base commands")
    help_utils.register_command("disconnect", "Disconnects from channel that bot is in", "Music: Base commands")
    await bot.add_cog(VC_Handler(bot),
                      guilds=[discord.Object(id=g.id) for g in bot.guilds])
