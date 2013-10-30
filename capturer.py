import ImageGrab
import win32gui
from screenshot import getScreenshotData
import time
import win32com.client as comclt
import win32api
import sendinput

def sendkey(keychar):
    charcode = ord(keychar.upper())
    inputarray = sendinput.make_input_array([sendinput.KeyboardInput(charcode, 1)])
    sendinput.send_input_array(inputarray)

def grabScreenshotData(bbox):
    im = ImageGrab.grab(bbox)
    data = (getScreenshotData(im))
    return data

window_title = 'league of legends (tm) client'
#window_title = 'notepad'

toplist, winlist = [], []
def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
win32gui.EnumWindows(enum_cb, toplist)

client = [(hwnd, title) for hwnd, title in winlist if window_title in title.lower()]
# just grab the hwnd for first window matching firefox
client = client[0]
hwnd = client[0]

wsh= comclt.Dispatch("WScript.Shell")
wsh.AppActivate(window_title)

win32gui.SetForegroundWindow(hwnd)
bbox = win32gui.GetWindowRect(hwnd)

print hwnd

time.sleep(0.1)
im = ImageGrab.grab(bbox)
im.save("tmp.png")
data = (getScreenshotData(im))
print data

time.sleep(1)
sendkey('x')


#for i in range(0, 100):
#    win32api.keybd_event(0x2D, 0, 1, 0)
#    time.sleep(0.01)
#
#win32api.keybd_event(0x2D, 0, 2, 0)