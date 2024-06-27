# 📋 DJ Cloudy changelog
Welcome to DJ Cloudy's release notes / change log! As the name of this file says this is a file when we log changes. What you can find here is some informations about latest releases

## Version 1.4.2
This version adds the blacklist and `allowExplicit` guild setting [(#18)](https://github.com/konradsic/dj-cloudy/issues/18). There are three types of rules in the track blacklist:
* 0 - Exclude track when author's name contains `<value>`
* 1 - Exclude track when track title contains `<value>`
* 2 - Exclude track when it's link is equal to `<value>`

Note that `allowExplicit` setting works only for Spotify tracks.
Bug fixes:
* Finally removed `lib.utils.run` - nobody uses that, it caused flask errors (it wasn't in `requirements.txt`) and quickly patched `lib.utils.run` does not exist error
* Small tweaks and improvements 

## Version 1.4.1
This version resolves some bugs and adds simple new functionality.
* Added message context menus ([#22](https://github.com/konradsic/dj-cloudy/issues/22))
    - "Search for songs" message context menus: right-click on a message -> apps -> "Search for songs"
* Added more autocomplete fields ([#24](https://github.com/konradsic/dj-cloudy/issues/24)). COmmands which got autocomplete fields
    - Queue remove, skipto: `index`
    - All playlists commands: `name`, `index` (playlists remove)
* Added `defaultVolume` user setting - when you have DJ permissions and play a track when nothing is playing the volume will be set to `defaultVolume` (or 100 if not configured)
* Marked issue [#48](https://github.com/konradsic/dj-cloudy/issues/48) because source was already replaced and I'm not adding `search.defaultSource` for now.
* "mode" argument in `/repeat` is now optional - if not passed it will send an embed with current repeat mode [#53](https://github.com/konradsic/dj-cloudy/issues/53)
* Bug fixes: 
    - Fixed indexing bugs in playlist remove (autocomplete)
    - Fixed embed paginator "Index out of range" error
    - Fixed grammar in readme (not really a bug but grammar fix)
* Small tweaks and improvements

## Version 1.4.0
After a full year the bot gets un-privated and is now open-source again. A lot of bugs are now fixed, performance is even better and new commands have been added. Here is a list of what has been updated:
1. Quiz now fully works (hopefully). New commands have been added: `/equalizers list` and `/filters list`. 
1. Emojis have been redesigned. 
1. Added play source (youtube, spotify, etc.) to `/playlists add-song` command
1. New README
1. Finally added progress bar when loading playlists to play
1. YouTube support has been added back
1. Added `force` parameter to `/skip` and `/previous` commands.
1. Fixed a bug when repeat mode is set to `REPEAT_QUEUE` and users can't skip when it's the last track (if they would wait until the song has finished it would go to the first song)
1. `/queue view` finally got a complete redesign
1. `/config view` also got redesigned
1. Updated wavelink to `3.3.0` and Lavalink to `>4.0.0` which caused the entire bot to crash, but made it stable again

**What has not been added but will be implemented soon (versions 1.4.1...1.5.0)**
- Track blacklist actually working [#18](https://github.com/konradsic/dj-cloudy/issues/18)
- [#24](https://github.com/konradsic/dj-cloudy/issues/24)
- [#22](https://github.com/konradsic/dj-cloudy/issues/22) 
- [#48](https://github.com/konradsic/dj-cloudy/issues/48)
- [#23](https://github.com/konradsic/dj-cloudy/issues/23)
- and of course many ~~bugfixes~~ quality of life and design updates

## Version 1.4.0b
I'm proud to announce the open beta of 1.4.0! This brings a lot of functionality and bug fixes.

Tracking all commits and issues here's a list of what has been implemented:
- Added `/credits` command to display devs, testers and sponsors
- `/play` command - added `put_force`, `play_force`, `source` parameters, so you can force play the track and select source of the track (yt/sc/link)
- Queue shuffle-mode - it re-shuffles when the queue ends
- `announceTracks` config - will send an embed with currently playing track info when one starts
- New quiz songs list - top songs of 2022 (billboard.com)
- Spotify update - from now there is full support for spotify tracks, albums and playlists! Also if a song is explicit it will be marked with an [E] before song name 
- Quiz end command

**What I have not implemented, that is planned to arrive in the stable version**
- Ranking at the end of quiz
- Track blacklist (or atleast `allowExplicit` config for spotify tracks) [#18](https://github.com/konradsic/dj-cloudy/issues/18)
- more autocomplete fields [#24](https://github.com/konradsic/dj-cloudy/issues/24)
- bring back YT support [#29](https://github.com/konradsic/dj-cloudy/issues/29)
- QoL [#25](https://github.com/konradsic/dj-cloudy/issues/25) (auto bug report, `/play` more user friendly)

## Version 1.4.0a2
Another alpha pre-release of the quiz update. This update fixes some major bugs.
- Fixed volume command (it was completely broken)
- Added "quiz checks" - you cannot use commands during the quiz (I mean commands related to music), see Issue [#20](https://github.com/konradsic/dj-cloudy/issues/20)
- Fixed djRole checks in buttons [#15](https://github.com/konradsic/dj-cloudy/issues/15)

Beta will be coming soon and will fix bugs and bring new functionality!


## Version 1.4.0a1
This is the first alpha release of the `1.4.0` upcoming version. It adds the music quiz functionality, read more about it down below

### Intro
After hundreds lines of code and two weeks of coding and debugging the music quiz update v.alpha is ready! Using the powers of discord's UI views - buttons and modals, previously implemented cache the result is pretty satisfying

### The story
I decided to focus on the bot more, because my vacations just started. First of all, I've made the `1.3.0` version, but I've always wanted to implement music quiz functionality. The music quiz update was planned for the end of January and here we are, in July. Why? I had school and other plans, hosting platform was unavailable, I even thought that the bot will be discontinued. 

I also had a deadline, because I scheduled a Discord event in my private server, I needed to get it done before the event. Luckily, I deployed the alpha version ideally on time, I also had an extra hour :)

### Okay, but what changed? What's new?
- The music quiz command - `/quiz start`, planning to do `/quiz end`, because you cannot run two quizzes at the same time. Running quiz can bug, so `/quiz end` is necessary.
- Some bugfixes, although more of bugs will be fixed in the stable version
- Quiz functionality - After running the command, an embed with a "Join quiz" button will appear, click the button to join the quiz. Individual round is 60 seconds, with a 5 seconds break between each round. In the break a ranking is displayed. To submit your answer in a round, click a special button, after that a modal will appear. Fill it with your answer and submit. Your score will be displayed to you after the submission.

### Plans for the official 1.4.0
- To fix bugs
- To release next alpha and beta releases packed with new quiz features and bugfixes
- To add the `/quiz end` command
- Change the song collection (current is kinda old ngl)
- Improve the quiz experience

**DO NOT** expect that the `1.4.0` stable will come so early, I also wanna rest during the vacations :D

### tl;dr
A new alpha version has just been released. It adds music quiz functionality. To start a quiz use `/quiz start`.
Some bugs have not been fixed, and this **is not** a stable version.

## Version 1.3.0
This version focuses on cache/temporary data and performance. It affects only the playlists commands & context menus group.

**Are my playlists gone? How it works?**
* This change ⚠ **WILL NOT** ⚠ affect your playlists in any way, just more data will be stored. 
* Cache or an primitive implementation of it in our way is just storing songs, so there is no need to request them from the wavelink server.
* Every cache entry (for songs its a link to the track) has an expiration time (usually one month after last time retrieved). After that the song or rather the entry is "deprecated", so it's removed from the cache and needs to be requested again. **Why?** Songs are deleted from YouTube, Soundcloud and Spotify so after a month there is a need to check it. We're working on a way to remove songs from the cache closer to the time they are deleted from the platform.
* This update fixed all playlists commands & context menus (so buggy). We are on the way to remove (almost) all bugs from the bot (not as easy as you think).
* Sneak peak: `v1.4.0` will be the music quiz update.

## Version 1.2.2
This version fixes all bugs related to random status changing and `djRole` checks. Make sure to update your bot to this version.

This is the new **required version**, make sure to update your local bot now! All version below are **deprecated** and won't work (the bot will throw a critical error).

## Version 1.2.1
This version adds new and cool features to the bot.

First of all, as promised, `djRole` checks are now in all commands that require it (check list below). 
**Note**: if `djRole` was not set (by `/config set-guild key:djRole value:roleid`) then all users have elevated, DJ permissions (they can use all DJ commands)
Support for custom changing status has been added. You can easily modify the interval between changes and randomly displaying statuses (`PLAYING, WATCHING, COMPETING, LISTENING`).

**List of commands that require DJ Role**
1. `/volume` when setting volume (when no arguments are passed everyone can use it)
2. `/repeat`
3. (selected - not all) Queue related:
    **a)** `/queue shuffle`
    **b)**`/queue remove`
    **c)** `/queue cleanup`
6. Equalizer and filters related
    **a)** `/equalizers choose`
    **b)** `/equalizers reset`
    **c)** `/equalizers advanced`
    **d)** `/filters choose`
    **e)** `/filters reset`
7. `/disconnect`
8. Pause and resume commands
    **a)** `/pause`
    **b)** `/resume`
9. `/playlists play` when `replace_queue: True`
10. Seeking commands:
    **a)** `/seek`
    **b)** `/restart`

If any other command will require DJ role checks, or if I didn't add all commands to this list, then it will be updated - stay tuned!

This is the new **required version**, make sure to update your local bot now! All version below are **deprecated** and won't work (the bot will throw a critical error).

## Version 1.2.0
One of the biggest updates to this bot so far. This update focuses on configuration features, but there are also a lot of side changes that this update has

**Developers side**
* Added `extraConfig` to configuration alongside two extra configs.
    Example:
    ```json
    {
        ...,
        "extraConfig": {
            "logger.formatFilesUsingDatetime": true,
            "logger.limitLogsTo": ["100", "MB"]
        }
    }
    ```
    As you can see, you can now additionally format logger files using datetime and limit log files to specific limit. Values are just examples, have fun with setting them
* Renamed `save_file` to `logs_directory`, it now acts as a directory, not file due to `extraConfig:logger.formatFilesUsingDatetime`
* Added `music.songs` for getting lyrics, but the `GeniusSong` class I've implemented can be used in future to gather song data
* Updated WaveLink to 2.0, now requires Lavalink v3.5 or higher
* Added lavalink config to config file
* Updates to logger, now saves only messages above or equal to the set level

**Users side**
* Fixed bugs caused by updating wavelink version
* Fixed seeking
* Added configuration commands:
```
/config view <user: bool>
/config set-user <key: str> <value: str>
/config set-guild <key: str> <value: str>
/config reset <profile: USER/GUILD>
/config reset-value <profile: USER/GUILD> <key: str>
``` 
* Config keys and types of values:
```
USER:
seekForward (bool)
defaultSeekAmount (int, in seconds)
GUILD:
inactiveTimeout (int, in minutes)
djRole (role, NotImplementedFunctionality)
maxVolume (int)
```
* Bugfixes and many more...

## Version pre-1.2.0
Version 1.2.0 brings the configuration update to us, but this is just a pre-release. What is added:
- Configuration utils file (utils/configuration.py) with handler class
    - Handler has these functions: load profile, set key to value, update profile with default, reset key to default, reset profile to default
- Configuration profile are split to 2 diffrent types: *guild* and *user*
- Added command `/config view` alongside with the `config` command group

More commands coming in further updates. Stay tuned!

## Version v1.1.2
This version brings some QoL (Quality of Life) functionality. First of all - playlist renaming system has been added. If you're bored of your old playlist name just rename it. To do so use the `/playlist rename command`. Second change is now the "star" button in the song controls toggles between adding and removing song from starred playlist. For example: you click first time - checking... no, this song is not in the starred playlist, so the bot adds it. Second click - checking... yes, song is in the playlist, bot removes it.

## Version v1.1.1
Wow! Three "ones" in this update. This update added more configurable logger so you can create an entry (in your config file) called `logger` and add `level` 
so you can change what informations are visible in the console (everything is written to log save file, saving data ignores this parameter). 
You can also modify where informations are saved by creating a value in `logger`: `save_file`. Example logging config (copied from **data/config.json**)
```json
"logger": {
    "level": "DEBUG",
    "save_file": "bot-logs/bot.log"
}
```

## Version v1.1.0
This update fixes bugs from 1.1.0-alpha update. Basically it adds Spotify extensions to the bot. Read about v1.1.0-alpha to learn more.


## Version v1.1.0-alpha
Version 1.1.0 brings spotify functionality - now you can play Spotify tracks and playlists. Sad part - loading large playlists is slow (about 15-60 seconds). I will try to make it faster in the future but for now it will stay. **Developers** note that you need a spotify application to do that. We also added a queue paginator in case of you appending milions of tracks to the queue

## Version v1.0.2 release notes
Sad fact: I've released 1.0.0 a few days ago and me and my friends are still encountering many bugs. Hopefully they are fixed before anyone notices ;) This update fixed kind of "forced disconnect" issue that kept player class registered/not disconnected and caused issues becuase it was actually not connected. It's fixed now and lets hope that it'll be the last bug here. *Marked as required update*

## Version v1.0.1 release notes
In this version I've removed my friend from collaborators because he wasn't doing anything here. This update is really important - it fixes the volume bug. I'm really sorry that I didn't see that before. But hopefully DJ Cloudy is now both awesome and bug free.

## Version v1.0.0 release notes
Yes, this update has finally come. We will document as many as we can in the Wiki section to make sure you understand how to use the bot. From now we will be giving a long description of __every__ release.
### What we've added
- Some improvements on the developers side
    - Aesthetical changes to logger
    - Checking for updates and version deprecation system - we want to ensure that you have the latest release that covers newest security standards to keep everything safe. You can always `git pull` or sync your fork to get those changes on your computer
    - Fixed "Catching exceptions that do not inherit from `BaseException` is not allowed". It was caused by logger
    - Auto setup of JSON files and more configuration overall
- But there are also changes on the user interaction side!
    - Case insensitive searching both for playlists and help categories
    - Better help command
    - Changes to `/changelog` command so it can handle new format explained above
    - Added `/grab` command so you can grab your favorite tracks to DMs and save them there (if you really hate playlists tho)
- Fixed (hopefully) all bugs

## 1.0.0-alpha release notes
Getting really close to `v1.0.0`. This is the alpha release - everything should work but we are making sure everything works properly and nothing is missing (from out list). Version 1.0.0-alpha is like a pre-release so it covers most of 1.0.0
### What we've added
- Customizable logging levels (set to warn - supress infos and debugs etc.)
- Fixed lyrics text showing weird lines like "You might also like" or "Embed"
- Fixed seeking - I don't know why but before seeking to less than one minute (for example `0:45`) caused an error. Now it's fixed
### What bot covers - everything in 1.0.0 (should be)
- Basic commands such as play, pause, resume, connect, disconnect etc.
- Playlist system - categorize, star and play your favorite tracks
- Advanced commands - equalizers, filters, precise seeking and track restarting
- Repeating tracks
- Miscellaneous commands such as ping, botinfo or changelog
- Cool help command
- (dev) Advanced logging and understandable code structure

## 0.9.2 release notes
This update is mainly dev-side including (third!) new logger. I personally think that this is the best one out of them, but 
What we've added:
- Complete new logger (v3, wow, I wonder how many logger versions there will be overall by the next month)
- Fixed some small bugs and issues
- We are approaching the end of fixing bugs and adding new features. Version v1.0.0 will come soon!

## Before v0.9.2: Release history
**0.9.1** Brand new help command <br/>
**0.9.0** Complete playlist system: commands, context menus and more <br/>
**pre-0.9.0** Playlist system + some playlist commands <br/>
**0.8.0** Filters and Equalizers <br/>
**0.8.0-alpha** Pre-defined equalizer cog and functional filters commands <br/>
**0.7.1** Make position parameter in seek command non-required, defaults to +15s <br/>
**0.7.0** Seeking and restarting functionality + buttons <br/>
**pre-0.7.0** Restart command, working on seeking <br/>
**0.6.1** Improved lyrics handler and paginator <br/>
**0.6.0** Lyrics update: lyrics command <br/> 
**0.5.1** Event on mentioning the bot <br/>
**0.5.0** Repeating update <br/>
**pre-0.5.0** Repeat command, working on buttons <br/>
**0.4.4** `/botinfo` command <br/>
**0.4.3** Bugfixes + nowplaying command <br/>
**0.4.2** {queue moveto => skipto}, sneak peak on 0.5.0 and bug fixes <br/>
**0.4.1** Squished volume commands to one <br/>
**0.4.0** Volume controlling by buttons, change lavalink server <br/>
**pre-0.4.0** Volume get and set commands <br/>
**0.3.0** Queue moveto, end queue navigation commands, small bugfixes <br/>
**pre3-0.3.0** Queue previous and cleanup commands <br/>
**pre2-0.3.0** Queue skip command <br/>
**pre1-0.3.0** Queue view and shuffle <br/>
**0.2.4** Song autocompletion in `/play` command <br/>
**0.2.3** Changelog command <br/>
**0.2.2** Help command <br/>
**0.2.1** Player advance patch <br/>
**0.2.0** Pause and resume commands <br/>
**0.1.0** Everything is now embedded, complete new logger and many more <br/>
**0.0.1** Initial update -> 4th of October 2022
