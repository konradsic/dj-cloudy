# [DJ Cloudy](https://konradsic.github.io/dj-cloudy)
🤖 A Discord music bot made for fun using Python and Wavelink

If you are cloning this repo make sure to credit me for my hard work!

🌟 Star the repo if you like music and DJ Cloudy!

* Closed-source, access only for developers

## 🎶 Easy to use, rich feature music bot
With a lot of commands and features people will become more active on your server. <br>
 **Featured commands:**
* `/play <query>` plays music in your voice channel
* `/help` get embedded help in one place at any time
* `/filters choose` change how the music plays using specific effects. 
* ...and over 40 commands! 

## 🎧 No need to paste a long URL.
DJ Cloudy provides an amazing and advanced solution to searching tracks. 
Just enter the query and a list of max. 10 results will appear in form of choices.

Searching is supported only from YouTube. 
You can paste links from YT, YT Music, SoundCloud and Spotify 
(using the `/spotify` command for spotify) 

## 📑 Save your favourite songs using playlists
With an advanced yet easy to use playlist system you can view, play and manage your playlists with simple command.

Save your hits using the "star" button appearing at the bottom of `/nowplaying` and `/play` command embeds.


## 🔗 Links
* [Invite me by clicking here](https://dsc.gg/dj-cloudy)
* [Join our server](https://discord.gg/t6qPGdHypw)
* [Discuss with others about latest announcements](https://github.com/konradsic/dj-cloudy/discussions) [^1]
* [Report bugs, ask for help and request features](https://github.com/konradsic/dj-cloudy/issues) [^1]
* [DJ Cloudy Website](https://konradsic.github.io/dj-cloudy)

[^1]: Also available via Discord server

# 📥 Hosting the bot by yourself

📦 Table of prerequesties

Name | Version | Note 
-----|---------|------
Python | >= 3.10 | Lower versions won't work
pip | latest | Used to download packages, version doesn't matter
discord.py | >= 2.0.0 | Tested on v2.0.1
Wavelink | >=2.0.0 | Tested on v2.1.0
Others | - | found in `requirements.txt`

To install all packages using one command run
(every line is other variant, first should work, second is on Windows, thirt on Linux) 

```sh
pip install -r requirements.txt
py -v -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
```
On Windows, replace `v` with your Python version

## Steps
1. Clone the repository

    To do so, install [Git](https://git-scm.com/downloads) and run
```sh
git clone https://github.com/konradsic/dj-cloudy
```
2. Prepare bot token and application ID

	* Head to https://discord.com/developers and click the "New Application" button
	* Give your app a name, accept ToS and click "Create" 
	* On The navbar, click bot, then "Add bot". 
	* Once you've added a bot to your app, copy the token
	* Head to "General information", find "Application ID" and save it **with** the token. You can't lose the token!

3. Configure the bot before running

	* Go to the directory you cloned the bot in (should be **dj-cloudy**), and go into the folder named "data" 
	* Copy `config.json` as a new file, rename it to `bot-config.json` and open it.
	* Find `token` and pass the token you copied before as a value
	* Pass the application ID to the `application_id` entry and save the file. You can experiment with configuring other things, 
	but now we focus on running the bot
	* Lavalink - paste the URI, password, set to secure if you want to use secure connection, if it doesn't work set secure to opposite value (e.g. True -> False)

4. Run the bot

📁 It's recommended to chnage the folder to `dj-cloudy` (project root) before doing anything else

* Windows

When in project root:
```sh
py -v main.py
```

Anywhere else:
```sh
py -v "C:/path/to/project/main.py"
```
Replace `v` with your Python version 
and in the second one, pass an absolute path to `main.py` in the project root. 

* Linux
When in project root:
```sh
python3 main.py
```

Anywhere else:
```sh
python3 /path/to/project/main.py
```
With the path, it's the same as in Windows section

# 💻 Contributing
You can always submit issues, pull requests or chat in "Discussions" page if you have any questions or you found a bug.

🐛 There are some issue and pull request templates if you want some help with it. You can also post it via our Discord Support Server (link in the links section). 

‼️ You should only submit issues, pull request and discussions in English language.

⚠️ Warning: We are not responsible for any ear injuries caused by changing volume, applying filters and equalizers. Stay safe!
