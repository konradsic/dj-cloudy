import wavelink
from enum import Enum

EQ_HZ_BANDS = (20, 40, 63, 100, 150, 250, 400, 450, 630, 1000, 1600, 2500, 4000, 10000, 16000)
FILTERS = ["karaoke", "timescale", "tremolo", "vibrato", "rotation", "distortion", "channel_mix", "low_pass"]

EQ_PRESETS = {
    "piano": [
        {"band": 0, "gain": 0.0},
        {"band": 1, "gain": 0.0},
        {"band": 2, "gain": 0.0},
        {"band": 3, "gain": 0.1},
        {"band": 4, "gain": 0.1},
        {"band": 5, "gain": 0.2},
        {"band": 6, "gain": 0.2},
        {"band": 7, "gain": 0.1},
        {"band": 8, "gain": 0.1},
        {"band": 9, "gain": 0.0},
        {"band": 10, "gain": 0.0},
        {"band": 11, "gain": 0.0},
        {"band": 12, "gain": 0.0},
        {"band": 13, "gain": 0.0},
        {"band": 14, "gain": 0.0}
    ],
    "metal": [
        {"band": 0, "gain": 0.4},
        {"band": 1, "gain": 0.4},
        {"band": 2, "gain": 0.3},
        {"band": 3, "gain": 0.3},
        {"band": 4, "gain": 0.3},
        {"band": 5, "gain": 0.0},
        {"band": 6, "gain": -0.1},
        {"band": 7, "gain": 0.0},
        {"band": 8, "gain": 0.1},
        {"band": 9, "gain": 0.3},
        {"band": 10, "gain": 0.4},
        {"band": 11, "gain": 0.4},
        {"band": 12, "gain": 0.4},
        {"band": 13, "gain": 0.4},
        {"band": 14, "gain": 0.4}
    ],
    "bassboost": [
        {"band": 0, "gain": 0.4},
        {"band": 1, "gain": 0.4},
        {"band": 2, "gain": 0.4},
        {"band": 3, "gain": 0.4},
        {"band": 4, "gain": 0.4},
        {"band": 5, "gain": 0.4},
        {"band": 6, "gain": 0.4},
        {"band": 7, "gain": 0.4},
        {"band": 8, "gain": 0.4},
        {"band": 9, "gain": 0.4},
        {"band": 10, "gain": 0.4},
        {"band": 11, "gain": 0.4},
        {"band": 12, "gain": 0.4},
        {"band": 13, "gain": 0.4},
        {"band": 14, "gain": 0.4}
    ],
    "bassboost++": [
        {"band": 0, "gain": 1},
        {"band": 1, "gain": 1},
        {"band": 2, "gain": 1},
        {"band": 3, "gain": 1},
        {"band": 4, "gain": 1},
        {"band": 5, "gain": 1},
        {"band": 6, "gain": 1},
        {"band": 7, "gain": 1},
        {"band": 8, "gain": 1},
        {"band": 9, "gain": 1},
        {"band": 10, "gain": 1},
        {"band": 11, "gain": 1},
        {"band": 12, "gain": 1},
        {"band": 13, "gain": 1},
        {"band": 14, "gain": 1}
    ]
}


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
    
async def set_equalizer(player: wavelink.Player, preset: str):
    bands = EQ_PRESETS.get(preset, None)
    if not bands:
        return False
    
    pfilters: wavelink.Filters = player.filters
    pfilters.equalizer.set(bands=bands)
    await player.set_filters(pfilters)
    return True
    
    