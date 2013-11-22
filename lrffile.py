import os
import time
import win32gui
import tkFileDialog
import Tkinter
from capturer import client_capture
import pipes
import subprocess
import config
from itertools import islice
import re
import json
import zlib
import win32con
import gzip

def getLRFMetadata(fileh):
    head=list(islice(fileh,1))
    jsonstr = re.search("(\{.*\})", str(head)).group(1)
    data = json.loads(jsonstr)
    print dict(data)
    return data

def analyseLRFFile(filename = None, savefile = None):
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
    
        lrfmeta = getLRFMetadata(open(filename))
    else:
        lrfmeta = {}
    
    if(not filename):
        filename = "tmp.lrf"
    print "Analysis will be saved to output/"+os.path.splitext(os.path.basename(filename))[0]+".lra"
    
    print "Beginning client capture."
    output = client_capture(lrfmeta)
    print "Client capture completed."
    
    hwnd = find_windows_with_name(window_title)[0][0]
    # Close the LOL Client Window
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    
    savefile = "output/"+os.path.splitext(os.path.basename(filename))[0]+".lra"
    output['lra_version'] = "0.1"
    output['lrf_meta'] = lrfmeta
    
    if(savefile):
        savefileh = gzip.open(savefile, "wb")
        jsonstring = json.dumps(output)
        savefileh.write(jsonstring)
        
        savefileh = open(savefile+".txt", "w")
        print >> savefileh, jsonstring
    
    return output

def promptOpenFile():
    root = Tkinter.Tk()
    root.withdraw()
    
    file_path = tkFileDialog.askopenfilename()
    print file_path
    return file_path

if __name__ == "__main__":
    analyseLRFFile()