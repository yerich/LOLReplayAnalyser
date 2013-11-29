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
import ImageDraw

iconData = None
iconFolder = "icons/"

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
    icons = [ f for f in listdir(iconFolder) if isfile(join(iconFolder,f)) and f.split(".")[-1] == "png" ]
    
    icon_dat = {}
    for i in icons:
        imdat = imageToIconData(Image.open(iconFolder+i))
        icon_dat[i.split(".")[0]] = imdat
        
    pickle.dump(icon_dat, open(iconFolder+"icons.dat", "w"))
    return icon_dat

def getIconData():
    global iconData;
    if iconData != None:
        return iconData
    
    if isfile(iconFolder+"icons.dat"):
        iconData = pickle.load(open(iconFolder+"icons.dat", "r"))
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

# Utility function that is used to automatically generated icons for activated versions of items
# on cooldown
def generateActivatedItemIcons():
    icons = [ f for f in listdir("icons_activated/") if isfile(join("icons_activated/",f)) and f.split(".")[-1] == "png" ]
    
    for i in icons:
        filename = ".".join(i.split(".")[0:-1])
        
        im = Image.open("icons_activated/"+i).convert("RGBA")
        color_layer = Image.new('RGBA', im.size, (0, 0, 0))
        
        line_layer = Image.new('RGBA', im.size, (109, 109, 109))
        alpha_mask = Image.new('L', im.size, 0)
        alpha_mask_draw = ImageDraw.Draw(alpha_mask)
        alpha_mask_draw.line([(im.size[0]//2, im.size[1]//2), (im.size[0]//2, 0)], fill=186, width = 3)
        
        newim = Image.blend(im, color_layer, 0.51)
        newim = Image.composite(line_layer, newim, alpha_mask)
        newim.save("icons_activated/"+filename+"-activated.png")
        
        newim = Image.blend(im, color_layer, 0.29)
        newim = Image.composite(line_layer, newim, alpha_mask)
        newim.save("icons_activated/"+filename+"-activated-done.png")
        
        rect_layer = Image.new('RGBA', im.size, (0, 0, 0))
        rect_alpha_mask = Image.new("L", im.size, 0)
        rect_alpha_mask_draw = ImageDraw.Draw(rect_alpha_mask)
        rect_alpha_mask_draw.rectangle((0, 0, im.size[0]//2, im.size[1]), fill=131)
        rect_alpha_mask_draw.rectangle((im.size[0]//2+1, 0, im.size[0], im.size[1]), fill=75)
        
        newim = Image.composite(rect_layer, im, rect_alpha_mask)
        newim = Image.composite(line_layer, newim, alpha_mask)
        newim.save("icons_activated/"+filename+"-activated-half.png")
        
def setIconFolder(folder = "icons/"):
    global iconFolder
    iconFolder = folder
        
if __name__ == "__main__":
    print "Generating icon data file."
    dat = generateIconDataFile()
    print "Icon data file generated. "+str(len(dat))+" icons in database."
    
    generateActivatedItemIcons()