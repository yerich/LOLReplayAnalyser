from __future__ import division
import ocr
import Image

def getScreenshotData(im):
    results = {};
    results['teams'] = [[], []];
    results['time'] = ocr.imagetostring(im.crop((934, 80, 984, 94))).split(",")
    results['time'] = int(results['time'][0]) * 60 + int(results['time'][1])
    return results

print getScreenshotData(Image.open("tests/screenshot1.png"))