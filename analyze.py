from __future__ import division
import gzip
import json
import os
import re

class LOLGameData:
    data = {}
    filename = ""
    
    def __init__(self, filename):
        self.filename = filename
        self.data = self.getDataFromLRA(filename)
    
    def getDataFromLRA(self, filename):
        file_contents = gzip.open(filename, 'rb').read()
        data = json.loads(file_contents)
        return data
    
    def __convertDataToTuples(self, data):
        for k, v in data.iteritems():
            if type(v) is dict:
                data[k] = sorted(v.items(), key=lambda tup: tup[0])
        
        if('teams' in data):
            data['teams'][0] = sorted(data['teams'][0].items(), key=lambda tup: tup[0])
            data['teams'][1] = sorted(data['teams'][1].items(), key=lambda tup: tup[0])
        
        if('players' in data):
            for team in [0, 1]:
                for player in range(0, 4):
                    data['players'][team][player] = sorted(data['players'][team][player].items(), key=lambda tup: tup[0])
        
        return data
    
    def __removeActivatedItems(self, itemList):
        for k, v in enumerate(itemList):
            itemList[k] = re.sub("\-activated.*", "", v)
        return itemList
    
    def getTotalGoldOverTime(self):
        gold_data = { 'teams' : [{}, {}], 'players' : [[{}, {}, {}, {}, {}], [{}, {}, {}, {}, {}]], 'difference' : {}}
        for i in self.data['history']:
            if("gold_data_available" in i and i['gold_data_available'] == True):
                gold_data['teams'][0][i['time']] = i['teams'][0]['gold']
                gold_data['teams'][1][i['time']] = i['teams'][1]['gold']
                gold_data['difference'][i['time']] = i['teams'][0]['gold'] - i['teams'][1]['gold']
                for team in [0, 1]:
                    for player in range(0, 5):
                        gold_data['players'][team][player][i['time']] = i['players'][team][player]['gold']
        
        return self.__convertDataToTuples(gold_data)
    
    # Get final scoreboard, summoner names, etc.
    def getGameData(self):
        basename = ".".join(self.filename.split(".")[0:-1])
        game_data = { 'players' : [[], []] }
        
        itemAvaliableIndex = len(self.data['history']) - 1
        while(self.data['history'][itemAvaliableIndex]['item_data_available'] == False):
            itemAvaliableIndex -= 1
        
        goldAvailableIndex = len(self.data['history']) - 1
        while(self.data['history'][goldAvailableIndex]['gold_data_available'] == False):
            goldAvailableIndex -= 1
        
        for i in range (0, 10):
            game_data['players'][i//5].append({"summoner" : self.data['lrf_meta']['players'][i]['summoner'], 
                                               "champion" : self.data['history'][0]['players'][i//5][i%5]['champion'],
                                               "summoner-spells" : self.data['summoner_spells'][i//5][i%5],
                                               "items" : self.__removeActivatedItems(self.data['history'][itemAvaliableIndex]['players'][i//5][i%5]['items']),
                                               "total_gold" : self.data['history'][goldAvailableIndex]['players'][i//5][i%5]['total_gold'],
                                               "kills" : self.data['history'][-1]['players'][i//5][i%5]['kills'],
                                               "deaths" : self.data['history'][-1]['players'][i//5][i%5]['deaths'],
                                               "assists" : self.data['history'][-1]['players'][i//5][i%5]['assists'],
                                               "kda" : self.data['history'][-1]['players'][i//5][i%5]['kda'],
                                               "minions" : self.data['history'][-1]['players'][i//5][i%5]['minions'],
                                               "level" : self.data['history'][-1]['players'][i//5][i%5]['level']})
        
        for team in [0, 1]:
            for player in range(0, 5):
                reverse_counter = 1
                while(game_data['players'][team][player]['level'] == 0):
                    reverse_counter += 1
                    game_data['players'][team][player]['level'] = self.data['history'][-reverse_counter]['players'][team][player]['level']
        
        json.dump(game_data, open(basename+"/data2.json", "w+"))
        return game_data
    
    def generateAnalysisFile(self):
        basename = ".".join(self.filename.split(".")[0:-1])
        if not os.path.exists(basename):
            os.makedirs(basename)
        
        jsondata = { 
                    "gold" : self.getTotalGoldOverTime(),
                    "game" : self.getGameData() 
                    }
        json.dump(jsondata, open(basename+"/data.json", "w+"))

if __name__ == "__main__":
    data = LOLGameData("output/Gentium - Sona (7) - Spec.lra")
    print str(len(data.data['history'])) + " data points loaded."
    data.generateAnalysisFile()