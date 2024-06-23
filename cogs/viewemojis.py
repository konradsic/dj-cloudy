import datetime

import discord
from discord import app_commands
from discord.ext import commands
from lib.utils import help_utils
from lib.ui.colors import BASE_COLOR
from lib.ui.embeds import ShortEmbed, NormalEmbed, FooterType
from lib.utils.base_utils import get_config
from lib.ui.buttons import EmbedPaginator

class ViewAllEmojis(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        
    @app_commands.command(name="viewemojis", description="[only in configured guilds]")
    async def view_emojis(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        # print(get_config()["bot"]["emoji-guilds"])
        guilds: list[discord.Guild] = list([self.bot.get_guild(int(x)) for x in get_config()["bot"]["emoji-guilds"]])
        # print(guilds)
        embeds = []
        
        for i,guild in enumerate(guilds):
            embed = NormalEmbed(timestamp=True, description="")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_author(name=f"Emojis from server {guild.name} ({guild.id}) ({i+1}/{len(guilds)})", icon_url=self.bot.user.display_avatar.url)
            emojis = guild.emojis
            for i,emoji in enumerate(emojis):
                embed.description += f"> `{i}.` <{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}> `<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>`\n"
            embed.description += "\n"
            embeds.append(embed)
            
        await interaction.followup.send(embed=embeds[0], view=EmbedPaginator(pages=embeds, timeout=1200, user=interaction.user))
        

async def setup(bot: commands.Bot):
    await bot.add_cog(ViewAllEmojis(bot), guilds=[discord.Object(int(id)) for id in get_config()["bot"]["emoji-guilds"]])

