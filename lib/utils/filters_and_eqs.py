import wavelink
from enum import Enum

EQ_HZ_BANDS = (20, 40, 63, 100, 150, 250, 400, 450, 630, 1000, 1600, 2500, 4000, 10000, 16000)
FILTERS = ["karaoke", "timescale", "tremolo", "vibrato", "rotation", "distortion", "channel_mix", "low_pass"]

async def set_filter(player: wavelink.Player, filter: str):
    pfilters: wavelink.Filters = player.filters
    if filter == "karaoke":
        pfilters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
    elif filter == "timescale":
        pfilters.timescale.set(speed=1.2, pitch=0.7, rate=1.0)
    elif filter == "tremolo":
        pfilters.tremolo.set(frequency=4.0, depth=0.5)
    elif filter == "vibrato":
        pfilters.vibrato.set(frequency=5.0, depth=0.5)
    elif filter == "rotation":
        pfilters.rotation.set(rotation_hz=0.2)
    elif filter == "distortion":
        pfilters.distortion.set(sin_offset=0.30, sin_scale=2.0, cos_offset=0.1, cos_scale=2.3, 
                                tan_offset=0.5, tan_scale=1.4, offset=0.4, scale=2.0)
    elif filter == "channel_mix":
        pfilters.channel_mix.set(left_to_left=0.7, left_to_right=0.3,
                                 right_to_left=0.3, right_to_right=0.7)
    elif filter == "low_pass":
        pfilters.low_pass.set(smoothing=20.0)
    
    await player.set_filters(pfilters, seek=True)
    
    