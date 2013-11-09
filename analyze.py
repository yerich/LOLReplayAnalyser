import os
import time
import win32gui

def analyseLRFFile(filename):
    os.system("start "+filename)
    while(1):
        time.sleep(0.1)
        
    window_title = 'league of legends (tm) client'
    #window_title = 'notepad'
    
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)
    
    client = [(hwnd, title) for hwnd, title in winlist if window_title in title.lower()]
    if(len(client) == 0):
        continue
    else:
        break
    
if __name__ == "__main__":
    analyseLRFFile("test/testgame.lrf")