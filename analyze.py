from __future__ import division
import gzip
import json
import os

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
        
        print data['teams']
        return data
    
    def getTotalGoldOverTime(self):
        gold_data = { 'teams' : [{}, {}], 'players' : [[{}, {}, {}, {}, {}], [{}, {}, {}, {}, {}]], 'difference' : {}}
        for i in self.data['history']:
            if("gold_data_available" in i and i['gold_data_available'] == True):
                gold_data['teams'][0][i['time']] = i['teams'][0]['gold']
                gold_data['teams'][1][i['time']] = i['teams'][1]['gold']
                gold_data['difference'][i['time']] = i['teams'][0]['gold'] - i['teams'][1]['gold']
                for team in [0, 1]:
                    for player in range(0, 4):
                        gold_data['players'][team][player][i['time']] = i['players'][team][player]['gold']
        
        return self.__convertDataToTuples(gold_data)
    
    def generateAnalysisFile(self):
        basename = ".".join(self.filename.split(".")[0:-1])
        if not os.path.exists(basename):
            os.makedirs(basename)
        
        json.dump(self.getTotalGoldOverTime(), open(basename+"/gold.json", "w+"))

if __name__ == "__main__":
    data = LOLGameData("output/sample.lra")
    print str(len(data.data['history'])) + " data points loaded."
    data.generateAnalysisFile()