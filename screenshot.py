from __future__ import division
import ocr

def getScreenshotData(im):
    width, height = im.size
    
    if(width != 1920 or height != 1080):
        print "Error: screenshot must be 1920x1080px exactly."
        return False
    
    if(im.getpixel((948, 538))[0:3] == (212, 161, 89) and im.getpixel((974, 537))[0:3] == (216, 163, 90)):
        return {'loading' : True}
    
    if(im.getpixel((615, 38))[0:3] != (247, 235, 215) or im.getpixel((672, 38))[0:3] != (201, 37, 38)):
        print "Error: not a valid League of Legends screenshot"
        return False
    
    results = {};
    results['loading'] = False
    results['players'] = [[], []];
    results['time'] = ocr.imagetostring(im.crop((934, 80, 984, 94))).split(",")
    results['time'] = int(results['time'][0]) * 60 + int(results['time'][1])
    results['speed'] = int(ocr.imagetostring(im.crop((705, 862, 715, 874))))
    if (im.getpixel((674, 905))[0:3] == (247, 231, 173)):
        results['gold_data_available'] = True
        results['item_data_available'] = False
    else:
        results['gold_data_available'] = False
        results['item_data_available'] = True
    
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 218, 85, 228))) if im.getpixel((86, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 931, 869, 946))),
         "minions" : ocr.imagetostring(im.crop((884, 930, 919, 946))),
         "dead" : True if im.getpixel((86, 238))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 930, 762, 946))) if results['gold_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 324, 85, 334))) if im.getpixel((86, 348))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 958, 869, 981))),
         "minions" : ocr.imagetostring(im.crop((884, 958, 919, 981))),
         "dead" : True if im.getpixel((86, 348))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 958, 762, 981))) if results['gold_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 430, 85, 440))) if im.getpixel((86, 448))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 992, 869, 1012))),
         "minions" : ocr.imagetostring(im.crop((884, 992, 919, 1012))),
         "dead" : True if im.getpixel((86, 448))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 992, 762, 1012))) if results['gold_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 536, 85, 546))) if im.getpixel((86, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 1023, 869, 1043))),
         "minions" : ocr.imagetostring(im.crop((884, 1023, 919, 1043))),
         "dead" : True if im.getpixel((86, 560))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 1023, 762, 1043))) if results['gold_data_available'] else None
         })
    results['players'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 642, 85, 652))) if im.getpixel((86, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 1053, 869, 1073))),
         "minions" : ocr.imagetostring(im.crop((884, 1053, 919, 1073))),
         "dead" : True if im.getpixel((86, 666))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((618, 1053, 762, 1073))) if results['gold_data_available'] else None
         })
    
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 218, 1879, 228))) if im.getpixel((1879, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 931, 1140, 946))),
         "minions" : ocr.imagetostring(im.crop((997, 930, 1037, 946))),
         "dead" : True if im.getpixel((1879, 238))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 930, 1337, 946))) if results['gold_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 324, 1879, 334))) if im.getpixel((1879, 344))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 958, 1140, 981))),
         "minions" : ocr.imagetostring(im.crop((997, 958, 1037, 981))),
         "dead" : True if im.getpixel((1879, 344))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 958, 1337, 981))) if results['gold_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 430, 1879, 440))) if im.getpixel((1879, 450))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 992, 1140, 1012))),
         "minions" : ocr.imagetostring(im.crop((997, 992, 1037, 1012))),
         "dead" : True if im.getpixel((1879, 450))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 992, 1337, 1012))) if results['gold_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 536, 1879, 546))) if im.getpixel((1879, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 1023, 1140, 1043))),
         "minions" : ocr.imagetostring(im.crop((997, 1023, 1037, 1043))),
         "dead" : True if im.getpixel((1879, 560))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 1023, 1337, 1043))) if results['gold_data_available'] else None
         })
    results['players'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 642, 1879, 652))) if im.getpixel((1879, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 1053, 1140, 1073))),
         "minions" : ocr.imagetostring(im.crop((997, 1053, 1037, 1073))),
         "dead" : True if im.getpixel((1879, 666))[0] == 0 else False,
         "gold" : ocr.imagetostring(im.crop((1196, 1053, 1337, 1073))) if results['gold_data_available'] else None
         })
    
    results['teams'] = [{}, {}]
    for team, _ in enumerate(results['teams']):
        results['teams'][team]['gold'] = 0 if results['gold_data_available'] else None
    
    for team, _ in enumerate(results['players']):
        for player, _ in enumerate(results['players'][team]):
            if(results['gold_data_available']):
                results['players'][team][player]['gold'] = results['players'][team][player]['gold'].replace(",", "")
                results['players'][team][player]['current_gold'] = int(results['players'][team][player]['gold'].split("(")[0])
                results['players'][team][player]['total_gold'] = int(results['players'][team][player]['gold'].split("(")[1].replace(")", ""))
                results['teams'][team]['gold'] += results['players'][team][player]['total_gold']
            results['players'][team][player]['kda'] = results['players'][team][player]['kda'].split("/")
            results['players'][team][player]['kills'] = int(results['players'][team][player]['kda'][0])
            results['players'][team][player]['deaths'] = int(results['players'][team][player]['kda'][1])
            results['players'][team][player]['assists'] = int(results['players'][team][player]['kda'][2])
            
            
    return results