volume_guilds = {}

def change_volume(guild, val):
    volume_guilds[str(guild.id)] = val

def get_volume(guild):
    try:
        return volume_guilds[str(guild.id)]
    except:
        volume_guilds[str(guild.id)] = 100
        return 100
