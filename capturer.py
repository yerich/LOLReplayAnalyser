import ImageGrab
import win32gui
import time
import sendinput
import ctypes
import json
import zlib
from config import MOUSEEVENTF_MOVEABS, MOUSEEVENTF_CLICK
import screenshot
import sys
import os

keypressdelay = {}
def sendkey(keychar, delay = 0.2):
    global keypressdelay
    
    def keyup(keyrecord):
        if(keyrecord['time'] > time.clock()):
            inputarray = sendinput.make_input_array([sendinput.KeyboardInput(keyrecord['charcode'], 0)])
            sendinput.send_input_array(inputarray)
            time.sleep(0.025)
            return True
        else:
            return False
    
    if(isinstance(keychar, (int, long))):
        charcode = keychar
    else:
        charcode = ord(keychar.upper())
    
    inputarray = sendinput.make_input_array([sendinput.KeyboardInput(charcode, 1)])
    sendinput.send_input_array(inputarray)
    time.sleep(0.025)
    
    keypressdelay[charcode] = {'charcode' : charcode, 'time': time.clock() + delay}
    
    keypressdelay = {key: value for (key, value) in keypressdelay.iteritems() if not keyup(value)}


def sendmouseclick(coords, delay = 0.2):
    x, y = coords
    #move first
    x = 65536L * x / ctypes.windll.user32.GetSystemMetrics(0) + 1
    y = 65536L * y / ctypes.windll.user32.GetSystemMetrics(1) + 1
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVEABS, x, y, 0, 0)
    
    time.sleep(delay)

    #then click
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_CLICK, 0, 0, 0, 0)
    
def grabScreenshotWinner(im):
    return screenshot.getGameWinner(im)

def grabScreenshotData(im, metadata = None):
    data = (screenshot.getScreenshotData(im, metadata))
    return data

logfile = open("output/capturelog.txt", "a")

def client_capture(metadata = None):
    window_title = 'league of legends (tm) client'
    #window_title = 'notepad'
    champ_key_map = ['1', '2', '3', '4', '5', 'q', 'w', 'e', 'r', 't']
    
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)
    
    client = [(hwnd, title) for hwnd, title in winlist if window_title in title.lower()]
    if(len(client) == 0):
        MessageBox = ctypes.windll.user32.MessageBoxA
        MessageBox(None, "Error: League of Legends client window not found. Make sure that a League of Legends replay is playing.", 'Error', 0)
        return
        
    client = client[0]
    hwnd = client[0]
    
    win32gui.SetForegroundWindow(hwnd)
    
    window_coords = win32gui.GetWindowRect(hwnd)
    print window_coords
    
    time.sleep(0.1)
    
    bbox = win32gui.GetWindowRect(hwnd)
    
    history = []
    overlay_inactive_counter = 0
    turns_with_gold = 0
    turns_with_items = 0
    turns_too_many_events = 0
    winner = -1
    exception_count = 0
    failure_count = 0
    invalid_champion_count = 0
    
    logfile.write("============================================================\n")
    currchamp = -1  # Active champion
    
    currchamp_death_switcher = [[0 for i in range(0, 5)], [0 for i in range(0, 5)]];
    
    while True:
        sys.stdout.flush()
        
        start = time.clock()
        im = ImageGrab.grab(bbox)
        try:
            data = grabScreenshotData(im, metadata)
        except Exception, e:
            print "Error: Exception caught: "+str(e)
            exception_count += 1
            if(exception_count % 10 == 0):
                sendkey('p')
            if(exception_count > 50):
                print "Fatal Error: Too many exceptions"
                return False
            continue
        
        exception_count = 0
        
        if(failure_count > 15):
            print "Fatal Error: Too many failures."
            return False
        
        if(invalid_champion_count > 15):
            print "Fatal Error: Too many invalid champions"
            return False
        
        if(data == -1):
            print "OCR Error. Skipping this screenshot"
            failure_count += 1
            continue
        
        if(not data):
            print "Could not load screenshot. Waiting 2 seconds to try again..."
            failure_count += 1
            time.sleep(2)
            continue
        
        if('loading' in data and data['loading'] == True):
            print "In loading screen. Continuing..."
            summoner_spells = data['summoner_spells']
            failure_count += 1
            time.sleep(3)
            continue
        
        if('teamfight' in data and data['teamfight'] == True):
            print "In teamfight mode (not supported). Disabling..."
            failure_count += 1
            sendkey('a', 0.1)
            time.sleep(1)
            continue
        
        failure_count = 0
        
        if(data['game_finished'] == True):
            print "Game Finished. Getting game winner..."
            # Move the mouse to a location where we can see the purple team nexus
            sendmouseclick((window_coords[0] + 1886, window_coords[1] + 803))
            time.sleep(10)
            im = ImageGrab.grab(bbox)
            winner = grabScreenshotWinner(im)
            if(winner == 0):
                print "Blue team wins."
            else:
                print "Purple team wins."
            
            data['winner'] = winner
            
            print "Capture Complete."
            break
        
        
        # Check to see if the game is paused.
        if(data['paused'] == True and turns_with_gold <= 10):
            sendkey('p', 0.1)
        
        # Control game speed with numpad + and - keys
        # Virtual key codes from here: http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
        if(data['speed'] != 8 and len(data['events']) < 4):
            if(turns_too_many_events <= 0):
                sendkey(0x6B)
            else:
                turns_too_many_events -= 1
        
        if(len(data['events']) != 0):
            for event in data['events']:
                if(event['victim'].startswith("champion")):
                    for team in [0, 1]:
                        for player in range(0, 5):
                            if("champion-" + data['players'][team][player]['champion'] == event['victim']):
                                if(currchamp_death_switcher[team][player] == 0):
                                    currchamp_death_switcher[team][player] = 10
                                    sendkey('0')
                                break
        
        # Slow game down if too many events on screen
        if(len(data['events']) == 4):
            sendkey('0')
            turns_too_many_events = 7
        
        #switch between active champions, center camera
        
        if(data['active_champion']):
            if(data['active_champion']['champion'] != data['players'][currchamp // 5][currchamp % 5]['champion']):
                print "Error: active champion not expected value. Disregarding. Was " + data['active_champion']['champion'] + \
                    ", expected " + data['players'][currchamp // 5][currchamp % 5]['champion']
                invalid_champion_count += 1
            else:
                invalid_champion_count = 0
                data['active_champion']['champion_id'] = currchamp
                    
                # Write active champ info back into results, if available
                if(data['active_champion']['overlay_active']):
                    team = data['active_champion']['champion_id'] // 5
                    player = data['active_champion']['champion_id'] % 5
                    if(not data['players'][team][player]['level']):
                        data['players'][team][player]['level'] = data['active_champion']['level']
                
                currchamp = (currchamp + 1) % 10
                for team in range(0, 1):
                    for player in range(0, 5):
                        if(currchamp_death_switcher[team][player] == 10):
                            currchamp = team * 5 + player
                            sendkey('0')
                        if(currchamp_death_switcher[team][player] > 0):
                            currchamp_death_switcher[team][player] -= 1
        
        if(currchamp < 0):
            currchamp = 0
            
        sendkey('s')    # Force manual camera
        sendkey(champ_key_map[currchamp])   # Select currchamp
        sendkey(champ_key_map[currchamp])   # Center camera on currchamp
        
        #switch between gold and items
        if(data['gold_data_available']):
            turns_with_items = 0
            turns_with_gold += 1
            if(turns_with_gold > 10):
                sendkey('x')
                sendkey('p')
        else:
            turns_with_gold = 0
            turns_with_items += 1
            sendkey('p')
            sendkey('x')
        
        #turn on info overlay
        if(data['active_champion'] and not data['active_champion']['overlay_active']):
            overlay_inactive_counter += 1
            if(overlay_inactive_counter > 1):
                sendkey('c', 0.1)
                overlay_inactive_counter = 0
        else:
            overlay_inactive_counter = 0
        
        #print data['towers']
        if(data['valid'] == True):
            history.append(data)
        else:
            print data['errmsg']
            im.save("wtf.png")
        
        logfile.write(str(data['time']) + ": " + str(data['teams'][0]['gold']) + "|" + str(data['teams'][1]['gold'])+"\n")
        print "Capture successful (" + str(round((time.clock() - start)*1000))+"ms). "+str(data['time']//60)+":"+str(data['time'] % 60)+" - " + str(data['teams'][0]['kills']) + "|" + str(data['teams'][1]['kills']) + ". Gold: " + str(data['teams'][0]['gold']) + "|" + str(data['teams'][1]['gold'])
    
    sys.stdout.flush()
    return { 'history' : history, 'summoner_spells': summoner_spells, 'winner' : winner }