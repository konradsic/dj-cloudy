from .colors import BASE_COLOR
import discord
from enum import Enum
import datetime

class FooterType(Enum):
    LICENSED = "Licensed under the MIT License"
    MADE_BY = "Made with love and passion, by @konradsic"
    GH_LINK = "Contribute https://github.com/konradsic/dj-cloudy"
    COMMANDS = "Did you know that there are over 40+ commands that you can use?"
    NONE = ""

class ShortEmbed(discord.Embed): # used only with description
    def __init__(self, description: str, color = BASE_COLOR, **kwargs):
        super().__init__(color=color, description=description, **kwargs)
        
class NormalEmbed(discord.Embed): # normal embed, used everywhere else
    def __init__(self, timestamp: bool, footer_add: str, replace_footer: bool, footer: FooterType=FooterType.MADE_BY, color=BASE_COLOR, **kwargs):
        super().__init__(color=color, **kwargs)
        footer = footer.value + footer_add
        if replace_footer: footer = footer_add
        if footer: self.set_footer(text=footer)
        if timestamp: self.timestamp = datetime.datetime.utcnow()
        