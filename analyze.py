from __future__ import division
import gzip
import json
import os
import re
import config

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
        
        return gold_data
    
    # Get final scoreboard, summoner names, etc.
    def getGameData(self):
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
        last_data = { 'teams' : [{}, {}]}
        for i in self.data['history']:  # Loop through data points
            for j in i['events']:
                # Detect dragon and baron based on the event notifications
                if(j['victim'] == "monster-dragon" and i['time'] > last_dragon + 200):
                    last_dragon = i['time']
                    num_dragons['teams'][j['team']] += 1
                    
                    # Dragon data is a bit delayed, so we'll have to rewrite history
                    for k, _ in enumerate(objective_data['teams'][0]):
                        if(k > i['time'] - 2):
                            objective_data[k][j['team']]['num_dragons'] += 1
                    
                if(j['victim'] == "monster-baron" and i['time'] > last_baron + 200):
                    last_baron = i['time']
                    num_barons['teams'][j['team']] += 1
                    
                    for k, _ in enumerate(objective_data['teams'][0]):
                        if(k > i['time'] - 2):
                            objective_data[k][j['team']]['num_barons'] += 1
            
            # Inhibitors
            num_inhibitors = [0, 0]
            
            # Sometimes we can't get the state of an inhibitor because something is covering it on the minimap
            unknown_inhibitors = [{"top" : 0, "middle" : 0, "bottom" : 0}, {"top" : 0, "middle" : 0, "bottom" : 0}]
            up_inhibitors = [{"top" : 0, "middle" : 0, "bottom" : 0}, {"top" : 0, "middle" : 0, "bottom" : 0}]
            down_inhibitors = [{"top" : 0, "middle" : 0, "bottom" : 0}, {"top" : 0, "middle" : 0, "bottom" : 0}]
            for team in [0, 1]:
                for lane in i['inhibitors'][team]:
                    if i['inhibitors'][team][lane] == False:
                        num_inhibitors[-(team-1)] += 1  # -(team-1) turns 0 into 1 and vice versa
                        down_inhibitors[-(team-1)][lane] = 1
                    elif i['inhibitors'][team][lane] == None:
                        unknown_inhibitors[-(team-1)][lane] = 1
                    elif i['inhibitors'][team][lane] == True:
                        up_inhibitors[-(team-1)][lane] = 1
                                
            # Conpile data into our list for this data point
            for team in [0, 1]:
                objective_data['teams'][team][i['time']] = {
                                                             "num_dragons" : num_dragons['teams'][team], 
                                                             "num_barons" : num_barons['teams'][team], 
                                                             "num_towers" : i['towers'][team], 
                                                             "num_inhibitors" : num_inhibitors[team], 
                                                             "up_inhibitors" : up_inhibitors[team].copy(),
                                                             "down_inhibitors" : down_inhibitors[team].copy(),
                                                             "unknown_inhibitors" : unknown_inhibitors[team].copy(),
                                                             }

                last_data['teams'][team] = objective_data['teams'][team][i['time']]
        
        
        # Fill in the gaps in our knowledge of inhibitors
        for team in [0, 1]:
            last = False
            for time in sorted(objective_data['teams'][team].keys()):
                for lane in ["top", "middle", "bottom"]:
                    # Unknown -> True
                    if(last and objective_data['teams'][team][time]['up_inhibitors'][lane] == 1 and last['unknown_inhibitors'][lane]):
                        # Look for True -> Unknown -> True. If length of Unknown < 5 minutes, we know that the inhib was up during that time
                        last_true = -1000
                        for i in objective_data['teams'][team]:
                            if(i < time and i > last_true and i > (time - config.INHIB_RESPAWN_TIME) and objective_data['teams'][team][i]['up_inhibitors'][lane]):
                                last_true = i
                        if(last_true > time - config.INHIB_RESPAWN_TIME):
                            #print "Case 1 looking between "+str(last_true)+" and "+str(time)+" for "+lane
                            for i in objective_data['teams'][team]:
                                if(i <= time and i >= last_true and objective_data['teams'][team][i]['unknown_inhibitors'][lane]):
                                    objective_data['teams'][team][i]['unknown_inhibitors'][lane] = 0
                                    objective_data['teams'][team][i]['up_inhibitors'][lane] = 1
                                    #print "case 1 at "+str(i)
                    
                    #(Unknown/False) -> True.
                    if(last and objective_data['teams'][team][time]['up_inhibitors'][lane] == 1 and (last['unknown_inhibitors'][lane] or last['down_inhibitors'][lane])):
                        # Look for True -> False -> (Unknown) -> True. False must be exactly 5 minutes.
                        last_false = -1000
                        last_true = -1000
                        
                        for i in objective_data['teams'][team]:
                            if(i < time and objective_data['teams'][team][i]['down_inhibitors'][lane]):
                                last_false = i
                        
                        print last_false
                        
                        for i in objective_data['teams'][team]:
                            if(i < time and i > last_true and i <= (time - config.INHIB_RESPAWN_TIME) and i > (time - 2*config.INHIB_RESPAWN_TIME) and objective_data['teams'][team][i]['up_inhibitors'][lane]):
                                last_true = i
                        
                        print last_true
                        
                        if(last_true < last_false and last_true <= (time - config.INHIB_RESPAWN_TIME) and last_true > (time - 2*config.INHIB_RESPAWN_TIME)):
                            for i in objective_data['teams'][team]:
                                if(i <= last_false - config.INHIB_RESPAWN_TIME and i >= last_true and objective_data['teams'][team][i]['unknown_inhibitors'][lane]):
                                    objective_data['teams'][team][i]['unknown_inhibitors'][lane] = 0
                                    objective_data['teams'][team][i]['up_inhibitors'][lane] = 1
                        
                    # Unknown -> False
                    if(last and objective_data['teams'][team][time]['down_inhibitors'][lane] == 1 and last['unknown_inhibitors'][lane]):
                        # Look for Unknown -> False -> (Unknown) -> True.
                        first_true = 10000000
                        for i in objective_data['teams'][team]:
                            if(i > time and i < first_true and i < (time + config.INHIB_RESPAWN_TIME) and objective_data['teams'][team][i]['up_inhibitors'][lane]):
                                first_true = i
                        
                        if(first_true < time + config.INHIB_RESPAWN_TIME):
                            #print "Case 2 looking between "+str(first_true - config.INHIB_RESPAWN_TIME)+" and "+str(time)+" for "+lane
                            for i in objective_data['teams'][team]:
                                if(i > first_true - config.INHIB_RESPAWN_TIME and i < time and objective_data['teams'][team][i]['unknown_inhibitors'][lane]):
                                    objective_data['teams'][team][i]['unknown_inhibitors'][lane] = 0
                                    objective_data['teams'][team][i]['down_inhibitors'][lane] = 1
                                    objective_data['teams'][team][i]['num_inhibitors'] += 1
                                    #print "case 2 at "+str(i)
                        
                        # Look for True -> Unknown -> False
                        last_true = -1000
                        for i in objective_data['teams'][team]:
                            if(i < time and i > last_true and i > (time - config.INHIB_RESPAWN_TIME) and objective_data['teams'][team][i]['up_inhibitors'][lane]):
                                last_true = i
                        if(last_true > time - config.INHIB_RESPAWN_TIME):
                            #print "Case 3 looking between "+str(last_true)+" and "+str(time)+" for "+lane
                            for i in objective_data['teams'][team]:
                                if(i > time and i < last_true + config.INHIB_RESPAWN_TIME and objective_data['teams'][team][i]['unknown_inhibitors'][lane]):
                                    objective_data['teams'][team][i]['unknown_inhibitors'][lane] = 0
                                    objective_data['teams'][team][i]['down_inhibitors'][lane] = 1
                                    objective_data['teams'][team][i]['num_inhibitors'] += 1
                                    #print "case 3 at "+str(i)
                        
                last = objective_data['teams'][team][time].copy()
                                    
        
        
        # Generate the area of uncertainty for unknown inhibitors
        for team in [0, 1]:
            last = False
            for k in objective_data['teams'][team]:
                unknown_inhibitors_count = 0
                for lane in objective_data['teams'][team][k]['unknown_inhibitors']:
                    if(objective_data['teams'][team][k]['unknown_inhibitors'][lane]):
                        unknown_inhibitors_count += 1
                
                objective_data['teams'][team][k]['num_inhibitors_range'] = [objective_data['teams'][team][k]['num_inhibitors'], 
                                                                            objective_data['teams'][team][k]['num_inhibitors'] + unknown_inhibitors_count]
                
                #if(objective_data['teams'][team][k]['num_inhibitors_range'][0] != objective_data['teams'][team][k]['num_inhibitors_range'][1]):
                #     print k, objective_data['teams'][team][k]['num_inhibitors_range'], team
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
    print "Generating analysis json file..."
    data.generateAnalysisFile()
    print "Done."