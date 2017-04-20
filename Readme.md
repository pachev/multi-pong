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

There are different ways of installing these dependencies depending on your operating system. This can easily be found with a google search.

// TODO: We probably want to have these dependencies in a package already as part of the game.

## Running

Since the game uses TCP, the `gameserver.py` file needs to be ran first. This is done with the following command:

```
$ python3 gameserver.py
```
// Maybe we can add some command line arguments to set up the host and the port.

## Playing

If you just want to play the game, the `gameserver.py` file is actually already running on @pachev's personal server.

So, to start playing, all you have to do is run:

```
$ python3 PingPong.py
```


## Chatting

## Screenshots & Videos

## Known Issues

Pygame tends to run slower on the the mac due to the retina display. 
click [here][3] for more info.

[3]:http://stackoverflow.com/questions/29834292/pygame-simple-loop-runs-very-slowly-on-mac
