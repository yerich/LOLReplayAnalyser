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

def pixelDiff(pixel, color):
    return abs(pixel[0]-color[0])+abs(pixel[1]-color[1])+abs(pixel[2]-color[2])

def iconDataDiff(icon, data):
    return sum([ pixelDiff(icon[i], data[i]) for i, _ in enumerate(icon) ])

def generateIconDataFile():
    icons = [ f for f in listdir("icons/") if isfile(join("icons/",f)) and f.split(".")[-1] == "png" ]
    
    icon_dat = {}
    for i in icons:
        imdat = imageToIconData(Image.open("icons/"+i))
        icon_dat[i.split(".")[0]] = imdat
        
    pickle.dump(icon_dat, open("icons/icons.dat", "w"))
    return icon_dat

def getIconData():
    if isfile("icons/icons.dat"):
        return pickle.load(open("icons/icons.dat", "r"))
    else:
        return generateIconDataFile()

def imageToIconData(im):
    imdat = im.resize((4, 4), Image.ANTIALIAS).getdata()
    
    dat = []
    for i in range(0, 4):
        for j in range(0, 4):
            dat.append(imdat[i*4 + j][0:3])
    
    return dat

def imageToIconName(im):
    imdat = imageToIconData(im)
    icon_dat = getIconData()
    
    differences = {};
    for dat, name in enumerate(icon_dat):
        differences[name] = iconDataDiff(imdat, icon_dat[name])
    
    matches = sorted(differences.iteritems(), key=operator.itemgetter(1))
    if(matches[0][1] < 200):
        return matches[0][0]

if __name__ == "__main__":
    generateIconDataFile()