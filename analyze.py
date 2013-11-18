from __future__ import division
import gzip
import json

class LOLGameData:
    data = {}
    
    def __init__(self, filename):
        self.data = self.getDataFromLRA(filename)

    def getDataFromLRA(self, filename):
        file_contents = gzip.open(filename, 'rb').read()
        data = json.loads(file_contents)
        return data

if __name__ == "__main__":
    data = LOLGameData("output/sample.lra")
    print len(data['history'])