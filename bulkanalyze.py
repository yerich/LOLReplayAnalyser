from __future__ import division
import gzip
import json
import os
import Image
import ImageDraw
import math

lra = []

def loadLRAData():
    files = [ f for f in os.listdir("output/") if os.path.isfile(os.path.join("output/",f)) and f.split(".")[-1] == "lra" ]
    print str(len(files)) + " files found"
    
    for filename in files:
        f = gzip.open("output/"+filename, 'rb')
        file_content = f.read()
        f.close()
        lra.append(json.loads(file_content))
        
    print str(len(lra)) + " replays loaded"

def generateHeatmap(map_positions):
    im = Image.open("minimap.png").convert("RGBA")
    width, height = im.size
    
    heatmap = [[float(0) for _ in xrange(height)] for _ in xrange(width)] 
    
    for point in map_positions:
        for x in range(-4, 5):
            for y in range(-4, 5):
                try:
                    heatmap[x + point[0]][y + point[1]] += float(math.log(5-abs(x)) + math.log(5-abs(y)))
                except IndexError:
                    pass
        
    highestValue = 0
    for x in range(0, width):
        for y in range(0, height):
            if(heatmap[x][y] > 0):
                heatmap[x][y] = math.log(heatmap[x][y], 2)
            if(heatmap[x][y] > highestValue):
                highestValue = heatmap[x][y]
    
    overlay = Image.new('RGBA', im.size)
    draw = ImageDraw.Draw(overlay)
    for x in range(0, width):
        for y in range(0, height):
            heatmap[x][y] = heatmap[x][y] / float(highestValue)
            
            if(heatmap[x][y] > 0):
                alpha = int(heatmap[x][y] * 200)
                yellow = int(max(0, 1-heatmap[x][y]) * 255)
                draw.point((x, y), (255, yellow, 0, alpha))
                
    im.paste(overlay,mask=overlay)
    im.save("heatmap.png")

def generateDeathMapLocations():
    deaths = []
    for game in lra:
        champRegisteredAsDead = [[False for i in range(0, 5)] for t in range(0, 2)]
        for entry in game['history']:
            if(not entry['players'] or not entry['active_champion']):
                continue
            
            for team in [0, 1]:
                for player in range(0, 5):
                    if(entry['active_champion']['champion'] == entry['players'][team][player]['champion'] and entry['players'][team][player]['dead']):
                        if(champRegisteredAsDead[team][player] != False):
                            continue
                        champRegisteredAsDead[team][player] = True
                        deaths.append({"map_position": entry['map_position'],
                                       "time": entry['time'],
                                       "team": team,
                                       "is_winning": (entry['teams'][team]['gold'] > entry['teams'][(team + 1) % 2]['gold']),
                                       "level": entry['players'][team][player]['level']
                                       })
                    
                    if(entry['players'][team][player]['dead'] == False):
                        champRegisteredAsDead[team][player] = False
    
    map_positions = []
    for death in deaths:
        map_positions.append(death['map_position'])
    
    print str(len(deaths))+ " deaths recorded."
    generateHeatmap(map_positions)

if __name__ == "__main__":
    print "Performing bulk analysis"
    loadLRAData()
    generateDeathMapLocations()
    print "Done."