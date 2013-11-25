from __future__ import division
import ocr
import re
import icon
import Image
import config
from icon import pixelDiff

last = False

def cint(s):
    if s == '' or s == None:
        return 0
    if type(s) is int:
        return s
    
    s = re.sub(r'[^\d.]+', '', s)
    if s == '' or s == None:
        return 0
    return int(s)

# Returns an item dict for an icon
def getItemFromIcon(im):
    icon_name = icon.imageToIconName(im, "item")
    if icon_name == "blank":
        return None
    return icon_name.replace("item-", "")

def getSummonerSpellFromIcon(im):
    icon_name = icon.imageToIconName(im, "summoner")
    if icon_name == "blank":
        return None
    return icon_name.replace("summoner-", "")

def getChampionFromIcon(im):
    icon_name = icon.imageToIconName(im, "champion")
    if icon_name == "blank":
        return None
    return icon_name.replace("champion-", "")

# Returns an array of items, given the (x, y) coordinate (where (0, 0) is top-left) 
# of the top-left pixel of the first item in the bar
def getItems(im, tl):
    items = []
    for i in [im.crop((tl[0], tl[1], tl[0]+26, tl[1]+26)), im.crop((tl[0]+27, tl[1], tl[0]+53, tl[1]+26)),
              im.crop((tl[0]+54, tl[1], tl[0]+80, tl[1]+26)), im.crop((tl[0]+81, tl[1], tl[0]+107, tl[1]+26)),
              im.crop((tl[0]+108, tl[1], tl[0]+134, tl[1]+26)), im.crop((tl[0]+135, tl[1], tl[0]+161, tl[1]+26)),
              im.crop((tl[0]+162, tl[1], tl[0]+188, tl[1]+26))]:
        item = getItemFromIcon(i)
        if(item != None):
            items.append(item)
    
    return items

# Returns event information for the given top-right pixel, if available
# TODO: assists
def getEvent(im, tr):
    if ((pixelDiff(im.getpixel((tr[0], tr[1]+1))[0:3], (41, 130, 192)) < 10) and 
        (pixelDiff(im.getpixel((tr[0], tr[1]))[0:3], (41, 130, 192)) >= 10) and
        (pixelDiff(im.getpixel((tr[0], tr[1]+62))[0:3], (41, 130, 192)) < 10) and 
        (pixelDiff(im.getpixel((tr[0], tr[1]+63))[0:3], (41, 130, 192)) >= 10)):
        eventinfo = { 'team' : 0 }
    elif ((pixelDiff(im.getpixel((tr[0], tr[1]+1))[0:3], (132, 40, 192)) < 10) and 
        (pixelDiff(im.getpixel((tr[0], tr[1]))[0:3], (132, 40, 192)) >= 10) and
        (pixelDiff(im.getpixel((tr[0], tr[1]+62))[0:3], (132, 40, 192)) < 10) and 
        (pixelDiff(im.getpixel((tr[0], tr[1]+63))[0:3], (132, 40, 192)) >= 10)):
        eventinfo = { 'team' : 1 }
    else:
        return None
    
    eventinfo['killer'] = icon.imageToIconName(im.crop((tr[0] - 144, tr[1] + 12, tr[0] - 98, tr[1] + 58)))
    eventinfo['victim'] = icon.imageToIconName(im.crop((tr[0] - 53, tr[1] + 12, tr[0] - 7, tr[1] + 58)))
    return eventinfo

# This will return the winner of the game given a very specific screenshot: one side must have already won,
# and the pixel (1886, 803) MUST be clicked on the minimap. This function will then check if the purple nexus
# is destroyed or not. If it is, blue team won and return 0. Otherwise purple team won so return 1.
def getGameWinner(im):
    if(pixelDiff(im.getpixel((1181, 711)), (33, 32, 33)) < 150):
        return 0
    else:
        return 1

# Returns a dict of data retrieved from a screenshot
def getScreenshotData(im, metadata = None):
    global last
    
    if(metadata and "clientVersion" in metadata):
        clientVersion = metadata["clientVersion"]
        if(clientVersion < "3.14"):
            icon.setIconFolder("icons/3.13/")
    else:
        clientVersion = None
    
    im = im.convert("RGB")
    width, height = im.size
    valid = True    # Set to false when there's some blantantly incorrect OCR'd value
    
    if(width != 1920 or height != 1080):
        print "Error: screenshot must be 1920x1080px exactly."
        return False
    
    if(im.getpixel((0, 300))[0:3] == (0, 0, 0) and im.getpixel((1900, 300))[0:3] == (0, 0, 0)):
        def getSummonerSpellIcon(tr):
            return im.crop((tr[0], tr[1], tr[0]+36, tr[1]+36))
        results = {'loading' : True, "valid" : True}
        results['summoner_spells'] = [[], []];
        results['summoner_spells'][0].append([getSummonerSpellFromIcon(getSummonerSpellIcon((362, 455))), getSummonerSpellFromIcon(getSummonerSpellIcon((409, 455)))])
        results['summoner_spells'][0].append([getSummonerSpellFromIcon(getSummonerSpellIcon((644, 455))), getSummonerSpellFromIcon(getSummonerSpellIcon((690, 455)))])
        results['summoner_spells'][0].append([getSummonerSpellFromIcon(getSummonerSpellIcon((925, 455))), getSummonerSpellFromIcon(getSummonerSpellIcon((972, 455)))])
        results['summoner_spells'][0].append([getSummonerSpellFromIcon(getSummonerSpellIcon((1207, 455))), getSummonerSpellFromIcon(getSummonerSpellIcon((1253, 455)))])
        results['summoner_spells'][0].append([getSummonerSpellFromIcon(getSummonerSpellIcon((1488, 455))), getSummonerSpellFromIcon(getSummonerSpellIcon((1535, 455)))])
        results['summoner_spells'][1].append([getSummonerSpellFromIcon(getSummonerSpellIcon((362, 1006))), getSummonerSpellFromIcon(getSummonerSpellIcon((409, 1006)))])
        results['summoner_spells'][1].append([getSummonerSpellFromIcon(getSummonerSpellIcon((644, 1006))), getSummonerSpellFromIcon(getSummonerSpellIcon((690, 1006)))])
        results['summoner_spells'][1].append([getSummonerSpellFromIcon(getSummonerSpellIcon((925, 1006))), getSummonerSpellFromIcon(getSummonerSpellIcon((972, 1006)))])
        results['summoner_spells'][1].append([getSummonerSpellFromIcon(getSummonerSpellIcon((1207, 1006))), getSummonerSpellFromIcon(getSummonerSpellIcon((1253, 1006)))])
        results['summoner_spells'][1].append([getSummonerSpellFromIcon(getSummonerSpellIcon((1488, 1006))), getSummonerSpellFromIcon(getSummonerSpellIcon((1535, 1006)))])
        return results
    
    if(im.getpixel((945, 945))[0:3] == (148, 150, 156)):
        return {'teamfight' : True, "valid" : True}
    
    if(im.getpixel((615, 38))[0:3] != (247, 235, 215) or im.getpixel((672, 38))[0:3] != (201, 37, 38)):
        return False
    
    results = {};
    results['valid'] = True
    results['loading'] = False
    results['teamfight'] = False
    results['players'] = [[], []];
    results['time'] = ocr.imagetostring(im.crop((934, 80, 984, 94))).split(",")
    results['time'] = cint(results['time'][0]) * 60 + int(results['time'][1])
    results['speed'] = cint(ocr.imagetostring(im.crop((700, 862, 730, 876))).replace('x', ''))
    results['events'] = []
    
    #if(im.getpixel((1259, 189))[0:3] == (41, 250, 254) and im.getpixel((1236, 205))[0:3] == (240, 229, 169)):
    #    results['events'].append({'type' : 'dragon', 'team': 0})
    #elif(im.getpixel((1274, 189))[0:3] == (41, 250, 254) and im.getpixel((1251, 205))[0:3] == (240, 229, 169)):
    #    results['events'].append({'type' : 'dragon', 'team': 1})
    
    # Get the event (kill) notifications that appear in the right side for kills, dragons, barons, etc.
    for tr in [(1685, 694), (1685, 625), (1685, 556), (1685, 487)]:
        event = getEvent(im, tr)
        if(event != None):
            results['events'].append(event)
        else:   # Events with many assists are shifted right 3 pixels
            event = getEvent(im, (tr[0]+3, tr[1]))
            if(event == None):
                break
            else:
                results['events'].append(event)
    
    # Get number of towers down for each team
    results['towers'] = [];
    results['towers'].append(int(icon.imageToIconName(im.crop((688, 24, 688+30, 24+30)), "tower").split("-")[-1]))
    results['towers'].append(int(icon.imageToIconName(im.crop((1234, 24, 1234+30, 24+30)), "tower").split("-")[-1]))
    
    # Get the current map position based on the box in the minimap
    camera_box_y = []
    camera_box_y[:] = []
    results['map_position'] = [-1, -1]
    for x in [1630, 1700, 1770, 1840, 1890] + range(1625, 1914):
        prevpixel = (0, 0, 0)
        for y in range(784, 1071):
            pixel = im.getpixel((x, y))[0:3]
            if(pixel == (255, 255, 255) and prevpixel == (255, 255, 255)):
                camera_box_y.append((x, y))
            prevpixel = pixel
        
        if len(camera_box_y) > 0:
            break
    
    if(len(camera_box_y) == 1):
        if(camera_box_y[0][1] < 900):
            camera_box_search_y = camera_box_y[0][1] - 15
            results['map_position'][1] = camera_box_y[0][1] - 16 - 782
        else:
            camera_box_search_y = camera_box_y[0][1] + 15
            results['map_position'][1] = camera_box_y[0][1] + 33 - 782
    elif(len(camera_box_y) > 1):
        camera_box_search_y = min(camera_box_y[0][1], camera_box_y[1][1]) + 15
        results['map_position'][1] = min(camera_box_y[0][1], camera_box_y[1][1]) + 33 - 782
    
    
    camera_box_x = []
    camera_box_x[:] = []
    if(len(camera_box_y) > 0):
        for y in [camera_box_search_y] + range(864, 1075):
            prevpixel = (0, 0, 0)
            for x in range(1625, 1914):
                pixel = im.getpixel((x, y))[0:3]
                if (pixel == (255, 255, 255) and prevpixel == (255, 255, 255)):
                    camera_box_x.append((x, y))
                prevpixel = pixel
                
            if len(camera_box_x) > 0:
                break
        
        if(len(camera_box_x) == 1 and camera_box_x[0][0] < 1720):
            results['map_position'][0] = camera_box_x[0][0] - 51 - 1623
        elif(len(camera_box_x) > 0):
            results['map_position'][0] = camera_box_x[0][0] + 44 - 1623

    
    # Get spectator client states
    if(im.getpixel((638, 867))[0:3] == (165, 166, 165)):
        results['paused'] = True
    else:
        results['paused'] = False
    
    if (im.getpixel((690, 905))[0:3] == (247, 231, 173)):
        results['gold_data_available'] = True
        results['item_data_available'] = False
    else:
        results['gold_data_available'] = False
        results['item_data_available'] = True
    
    if(pixelDiff(im.getpixel((425, 326))[0:3], (195, 250, 249)) < 3 and pixelDiff(im.getpixel((958, 348))[0:3], (243, 223, 184)) < 3 
       and pixelDiff(im.getpixel((1410, 323))[0:3], (116, 175, 186)) < 3):
        results['game_finished'] = True
    else:
        results['game_finished'] = False
    
    #Active Champion Information
    if(im.getpixel((6, 848))[0:3] == (40, 36, 40) and im.getpixel((309, 849))[0:3] == (178, 184, 186)):
        def greenthreshold(img):
            width, _ = img.size
            for i, px in enumerate(img.getdata()):
                y = i // width
                x = i % width
                if px[1] > 130:
                    img.putpixel((x, y), (255, 255, 255))
                else:
                    img.putpixel((x, y), (0, 0, 0))
            return img
        
        results['active_champion'] = {}
        results['active_champion']['champion'] = getChampionFromIcon(im.crop((16, 856, 49, 889)))
        champion_overlay_active = (im.getpixel((647, 401))[0:3] == (8, 8, 8) and im.getpixel((1272, 401))[0:3] == (41, 40, 41))
        results['active_champion']['hitpoints'] = ocr.imagetostring(greenthreshold(im.crop((851, 458, 953, 472)))) if champion_overlay_active else None
        results['active_champion']['attack_damage'] = ocr.imagetostring(greenthreshold(im.crop((910, 505, 953, 520)))) if champion_overlay_active else None
        results['active_champion']['mana'] = ocr.imagetostring(greenthreshold(im.crop((1160, 458, 1265, 473)))) if champion_overlay_active and results['active_champion']['champion'] not in config.MANALESS_CHAMPS else None
        results['active_champion']['ability_power'] = ocr.imagetostring(greenthreshold(im.crop((1225, 505, 1265, 520)))) if champion_overlay_active else None
        results['active_champion']['armor'] = ocr.imagetostring(greenthreshold(im.crop((1225, 627, 1265, 642)))) if champion_overlay_active else None
        results['active_champion']['magic_resist'] = ocr.imagetostring(greenthreshold(im.crop((1225, 651, 1265, 666)))) if champion_overlay_active else None
        results['active_champion']['overlay_active'] = True if champion_overlay_active else False
    else:
        results['active_champion'] = None
    
    results['inhibitors'] = [{}, {}];
    
    # Blue Inhibitors
    if(im.getpixel((1696, 1049))[0:3] == (147, 147, 143) and im.getpixel((1697, 1049))[0:3] == (83, 75, 66)):
        results['inhibitors'][0]['bottom'] = False
    elif(im.getpixel((1696, 1049))[0:3] == (25, 165, 236) and im.getpixel((1697, 1049))[0:3] == (21, 139, 201)):
        results['inhibitors'][0]['bottom'] = True
    else:
        results['inhibitors'][0]['bottom'] = None
    
    if(im.getpixel((1688, 1013))[0:3] == (146, 148, 146) and im.getpixel((1689, 1013))[0:3] == (108, 112, 108)):
        results['inhibitors'][0]['middle'] = False
    elif(im.getpixel((1688, 1013))[0:3] == (33, 153, 208) and im.getpixel((1689, 1013))[0:3] == (10, 108, 176)):
        results['inhibitors'][0]['middle'] = True
    else:
        results['inhibitors'][0]['middle'] = None
    
    if(im.getpixel((1649, 1005))[0:3] == (126, 127, 126) and im.getpixel((1650, 1005))[0:3] == (72, 73, 72)):
        results['inhibitors'][0]['top'] = False
    elif(im.getpixel((1649, 1005))[0:3] == (22, 108, 163) and im.getpixel((1650, 1005))[0:3] == (25, 78, 147)):
        results['inhibitors'][0]['top'] = True
    else:
        results['inhibitors'][0]['top'] = None
    
    # Purple Inhibitors
    if(im.getpixel((1900, 846))[0:3] == (90, 89, 88) and im.getpixel((1901, 846))[0:3] == (142, 140, 134)):
        results['inhibitors'][1]['bottom'] = False
    elif(im.getpixel((1900, 846))[0:3] == (109, 44, 137) and im.getpixel((1901, 846))[0:3] == (183, 9, 196)):
        results['inhibitors'][1]['bottom'] = True
    else:
        results['inhibitors'][1]['bottom'] = None
    
    if(im.getpixel((1861, 839))[0:3] == (128, 127, 125) and im.getpixel((1862, 839))[0:3] == (77, 70, 65)):
        results['inhibitors'][1]['middle'] = False
    elif(im.getpixel((1861, 839))[0:3] == (229, 21, 237) and im.getpixel((1862, 839))[0:3] == (245, 38, 246)):
        results['inhibitors'][1]['middle'] = True
    else:
        results['inhibitors'][1]['middle'] = None
        
    if(im.getpixel((1853, 803))[0:3] == (124, 126, 124) and im.getpixel((1854, 803))[0:3] == (81, 81, 80)):
        results['inhibitors'][1]['top'] = False
    elif(im.getpixel((1853, 803))[0:3] == (167, 9, 182) and im.getpixel((1854, 803))[0:3] == (127, 11, 146)):
        results['inhibitors'][1]['top'] = True
    else:
        results['inhibitors'][1]['top'] = None
    
    #Information on each of the ten champions
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 218, 85, 228))) if im.getpixel((86, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((785, 931, 880, 946))),
         "minions" : ocr.imagetostring(im.crop((884, 930, 927, 946))),
         "dead" : True if im.getpixel((86, 238))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 930, 762, 946))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 926, 954, 949))),
         "items" : getItems(im, (590, 925)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 324, 85, 334))) if im.getpixel((86, 348))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((785, 958, 880, 981))),
         "minions" : ocr.imagetostring(im.crop((884, 958, 927, 981))),
         "dead" : True if im.getpixel((86, 348))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 958, 762, 981))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 957, 954, 980))),
         "items" : getItems(im, (590, 956)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 430, 85, 440))) if im.getpixel((86, 448))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((785, 992, 880, 1012))),
         "minions" : ocr.imagetostring(im.crop((884, 992, 927, 1012))),
         "dead" : True if im.getpixel((86, 448))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 992, 762, 1012))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 987, 954, 1010))),
         "items" : getItems(im, (590, 986)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 536, 85, 546))) if im.getpixel((86, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((785, 1023, 880, 1043))),
         "minions" : ocr.imagetostring(im.crop((884, 1023, 927, 1043))),
         "dead" : True if im.getpixel((86, 560))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 1023, 762, 1043))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 1018, 954, 1041))),
         "items" : getItems(im, (590, 1017)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 642, 85, 652))) if im.getpixel((86, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((785, 1053, 880, 1073))),
         "minions" : ocr.imagetostring(im.crop((884, 1053, 927, 1073))),
         "dead" : True if im.getpixel((86, 666))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 1053, 762, 1073))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 1049, 954, 1072))),
         "items" : getItems(im, (590, 1048)) if results['item_data_available'] else None
         })
    
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 218, 1879, 228))) if im.getpixel((1879, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1045, 931, 1140, 946))),
         "minions" : ocr.imagetostring(im.crop((992, 930, 1033, 946))),
         "dead" : True if im.getpixel((1879, 238))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 930, 1337, 946))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 926, 990, 950))),
         "items" : getItems(im, (1145, 925)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 324, 1879, 334))) if im.getpixel((1879, 344))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1045, 958, 1140, 981))),
         "minions" : ocr.imagetostring(im.crop((992, 958, 1033, 981))),
         "dead" : True if im.getpixel((1879, 344))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 958, 1337, 981))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 957, 990, 981))),
         "items" : getItems(im, (1145, 956)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 430, 1879, 440))) if im.getpixel((1879, 450))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1045, 992, 1140, 1012))),
         "minions" : ocr.imagetostring(im.crop((992, 992, 1033, 1012))),
         "dead" : True if im.getpixel((1879, 450))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 992, 1337, 1012))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 987, 990, 1011))),
         "items" : getItems(im, (1145, 986)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 536, 1879, 546))) if im.getpixel((1879, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1045, 1023, 1140, 1043))),
         "minions" : ocr.imagetostring(im.crop((992, 1023, 1033, 1043))),
         "dead" : True if im.getpixel((1879, 560))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 1023, 1337, 1043))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 1018, 990, 1042))),
         "items" : getItems(im, (1145, 1017)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 642, 1879, 652))) if im.getpixel((1879, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1045, 1053, 1140, 1073))),
         "minions" : ocr.imagetostring(im.crop((992, 1053, 1033, 1073))),
         "dead" : True if im.getpixel((1879, 666))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 1053, 1337, 1073))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 1049, 990, 1073))),
         "items" : getItems(im, (1145, 1048)) if results['item_data_available'] else None
         })
    
    errmsg = ""
    results['teams'] = [{}, {}]
    for team, _ in enumerate(results['teams']):
        results['teams'][team]['gold'] = 0 if results['gold_data_available'] else None
        results['teams'][team]['kills'] = 0
        results['teams'][team]['towers'] = results['towers'][team]
    
    for team, _ in enumerate(results['players']):
        for player, _ in enumerate(results['players'][team]):
            if(results['gold_data_available']):
                results['players'][team][player]['gold'] = results['players'][team][player]['gold'].replace(",", "")
                results['players'][team][player]['current_gold'] = cint(results['players'][team][player]['gold'].split("(")[0])
                results['players'][team][player]['total_gold'] = cint(results['players'][team][player]['gold'].split("(")[-1].replace(")", ""))
                results['teams'][team]['gold'] += results['players'][team][player]['total_gold']
                if(results['players'][team][player]['current_gold'] > results['players'][team][player]['total_gold']):
                    errmsg = "Total gold greater than current gold."
                    valid = False
                
            results['players'][team][player]['kda'] = results['players'][team][player]['kda'].split("/")
            results['players'][team][player]['kills'] = cint(results['players'][team][player]['kda'][0])
            results['players'][team][player]['deaths'] = cint(results['players'][team][player]['kda'][1])
            results['players'][team][player]['assists'] = cint(results['players'][team][player]['kda'][2])
            
            results['players'][team][player]['level'] = cint(results['players'][team][player]['level'])
            results['players'][team][player]['minions'] = cint(results['players'][team][player]['minions'])
            
            if(results['players'][team][player]['level'] and results['players'][team][player]['level'] > 18):
                errmsg = "Player level above 18."
                valid = False
            
            if last:
                if(results['players'][team][player]['minions'] < results['players'][team][player]['minions']):
                    errmsg = "Some how player "+str((team, player))+" CS decreased!"
                    valid = False
            
            results['teams'][team]['kills'] += int(results['players'][team][player]['kills'])
    
    # Check to see if the teams' gold are sane values
    if(results['teams'][0]['gold'] > 200000 or results['teams'][1]['gold'] > 200000):
        errmsg = "A team's gold is absurdly high."
        valid = False
        
    if last:
        if(results['gold_data_available'] and last['gold_data_available'] and (results['teams'][0]['gold'] < last['teams'][0]['gold'] or results['teams'][1]['gold'] < last['teams'][1]['gold'])):
            errmsg = "Somehow, a team's gold decreased!"
            valid = False
    
    
    if(valid == True):
        last = results
        return results
    else:
        results['valid'] = False
        results['errmsg'] = errmsg
        return results