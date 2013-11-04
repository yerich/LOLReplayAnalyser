LOLReplayAnalyser
=================

League of Legends Replay Analysis (experimental)

Current status:
- Requires Windows, Python 2.7, with Python Image Library (PIL) and Python for Windows extensions.
- Run `test.py` to make sure that OCR and everything else works.
- Start LOLReplay and get it to start running a League Replay File (`.lrf`). The PBE replay client should also work, but it is untested.
- Make sure that League is running in Borderless mode at 1920x1080 resolution. The program will fail otherwise.
- Move your mouse somewhere such that no text is covered by tooltips, and run `capturer.py`. It will automatically switch to the open League of Legends window, send keystrokes to control the replay, and capture the data, which can be found in `/output`.
