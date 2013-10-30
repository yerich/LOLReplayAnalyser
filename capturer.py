import ImageGrab
import win32gui
from screenshot import getScreenshotData
import time
import win32com.client as comclt
import win32api
import sendinput

def sendkey(keychar):
    if(isinstance(keychar, (int, long))):
        charcode = keychar
    else:
        charcode = ord(keychar.upper())
    inputarray = sendinput.make_input_array([sendinput.KeyboardInput(charcode, 1)])
    sendinput.send_input_array(inputarray)
    time.sleep(0.005)   #League sometimes does't like it if we type too fast
    inputarray = sendinput.make_input_array([sendinput.KeyboardInput(charcode, 0)])
    sendinput.send_input_array(inputarray)
    time.sleep(0.005)

def grabScreenshotData(bbox):
    im = ImageGrab.grab(bbox)
    data = (getScreenshotData(im))
    return data

logfile = open("output/capturelog.txt", "a")

window_title = 'league of legends (tm) client'
#window_title = 'notepad'

toplist, winlist = [], []
def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
win32gui.EnumWindows(enum_cb, toplist)

client = [(hwnd, title) for hwnd, title in winlist if window_title in title.lower()]
client = client[0]
hwnd = client[0]

win32gui.SetForegroundWindow(hwnd)

time.sleep(0.1)

bbox = win32gui.GetWindowRect(hwnd)

history = []
pausedcounter = 0

logfile.write("============================================================\n")

while True:
    start = time.clock()
    data = grabScreenshotData(bbox)
    
    if(not data):
        print "Could not load screenshot. Waiting 5 seconds to try again..."
        time.sleep(5)
        continue
    
    if(data['loading'] == True):
        continue
    
    if(data['game_finished'] == True):
        print "Game Finished."
        break
    
    print str(data['time']) + ": " + str(data['teams'][0]['gold']) + "|" + str(data['teams'][1]['gold'])
    logfile.write(str(data['time']) + ": " + str(data['teams'][0]['gold']) + "|" + str(data['teams'][1]['gold'])+"\n")
    
    if(data['speed'] != 8):
        sendkey(0x6B)
    
    if(data['gold_data_available'] == False):
        sendkey('x')
    
    if(len(history) > 5):
        if('time' in history[-5] and 'time' in data and data['time'] == history[-5]['time']):
            pausedcounter += 1
            if(pausedcounter >= 5):
                sendkey('p')
                pausedcounter = 0
        else:
            pausedcounter = 0
    
    history.append(data)
    print "Finished in " + str((time.clock() - start)*1000)+"ms"