from __future__ import division
import ocr
import re
import icon

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
    
def getChampionFromIcon(im):
    icon_name = icon.imageToIconName(im, "champion")
    if icon_name == "blank":
        return None
    return icon_name.replace("champion-", "")

# Returns a dict of data retrieved from a screenshot. If staticdata=true, then
# static data, such as champion names, summoner spell, etc. will also be retrieved.
# TODO: implement staticdata
def getScreenshotData(im, staticdata = False):
    width, height = im.size
    
    if(width != 1920 or height != 1080):
        print "Error: screenshot must be 1920x1080px exactly."
        return False
    
    if(im.getpixel((948, 538))[0:3] == (212, 161, 89) and im.getpixel((974, 537))[0:3] == (216, 163, 90)):
        return {'loading' : True}
    
    if(im.getpixel((615, 38))[0:3] != (247, 235, 215) or im.getpixel((672, 38))[0:3] != (201, 37, 38)):
        return False
    
    results = {};
    results['loading'] = False
    results['players'] = [[], []];
    results['time'] = ocr.imagetostring(im.crop((934, 80, 984, 94))).split(",")
    results['time'] = cint(results['time'][0]) * 60 + int(results['time'][1])
    results['speed'] = cint(ocr.imagetostring(im.crop((700, 862, 730, 876))).replace('x', ''))
    results['events'] = []
    
    if(im.getpixel((1259, 189))[0:3] == (41, 250, 254) and im.getpixel((1236, 205))[0:3] == (240, 229, 169)):
        results['events'].append({'type' : 'dragon', 'team': 0})
    elif(im.getpixel((1274, 189))[0:3] == (41, 250, 254) and im.getpixel((1251, 205))[0:3] == (240, 229, 169)):
        results['events'].append({'type' : 'dragon', 'team': 1})
    
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
            results['teams'][team]['kills'] += int(results['players'][team][player]['kills'])
            
            
    return results