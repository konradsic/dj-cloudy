from .colors import BASE_COLOR
import discord
from enum import Enum
import datetime
import random

class FooterType(Enum):
    LICENSED = "Licensed under the MIT License"
    MADE_BY = "Made with love and passion, by @konradsic"
    GH_LINK = "Contribute at https://github.com/konradsic/dj-cloudy"
    COMMANDS = "Discover over 40 amazing commands by typing /help"
    NONE = ""
    
def random_footer() -> FooterType:
    footers = [f.value for f in FooterType]
    return random.choice(footers)

class ShortEmbed(discord.Embed): # used only with description
    def __init__(self, description: str, color = BASE_COLOR, **kwargs) -> None:
        super().__init__(color=color, description=description, **kwargs)
        
class NormalEmbed(discord.Embed): # normal embed, used everywhere else
    def __init__(self, timestamp: bool=False, footer_add: str="", replace_footer: bool=False, 
                 footer: FooterType | str=FooterType.MADE_BY.value, color=BASE_COLOR, **kwargs) -> None:
        super().__init__(color=color, **kwargs)
        try: # provided FooterType class with no .value -> a string
            footer = footer.value + footer_add
        except: # provided a string
            footer = footer + footer_add
        if replace_footer: footer = footer_add
        if footer: self.set_footer(text=footer)
        if timestamp: self.timestamp = datetime.datetime.utcnow()

# embed paginator in lib.ui.buttons
        