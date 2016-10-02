Appelize
========

[![build status](https://gitlab.uxix.de/klaus/appelize/badges/master/build.svg)](https://gitlab.uxix.de/klaus/appelize/commits/master)

This program "appelizes" your music collection into a separate directory.

It recodes audio files that don't work in the Apple world (like FLAC and OGG)
and hardlinks the unknown ones (like mp3, jpeg and so on...). The result is a
space saving copy of your music.

In fact, it's also quite usefull for other mobile device with limited space
(e.g. android phone or notebook with an expensive SSD) or limited capabilities
(e.g. Car HiFi devices or cheap mp3 players).

It recodes all FLACs and OGGs to either mp3 or m4a (AAC).

One of the design goals is, to have an intuitive userfriendly and simple
command line user interface.

```
$ appelize --help                                                                     :(
Usage: appelize <options>

appelizes your music in a space-saving way.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s SRCDIR, --source=SRCDIR
                        Source directory (mandatory)
  -d DESTDIR, --destination=DESTDIR
                        Destination directory (mandatory), will be created if
                        not there, has to be on the same device as the source
                        directory!
  -e ENC, --encoder=ENC
                        The encoder to use, "lame" (256kbit/s VBR mp3) or
                        "faac" (VBR m4a with maximum quality). You need "lame"
                        and/or "faac" in your $PATH. default="lame"
  -t THREADS, --threads=THREADS
                        Threads to start, default=<number of CPUs or 1>
  --no-ogg              don't recode OGG, only FLAC.
  --debug               debug mode, print out some colored useless stuff

"Unfree your music!"
$
```

simple example:
---------------

    $ appelize -s ~/Music -d ~/Applemusic


Now wait and watch your CPU(s) get hot! When it's done, all files in ~/Music
will be hardlinked to ~/Applemusic, except OGG and FLAC, which will all be
recoded to mp3.

other example:
--------------

    $ appelize -s ~/Music -d ~/.androidmusic/ --no-ogg
    $ appelize -s ~/.androidmusic/ ~/.applemusic -e faac


After this you have two new directories:

~/.androidmusic contains hardlinks of everything but your FLAC-Files, which
are now encoded to mp3

~/.applemusic contains hardlinks to the upper, except all your OGGs, which
are now recoded to m4a.


