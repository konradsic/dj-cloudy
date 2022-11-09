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

## #3 - Pausing/resuming playback
Pausing playback has been shown up there, it's simple to write and understand
```py
# somewhere in the universe...
player = ... # get the player

if player is not None: # check if there is a player
	player.set_pause(True)  # pause
	player.set_pause(False) # resume
```
Fairly easy, right? Yeah. You can also look into "#7 - Button menus for controlling the player" to see how it can work in buttons

*Implemented in 0.2.0*


## #4 - Logging to make informations clearer

#### The logging problem
Viewing informations in standard output like `print` is lame. We should look at the solution that satisfies all of the requirements below, so informations are clear and readable
* Logger saves informations to a file
* There are various types of output such as `INFO`, `WARN`, `ERROR`, etc.
* It shows date, module that the function has been called from, type of message and the message itself
* It's easy to use and good :)

#### Solution
Use classes to implement logging types
```py
# Higher level = higher priority
class LogLevels:
    DEBUG = 1
    INFO = 5
    WARN = 20
    ERROR = 50
    CRITICAL = 1000
```

Use decorators to register classes/functions that uses logger. Pass the logger automatically to make it even more easy-to-use.
```py
# somewhere...
import logger

@logger.LoggerApplication
class SomeGreatClassApp:
	def __init__(self, logger: logger.Logger): # logger is passes automatically by the @deco
		self.logger = logger
		self.logger.info("Hello, I am working")

# or register manually
logger.register_class("somefile.AnotherClass")
```

Make a logger manually
```py
import logger

some_logger = logger.Logger("main")
some_logger.warn("I am warning you")
```
Set logging levels to prevent unused informations appear
```py
import logger
logger.set_level(logger.LogLevels.WARN) # disable DEBUG and INFO
```

Logger automatically saves history. You can also print it anytime
```py
import logger

logger.print_logs(history=4096) # 4096 last lines of saved output
```

And finally use the logger
```py
import logger

@logger.LoggerApplication
class SomeClass:
	def __init__(self, logger):
		self.logger = logger
	
	def print_some_things(self):                         # function called to print some things, uses self.logger added in init.
		self.logger.info("Information")	                 # Print in INFO style
		self.logger.warn("Warning!")                     # Print a WARN/warning
		self.logger.error("Houston we have a problem")   # Print an error
		self.logger.critical("We need to quit.")         # Print an all-red bad critical error
```

*Implemented fairly early, propably in 0.3.0 or 0.4.0. Almost every update adds or changes something here*

## #5 - Queue commands, queue navigation
Queue navigation is one of the essential functions of the bot. The queue is a holy part of the bot - it makes that you can queue songs and not add them one by one after a track finishes. Following commands/functions should be implemented:
* Viewing the queue
* Shuffling the queue
* Clearing the queue
* Skipping to the next track
* Playing previous track
* Skipping to given position

Queue view command should be sent using an Embed Paginator[^2]. Skipto, skip and previous commands work by offsetting player position and stopping the player. That will call player advance and play wanted track.

*Implemented in 0.3.0*

## #6 - Volume controls
Volume controlling is a great feature of this bot. As it says it allows users to manipulate the track's volume and play with it.
According to wavelink wiki the max volume is 1000, thats bad. There will be some settings to change that. 

**What this should cover**
* Changing volume
* Using buttons to change volume
* View current volume
* Settings for volume controlling - `maxVolume`, `allowOverLimitFor` and maybe `volumeControllerRole`

*Implemented in 0.4.0, fixed minor bugs in other updates*


## #7 - Button menus for controlling the player
#### The problem
Users are lazy. They __do not have time__ to type commands such as `skip`, `pause` and `restart`. Automation says hello...

#### The solution
1. Not being lazy - encourage people to touch grass (oh, wait, that's a bad idea, because they won't use the bot then)
2. Automation - Make a `discord.ui.View` View that will add some cool buttons to the embed. Buttons that should be there:
	* Pause/resume playback
	* Skip to next track
	* Play previous track
	* Volume up/down
	* Restart track

*Implemented some of the buttons before 1.0.0. I don't remember the exact time*


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

###### Please contribute to this repository and/or file if you have any ideas, You can also submit them via issues or pull requests. It should be added here.

### Footnotes
[^1]: Lavalink repo: https://github.com/freyacodes/Lavalink

[^2]: Embed Paginator - A tool that you can use to view multiple embeds with arrows to navigate between them. Code reference: [**here**](https://github.com/konradsic/dj-cloudy/blob/main/utils/buttons.py#L112)
