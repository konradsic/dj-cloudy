import discord

class DJCloudyEmoji():
    def __init__(self, emoji_id: str, emoji_name: str, is_animated: bool=False):
        self.id = emoji_id
        self.name = emoji_name
        self.is_animated = is_animated
        
    @property
    def string(self):
        return self.__str__()
    
    @property
    def mention(self):
        return self.__str__()
    
    @classmethod
    def from_id(cls, emoji_id: str, bot: discord.Client):
        # is_animated check
        emoji: discord.Emoji = bot.get_emoji(int(emoji_id))
        return cls(emoji.id, emoji.name, emoji.animated)
    
    @classmethod
    def from_mention(cls, mention: str):
        """Emoji mention format - <{a if animated}:name:id>"""
        if mention.startswith("<a"): # animated
            is_animated = True
            mention = mention[3:-1]
        else:
            is_animated = False
            mention = mention[2:-1]
        emoji_name, emoji_id = mention.split(":")
        return cls(emoji_id, emoji_name, is_animated)
    
    def __str__(self):
        return f"<{'a' if self.is_animated else ''}:{self.name}:{self.id}>"

# NOTE: all emojis except a few are now redesigned
# general
CHANNEL   = DJCloudyEmoji.from_mention("<:channel:1202669694180655134>")
COMMANDS  = DJCloudyEmoji.from_mention("<:command:1202669931657695362>")
PAUSE     = DJCloudyEmoji.from_mention("<:pause:1202669937844559892>")
PLAY      = DJCloudyEmoji.from_mention("<:play:1202669940591824920>")
PLAYLIST  = DJCloudyEmoji.from_mention("<:playlist:1202669715743445082>")
REPEAT    = DJCloudyEmoji.from_mention("<:repeat:1202669723746304131>")
SEEK      = DJCloudyEmoji.from_mention("<:seek:1202669666154323968>")
SHUFFLE   = DJCloudyEmoji.from_mention("<:shuffle:1202669670474186782>")
PREVIOUS  = DJCloudyEmoji.from_mention("<:previous:1202669721305088030>")
SKIP      = DJCloudyEmoji.from_mention("<:next:1202669705178124361>")
STAR      = DJCloudyEmoji.from_mention("<:star:1202669672051253410>")
STATS     = DJCloudyEmoji.from_mention("<:ping:1202669712169898004>")
TESTER    = DJCloudyEmoji.from_mention("<:tester:1146013014131220521>")
DEVELOPER = DJCloudyEmoji.from_mention("<:developer:1146013009806905344>")
SPONSOR   = DJCloudyEmoji.from_mention("<:money:1202669702908739634>")
LOADING   = DJCloudyEmoji.from_mention("<a:loading:1146737041867022376>")
# new emojis after emoji redesign update
SHARE     = DJCloudyEmoji.from_mention("<:share:1202669669073289337>")
CONFIG    = DJCloudyEmoji.from_mention("<:config:1202669697737424926>")
PLUS      = DJCloudyEmoji.from_mention("<:plus:1202669928478675017>")
MINUS     = DJCloudyEmoji.from_mention("<:minus:1202669933532553297>")
SEARCH    = DJCloudyEmoji.from_mention("<:search:1203719924594511963>")

TICK1 = DJCloudyEmoji.from_mention("<:ok1:1202669936120565862>")
TICK2 = DJCloudyEmoji.from_mention("<:ok2:1202669709259177996>")
XMARK = DJCloudyEmoji.from_mention("<:xmark:1202669692754595880>")

STATS1 = DJCloudyEmoji.from_mention("<:stats1:1202669674685276231>")
STATS2 = DJCloudyEmoji.from_mention("<:stats2:1202669676178706552>")

# volume
VOLUME_HIGH  = DJCloudyEmoji.from_mention("<:volume_max:1202669683795304548>")
VOLUME_MID   = DJCloudyEmoji.from_mention("<:volume_mid:1202669685209047051>")
VOLUME_LOW   = DJCloudyEmoji.from_mention("<:volume_low:1202669681001889894>")
VOLUME_MUTED = DJCloudyEmoji.from_mention("<:volume_muted1:1202669687822098452>")
VOLUME_NONE  = DJCloudyEmoji.from_mention("<:volume_quiet:1202669689814122587>")

# progressbars
PROGRESSBAR_LEFT_FILL   = DJCloudyEmoji.from_mention("<:progress_start_full:1201526967778947183>")
PROGRESSBAR_LEFT_EMPTY  = DJCloudyEmoji.from_mention("<:progress_start_empty:1201526964448661525>")
PROGRESSBAR_MID_FILL    = DJCloudyEmoji.from_mention("<:progress_mid_full:1201526960933843065>")
PROGRESSBAR_MID_HALF    = DJCloudyEmoji.from_mention("<:progress_mid_half:1201526963379122226>")
PROGRESSBAR_MID_EMPTY   = DJCloudyEmoji.from_mention("<:progress_mid_empty:1201526959201599558>")
PROGRESSBAR_RIGHT_FILL  = DJCloudyEmoji.from_mention("<:progress_end_full:1201526957637116015>")
PROGRESSBAR_RIGHT_EMPTY = DJCloudyEmoji.from_mention("<:progress_end_empty:1201526954759823400>")

# paginator
NEXT           = DJCloudyEmoji.from_mention("<:next:1202669705178124361>")
PREVIOUS       = DJCloudyEmoji.from_mention("<:previous:1202669721305088030>")
NEXT_SHORT     = DJCloudyEmoji.from_mention("<:next_short:1204016580569333811>")
PREVIOUS_SHORT = DJCloudyEmoji.from_mention("<:previous_short:1204016577662427176>")
TRASH          = DJCloudyEmoji.from_mention("<:trash:1202669678951014472>")

