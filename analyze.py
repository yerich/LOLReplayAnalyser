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
        game_data = { 'players' : [[], []], 'teams' : [{}, {}] }
        
        itemAvaliableIndex = len(self.data['history']) - 1
        while(self.data['history'][itemAvaliableIndex]['item_data_available'] == False):
            itemAvaliableIndex -= 1
        
        goldAvailableIndex = len(self.data['history']) - 1
        while(self.data['history'][goldAvailableIndex]['gold_data_available'] == False):
            goldAvailableIndex -= 1
        
        for i in range (0, 10):
            game_data['players'][i//5].append({"summoner" : self.data['lrf_meta']['players'][i]['summoner'], 
                                               "champion" : self.data['history'][0]['players'][i//5][i%5]['champion'],
                                               "summoner_spells" : self.data['summoner_spells'][i//5][i%5],
                                               "items" : self.__removeActivatedItems(self.data['history'][itemAvaliableIndex]['players'][i//5][i%5]['items']),
                                               "total_gold" : self.data['history'][goldAvailableIndex]['players'][i//5][i%5]['total_gold'],
                                               "kills" : self.data['history'][-1]['players'][i//5][i%5]['kills'],
                                               "deaths" : self.data['history'][-1]['players'][i//5][i%5]['deaths'],
                                               "assists" : self.data['history'][-1]['players'][i//5][i%5]['assists'],
                                               "kda" : self.data['history'][-1]['players'][i//5][i%5]['kda'],
                                               "minions" : int(self.data['history'][-1]['players'][i//5][i%5]['minions']),
                                               "level" : self.data['history'][-1]['players'][i//5][i%5]['level']})
        
        for team in [0, 1]:
            game_data['teams'][team]['gold'] = 0
            game_data['teams'][team]['kills'] = 0
            game_data['teams'][team]['deaths'] = 0
            game_data['teams'][team]['assists'] = 0
            game_data['teams'][team]['minions'] = 0
            
            for player in range(0, 5):
                # Get player level from history, discarding invalid entries
                reverse_counter = 1
                while(game_data['players'][team][player]['level'] == 0):
                    reverse_counter += 1
                    game_data['players'][team][player]['level'] = self.data['history'][-reverse_counter]['players'][team][player]['level']
                
                # Compute team gold, K/D/A
                game_data['teams'][team]['kills'] += self.data['history'][-1]['players'][team][player]['kills']
                game_data['teams'][team]['deaths'] += self.data['history'][-1]['players'][team][player]['deaths']
                game_data['teams'][team]['assists'] += self.data['history'][-1]['players'][team][player]['assists']
                game_data['teams'][team]['gold'] += self.data['history'][-1]['players'][team][player]['total_gold']
                game_data['teams'][team]['minions'] += int(self.data['history'][-1]['players'][team][player]['minions'])
            
            game_data['teams'][team]['kda'] = [game_data['teams'][team]['kills'], game_data['teams'][team]['deaths'], game_data['teams'][team]['assists']]
            
            if(self.data['winner'] == team):
                game_data['teams'][team]['winner'] = True
            else:
                game_data['teams'][team]['winner'] = False
            
        return game_data
    
    # Gets data on towers, inhibitors, dragons, barons
    def getObjectiveData(self):
        objective_data = { 'teams' : [{}, {}]}
        last_dragon = -1000
        last_baron = -1000
        num_dragons = { 'teams' : [0, 0]}
        num_barons = { 'teams' : [0, 0]}
        for i in self.data['history']:
            for j in i['events']:
                # Detect dragon and baron based on the event notifications
                if(j['victim'] == "monster-dragon" and i['time'] > last_dragon + 200):
                    last_dragon = i['time']
                    num_dragons['teams'][j['team']] += 1
                    
                    # Dragon data is a bit delayed, so we'll have to rewrite history
                    for k, _ in enumerate(objective_data):
                        if(k > i['time'] - 4):
                            objective_data[k][j['team']]['num_dragons'] += 1
                    
                if(j['victim'] == "monster-baron" and i['time'] > last_baron + 200):
                    last_baron = i['time']
                    num_barons['teams'][j['team']] += 1
                    
                    for k, _ in enumerate(objective_data):
                        if(k > i['time'] - 4):
                            objective_data[k][j['team']]['num_barons'] += 1
            
            for team in [0, 1]:
                objective_data['teams'][team][i['time']] = { "num_dragons" : num_dragons['teams'][team], "num_barons" : num_barons['teams'][team], "num_towers" : i['towers'][team] }
            
        return objective_data
    
    def generateAnalysisFile(self):
        basename = ".".join(self.filename.split(".")[0:-1])
        if not os.path.exists(basename):
            os.makedirs(basename)
        
        jsondata = { 
                    "gold" : self.getTotalGoldOverTime(),
                    "game" : self.getGameData(),
                    "objectives" : self.getObjectiveData()
                    }
        json.dump(jsondata, open(basename+"/data.json", "w+"))

if __name__ == "__main__":
    data = LOLGameData("sample.lra")
    print str(len(data.data['history'])) + " data points loaded."
    data.generateAnalysisFile()