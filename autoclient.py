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

# Wade Leftwich - http://code.activestate.com/recipes/146306/. PSF License
def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'



def monitorAnalysis(filename, savefile):
    p = subprocess.Popen(["python", "lrffile.py", filename, savefile], stdout=subprocess.PIPE)
    
    count=0    
    while True:
        buff = p.stdout.readline()
    
        if buff == '':    
            count += 1
    
        if buff == '' and p.poll() != None: 
            break
    
        sys.stdout.write(buff)
    
    p.wait()

def uploadAnalysisFile(id, filename):
    host = urlparse(config.LOL_ANALYSIS_SERVER).newloc
    selector = urlparse(config.LOL_ANALYSIS_SERVER).path
    post_multipart(host, selector, ("id", id), (filename))

def runAutoAnalysis():
    print "Connecting to server using URL "+config.LOL_ANALYSIS_SERVER+"."
    while(1):
        response = urllib.urlopen(config.LOL_ANALYSIS_SERVER+"?action=get_unanalyzed_lrf")
        if(response.getcode() == 404 and response.read() == "No results"):
            print "No replays available. Will try again in 5 seconds."
            time.sleep(5)
            continue
        
        print "lrf file found"
        url = response.geturl()
        filename = url.split("/")[-1]
        id = filename.split(".")[0]
        filename = "lrf/"+filename
        fh = open(filename, "w")
        fh.write(response.read())
        fh.close()
        
        print "Beginning analysis..."
        monitorAnalysis(filename, "output/"+id)
        print "Analysis complete."
        
        print "Uploading data to server"
        
if __name__ == "__main__":
    runAutoAnalysis()