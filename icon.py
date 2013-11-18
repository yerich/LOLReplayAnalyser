# Icon processing
# Resize each icon to a 4x4 image. To see if a given icon matches one we have, also
# resize it to a 4x4 image and compare each pixel

from __future__ import division
import Image
from os import listdir
from os.path import isfile, join
import pickle
import operator
import os

iconData = None

# Get the difference i color between two pixels. The difference is calculated by adding
# the sum of differences for each layer (RGB)
def pixelDiff(pixel, color):
    # This is for performance purposes; this function is called thousands of times per second
    if(pixel[0] > color[0]):
        if(pixel[1] > color[1]):
            if(pixel[2] > color[2]):
                return (pixel[0] - color[0]) + (pixel[1] - color[1]) + (pixel[2] - color[2])
            else:
                return (pixel[0] - color[0]) + (pixel[1] - color[1]) - (pixel[2] - color[2])
        else:
            if(pixel[2] > color[2]):
                return (pixel[0] - color[0]) - (pixel[1] - color[1]) + (pixel[2] - color[2])
            else:
                return (pixel[0] - color[0]) - (pixel[1] - color[1]) - (pixel[2] - color[2])
    else:
        if(pixel[1] > color[1]):
            if(pixel[2] > color[2]):
                return -(pixel[0] - color[0]) + (pixel[1] - color[1]) + (pixel[2] - color[2])
            else:
                return -(pixel[0] - color[0]) + (pixel[1] - color[1]) - (pixel[2] - color[2])
        else:
            if(pixel[2] > color[2]):
                return -(pixel[0] - color[0]) - (pixel[1] - color[1]) + (pixel[2] - color[2])
            else:
                return -(pixel[0] - color[0]) - (pixel[1] - color[1]) - (pixel[2] - color[2])

def iconDataDiff(icon, data):
    # Expanded out loop to save running time
    return pixelDiff(icon[0], data[0]) + \
        pixelDiff(icon[1], data[1]) + \
        pixelDiff(icon[2], data[2]) + \
        pixelDiff(icon[3], data[3]) + \
        pixelDiff(icon[4], data[4]) + \
        pixelDiff(icon[5], data[5]) + \
        pixelDiff(icon[6], data[6]) + \
        pixelDiff(icon[7], data[7]) + \
        pixelDiff(icon[8], data[8]) + \
        pixelDiff(icon[9], data[9]) + \
        pixelDiff(icon[10], data[10]) + \
        pixelDiff(icon[11], data[11]) + \
        pixelDiff(icon[12], data[12]) + \
        pixelDiff(icon[13], data[13]) + \
        pixelDiff(icon[14], data[14]) + \
        pixelDiff(icon[15], data[15])

def generateIconDataFile():
    icons = [ f for f in listdir("icons/") if isfile(join("icons/",f)) and f.split(".")[-1] == "png" ]
    
    icon_dat = {}
    for i in icons:
        imdat = imageToIconData(Image.open("icons/"+i))
        icon_dat[i.split(".")[0]] = imdat
        
    pickle.dump(icon_dat, open("icons/icons.dat", "w"))
    return icon_dat

def getIconData():
    global iconData;
    if iconData != None:
        return iconData
    
    if isfile("icons/icons.dat"):
        iconData = pickle.load(open("icons/icons.dat", "r"))
    else:
        iconData = generateIconDataFile()
        
    return iconData

def imageToIconData(im):
    imdat = im.resize((4, 4), Image.ANTIALIAS).getdata()
    
    dat = []
    for i in range(0, 4):
        for j in range(0, 4):
            dat.append(imdat[i*4 + j][0:3])
    
    return dat

# Convert an image to the name of an icon
def imageToIconName(im, restrict = None):
    imdat = imageToIconData(im)
    icon_dat = getIconData()
    
    differences = {};
    for _, name in enumerate(icon_dat):
        if restrict and not name.startswith(restrict) and name != "blank":
            continue
        differences[name] = iconDataDiff(imdat, icon_dat[name])
    
    matches = sorted(differences.iteritems(), key=operator.itemgetter(1))
    #print matches[0][0], matches[0][1], matches[1][0], matches[1][1], matches[2][0], matches[2][1]
    return matches[0][0]

if __name__ == "__main__":
    print "Generating icon data file."
    dat = generateIconDataFile()
    print "Icon data file generated. "+str(len(dat))+" icons in database."