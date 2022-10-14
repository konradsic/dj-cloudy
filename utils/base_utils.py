volume_guilds = {}
registered_nodes = []

def change_volume(guild, val):
    volume_guilds[str(guild.id)] = val

def get_volume(guild):
    try:
        return volume_guilds[str(guild.id)]
    except:
        volume_guilds[str(guild.id)] = 100
        return 100

def register_node(node_cls):
    if node_cls not in registered_nodes:
        registered_nodes.append(node_cls)

def get_nodes():
    return registered_nodes

progressbar_emojis = {
    "bar_left_nofill": "<:progressbarleftnofill:1030469955512193025>",
    "bar_left_fill": "<:progressbarleftfill:1030469953754775552>",
    "bar_mid_fill": "<:progressbarmidfullfill:1030469957592563712>",
    "bar_mid_halffill": "<:progressbarmidhalffill:1030469959232536606>",
    "bar_mid_nofill": "<:progressbarmidnofill:1030469960553746552>",
    "bar_right_nofill": "<:progressbarrightnofill:1030469964383133777>",
    "bar_right_fill": "<:progressbarrightfill:1030469962583785552>"
}
