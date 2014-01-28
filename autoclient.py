import sys
import subprocess
import random
import time
import threading
import lrffile
import urllib
import config
import platform
import os
import httplib, mimetypes
import urlparse
import requests
import keys
import shutil
import win32com.shell.shell as shell
import traceback
ASADMIN = 'asadmin'


def monitorAnalysis(filename, savefile):
    p = subprocess.Popen(["python", "lrffile.py", filename, savefile], stdout=subprocess.PIPE)
    
    count=0
    lastline = ""
    while True:
        buff = p.stdout.readline()
    
        if buff == '':
            count += 1
    
        if buff == '' and p.poll() != None: 
            break
    
        sys.stdout.write(buff)
        if(buff.strip() != ""):
            lastline = buff.strip()
    
    p.wait()
    return lastline

def uploadAnalysisFile(fid):
    fid = str(fid)
    url = config.LOL_ANALYSIS_SERVER+"?action=upload_lrf_data&auth_token="+keys.SERVER_AUTH_TOKEN
    files = {'lrafile': open("output/"+fid+".lra", 'rb'), 'datafile': open("output/"+fid+".json", 'rb')}
    r = requests.post(url, files=files, data={"id" : fid})
    return r.text

def runAutoAnalysis():
    print "Connecting to server using URL "+config.LOL_ANALYSIS_SERVER+"."
    while(1):
        response = urllib.urlopen(config.LOL_ANALYSIS_SERVER+"?action=get_unanalyzed_lrf&auth_token="+keys.SERVER_AUTH_TOKEN)
        if(response.getcode() == 404):
            time.sleep(60)
            continue
        
        print "LRF file found. Beginning download."
        url = response.geturl()
        filename = url.split("/")[-1]
        fid = filename.split(".")[0]
        filename = "lrf/"+filename
        fh = open(filename, "wb")
        fh.write(response.read())
        fh.close()
        print "Download complete."
        
        print "Beginning analysis on "+os.path.abspath(filename)+"..."
        analysis_status = monitorAnalysis(os.path.abspath(filename), "output/"+fid+".lra")
        
        print analysis_status
        print "=============================================="
        if(analysis_status == "Done."):
            print "Analysis complete."
            
            print "Uploading data to server..."
            text = uploadAnalysisFile(fid)
            if(text == "Upload Sucessful."):
                print "Upload Completed."
            else:
                print "Upload Failed."
        else:
            response = urllib.urlopen(config.LOL_ANALYSIS_SERVER+"?action=lrf_analysis_failed&lrf_id="+str(fid)+"&auth_token="+keys.SERVER_AUTH_TOKEN)
            
        time.sleep(10)
        print "Moving on to next replay..."

def runLocalAutoAnalysis():
    print "Beginning batch analysis"
    files = [ f for f in os.listdir("lrf/") if os.path.isfile(os.path.join("lrf/",f)) and f.split(".")[-1] == "lrf" ]
    print str(len(files)) + " files found"
    for f in files:
        filename = "lrf/"+f
        savefilename = str(int(time.time()))
        print "Beginning analysis on "+os.path.abspath(filename)+" (saving to output/"+savefilename+".lra)..."
        #analysis_status = monitorAnalysis(os.path.abspath(filename), "output/"+savefilename+".lra")
        #
        #print analysis_status
        try:
            status = lrffile.analyseLRFFile(os.path.abspath(filename), "output/"+savefilename+".lra")
        except Exception, e:
            print "Exception!"
            print "Couldn't do it: %s" % e
            traceback.print_exc()
            status = False 
            
        print "=============================================="
        if(status):
            print "Analysis complete."
            print "Saved to output/"+savefilename+".lra"
            shutil.move(filename, "lrf/done/"+f)
        else:
            print "Analysis Failed."
            try:
                shutil.move(filename, "lrf/failed/"+f)
            except Exception, e:
                print "Could not move LRF file: %s" % e
                shutil.copy(filename, "lrf/failed/"+f)
        print "=============================================="
        
        os.system('taskkill /f /im \"League of Legends.exe\"')
        os.system('taskkill /f /im LOLReplay.exe')
        os.system('taskkill /f /im BsSndRpt.exe')
            
        time.sleep(2)
        print "Moving on to next replay..."

if __name__ == "__main__":
    #uploadAnalysisFile(5)
    #runAutoAnalysis()
    runLocalAutoAnalysis()