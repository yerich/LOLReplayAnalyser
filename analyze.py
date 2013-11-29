from __future__ import division
import gzip
import json
import os
import re
import config
from screenshot import cint

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
        # Queue for last 1 and 5 minutes of current gold value, per player
        gold_history_queue_1 = [[[], [], [], [], []], [[], [], [], [], []]]
        gold_history_queue_5 = [[[], [], [], [], []], [[], [], [], [], []]]
        for i in self.data['history']:
            if("gold_data_available" in i and i['gold_data_available'] == True):
                gold_data['teams'][0][i['time']] = { "total" : i['teams'][0]['gold'], "effective" : i['teams'][0]['gold'], "held" : 0 }
                gold_data['teams'][1][i['time']] = { "total" : i['teams'][1]['gold'], "effective" : i['teams'][1]['gold'], "held" : 0 }
                gold_data['difference'][i['time']] = i['teams'][0]['gold'] - i['teams'][1]['gold']
                
                for team in [0, 1]:
                    for player in range(0, 5):
                        gold_history_queue_5[team][player].append([i['time'], i['players'][team][player]['total_gold']])
                        gold_history_queue_1[team][player].append([i['time'], i['players'][team][player]['total_gold']])
                        five_minutes_ago_gold = 0
                        while(len(gold_history_queue_5[team][player]) > 1 and gold_history_queue_5[team][player][1][0] < i['time'] - 300):
                            gold_history_queue_5[team][player].pop(0)
                        if(gold_history_queue_5[team][player][0][0] < i['time'] - 300):
                            five_minutes_ago_gold = gold_history_queue_5[team][player][0]
                            
                        one_minute_ago_gold = 0
                        while(i['time'] >= 180 and gold_history_queue_1[team][player][1][0] < i['time'] - 60):
                            gold_history_queue_1[team][player].pop(0)
                        if(gold_history_queue_1[team][player][0][0] < i['time'] - 60):
                            one_minute_ago_gold = gold_history_queue_1[team][player][0]
                        
                        gold_data['players'][team][player][i['time']] = { 
                                                                         "total" : i['players'][team][player]['total_gold'], 
                                                                         "current" : i['players'][team][player]['current_gold'],
                                                                         "gpm" : i['players'][team][player]['total_gold'] * 60 / i['time'] if (i['time'] >= 120) else None,
                                                                         "gpm5" : ((i['players'][team][player]['total_gold'] - five_minutes_ago_gold[1]) * 60 / (i['time'] - five_minutes_ago_gold[0])) if five_minutes_ago_gold else None,
                                                                         "gpm1" : ((i['players'][team][player]['total_gold'] - one_minute_ago_gold[1]) * 60 / (i['time'] - one_minute_ago_gold[0])) if one_minute_ago_gold else None
                                                                         }
                        
                        gold_data['teams'][team][i['time']]['effective'] -= i['players'][team][player]['current_gold']
                        gold_data['teams'][team][i['time']]['held'] += i['players'][team][player]['current_gold']
        
        return gold_data
    
    def getTotalKDAOverTime(self):
        kda_data = { 'teams' : [{}, {}], 'players' : [[{}, {}, {}, {}, {}], [{}, {}, {}, {}, {}]], 'difference' : {}}
        for i in self.data['history']:
            if("gold_data_available" in i and i['gold_data_available'] == True):
                kda_data['teams'][0][i['time']] = {'kills' : 0, 'deaths' : 0, 'assists' : 0, 'kda' : [0, 0, 0], 'currently_dead' : 0}
                kda_data['teams'][1][i['time']] = {'kills' : 0, 'deaths' : 0, 'assists' : 0, 'kda' : [0, 0, 0], 'currently_dead' : 0}
                kda_data['difference'][i['time']] = i['teams'][0]['kills'] - i['teams'][1]['kills']
                for team in [0, 1]:
                    for player in range(0, 5):
                        kda_data['players'][team][player][i['time']] = {"kills" : cint(i['players'][team][player]['kills']),
                                                                        "deaths" : cint(i['players'][team][player]['deaths']),
                                                                        "assists" : cint(i['players'][team][player]['assists']),
                                                                        "is_dead" : 1 if (i['players'][team][player]['dead']) else 0 }
                        kda_data['teams'][team][i['time']]['kills'] += cint(i['players'][team][player]['kills'])
                        kda_data['teams'][team][i['time']]['deaths'] += cint(i['players'][team][player]['deaths'])
                        kda_data['teams'][team][i['time']]['assists'] += cint(i['players'][team][player]['assists'])
                        if i['players'][team][player]['dead']:
                            kda_data['teams'][team][i['time']]['currently_dead'] += 1
                        for val in range(0, 3):
                            kda_data['teams'][team][i['time']]['kda'][val] += cint(i['players'][team][player]['kda'][val])
        
        return kda_data
    
    # Get final scoreboard, summoner names, etc.
    def getGameData(self):
        game_data = { 'players' : [[], []], 'teams' : [{}, {}], "clientVersion" : "0.0" }
        
        itemAvaliableIndex = len(self.data['history']) - 1
        while(self.data['history'][itemAvaliableIndex]['item_data_available'] == False):
            itemAvaliableIndex -= 1
        
        goldAvailableIndex = len(self.data['history']) - 1
        while(self.data['history'][goldAvailableIndex]['gold_data_available'] == False):
            goldAvailableIndex -= 1
        
        for team in range (0, 2):
            for player in range(0, 5):
                game_data['players'][team].append({"summoner" : self.data['lrf_meta']['players'][team*5 + player]['summoner'], 
                                                   "champion" : self.data['history'][0]['players'][team][player]['champion'],
                                                   "summoner_spells" : self.data['summoner_spells'][team][player],
                                                   "items" : self.__removeActivatedItems(self.data['history'][itemAvaliableIndex]['players'][team][player]['items']),
                                                   "total_gold" : self.data['history'][goldAvailableIndex]['players'][team][player]['total_gold'],
                                                   "kills" : self.data['history'][-1]['players'][team][player]['kills'],
                                                   "deaths" : self.data['history'][-1]['players'][team][player]['deaths'],
                                                   "assists" : self.data['history'][-1]['players'][team][player]['assists'],
                                                   "kda" : self.data['history'][-1]['players'][team][player]['kda'],
                                                   "minions" : cint(self.data['history'][-1]['players'][team][player]['minions']),
                                                   "level" : self.data['history'][-1]['players'][team][player]['level']})
                if team == 0:
                    game_data['players'][team][player]['items'].reverse()
        
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
                game_data['teams'][team]['gold'] += self.data['history'][goldAvailableIndex]['players'][team][player]['total_gold']
                game_data['teams'][team]['minions'] += cint(self.data['history'][-1]['players'][team][player]['minions'])
            
            game_data['teams'][team]['kda'] = [game_data['teams'][team]['kills'], game_data['teams'][team]['deaths'], game_data['teams'][team]['assists']]
            
            if(self.data['winner'] == team):
                game_data['teams'][team]['winner'] = True
            else:
                game_data['teams'][team]['winner'] = False
        
        game_data['clientVersion'] = self.data['lrf_meta']['clientVersion']
        game_data['gameLength'] = self.data['history'][-1]['time']
        return game_data
    
    # Gets data on towers, inhibitors, dragons, barons
    def getObjectiveData(self):
        objective_data = { 'teams' : [{}, {}], 'players' : [[{}, {}, {}, {}, {}], [{}, {}, {}, {}, {}]]}
        last_dragon = -1000
        last_baron = -1000
        num_dragons = { 'teams' : [0, 0]}
        num_barons = { 'teams' : [0, 0]}
        last_data = { 'teams' : [{}, {}]}
        for i in self.data['history']:  # Loop through data points
            if(i['gold_data_available'] == False):
                continue
            
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
            cs = [0, 0]
            for team in [0, 1]:
                for lane in i['inhibitors'][team]:
                    if i['inhibitors'][team][lane] == False:
                        num_inhibitors[-(team-1)] += 1  # -(team-1) turns 0 into 1 and vice versa
                        down_inhibitors[-(team-1)][lane] = 1
                    elif i['inhibitors'][team][lane] == None:
                        unknown_inhibitors[-(team-1)][lane] = 1
                    elif i['inhibitors'][team][lane] == True:
                        up_inhibitors[-(team-1)][lane] = 1
                
                for player in range(0, 5):
                    cs[team] += i['players'][team][player]['minions']
                    objective_data['players'][team][player][i['time']] = { "minions" : i['players'][team][player]['minions']}
                                
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
                                                             "cs" : cs[team],
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
                        
                        for i in objective_data['teams'][team]:
                            if(i < time and i > last_true and i <= (time - config.INHIB_RESPAWN_TIME) and i > (time - 2*config.INHIB_RESPAWN_TIME) and objective_data['teams'][team][i]['up_inhibitors'][lane]):
                                last_true = i
                        
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
    
    
    def getItemBuildData(self):
        item_builds = {
                       "history" : [[{}, {}, {}, {}, {}], [{}, {}, {}, {}, {}]], 
                       "builds" : [[[], [], [], [], []], [[], [], [], [], []]], 
                       "finished_build_items" : [[[], [], [], [], []], [[], [], [], [], []]]}
        last_seen_build = [[[], [], [], [], []], [[], [], [], [], []]]
        is_level_9 = [[False, False, False, False, False], [False, False, False, False, False]]
        
        for team in [0, 1]:
            for player in range(0, 5):
                for entry in self.data['history']:
                    if not entry['item_data_available']:
                        continue
                    
                    time = entry['time']
                    curritems = self.__removeActivatedItems(entry['players'][team][player]['items'])
                    
                    if((entry['players'][team][player]['level'] >= 9 or is_level_9[team][player]) and "warding-totem" in curritems):
                        is_level_9[team][player] = True
                        curritems = ["greater-totem" if x == "warding-totem" else x for x in curritems]
                    elif(entry['players'][team][player]['level'] >= 9):
                        is_level_9[team][player] = True
                    
                    if(sorted(last_seen_build[team][player]) != sorted(curritems)):
                        item_builds['history'][team][player][time] = curritems
                    last_seen_build[team][player] = curritems
                    
                    if(entry['time'] > 90 and len(curritems) > 0 and len(item_builds['builds'][team][player]) == 0):
                        item_builds['builds'][team][player].append([time, curritems, []])
                        item_builds['finished_build_items'][team][player].append(curritems)
                    elif(len(item_builds['builds'][team][player]) > 0):
                        prev_build_items = [item for item in item_builds['finished_build_items'][team][player][-1] if item in config.BUILD_ITEMS]
                        curr_build_items = [item for item in curritems if item in config.BUILD_ITEMS]
                        new_build_items = [item for item in curr_build_items if item not in prev_build_items]
                        old_build_items = [item for item in prev_build_items if item not in curr_build_items]
                        if(len(new_build_items) > 0 or len(old_build_items) > 0):
                            item_builds['finished_build_items'][team][player].append(curr_build_items)
                            item_builds['builds'][team][player].append([time, new_build_items, old_build_items])
                        
        
        return item_builds
    
    def getSkillsData(self):
        skills = {"order" : [[[], [], [], [], []], [[], [], [], [], []]], 
                  "totals" : [[[], [], [], [], []], [[], [], [], [], []]]}
        
        for team in [0, 1]:
            for player in range(0, 5):
                for _ in range(0, 4):
                    skills['totals'][team][player].append(0);
        
        for entry in self.data['history']:
            if "active_champion" not in entry or not entry['active_champion'] or 'champion_id' not in entry['active_champion']:
                continue
            
            champ_data = entry['active_champion']
            
            team = champ_data['champion_id'] // 5
            player = champ_data['champion_id'] % 5
            champ_data['skills'] = [cint(x) for x in champ_data['skills']]
            
            if(skills['totals'][team][player] != champ_data['skills']):
                increasedSkills = []
                for skill in range(0, 4):
                    while(skills['totals'][team][player][skill] < champ_data['skills'][skill]):
                        increasedSkills.append(skill)
                        skills['order'][team][player].append([])
                        skills['order'][team][player][-len(increasedSkills)] = increasedSkills
                        skills['totals'][team][player][skill] += 1
                
        
        return skills
    
    def generateAnalysisFile(self):
        basename = ".".join(self.filename.split(".")[0:-1])
        if not os.path.exists(basename):
            os.makedirs(basename)
        
        jsondata = { 
                    "gold" : self.getTotalGoldOverTime(),
                    "kda" : self.getTotalKDAOverTime(),
                    "game" : self.getGameData(),
                    "objectives" : self.getObjectiveData(),
                    "item_builds" : self.getItemBuildData(),
                    "skills" : self.getSkillsData()
                    }
        json.dump(jsondata, open(basename+"/data.json", "w+"))

if __name__ == "__main__":
    data = LOLGameData("output/Gentium - Lux (9) - Spec.lra")
    print str(len(data.data['history'])) + " data points loaded."
    print "Generating analysis json file..."
    data.generateAnalysisFile()
    print "Done."