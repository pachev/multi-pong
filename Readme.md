# Multi-Pong
by [Alicia Rodriguez](https://github.com/arodr967) & [Pachev Joseph](https://github.com/pachev)

* [Installation & Dependencies](#installation-&-dependencies)
* [Running](#running)
* [Playing](#playing)
* [Chatting](#chatting)
* [Screenshots & Videos](#screenshots-&-videos)

## Installation & Dependencies

Dependencies needed in order to run the game are the following:

1. Python3
2. Tkinter
3. Pygame

There are different ways of installing these dependencies depending on your operating system.
If you are on a Windows, or linux system  Tkinter is installed with your python libary. On a Mac,
refer to [this][1] page for more information. For further assistance with Tkinter, the Tkinter
docs has more information [here][2] on installing their preconfigured package of python.

For pygame, simply install with `pip install pygame`. Pip comes already installed with the python3
distribution.

## Running

Since the game uses TCP/UDP sockets, the `game_server.py` file needs to be ran first. This is done with the following command:

```
$ python3 game_server.py [--host] host [--port] port
```
This starts a server that can now listen and server multiple clients wanting to play the game. The host and port
are configured in `data/constants.py` as localhost:2115. Howvever, running gameserver the arguments `--host` and/or `--port`
allows you set the port and the host during startup.

## Playing

To start playing, all you have to do is run the following command:

```
$ python3 pong.py
```

The following menu screen will appear:

![Menu](/assets/screenshot3.png?raw=true "Menu screen")

- The player name field will be set to a random username.
- The host appears as empty which is just the same as `localhost`.

> NOTE: If you just want to play the game, the `game_server.py` file is actually already running on host `pachevjoseph.com`. So change the host to `pachevjoseph.com` on the menu.

- The port is set to default as `2115`.


## Chatting

The game also comes with a chat system that allows users to interract between games. This is a
non distracting window that opens up on the side of the main game window.

## Screenshots & Videos

![2 Player](/assets/screenshot1.png?raw=true "Game with two player")

![Multi Player](/assets/screenshot2.png?raw=true "Game with Multiple player")

[![Live Demo](https://img.youtube.com/vi/1KAFB7u7vf4/0.jpg)](https://www.youtube.com/watch?v=1KAFB7u7vf4)



## Known Issues

Pygame tends to run slower on the the mac due to the retina display.
click [here][3] for more info.


## References

The original layout for the game was forked from https://github.com/smoross/Pygame


[1]:https://www.python.org/download/mac/tcltk/
[2]:http://www.tkdocs.com/tutorial/install.html
[3]:http://stackoverflow.com/questions/29834292/pygame-simple-loop-runs-very-slowly-on-mac
