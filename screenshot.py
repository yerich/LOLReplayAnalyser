from __future__ import division
import ocr
import re
import icon
import Image
import config
from icon import pixelDiff

def cint(s):
    if s == '' or s == None:
        return 0
    
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

# Returns an array of items, given the (x, y) coordinate (where (0, 0) is top-left) 
# of the top-left pixel of the first item in the bar
def getItems(im, tl):
    items = []
    for i in [im.crop((tl[0], tl[1], tl[0]+25, tl[1]+25)), im.crop((tl[0]+27, tl[1], tl[0]+52, tl[1]+25)),
              im.crop((tl[0]+54, tl[1], tl[0]+79, tl[1]+25)), im.crop((tl[0]+81, tl[1], tl[0]+106, tl[1]+25)),
              im.crop((tl[0]+108, tl[1], tl[0]+133, tl[1]+25)), im.crop((tl[0]+135, tl[1], tl[0]+160, tl[1]+25))]:
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

def getChampionFromIcon(im):
    icon_name = icon.imageToIconName(im, "champion")
    if icon_name == "blank":
        return None
    return icon_name.replace("champion-", "")

# Returns a dict of data retrieved from a screenshot. If staticdata=true, then
# static data, such as champion names, summoner spell, etc. will also be retrieved.
def getScreenshotData(im, staticdata = False):
    im = im.convert("RGB")
    width, height = im.size
    valid = True    # Set to false when there's some blantantly incorrect OCR'd value
    
    if(width != 1920 or height != 1080):
        print "Error: screenshot must be 1920x1080px exactly."
        return False
    
    if(im.getpixel((0, 300))[0:3] == (0, 0, 0) and im.getpixel((1900, 300))[0:3] == (0, 0, 0)):
        return {'loading' : True}
    
    if(im.getpixel((945, 945))[0:3] == (148, 150, 156)):
        return {'teamfight' : True}
    
    if(im.getpixel((615, 38))[0:3] != (247, 235, 215) or im.getpixel((672, 38))[0:3] != (201, 37, 38)):
        return False
    
    results = {};
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
    
    if(im.getpixel((638, 867))[0:3] == (165, 166, 165)):
        results['paused'] = True
    else:
        results['paused'] = False
    
    if (im.getpixel((674, 905))[0:3] == (247, 231, 173)):
        results['gold_data_available'] = True
        results['item_data_available'] = False
    else:
        results['gold_data_available'] = False
        results['item_data_available'] = True
    
    if(im.getpixel((425, 326))[0:3] == (195, 250, 249) and im.getpixel((958, 348))[0:3] == (243, 223, 184)):
        results['game_finished'] = True
    else:
        results['game_finished'] = False
    
    #Active Champion Information
    if(im.getpixel((314, 846))[0:3] == (39, 34, 40) and im.getpixel((4, 846))[0:3] == (50, 45, 50)):
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
    
    # Inhibitors
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
    
    #Information on each of the ten champions
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 218, 85, 228))) if im.getpixel((86, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 931, 869, 946))),
         "minions" : ocr.imagetostring(im.crop((884, 930, 919, 946))),
         "dead" : True if im.getpixel((86, 238))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 930, 762, 946))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 926, 954, 949))),
         "items" : getItems(im, (591, 926)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 324, 85, 334))) if im.getpixel((86, 348))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 958, 869, 981))),
         "minions" : ocr.imagetostring(im.crop((884, 958, 919, 981))),
         "dead" : True if im.getpixel((86, 348))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 958, 762, 981))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 957, 954, 980))),
         "items" : getItems(im, (591, 956)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 430, 85, 440))) if im.getpixel((86, 448))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 992, 869, 1012))),
         "minions" : ocr.imagetostring(im.crop((884, 992, 919, 1012))),
         "dead" : True if im.getpixel((86, 448))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 992, 762, 1012))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 987, 954, 1010))),
         "items" : getItems(im, (591, 987)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 536, 85, 546))) if im.getpixel((86, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 1023, 869, 1043))),
         "minions" : ocr.imagetostring(im.crop((884, 1023, 919, 1043))),
         "dead" : True if im.getpixel((86, 560))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 1023, 762, 1043))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 1018, 954, 1041))),
         "items" : getItems(im, (591, 1017)) if results['item_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 642, 85, 652))) if im.getpixel((86, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 1053, 869, 1073))),
         "minions" : ocr.imagetostring(im.crop((884, 1053, 919, 1073))),
         "dead" : True if im.getpixel((86, 666))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 1053, 762, 1073))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((931, 1049, 954, 1072))),
         "items" : getItems(im, (591, 1048)) if results['item_data_available'] else None
         })
    
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 218, 1879, 228))) if im.getpixel((1879, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 931, 1140, 946))),
         "minions" : ocr.imagetostring(im.crop((997, 930, 1037, 946))),
         "dead" : True if im.getpixel((1879, 238))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 930, 1337, 946))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 926, 990, 950))),
         "items" : getItems(im, (1170, 926)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 324, 1879, 334))) if im.getpixel((1879, 344))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 958, 1140, 981))),
         "minions" : ocr.imagetostring(im.crop((997, 958, 1037, 981))),
         "dead" : True if im.getpixel((1879, 344))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 958, 1337, 981))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 957, 990, 981))),
         "items" : getItems(im, (1170, 956)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 430, 1879, 440))) if im.getpixel((1879, 450))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 992, 1140, 1012))),
         "minions" : ocr.imagetostring(im.crop((997, 992, 1037, 1012))),
         "dead" : True if im.getpixel((1879, 450))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 992, 1337, 1012))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 987, 990, 1011))),
         "items" : getItems(im, (1170, 987)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 536, 1879, 546))) if im.getpixel((1879, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 1023, 1140, 1043))),
         "minions" : ocr.imagetostring(im.crop((997, 1023, 1037, 1043))),
         "dead" : True if im.getpixel((1879, 560))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 1023, 1337, 1043))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 1018, 990, 1042))),
         "items" : getItems(im, (1170, 1017)) if results['item_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 642, 1879, 652))) if im.getpixel((1879, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 1053, 1140, 1073))),
         "minions" : ocr.imagetostring(im.crop((997, 1053, 1037, 1073))),
         "dead" : True if im.getpixel((1879, 666))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 1053, 1337, 1073))) if results['gold_data_available'] else None,
         "champion" : getChampionFromIcon(im.crop((966, 1049, 990, 1073))),
         "items" : getItems(im, (1170, 1048)) if results['item_data_available'] else None
         })
    
    results['teams'] = [{}, {}]
    for team, _ in enumerate(results['teams']):
        results['teams'][team]['gold'] = 0 if results['gold_data_available'] else None
        results['teams'][team]['kills'] = 0
    
    for team, _ in enumerate(results['players']):
        for player, _ in enumerate(results['players'][team]):
            if(results['gold_data_available']):
                results['players'][team][player]['gold'] = results['players'][team][player]['gold'].replace(",", "")
                results['players'][team][player]['current_gold'] = cint(results['players'][team][player]['gold'].split("(")[0])
                results['players'][team][player]['total_gold'] = cint(results['players'][team][player]['gold'].split("(")[-1].replace(")", ""))
                results['teams'][team]['gold'] += results['players'][team][player]['total_gold']
                
            results['players'][team][player]['kda'] = results['players'][team][player]['kda'].split("/")
            results['players'][team][player]['kills'] = cint(results['players'][team][player]['kda'][0])
            results['players'][team][player]['deaths'] = cint(results['players'][team][player]['kda'][1])
            results['players'][team][player]['assists'] = cint(results['players'][team][player]['kda'][2])
            results['players'][team][player]['level'] = cint(results['players'][team][player]['level'])
            
            if(results['players'][team][player]['level'] and results['players'][team][player]['level'] > 18):
                valid = False
            
            results['teams'][team]['kills'] += int(results['players'][team][player]['kills'])
    
    # Check to see if the teams' gold are sane values
    if(results['teams'][0]['gold'] > 200000 or results['teams'][1]['gold'] > 200000):
        valid = False
    
    if(valid == True):
        return results
    else:
        return None