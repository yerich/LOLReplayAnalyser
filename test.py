from __future__ import division
import Image
import numpy
import sys
import time

# Returns 0 (black) or 1 (white) for a pixel tuple, depending on threshold value (betwwen 0 and 100)
def bwthreshold(pixel, threshold):
    return int((sum(pixel)/float(len(pixel))) / 2 > threshold)

def bwmap(func, pixels):
    for i, _ in enumerate(pixels):
        pixels[i] = map(func, pixels[i])
    return pixels

def bwrowhaspixel(row):
    for i in row:
        if i:
            return True
    return False

def bwtrimvertical(pixels):
    valid_rows_top = []
    valid_rows_bot = [];
    for i, row in enumerate(pixels):
        if len(valid_rows_top) > 0 or bwrowhaspixel(row):
            valid_rows_top.append(i)
            
    for i, row in reversed(list(enumerate(pixels))):
        if len(valid_rows_bot) > 0 or bwrowhaspixel(row):
            valid_rows_bot.append(i)
    
    return [row for i, row in enumerate(pixels) if (i in valid_rows_top and i in valid_rows_bot)]

def bwfindglyphs(pixels):
    pixels = bwtranspose(pixels)
    glyphs = []
    first_row = 0
    last_row = 0
    num_empty_rows = 0
    for i, row in enumerate(pixels):
        if(bwrowhaspixel(row)):
            if num_empty_rows > 10:
                glyphs.append(bwtranspose([pixels[last_row - 1]]))
            last_row += 1
            num_empty_rows = 0
        else:
            if(last_row - first_row > 0):
                glyphs.append(bwtranspose(pixels[first_row:last_row]))
            first_row = i+1
            last_row = i+1
            if num_empty_rows > 10:
                glyphs.append(bwtranspose([pixels[last_row - 1]]))
                num_empty_rows = 0
            num_empty_rows += 1
    
    if(last_row - first_row > 0):
        glyphs.append(bwtranspose(pixels[first_row:last_row]))
    return glyphs

def bwtranspose(pixels):
    return map(list, zip(*pixels))

def bwtrim(pixels):
    return bwtranspose(bwtrimvertical(bwtranspose(bwtrimvertical(pixels))))

def bwinvert(pixels):
    return bwmap(lambda x : int(not x), pixels)

# Primitive but fast OCR
def bwglyphtochar(pixels):
    pixels = bwtrimvertical(pixels)
    if len(pixels) == 0:
        return " "
    c = int(len(pixels[0])/2)    #Horizontal center
    m = int(len(pixels)/2)       #Vertical middle
    width = len(pixels[0])
    first_row_count = len([i for i in pixels[0] if i])
    first_row_ratio = first_row_count/float(width)
    last_row_count = len([i for i in pixels[-1] if i])
    last_row_ratio = last_row_count/float(width)
    
    if(pixels[0][c] and pixels[m][0] and pixels[m][-1] and pixels[-1][c] and not pixels[m][c]):
        return '0'
    elif(pixels[0][0] and pixels[0][-1] and pixels[-1][0] and pixels[-1][-1] and pixels[m][0]):
        return '1'
    elif(first_row_ratio > 0.5 and not pixels[0][-1] and pixels[0][c] and pixels[-1][1] and pixels[-1][c] and pixels[-1][-1] and not pixels[m][0]):
        return '2'
    elif(not pixels[0][-1] and pixels[0][c] and not pixels[-1][-1] and pixels[-1][c] and not pixels[m][0] and (not pixels[m][1] or not pixels[m][-1]) and pixels[3][-1] and last_row_ratio > 0.5):
        return '3'
    elif(not pixels[0][0] and not pixels[0][c] and not pixels[-1][0] and not pixels[-1][-1] and first_row_ratio < 0.30 and first_row_ratio > 0 and last_row_ratio < 0.30):
        return '4'
    elif(first_row_ratio > 0.5 and pixels[0][c] and pixels[-1][0] and pixels[-1][c] and not pixels[-1][-1] and not pixels[m][0] and pixels[m][c] and last_row_ratio > 0.5 and pixels[0][0] == pixels[1][0] and pixels[0][0] == pixels[2][0] and pixels[0][0] == pixels[3][0]):
        return '5'
    elif(not pixels[0][0] and not pixels[0][-1] and pixels[m][0] and pixels[m][c] and not pixels[-1][0] and pixels[-1][c] and not pixels[-1][-1] and first_row_ratio < 0.45):
        return '6'
    elif(pixels[0][0] and pixels[0][c] and pixels[0][-1] and not pixels[m][0] and not pixels[m][-1] and not pixels[-1][0] and not pixels[-1][-1]):
        return '7'
    elif(not pixels[0][0] and pixels[0][c] and not pixels[0][-1] and pixels[m][c] and not pixels[-1][0] and pixels[-1][c] and (not pixels[-1][-1]) and (first_row_ratio > 0.5 and last_row_ratio > 0.5)):
        return '8'
    elif(not pixels[0][0] and pixels[0][c] and not pixels[0][-1] and not pixels[m][0] and pixels[m][c] and not pixels[-1][0] and not pixels[-1][-1] and last_row_ratio < 0.30):
        return '9'
    elif(not pixels[0][0] and pixels[0][-1] and not pixels[m][0] and not pixels[m][-1] and pixels[-1][0] and not pixels[-1][-1]):
        return '/'
    elif(first_row_count == 0 and not pixels[0][0] and not pixels[0][-1] and not pixels[m][0] and not pixels[m][-1] and not pixels[-1][0] and not pixels[-1][-1]):
        return ' '
    elif(pixels[0][0] and not pixels[0][-1] and not pixels[m][0] and pixels[m][-1] and pixels[-1][0] and not pixels[-1][-1]):
        return ')'
    elif(not pixels[0][0] and pixels[0][-1] and pixels[m][0] and not pixels[m][-1] and not pixels[-1][0] and pixels[-1][-1]):
        return '('
    
    return False

def bwglyphstostring(glyphs):
    result = ""
    for i in glyphs:
        character = bwglyphtochar(i)
        if(character == False):
            print "Error: could not recognize the following glyph: "
            printpixels(i)
        else:
            result += character
            
    return result

def printpixels(pixels):
    for i in pixels:
        for j in i:
            sys.stdout.write("8" if j else ".")
        print ""

def imagetostring(path):
    im = Image.open(path)
    width, height = im.size
    
    pixelData = im.load()
    
    pixels = [];
    for i in range(0, height):
        pixels.append([])
        for j in range(0, width):
            pixels[i].append(bwthreshold(pixelData[j, i], 50))
        
    pixels = bwtrim(pixels)
    
    
    printpixels(pixels)
    glyphs = bwfindglyphs(pixels)
    
    return bwglyphstostring(glyphs)

for i in range(1, 26):
    print imagetostring('image'+str(i)+'.png')