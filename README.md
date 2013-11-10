LOLReplayAnalyser
=================

League of Legends Replay Analysis (experimental)

Current status:
- Requires Windows, Python 2.7, with Python Image Library (PIL) and Python for Windows extensions.
- Run `test.py` to make sure that OCR and everything else works.
- Start LOLReplay and get it to start running a League Replay File (`.lrf`). The PBE replay client should also work, but it is untested.
- Make sure that League is running in Borderless mode at 1920x1080 resolution. The program will fail otherwise.
- Move your mouse somewhere such that no text is covered by tooltips, and run `capturer.py`. It will automatically switch to the open League of Legends window, send keystrokes to control the replay, and capture the data, which can be found in `/output`.

##License

All code is licensed under the terms of the GNU General Public License, as specified in LICENSE, unless otherwise specified. All League of Legends screenshots, art, icons, and other assets are Copyright © Riot Games, Inc.

LOLReplayAnalyser isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
