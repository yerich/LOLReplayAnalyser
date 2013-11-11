import os
import time
import win32gui
import tkFileDialog
import Tkinter
from capturer import client_capture
import pipes
import subprocess

def analyseLRFFile(filename = None):
    if(filename == None):
        filename = promptOpenFile()
        if(not filename):
            print "Aborting."
            return
        
    subprocess.Popen(["C:\Program Files (x86)\LOLReplay\LOLReplay.exe", filename])
        
    window_title = 'league of legends (tm) client'
    
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
        
    while(1):
        win32gui.EnumWindows(enum_cb, toplist)
        
        client = [(hwnd, title) for hwnd, title in winlist if window_title in title.lower()]
        if(len(client) == 0):
            continue
        else:
            break
        
        print "continuing..."
        time.sleep(1)
    
    time.sleep(10)
    
    output = client_capture("output/test.lra")

def promptOpenFile():
    root = Tkinter.Tk()
    root.withdraw()
    
    file_path = tkFileDialog.askopenfilename()
    print file_path
    return file_path

if __name__ == "__main__":
    analyseLRFFile()