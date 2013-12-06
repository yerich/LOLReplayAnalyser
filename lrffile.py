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
import sys
from analyze import LOLGameData

def getLRFMetadata(fileh):
    head=list(islice(fileh,1))
    jsonstr = re.search("(\{.*\})", str(head)).group(1)
    data = json.loads(jsonstr)
    return data

def flushPrint(str):
    print str
    sys.stdout.flush()

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
        
        lrfmeta = getLRFMetadata(open(filename))
        if(lrfmeta['clientVersion'] not in config.LOL_VALID_CLIENT_VERSIONS):
            print "Invalid client version of replay. Replay client version is "+lrfmeta['clientVersion']+". Acceptable versions: "+", ".join(config.LOL_VALID_CLIENT_VERSIONS)
            return 
        
        subprocess.Popen([config.LOLREPLAY_PATH, filename])
            
        while(1):
            if(len(find_windows_with_name(window_title)) == 0):
                time.sleep(1)
                continue
            else:
                break
        
        flushPrint("League of Legends client window detected. Waiting 10 seconds for loading screen to appear...")
        time.sleep(10)
    else:
        lrfmeta = {}
    
    if(not filename):
        filename = "tmp.lrf"
    print "Analysis will be saved to output/"+os.path.splitext(os.path.basename(filename))[0]+".lra"
    
    flushPrint("Beginning client capture.")
    output = client_capture(lrfmeta)
    if(output == False):
        flushPrint("Client capture failed.")
        return False
    
    flushPrint("Client capture completed.")
    
    hwnd = find_windows_with_name(window_title)[0][0]
    # Close the LOL Client Window
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    
    if(not savefile):
        savefile = "output/"+os.path.splitext(os.path.basename(filename))[0]+".lra"
    output['lra_version'] = "0.1"
    output['lrf_meta'] = lrfmeta
    
    if(savefile):
        savefileh = gzip.open(savefile, "wb")
        jsonstring = json.dumps(output)
        savefileh.write(jsonstring)
        
        savefileh = open(savefile+".txt", "w")
        print >> savefileh, jsonstring
        savefileh.close()
    
    data = LOLGameData(savefile)
    print str(len(data.data['history'])) + " data points loaded."
    flushPrint("Generating analysis json file...")
    data.generateAnalysisFile()
    flushPrint("Done.")
    
    return output

def promptOpenFile():
    root = Tkinter.Tk()
    root.withdraw()
    
    file_path = tkFileDialog.askopenfilename()
    print "Opening "+file_path
    return file_path

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        analyseLRFFile(sys.argv[1])
    elif(len(sys.argv) > 2):
        analyseLRFFile(sys.argv[1], sys.argv[2])
    else:
        analyseLRFFile()