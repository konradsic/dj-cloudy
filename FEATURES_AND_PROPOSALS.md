# DJ Cloudy Features, Enhancements and Proposals list
A whole file dedicated to list bot features, enhancements and proposals (for new updates, features, etc.)

## What you can find here
- Documentation of implemented features
- List of upcoming updates/enhancements
- Update proposals
- Feature requests/Enhancment requests
- ...many more like that

## ⚠️ Disclaimer
Not all features below are implemented, those can be feature requests or other. 
This is a list of features and enhancements but also proposals so don't blame us
if the feature is not implemented yet. All features should be implemented but not now.

# Enhancements, Features and update Proposals :: The List

## #1 - "Initial"
DJ Cloudy is a music bot so the core functionality is music. 
Music decoding is done by sending informations to a 24/7 hosted Lavalink[^1] server via a Python package named Wavelink.

Everything is not handled in one file, there is a "cogs" folder in the root directory containing all modules

```
[root]/
   cogs/
      all cogs...
```

Everything is OOP-like so the Music Player, Queue, Playlist Handler etc. are classes.

Initial update adds connecting, disconnecting and playing music.

*Implemented in 0.1.0*

## #2 - Events on voice state update
There is a specific event in the discord.py module that we will focus on here. It is the `on_voice_state_update` event.
It is called wherever someone joins or leaves a voice channel. We can simply add a function that will pause the playback when there is no humans:
```py
# somewhere in cogs...
@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    try:
	player = ... # get the player
        if not [m for m in after.channel.members if not m.bot]:
            await player.set_pause(True)
    except:
	pass
```

You can do the same with unsetting the pause by checking if there are huamans. 
Finally you can also check if the bot has been disconnected by force - then disconnect it properly.

*Implemented in 0.1.0, fixed in 1.0.2*

## #3 - Pausing/resuming plsyback


## #4 - Logging to make informations clearer


## #5 - Queue commands, queue navigation


## #6 - Volume controls


## #7 - Button menus for controlling the player


## #8 - Repeating tracks


## #9 - Accessible bot configuration


## #10 - EQ and Filters


## #11 - Track restarting and seeking


## #12 - Lyrics


## #12 - Lavalink server info, small utility commands


## #13 - Playlist manager, playlist system

## #14 - Spotify extension


## #15 - Configuration command, settings for guilds and users, etc.


## #16 - Plugins

###### Please contribute to this repository if you have any ideas, You can also submit them via issues or pull requests. It should be added here.

### Footnotes
[^1]: Lavalink repo: https://github.com/freyacodes/Lavalink
