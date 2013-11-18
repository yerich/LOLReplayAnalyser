import os
import time
import win32gui
import tkFileDialog
import Tkinter
from capturer import client_capture
import pipes
import subprocess
import config

def analyseLRFFile(filename = None):
    window_title = config.LOL_WINDOW_TITLE
    
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    
    def find_windows_with_name(window_title):
        win32gui.EnumWindows(enum_cb, toplist)
        
        return [(hwnd, title) for hwnd, title in winlist if window_title in title.lower()]
    
    if(len(find_windows_with_name(window_title)) == 0):
        if(filename == None):
            filename = promptOpenFile()
            if(not filename):
                print "Aborting."
                return
            
        subprocess.Popen([config.LOLREPLAY_PATH, filename])
            
        while(1):
            if(len(find_windows_with_name(window_title)) == 0):
                time.sleep(1)
                continue
            else:
                break
        
        print "League of Legends client window detected. Waiting 10 seconds for loading screen to appear..."
        time.sleep(10)
    
    print "Beginning client capture."
    output = client_capture("output/test.lra")

def promptOpenFile():
    root = Tkinter.Tk()
    root.withdraw()
    
    file_path = tkFileDialog.askopenfilename()
    print file_path
    return file_path

if __name__ == "__main__":
    analyseLRFFile()