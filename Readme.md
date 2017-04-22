# Multi-Pong 

by Alicia Rodriguez & Pachev Joseph

* [Installation](#installation)
* [Running](#running)
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
$ python3 game_server.py
```
This starts a server that can now listen and server multiple clients wanting to play the game. The host and port 
are configured in `data/constants.py`.

## Playing

If you just want to play the game, the `game_server.py` file is actually already running on host `pachevjoseph.com`.
So, to start playing, all you have to do is run the following command after changing the host:

```
$ python3 PingPong.py
```


## Chatting

The game also comes with a chat system that allows users to interract between games. This is a 
non distracting window that opens up on the side of the main game window

## Screenshots & Videos

![Alt text](/assets/screenshot1.png?raw=true "Game with two player")
![Alt text](/assets/screenshot2.png?raw=true "Game with Multiple player")
![Alt text](/assets/screenshot3.jpg?raw=true "Gif of player")

## Known Issues

Pygame tends to run slower on the the mac due to the retina display. 
click [here][3] for more info.


## References

The original layout for the game was forked from https://github.com/smoross/Pygame


[1]:https://www.python.org/download/mac/tcltk/
[2]:http://www.tkdocs.com/tutorial/install.html
[3]:http://stackoverflow.com/questions/29834292/pygame-simple-loop-runs-very-slowly-on-mac
