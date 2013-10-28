from __future__ import division
import Image
import sys
import time

# Returns 0 (black) or 1 (white) for a pixel tuple, depending on threshold value (betwwen 0 and 100)
def bwthreshold(pixel, threshold):
    return int((sum(pixel)/float(len(pixel))) / 2 > threshold)

def bwmap(func, pixels):
    for i, _ in enumerate(pixels):
        pixels[i] = map(func, pixels[i])
    return pixels

def bwrowhaspixel(row, threshhold = 1):
    num = 0
    for i in row:
        if i:
            num += 1
    if(num >= threshhold):
        return True
    return False

def bwtrimvertical(pixels, threshhold = 1):
    valid_rows_top = []
    valid_rows_bot = [];
    for i, row in enumerate(pixels):
        if len(valid_rows_top) > 0 or bwrowhaspixel(row, threshhold):
            valid_rows_top.append(i)
            
    for i, row in reversed(list(enumerate(pixels))):
        if len(valid_rows_bot) > 0 or bwrowhaspixel(row, threshhold):
            valid_rows_bot.append(i)
    
    return { 'result' : [row for i, row in enumerate(pixels) if (i in valid_rows_top and i in valid_rows_bot)], 'range' : [i for i, row in enumerate(pixels) if (i in valid_rows_top and i in valid_rows_bot)]}

def bwfindglyphs(pixels, threshhold = 1):
    pixels = bwtranspose(pixels)
    glyphs = []
    first_row = 0
    last_row = 0
    num_empty_rows = 0
    for i, row in enumerate(pixels):
        if(bwrowhaspixel(row, threshhold)):
            if num_empty_rows > 10:
                glyphs.append([])
            last_row += 1
            num_empty_rows = 0
        else:
            if(last_row - first_row > 0):
                glyphs.append(bwtranspose(pixels[first_row:last_row]))
            first_row = i+1
            last_row = i+1
            if num_empty_rows > 10:
                glyphs.append([])
                num_empty_rows = 0
            num_empty_rows += 1
    
    if(last_row - first_row > 0):
        glyphs.append(bwtranspose(pixels[first_row:last_row]))
    return glyphs

def bwtranspose(pixels):
    return map(list, zip(*pixels))

def bwtrim(pixels):
    return bwtranspose(bwtrimvertical(bwtranspose(bwtrimvertical(pixels)['result']))['result'])

def bwinvert(pixels):
    return bwmap(lambda x : int(not x), pixels)

# Primitive but fast OCR
def bwglyphtochar(pixels, threshold = 1):
    pixels = bwtrimvertical(pixels)['result']
    if len(pixels) == 0:
        return " "
    c = int(len(pixels[0])/2)    #Horizontal center
    m = int(len(pixels)/2)       #Vertical middle
    width = len(pixels[0])
    height = len(pixels)
    first_row_count = len([i for i in pixels[0] if i])
    first_row_ratio = first_row_count/float(width)
    last_row_count = len([i for i in pixels[-1] if i])
    last_row_ratio = last_row_count/float(width)
    
    if(width/float(height) > 0.33 and width < 4):
        return ','
    elif(pixels[0][c] and pixels[m][0] and pixels[m][-1] and pixels[-1][c] and not pixels[m][c]):
        return '0'
    elif(width < 4 and pixels[0][c] and pixels[1][c] and pixels[2][c] and pixels[-1][c] and pixels[-2][c] and pixels[-3][c] and pixels[m][c] and pixels[int(round(float(height)/4))][c]):
        return '1'
    elif(first_row_ratio >= 0.5 and not pixels[0][-1] and pixels[0][c] and pixels[-1][1] and pixels[-1][c] and pixels[-1][-1] and not pixels[m][0]):
        return '2'
    elif(not pixels[0][-1] and pixels[0][c] and not pixels[int(round(height/4))][0] and not pixels[-1][-1] and pixels[-1][c] and not pixels[m][0] and (not pixels[m][1] or not pixels[m][-1]) and not pixels[int(round(height/4))][0] and not pixels[int(round(height/4))][1] and (pixels[int(round(height/4))][-1] or pixels[int(round(height/4))][-2]) and last_row_ratio >= 0.5):
        return '3'
    elif(not pixels[0][0] and not pixels[0][c] and not pixels[-1][0] and not pixels[-1][-1] and first_row_ratio < 0.30 and first_row_ratio > 0 and last_row_ratio < 0.40):
        return '4'
    elif(first_row_ratio > 0.5 and pixels[0][c] and pixels[-1][c] and not pixels[-1][-1] and not pixels[m][0] and pixels[m][c] and last_row_ratio > 0.5 and pixels[0][0] == pixels[1][0] and pixels[0][0] == pixels[int(height/4)][0] and pixels[0][0] == pixels[int(height/4)][0] and not pixels[int(round(height/4))][-1] and not pixels[int(round(height/4))][-2]):
        return '5'
    elif(not pixels[0][0] and not pixels[0][-1] and pixels[m][1] and pixels[m][c] and not pixels[-1][0] and pixels[-1][c] and not pixels[-1][-1] and first_row_ratio < 0.45 and not pixels[int(round(height/4))][-1] and not pixels[int(round(height/4))][-2]):
        return '6'
    elif(pixels[0][0] and pixels[0][c] and pixels[0][-1] and not pixels[m][0] and not pixels[m][-1] and not pixels[-1][0] and not pixels[-1][-1]):
        return '7'
    elif(not pixels[0][0] and pixels[0][c] and not pixels[0][-1] and pixels[m][c] and not pixels[-1][0] and pixels[-1][c] and (not pixels[-1][-1]) and (first_row_ratio >= 0.4 and last_row_ratio >= 0.4)):
        return '8'
    elif(not pixels[0][0] and pixels[0][c] and not pixels[0][-1] and pixels[m-1][c] and not pixels[-1][0] and not pixels[-1][-1] and last_row_ratio < 0.40):
        return '9'
    elif(not pixels[0][0] and (pixels[0][-1] or (pixels[0][-2] and pixels[1][-1])) and not pixels[m][0] and not pixels[m][-1] and (pixels[-1][0] or (pixels[-2][0] and pixels[-1][1])) and not pixels[-1][-1]):
        return '/'
    elif(first_row_count == 0 and not pixels[0][0] and not pixels[0][-1] and not pixels[m][0] and not pixels[m][-1] and not pixels[-1][0] and not pixels[-1][-1]):
        return ' '
    elif(pixels[0][0] and not pixels[0][-1] and not pixels[m][0] and pixels[m][-1] and pixels[-1][0] and not pixels[-1][-1]):
        return ')'
    elif(not pixels[0][0] and pixels[0][-1] and pixels[m][0] and not pixels[m][-1] and not pixels[-1][0] and pixels[-1][-1]):
        return '('
    
    if(threshold == 1):
        glyphs = bwfindglyphs(pixels, 2)
        return bwglyphstostring(glyphs, 2)
    
    return False

def bwglyphstostring(glyphs, threshold = 1):
    result = ""
    for i in glyphs:
        character = bwglyphtochar(i, threshold)
        if(character == False):
            print "Error: could not recognize the following glyph: "
            printpixels(bwtrimvertical(i, threshold)['result'])
        else:
            result += character
            
    return result

def printpixels(pixels):
    for i in pixels:
        for j in i:
            sys.stdout.write("8" if j else ".")
        print ""

def imagetostring(im):
    width, height = im.size
    
    pixelData = im.load()
    
    pixels = [];
    for i in range(0, height):
        pixels.append([])
        for j in range(0, width):
            pixels[i].append(bwthreshold(pixelData[j, i], 60))
    
    """
    vert_range = bwtrimvertical(pixels)['range']
    true_height = vert_range[-1] - vert_range[0]
    
    if(true_height == 14):
        old_height = height
        height = int(height * (15/true_height))
        width = int(width * ((height * 15/true_height)/old_height))
        
        im = im.resize((width, height), Image.BICUBIC)
        pixelData = im.load()
        width, height = im.size
        
        pixels = [];
        for i in range(0, height):
            pixels.append([])
            for j in range(0, width):
                pixels[i].append(bwthreshold(pixelData[j, i], 70))
    """
    pixels = bwtrim(pixels)
    
    #printpixels(pixels)
    glyphs = bwfindglyphs(pixels)
    
    return bwglyphstostring(glyphs)