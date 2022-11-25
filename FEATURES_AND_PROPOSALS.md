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
Repeating is one of the essential functions of the bot. It allows users to select between three types[^3] of repeat modes to change what is going to happen after the track ends.

**Changing the repeat mode will affect `async MusicPlayer.advance`, `async event on_track_end`, `async event on_track_error` and `async event on_track_stuck`**, 
here is how it will work:
* Class to represent repeat mode 
```py
class RepeatMode:
	REPEAT_NONE = 0
	REPEAT_CURRENT_TRACK = 1
	REPEAT_QUEUE = 2
```
* A class that handles repeating
```py
class Repeat:
	def __init__(self):
		self.mode = RepeatMode.REPEAT_NONE
# functions/properties for additional functionality
	@propetty
	def string_mode(self): ...

	def set_repeat_mode(self, mode): ... 
```
* Applying it to the queue
```py
# music/queue.py
class Queue:
	def __init__(...):
		...
		self.repeat = Repeat()
		# all functionality of repeating is handled by Repeat class
```
* Changing events and player advance: checking for repeat mode and offsetting player's position. Then calling the actual advanced and everything works perfectly

*Implemented in 0.5.0, fixed in a few further updates*

## #9 - Accessible bot configuration
#### Why? Configuration... Do I need it? 
The answer is simple - yes. Config files are essential if the bot is open source and many people are using it. Here it is explained how it works.

**Basic config file structure**
```json
{
	"bot": {
		"token": "ababababa.xyz.hello",
		"application_id": 1234567890
	},
	"extensions": {
		"spotify": {
			"app_id": "aeae272727", 
			"token": "secret pssst"
		}
	},
	"logger": {
		"level": "INFO", 
		"logs_file": "./somedir/somefile.log"
	}
}
```
As you can see It's easy to read and almost everyone knows how to edit it. It is really simple to configure it and add new fields.

*Implemented in 1.0.0 without logger param*


## #10 - EQ and Filters
Fun part - messing with music :) Equalizers (EQs) and filters can make you mess with their functionality for days! Especially with advanced EQ allowing you to configure your own presets.

**What it adds and how it works**
* Filters - Roations, Low Pass, Channel Mix, etc. [^4]
* EQ - choose from flat, metal, piano and boost
* Advanced EQ: 15 band equalizer
* Reset EQ and filter commands

[**Learn more**](https://wavelink.readthedocs.io/en/latest/wavelink.html#wavelink.Filter)

*Added in 0.8.0*

## #11 - Track restarting and seeking
### Idea
Don't want to listen to this specific moment in the track? Use seeking or restart the track completly.

**What "seeking" and "restarting" means:**
* Seeking means setting the player's position to given time (like `1:35`, `0:23` or `2:58:45`) and then playing the track from that moment
* Restarting - Literally seeking to the beginning of current track. Like seek to `0:00`

### Commmands
* `/seek` - (no arguments) seek forward by 15s (only if no arguments provided). *Also, add a new setting for users: `defaultSeekAmount` to specify how much to seek (in seconds) and `seekForward` - when user uses this command with no parameters should the player seek forward or backwards.*
* `/seek [position:time]` - (passed optional position parameter) Seeks to given position in format (`time`) **[h:]m:s** [^5]
* `/restart` - No arguments at all to this command, equal to `/seek 0:00` where `0:00` is the "position" argument/parameter.

### Implementation
Use `async player.seek` [**docs**](https://wavelink.readthedocs.io/en/latest/wavelink.html#wavelink.Player.seek)

Examples of seeking using things explained above
```py
# seek command
# lets say that user passed a position argument
# we also need to decode the position to seconds first

player = ... # get the player
await player.seek(position)
```

Track restarting
```py
player = ... # you know...
await player.seek(0) # yay restart the track
```

*Implemented in 0.7.0, made position param in seeking not required in 0.7.1*

##### Fun fact
During testing a "bug" was discovered: 
you can enter a negative position and go over 60s and 60m limit and player will seek sucessfully **only** when after all it calculates a positive position. 
What do I mean? 
You can literally type `/seek -2:130`. 
This will convert to *-2\*60+1\*130 = -120+130 = 10* so it will seek to position `0:10`. 
Funny, right? 

## #12 - Lyrics
#### The problem
Well - You can play songs, but you cannot read the lyrics for now... 

Let's say that you are making a karaoke channel where people can sing what is playing right now. But they don't know the lyrics. 
So they type `/lyrics` but nothing shows. They are a gry at the owner that he made such a bad VC without this one command and leave the server.
Actually this is our (developers) fault...

#### Solution
Genius provides a lyrics API and there is even a Python API wrapper for it.
The `lyricsgenius` python module is easy to use and it provides essential features. 
We can simply call some functions and paginate [^2] the lyrics so people can view them **without** errors about embed characters limit.

The command should also support getting lyrics for currently playing song.

Lyrics genius token and app id should be fully cinfigurable in data/config.json

*Added in 0.6.0 on October 17, 2022*

## #13 - Lavalink server info, small utility commands
This feature is *optional*, it does not add anything really to the bot, no new functionality.

#### Lavalink server info
This command:
- Shows lavalink server informations: port, IP and other things
- Shows connected players and nodes
- Uses a simple authentication system so not all users can see server name

#### Small utility commands
Commands such as:
- `/ping` : Show latency and uptime of the bot
- More ideas coming soon! 


## #14 - Playlist manager, playlist system
You can already play music, add multiple tracks to the queue, **but** you still can't save the queue or create a list of favourite the tracks

Good news, we came with an idea for that.

#### Playlist system: idea
Playlist system consists of:
* Viewing your/others playlists
* Viewing contents of playlists
* Adding song to (your) playlists
* Playing playlists
* Starred playlist for additional functionality and ease of access
* Context menus:
	* View user's playlist (right-click on user -> Apps -> View playlists)
	* View user's starred playlists (right-click on user -> Apps -> View starred playlist)
	* Copy user's starred playlist to yours (right-click on user -> Apps -> Copy starred playlist)

#### The code part
Create a class `PlaylistHandler` (name may vary, it does not affect anything) - it will have all essential functions to create app commands and handle playlists.
`_load` function is private and used on init. It loads saved user, copies parameters and playlists to this class. 

Searching for a playlist:
```py
# lets say we are in a function called "get_playlist(self, name_or_id)" in class "PlaylistHandler"

for playlist in self.data["playlists"]:
	# case insensitive -> using .lower()
	if playlist["name"].lower() == name_or_id.lower() or playlist["id"].lower() == name_or_id.lower():
		return playlist
```

Playing playlists is similiar to the play command, it just appends multiple tracks

#### Ideas and proposals for future playlist system expansions
* Play only **one** track from playlist
* Replace track [i] with other track
* Remove element [i] from playlist
* More coming soon!

*Added in 0.9.0, improved in later versions (without the section above)*

## #15 - Spotify extension
The problem about this bot __was__ that you can only play music from YT Music, SoundCloud but not Spotify. Not for long - this update will add spotify tracks and playlists functionality.

##### Idea and implementation
Use wavelink's spotify EXT to handle spotify API calls. Make a command called `/spotify <query>` where query is a spotify link to a playlist or track.

**Implementation: [(Spotify extension - Wavelink)](https://wavelink.readthedocs.io/en/latest/exts/spotify.html)**
```py
# search for tracks:
track = await spotify.SpotifyTrack.search(query="SPOTIFY_TRACK_URL_OR_ID", return_first=True) # get first, not playlist

# search for playlist:
playlist = await spotify.SpotifyTrack.search(query="SPOTIFY_ALBUM_URL_OR_ID")
```

Idea is really simple, implementation is also easy. The problem is that wavelink returns a track of type `YouTubeTrack` so it is a little bit messed up.


## #16 - Configuration command, settings for guilds and users, etc.


## #17 - Plugins

###### Please contribute to this repository and/or file if you have any ideas, You can also submit them via issues or pull requests. It should be added here.

### Footnotes
[^1]: Lavalink repo: https://github.com/freyacodes/Lavalink

[^2]: Embed Paginator - A tool that you can use to view multiple embeds with arrows to navigate between them. Code reference: [**here**](https://github.com/konradsic/dj-cloudy/blob/main/utils/buttons.py#L112)

[^3]: Three types of repeating: NONE, CUREENT_TRACK, QUEUE. None means no repeat, current track - repeat only current track and queue - repeat whole queue, all tracks in it.

[^4]: All filters available using `/filters choose` command (implemented)

[^5]: Format in regex: text in `[]` means it is optional, `0-9`,`a-z` etc. specifies a numerical/letter range e.g. 0-9 means any number from 0 to 9.
