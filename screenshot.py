from __future__ import division
import ocr
import Image
import pprint
import time

def getScreenshotData(im):
    width, height = im.size
    
    if(width != 1920 or height != 1080):
        print "Error: screenshot must be 1920x1080px exactly."
        return False
    
    results = {};
    results['teams'] = [[], []];
    results['time'] = ocr.imagetostring(im.crop((934, 80, 984, 94))).split(",")
    results['time'] = int(results['time'][0]) * 60 + int(results['time'][1])
    results['speed'] = int(ocr.imagetostring(im.crop((705, 862, 715, 874))))
    if (im.getpixel((674, 905))[0:3] == (274, 231, 173)):
        results['gold_data_available'] = True
        results['item_data_available'] = False
    else:
        results['gold_data_available'] = False
        results['item_data_available'] = True
    
    results['teams'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 218, 85, 228))) if im.getpixel((86, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 931, 869, 946))),
         "minions" : ocr.imagetostring(im.crop((884, 930, 919, 946))),
         "gold" : ocr.imagetostring(im.crop((608, 930, 722, 946))) if results['gold_data_available'] else None
         })
    results['teams'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 324, 85, 334))) if im.getpixel((86, 348))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 958, 869, 981))),
         "minions" : ocr.imagetostring(im.crop((884, 958, 919, 981))),
         "gold" : ocr.imagetostring(im.crop((608, 958, 722, 981))) if results['gold_data_available'] else None
         })
    results['teams'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 430, 85, 440))) if im.getpixel((86, 254))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 992, 869, 1012))),
         "minions" : ocr.imagetostring(im.crop((884, 992, 919, 1012))),
         "gold" : ocr.imagetostring(im.crop((608, 992, 722, 1012))) if results['gold_data_available'] else None
         })
    results['teams'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 536, 85, 546))) if im.getpixel((86, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 1023, 869, 1043))),
         "minions" : ocr.imagetostring(im.crop((884, 1023, 919, 1043))),
         "gold" : ocr.imagetostring(im.crop((608, 1023, 722, 1043))) if results['gold_data_available'] else None
         })
    results['teams'][0].append(
        {"level" : ocr.imagetostring(im.crop((74, 642, 85, 652))) if im.getpixel((86, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((770, 1053, 869, 1073))),
         "minions" : ocr.imagetostring(im.crop((884, 1053, 919, 1073))),
         "gold" : ocr.imagetostring(im.crop((608, 1053, 722, 1073))) if results['gold_data_available'] else None
         })
    
    results['teams'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 218, 1879, 228))) if im.getpixel((1879, 238))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 931, 1140, 946))),
         "minions" : ocr.imagetostring(im.crop((997, 930, 1037, 946))),
         "gold" : ocr.imagetostring(im.crop((1176, 930, 1297, 946))) if results['gold_data_available'] else None
         })
    results['teams'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 324, 1879, 334))) if im.getpixel((1879, 334))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 958, 1140, 981))),
         "minions" : ocr.imagetostring(im.crop((997, 958, 1037, 981))),
         "gold" : ocr.imagetostring(im.crop((1176, 958, 1297, 981))) if results['gold_data_available'] else None
         })
    results['teams'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 430, 1879, 440))) if im.getpixel((1879, 440))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 992, 1140, 1012))),
         "minions" : ocr.imagetostring(im.crop((997, 992, 1037, 1012))),
         "gold" : ocr.imagetostring(im.crop((1176, 992, 1297, 1012))) if results['gold_data_available'] else None
         })
    results['teams'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 536, 1879, 546))) if im.getpixel((1879, 560))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 1023, 1140, 1043))),
         "minions" : ocr.imagetostring(im.crop((997, 1023, 1037, 1043))),
         "gold" : ocr.imagetostring(im.crop((1176, 1023, 1297, 1043))) if results['gold_data_available'] else None
         })
    results['teams'][1].append(
        {"level" : ocr.imagetostring(im.crop((1865, 642, 1879, 652))) if im.getpixel((1879, 666))[0] < 50 else None,
         "kda" : ocr.imagetostring(im.crop((1060, 1053, 1140, 1073))),
         "minions" : ocr.imagetostring(im.crop((997, 1053, 1037, 1073))),
         "gold" : ocr.imagetostring(im.crop((1176, 1053, 1297, 1073))) if results['gold_data_available'] else None
         })
    
    for team, _ in enumerate(results['teams']):
        for player, _ in enumerate(results['teams'][team]):
            if(results['gold_data_available']):
                results['teams'][team][player]['gold'] = results['teams'][team][player]['gold'].replace(",", "")
                results['teams'][team][player]['current_gold'] = results['teams'][team][player]['gold'].split("(")[0]
                results['teams'][team][player]['total_gold'] = results['teams'][team][player]['gold'].split("(")[1].replace(")", "")
            results['teams'][team][player]['kda'] = results['teams'][team][player]['kda'].split("/")
            results['teams'][team][player]['kills'] = results['teams'][team][player]['kda'][0]
            results['teams'][team][player]['deaths'] = results['teams'][team][player]['kda'][1]
            results['teams'][team][player]['assists'] = results['teams'][team][player]['kda'][2]
    return results

pp = pprint.PrettyPrinter(indent=4)
start = time.clock()
pp.pprint(getScreenshotData(Image.open("tests/screenshot2.png")))
print "Finished in " + str((time.clock() - start)*1000)+"ms"