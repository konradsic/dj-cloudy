# 📋 DJ Cloudy changelog
Welcome to DJ Cloudy's release notes / change log! As the name of this file says this is a file when we log changes. What you can find here is some informations about latest releases

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

## Release history
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
**0.0.1** Initial update -> 4 October 2022
