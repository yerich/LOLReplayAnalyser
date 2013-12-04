LOLReplayAnalyser
=================

League of Legends Replay Analysis (experimental)

Current status:
- Requires Windows, Python 2.7, with Python Image Library (PIL) and Python for Windows extensions.
- Run `test.py` to make sure that OCR and everything else works.
- Start LOLReplay and get it to start running a League Replay File (`.lrf`). The PBE replay client should also work, but it is untested. Make sure that the replay runs properly.
- Make sure that the settings are set so that the League of Legends replay client is running in Borderless mode at 1920x1080 resolution. The program will fail otherwise. For best results, I recommend you set all graphics settings to lowest.
- After making sure that everything works, quit the replay client.
- Run `lrffile.py`. It will prompt you o open an .lrf file, and it will take care of the rest. When the game is over, analysis of all data will be collected and saved to `/output`. Open `analysis.html?file=output/(NAME_OF_FOLDER)` to view it. If nothing loads, try starting chrome.exe with the `--allow-file-access-from-files` flag. You can do this by placing a shortcut on your desktop with the following address: `"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --allow-file-access-from-files`

##License

All code is licensed under the terms of the GNU General Public License, as specified in LICENSE, unless otherwise specified. All League of Legends screenshots, art, icons, and other assets are Copyright © Riot Games, Inc.

LOLReplayAnalyser isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
