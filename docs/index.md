

#orbital2020 #LastMinuteWonders #Splashdown

# Bach to the Future

A music rhythm game for computers!

1. [Poster](#Poster)
2. [Motivation](#Motivation)
3. [Installation](#Installation)
4. [Gameplay](#gameplay)
5. [Full Features](#full-features)
6. [Game Engine Breakdown](#game-engine-breakdown)
7. [Compatibility Issues](#Compatibility-Issues)
8. [Project Log](#project-log)

## Poster

<img alt="Poster" src="./docs/Splashdown Poster.png">

#### Proposed Level of Achievement: Apollo 11

## Motivation

Tap Tap Revenge was one of the original hits in music rhythm gaming, the premise of this arcade game was simple. There were orbs that flowed down from the top of the screen to give time for the player to anticipate the beats in the music. When the orbs reach the "line of action", the players were supposed to tap and hold the orb, the goal was to hit the orb **on time** and **hold on** to continue earning points. The "beatmaps" of Tap Tap Revenge were normally manually programmed by a human who would then share their map on the platform for others to play.

Our team has set out to automate this process of beatmap generation using an algorithm that works over MIDI files. We know that the classical music genre is one that is highly structured, which would be ideal for the application of our low-level algorithm. Coincidentally, it is also a highly neglected genre with a wealth of interesting information, we thought we would take this chance to make a classical-music-themed Tap Tap Revenge to fill in this gap.

## Installation

### For MacOS

1. Clone (Download) this repository into your **Downloads** folder and **unzip** the file.

2. Make sure you have a **modern Python** version installed. As of 27 July 2020, this is [version 3.8.5](https://www.python.org/downloads/mac-osx/). Follow the link to download the required installer and follow through with the installation process with the default settings.

3. Make sure you have **[VLC player](https://get.videolan.org/vlc/3.0.11/macosx/vlc-3.0.11.dmg)** on your system.

4. Launch your **Terminal** from Applications and **paste** in the following lines. **After pasting each line, press *return* and wait for it complete.**

   1. ```bash
      xcode-select --install
      ```

   2. ```bash
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
      ```

   3. ```bash
      curl https://bootstrap.pypa.io/get-pip.py | sudo python3
      ```

   4. ```bash
      pip3 install pretty_midi python-vlc
      ```

   5. ```bash
      python3 -m pip install pygame==2.0.0.dev10
      ```

   6. ```bash
      brew install fluidsynth
      ```

5. Open the folder and double click on ***BTTF Launcher (macOS)*** and enjoy the game!

From now on, just double click on the Launcher if you ever wish to revisit the game? Make an alias in your **Applications** or **Desktop** folder, for ease of access!

[Live installation video](https://youtu.be/Y02bGWqIAW8)

### For Windows

#### Source code distribution

1. Download the release (source code) file and unzip the file.

2. Make sure you have a **modern Python** version installed. As of 27 July 2020, this is [version 3.8.5](https://www.python.org/downloads/windows/). Follow the link to download the required installer and follow through with the installation process with the default settings. Ensure python.exe and pip.exe are both added to the system PATH 

3. Make sure you have **[VLC player](https://www.videolan.org/index.html)** on your system.

4. Launch Command Prompt and paste the following line. (Use the right click to paste text into the window)

	1. ```batch
		pip install pretty_midi python-vlc psutil pygame==2.0.0.dev10
		```
	
5. Open the folder containing the source code and double click the `BTTF Launcher (Windows).exe` file.

#### Embedded Python bundled with source code distribution

1. Download the release `BTTF_Windows_Packaged`and unzip the file.

2. Make sure you have **[VLC player](https://www.videolan.org/index.html)** on your system.

3. Open the folder in explorer and click on the `BTTF Launcher (Windows).exe` file (it helps if you sort by file type to locate it)

#### We no longer distribute a compiled binary version due to issues with modularity and compatibility.

## Gameplay

**For a quick taste of the game, go into ARCADE and choose any song. Use the keys `d`, `f`, `g` and `h` for the corresponding lanes.**

[Gameplay Video](https://youtu.be/ERKxTDv0J4M)

## Full Features

| S/N  | Feature                       | Description                                                  | Achieved |
| ---- | ----------------------------- | ------------------------------------------------------------ | -------- |
| 1    | Menu Selection                | Selection for Campaign, Chapter Select, Arcade Mode, Sandbox mode, Achievements, and Options with scrollable and clickable components. | ✅        |
| 2    | **Visual Novel Engine**       | To handle various audiovisual assets; scriptable.            | ✅        |
| 3    | Campaign Mode                 | Scrolling text, fading backgrounds, moving sprites, and an advance feature to fast forward animations. An immersive experience to guide the player through the history of music and leads them straight into the games. | ✅        |
| 4    | Pause and volume control      | Using `P` to pause and the `up` and `down` arrow keys during a game. | ✅        |
| 5    | Highscore and Achievments log | For every unique user.                                       | ✅        |
| 6    | Text Input                    | For new users to key in their name.<br />(restricted to lowercase letters, numbers and whitespace)<br />(The numpad cannot be used to input numbers currently) | ✅        |
| 7    | User Profiles                 | Create new user profiles and toggle between them swiftly.    | ✅        |
| 8    | **Sandbox Mode**              | A highly customisable sandbox mode for users to upload their own midi files, with a directory explorer implemented natively in Pygame to preserve theming, avoid extra dependencies or even potential clashes between Pygame and GUI frameworks (e.g. on MacOS launching Tkinter's file dialog prompt with an active Pygame window causes a crash) | ✅        |
| 9    | Sandbox Options               | Various options in the sandbox configuration mode for users to select the level of note quantization, volume, tempo, or even instrument tracks using *pretty-midi*, *midi2audio* and *FluidSynth* as a backend | ✅        |
| 10   | (Windows) Fluidsynth          | A included FluidSynth distribution for Windows users in the source code as it is difficult to install it. | ✅        |
| 11   | Arcade Mode                   | Robust system that lists all available songs (including sandbox) and provides song information and current highscore of the user. | ✅        |
| 12   | Options                       | An options menu allowing users to change FPS, toggle fullscreen mode, change default game volume (values above 100 are allowed) and background volume, and even number of lanes. The change applies immediately in the current game session without the need to restart.<br />*Unfortunately, we removed the option to change screen resolution as a design choice* | ✅        |
| 13   | Key Bindings                  | Any key from a-z for different lanes in the game mode.  Between 1 to 6 lanes are allowed and when fewer than 6 lanes are chosen, only the first few key bindings are active. Binding the same key to multiple lanes is allowed (at your own loss of points when playing). | ✅        |

## Game Engine Breakdown

### pretty_midi switch

Before Milestone 3, we had not known about the existence of [pretty_midi](https://craffel.github.io/pretty-midi/). This is a more intuitive library that builds upon [mido](https://mido.readthedocs.io/en/latest/). We can use it to isolate the note events of any instrument to generate the beatmaps we desire, enabling the player the flexiblity to play the same game with the choice of multiple instruments. We can also use it to get information such as *instruments* and *volume changes*.

```python
from pretty_midi import PrettyMIDI
mid = PrettyMIDI('Fate Symphony.midi')

for instrument in mid.instruments:
  print(f"Instrument: {instrument}")
  volume_changes = [message.value for message in instrument.control_changes if message.number == 7]
  print(f"Volume changes: {volume_changes}")
```

outputs:

```python
Instrument: Instrument(program=73, is_drum=False, name="Flute")
Volume changes: [127]
Instrument: Instrument(program=68, is_drum=False, name="Oboe")
Volume changes: [95]
Instrument: Instrument(program=71, is_drum=False, name="Bb Clarinet")
Volume changes: [95]
Instrument: Instrument(program=70, is_drum=False, name="Bassoon")
Volume changes: [95]
Instrument: Instrument(program=60, is_drum=False, name="Horn in Eb")
Volume changes: [105]
Instrument: Instrument(program=56, is_drum=False, name="C Trumpet")
Volume changes: [105]
Instrument: Instrument(program=47, is_drum=False, name="Timpani")
Volume changes: [100]
Instrument: Instrument(program=48, is_drum=False, name="Violin I")
Volume changes: [100]
Instrument: Instrument(program=48, is_drum=False, name="Violin II")
Volume changes: [100]
Instrument: Instrument(program=48, is_drum=False, name="Violas")
Volume changes: [104]
Instrument: Instrument(program=48, is_drum=False, name="Violoncellos")
Volume changes: [100]
Instrument: Instrument(program=48, is_drum=False, name="Contrabass")
Volume changes: [90]
```

We are also able to manipulate individual note timings, modify volume.

### [Fluidsynth](https://github.com/FluidSynth/fluidsynth)

This API allowed for the direct output of audio files directly from python. Previously, all the audio files you heard were manually exported from digital audio workstations. This is the last piece of the puzzle that enabled the **Sandbox Mode**. 

# Testing
User trials were conducted with our friends on Windows and macOS, alongside later verifications with Parallels VM.

## Compatibility Issues

Due to [pygame](https://www.pygame.org/news) being a less popular open source library than other game engines such as Unity, the library has not been keeping up with Python upgrades and OS upgrades over time. The last stable release was on 25 April 2019 and this version has various compatibility problems that affects our development.

### Phantom Orbs

For reasons unknown, among songs of longer durations (which would normally imply a greater number of orbs), the visuals of the orbs would break down - orbs that aren't meant to appear would appear on top of other orbs. **Fortunately, this does not happen when pygame 2.0.0.dev10 is being used.** **The stable release is essential when one wishes to deploy the scripts as executables for various OSes. This issue is only pertinent to users who are running the executable version.**

### Fluidsynth.exe triggering anti-malware software

The role of fluidsynth.exe is to render a modified MIDI file generated in sandbox mode into a .flac file for playback during a game. However, when attempting to overwrite an existing .flac file, certain anti-malware software such as Norton Data Protector might block this overwrite operation and cause a failure. There may or may not be a pop up notification when this happens. Regardless, it should be possible to check the security history of the anti-malware suite and find out if this is the case. **It is thus recommended to add whole game directory as an exclusion and set fluidsynth.exe as an excluded process to prevent this from happening.**

### Install directory of libvlc.dll (unable to be located, has spaces)

Libvlc.dll is an essential dependency for the game and we avoid including this in the packaged version of the game because we found it non-trivial to package and it is a common software already in most systems. **Thus, we require that all users install the VLC player themselves.** Issues that still occur with a system with VLC player already installed include:

#### `could not find "libvlc.dll"` VLC player not located in the PATH environmental variable (%PATH% for windows, $PATH for MacOS/Linux) and installed in a non-standard location.

We interface the system's installation of VLC player through the python-vlc module which in turn interfaces the libvlc.dll file. The module requires the location of the libvlc.dll file for this. To do this, it first searches the root directory of the game (which is not there), then the PATH environmental variable. If libvlc.dll is still not found, it searches a few common locations before giving the error. **Thus, in order to avoid this error, it is necessary to either include the `VideoLAN/VLC` directory in PATH, or install VLC in a standard location (e.g. the default install directory)**

#### `%1 is not a valid win32 application` (Windows) VLC player is installed in a directory with spaces

This is due to the limitations of python-vlc's parsing of the PATH environmental variable in Windows. To verify if this is the case, type `echo %PATH:;=&echo.%` inside a command prompt window and check the output. Look for the entry with `VideoLAN\VLC`and check if there are spaces within it. **If this is the case, the only way is to install VLC player in another directory which does not have spaces in it.**

### Audio Issues with certain Windows devices

On Orbitee Mingyi's computer, there were issues using python-vlc to play .wav and .flac files when an active Pygame window is open. Various attempts were made to fix this directly were unsuccessful we had to sidestep it by loading all available game tracks (the background and campaign audio uses mp3 which did not have this issue) before initialising the display. This worked perfectly (at the cost of unneeded RAM usage by preloading unnecessary audio assets) until the implementation of sandbox mode. Because we allow the user to upload his/her own MIDI file to play with, there is now no possible way to preload all possible tracks beforehand. This was solved by performing a re-initialisation of the game before after processing a MIDI file, similar to how the game automatically updates itself after changing an option. However, the audio error reappears in this case and all song tracks are muted, forcing him to manually close and reopen the game to play the newly generated MIDI file.

## [Project Log](https://docs.google.com/spreadsheets/d/1cvhibKC6C2piTqb6wom9Ge8BIiDPPLDGw0afi3QZ9Ro/edit?usp=sharing)
