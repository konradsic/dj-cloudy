import discord

class DJCloudyEmoji():
    def __init__(self, emoji_id: str, emoji_name: str):
        self.id = emoji_id
        self.name = emoji_name
        
    @property
    def string(self):
        return self.__str__()
    
    @property
    def mention(self):
        return self.__str__()
    
    @classmethod
    def from_id(cls, emoji_id: str, bot: discord.Client):
        emoji: discord.Emoji = bot.get_emoji(int(emoji_id))
        return cls(emoji.id, emoji.name)
    
    @classmethod
    def from_mention(cls, mention: str):
        """Emoji mention format - <:name:id>"""
        mention = mention[2:-1]
        emoji_name, emoji_id = mention.split(":")
        return cls(emoji_id, emoji_name)
    
    def __str__(self):
        return f"<:{self.name}:{self.id}>"
    
CHANNEL   = DJCloudyEmoji.from_mention("<:channel_button:1028004864556531824>")
COMMANDS  = DJCloudyEmoji.from_mention("<:commands_button:1028377812777828502>")
PAUSE     = DJCloudyEmoji.from_mention("<:pause_gradient_button:1028219593082286090>")
PLAY      = DJCloudyEmoji.from_mention("<:play_button:1028004869019279391>")
PLAYLIST  = DJCloudyEmoji.from_mention("<:playlist_button:1028926036181794857>")
REPEAT    = DJCloudyEmoji.from_mention("<:repeat_button:1030534158302330912>")
SEEK      = DJCloudyEmoji.from_mention("<:seek_button:1030534160844062790>")
SHUFFLE   = DJCloudyEmoji.from_mention("<:shuffle_button:1028926038153117727>")
PREVIOUS  = DJCloudyEmoji.from_mention("<:previous_button:1029418191274905630>")
SKIP      = DJCloudyEmoji.from_mention("<:skip_button:1029418193321725952>")
STAR      = DJCloudyEmoji.from_mention("<:star_button:1033999611238551562>")
STATS     = DJCloudyEmoji.from_mention("<:stats_gradient:1024352560724836444>")
TESTER    = DJCloudyEmoji.from_mention("<:tester:1146013014131220521>")
DEVELOPER = DJCloudyEmoji.from_mention("<:developer:1146013009806905344>")
SPONSOR   = DJCloudyEmoji.from_mention("<:sponsor:1146013011564298331>")

TICK  = DJCloudyEmoji.from_mention("<:tick:1028004866662084659>")
XMARK = DJCloudyEmoji.from_mention("<:x_mark:1028004871313563758>")

VOLUME_HIGH  = DJCloudyEmoji.from_mention("<:volume_high:1029437727294361691>")
VOLUME_MID   = DJCloudyEmoji.from_mention("<:volume_medium:1029437731354460270>")
VOLUME_LOW   = DJCloudyEmoji.from_mention("<:volume_low:1029437729265688676>")
VOLUME_MUTED = DJCloudyEmoji.from_mention("<:volume_none:1029437733631967233>")

PROGRESSBAR_LEFT_FILL   = DJCloudyEmoji.from_mention("<:progress_start_full:1201526967778947183>")
PROGRESSBAR_LEFT_EMPTY  = DJCloudyEmoji.from_mention("<:progress_start_empty:1201526964448661525>")
PROGRESSBAR_MID_FILL    = DJCloudyEmoji.from_mention("<:progress_mid_full:1201526960933843065>")
PROGRESSBAR_MID_HALF    = DJCloudyEmoji.from_mention("<:progress_mid_half:1201526963379122226>")
PROGRESSBAR_MID_EMPTY   = DJCloudyEmoji.from_mention("<:progress_mid_empty:1201526959201599558>")
PROGRESSBAR_RIGHT_FILL  = DJCloudyEmoji.from_mention("<:progress_end_full:1201526957637116015>")
PROGRESSBAR_RIGHT_EMPTY = DJCloudyEmoji.from_mention("<:progress_end_empty:1201526954759823400>")

# pag
NEXT = DJCloudyEmoji.from_mention("<:next:1202669705178124361>")
PREVIOUS = DJCloudyEmoji.from_mention("<:previous:1202669721305088030>")
NEXT_SHORT = DJCloudyEmoji.from_mention("<:next_short:1204016580569333811>")
PREVIOUS_SHORT = DJCloudyEmoji.from_mention("<:previous_short:1204016577662427176>")
TRASH = DJCloudyEmoji.from_mention("<:trash:1202669678951014472>")