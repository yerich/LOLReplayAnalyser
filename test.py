import ocr
import time
import Image
import pprint
import cProfile
from screenshot import getScreenshotData
import icon

KEYNOTFOUND = '<KEYNOTFOUND>'       # KeyNotFound for dictDiff

# By Michael Shepanski (http://code.activestate.com/recipes/576644-diff-two-dictionaries/). MIT.
def dict_diff(first, second):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one fo the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dicationary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    diff = {}
    # Check all keys in first dict
    for key in first.keys():
        if (not second.has_key(key)):
            diff[key] = (first[key], KEYNOTFOUND)
        elif (first[key] != second[key]):
            diff[key] = (first[key], second[key])
    # Check all keys in second dict to find missing
    for key in second.keys():
        if (not first.has_key(key)):
            diff[key] = (KEYNOTFOUND, second[key])
    return diff

fopentime = 0
def runOCRTests():
    correct = ['106    2/6/3', '87    3/3/4', '121    2/2/2', '92    0/3/2', '5    3/3/4', '2/2/7    131', '2/2/6    78', 
               '3/3/6    15', '7/1/4    155', '3/2/2    119', '3/3/11    177', '2/2/6    78', '3/3/6    15', '9/2/5    180', '7/2/4    171', 
               '126    3/5/7', '129    3/7/7', '160    4/4/4', '130    2/4/3', '7    3/5/7', '1,118(7,654)      4/3/1    141', 
               '540(6,399)      3/3/1    95', '311(5,451)      0/4/2    96', '545(6,980)      2/6/3    121', '1,112(5,673)      1/2/3    30', 
               '15    2/1/16        844(7,839)', '157    9/3/7        516(10,594)', '119   4/3/12       1,009(8,794)', 
               '178   8/4/10       1,815(11,000)', '137   5/2/13       1,549(9,664)', '31,01', '25,45', '28,39', "25,45/35,57", 
               "28,39/32,24", "3   5   5   3", "5   3   5   3", "0    1   0   0", "4   2    1    1", '5   4   3   2',
               '14', '12', '16', '13', '14', '13', '8', '9', '7', '4', '5', '6', '17', '18', '15', '13', '101    1/3/7        452(6,578)',
               "2,164(11,099)     6/6/3    204", "370", "5", "9", "251    8/1/6        155(13,049)", "1,282(10,931)     1/11/11   169", "7", 
               "1,38", "101(16,951)     9/3/16   304", "177(11,741)     1/12/11   187", "299(14,008)     2/10/10   271", 
               "287(11,866)     7/8/19    90", "838(18,438)     10/5/18   315", "302(14,207)     12/8/19   32", "113    2/0/5        629(7,174)"]
    
    global fopentime
    fopentime = 0
    
    print "Running OCR tests..."
    for i in range(1, 73):
        fopenstart = time.clock()
        im = Image.open('tests/image'+str(i)+'.png')
        fopentime += (time.clock() - fopenstart) * 1000
        result = ocr.imagetostring(im)
        if len(correct) < i:
            print "Test "+str(i)+" has no expected value. Returned value: '"+result+"'."
        elif result != correct[i-1]:
            print "Test "+str(i)+" failed. Expected: '"+correct[i-1]+"'. Actual: '"+result+"'."

def runIconTests():
    global fopentime
    fopentime = 0
    
    correct = ["champion-blitzcrank", "champion-heimerdinger", "monster-dragon", "champion-orianna", "item-ruby-sightstone", "item-frozen-heart",
               "item-dorans-ring", "item-mana-potion", "summoner-flash", "champion-sivir", "item-shurelyas-reverie-activated-half", "blank",
               "item-shurelyas-reverie-activated", "item-shurelyas-reverie-activated-half", "item-shurelyas-reverie-activated-half",
               "item-shurelyas-reverie-activated-done", "item-sightstone", "item-shurelyas-reverie"]
    
    print "Running Icon tests..."
    for i in range(1, 19):
        fopenstart = time.clock()
        im = Image.open('tests/icon'+str(i)+'.png')
        fopentime += (time.clock() - fopenstart) * 1000
        result = icon.imageToIconName(im)
        if len(correct) < i:
            print "Test "+str(i)+" has no expected value. Returned value: '"+result+"'."
        elif result != correct[i-1]:
            print "Test "+str(i)+" failed. Expected: '"+correct[i-1]+"'. Actual: '"+result+"'."

def runScreenshotTests():
    global fopentime
    """
    correct = [{'loading': False, 'gold_data_available': True, 'teams': [{'kills': 10, 'gold': 32157}, {'kills': 18, 'gold': 38996}], 'players': [[{'kills': 4, 'gold': '1118(7654)', 'level': 13, 'deaths': 3, 'kda': ['4', '3', '1'], 'dead': False, 'assists': 1, 'total_gold': 7654, 'current_gold': 1118, 'minions': '141'}, {'kills': 3, 'gold': '540(6399)', 'level': 13, 'deaths': 3, 'kda': ['3', '3', '1'], 'dead': False, 'assists': 1, 'total_gold': 6399, 'current_gold': 540, 'minions': '95'}, {'kills': 0, 'gold': '311(5451)', 'level': 13, 'deaths': 4, 'kda': ['0', '4', '2'], 'dead': False, 'assists': 2, 'total_gold': 5451, 'current_gold': 311, 'minions': '96'}, {'kills': 2, 'gold': '545(6980)', 'level': 13, 'deaths': 6, 'kda': ['2', '6', '3'], 'dead': False, 'assists': 3, 'total_gold': 6980, 'current_gold': 545, 'minions': '121'}, {'kills': 1, 'gold': '1112(5673)', 'level': 11, 'deaths': 2, 'kda': ['1', '2', '3'], 'dead': False, 'assists': 3, 'total_gold': 5673, 'current_gold': 1112, 'minions': '30'}], [{'kills': 1, 'gold': '245(6191)', 'level': 0, 'deaths': 1, 'kda': ['1', '1', '8'], 'dead': False, 'assists': 8, 'total_gold': 6191, 'current_gold': 245, 'minions': '11'}, {'kills': 7, 'gold': '391(8920)', 'level': 0, 'deaths': 2, 'kda': ['7', '2', '2'], 'dead': False, 'assists': 2, 'total_gold': 8920, 'current_gold': 391, 'minions': '145'}, {'kills': 1, 'gold': '452(6578)', 'level': 0, 'deaths': 3, 'kda': ['1', '3', '7'], 'dead': False, 'assists': 7, 'total_gold': 6578, 'current_gold': 452, 'minions': '101'}, {'kills': 5, 'gold': '725(9088)', 'level': 16, 'deaths': 3, 'kda': ['5', '3', '5'], 'dead': False, 'assists': 5, 'total_gold': 9088, 'current_gold': 725, 'minions': '169'}, {'kills': 4, 'gold': '3889(8219)', 'level': 14, 'deaths': 1, 'kda': ['4', '1', '7'], 'dead': False, 'assists': 7, 'total_gold': 8219, 'current_gold': 3889, 'minions': '125'}]], 'game_finished': False, 'time': 1545, 'item_data_available': False, 'speed': 1},
        {'loading': False, 'gold_data_available': False, 'teams': [{'kills': 14, 'gold': None}, {'kills': 32, 'gold': None}], 'players': [[{'kills': 6, 'gold': None, 'level': 17, 'deaths': 6, 'kda': ['6', '6', '3'], 'dead': True, 'assists': 3, 'minions': '204'}, {'kills': 4, 'gold': None, 'level': 16, 'deaths': 5, 'kda': ['4', '5', '4'], 'dead': False, 'assists': 4, 'minions': '133'}, {'kills': 0, 'gold': None, 'level': 16, 'deaths': 7, 'kda': ['0', '7', '3'], 'dead': False, 'assists': 3, 'minions': '126'}, {'kills': 3, 'gold': None, 'level': 16, 'deaths': 10, 'kda': ['3', '10', '4'], 'dead': False, 'assists': 4, 'minions': '162'}, {'kills': 1, 'gold': None, 'level': 14, 'deaths': 4, 'kda': ['1', '4', '7'], 'dead': False, 'assists': 7, 'minions': '40'}], [{'kills': 2, 'gold': None, 'level': 14, 'deaths': 1, 'kda': ['2', '1', '18'], 'dead': False, 'assists': 18, 'minions': '16'}, {'kills': 12, 'gold': None, 'level': 16, 'deaths': 3, 'kda': ['12', '3', '8'], 'dead': False, 'assists': 8, 'minions': '174'}, {'kills': 5, 'gold': None, 'level': 18, 'deaths': 3, 'kda': ['5', '3', '14'], 'dead': False, 'assists': 14, 'minions': '150'}, {'kills': 8, 'gold': None, 'level': 0, 'deaths': 5, 'kda': ['8', '5', '13'], 'dead': False, 'assists': 13, 'minions': '201'}, {'kills': 5, 'gold': None, 'level': 17, 'deaths': 2, 'kda': ['5', '2', '14'], 'dead': False, 'assists': 14, 'minions': '162'}]], 'game_finished': False, 'time': 2120, 'item_data_available': True, 'speed': 1},
        {'loading': False, 'gold_data_available': True, 'teams': [{'kills': 14, 'gold': 44590}, {'kills': 32, 'gold': 56297}], 'players': [[{'kills': 6, 'gold': '2164(11099)', 'level': 17, 'deaths': 6, 'kda': ['6', '6', '3'], 'dead': True, 'assists': 3, 'total_gold': 11099, 'current_gold': 2164, 'minions': '204'}, {'kills': 4, 'gold': '485(9059)', 'level': 16, 'deaths': 5, 'kda': ['4', '5', '4'], 'dead': False, 'assists': 4, 'total_gold': 9059, 'current_gold': 485, 'minions': '133'}, {'kills': 0, 'gold': '1066(7192)', 'level': 16, 'deaths': 7, 'kda': ['0', '7', '3'], 'dead': False, 'assists': 3, 'total_gold': 7192, 'current_gold': 1066, 'minions': '123'}, {'kills': 3, 'gold': '299(9360)', 'level': 16, 'deaths': 10, 'kda': ['3', '10', '4'], 'dead': False, 'assists': 4, 'total_gold': 9360, 'current_gold': 299, 'minions': '162'}, {'kills': 1, 'gold': '371(7880)', 'level': 14, 'deaths': 4, 'kda': ['1', '4', '7'], 'dead': False, 'assists': 7, 'total_gold': 7880, 'current_gold': 371, 'minions': '40'}], [{'kills': 2, 'gold': '945(9061)', 'level': 14, 'deaths': 1, 'kda': ['2', '1', '18'], 'dead': False, 'assists': 18, 'total_gold': 9061, 'current_gold': 945, 'minions': '16'}, {'kills': 12, 'gold': '2701(12780)', 'level': 16, 'deaths': 3, 'kda': ['12', '3', '8'], 'dead': False, 'assists': 8, 'total_gold': 12780, 'current_gold': 2701, 'minions': '172'}, {'kills': 5, 'gold': '1295(10680)', 'level': 0, 'deaths': 3, 'kda': ['5', '3', '14'], 'dead': False, 'assists': 14, 'total_gold': 10680, 'current_gold': 1295, 'minions': '150'}, {'kills': 8, 'gold': '1052(12539)', 'level': 18, 'deaths': 5, 'kda': ['8', '5', '13'], 'dead': False, 'assists': 13, 'total_gold': 12539, 'current_gold': 1052, 'minions': '200'}, {'kills': 5, 'gold': '1570(11237)', 'level': 17, 'deaths': 2, 'kda': ['5', '2', '14'], 'dead': False, 'assists': 14, 'total_gold': 11237, 'current_gold': 1570, 'minions': '162'}]], 'game_finished': False, 'time': 2095, 'item_data_available': False, 'speed': 1},
        {'loading': False, 'gold_data_available': True, 'teams': [{'kills': 14, 'gold': 44590}, {'kills': 32, 'gold': 56297}], 'players': [[{'kills': 6, 'gold': '2164(11099)', 'level': 17, 'deaths': 6, 'kda': ['6', '6', '3'], 'dead': True, 'assists': 3, 'total_gold': 11099, 'current_gold': 2164, 'minions': '204'}, {'kills': 4, 'gold': '485(9059)', 'level': 16, 'deaths': 5, 'kda': ['4', '5', '4'], 'dead': False, 'assists': 4, 'total_gold': 9059, 'current_gold': 485, 'minions': '133'}, {'kills': 0, 'gold': '1066(7192)', 'level': 16, 'deaths': 7, 'kda': ['0', '7', '3'], 'dead': False, 'assists': 3, 'total_gold': 7192, 'current_gold': 1066, 'minions': '123'}, {'kills': 3, 'gold': '299(9360)', 'level': 16, 'deaths': 10, 'kda': ['3', '10', '4'], 'dead': False, 'assists': 4, 'total_gold': 9360, 'current_gold': 299, 'minions': '162'}, {'kills': 1, 'gold': '371(7880)', 'level': 14, 'deaths': 4, 'kda': ['1', '4', '7'], 'dead': False, 'assists': 7, 'total_gold': 7880, 'current_gold': 371, 'minions': '40'}], [{'kills': 2, 'gold': '945(9061)', 'level': 14, 'deaths': 1, 'kda': ['2', '1', '18'], 'dead': False, 'assists': 18, 'total_gold': 9061, 'current_gold': 945, 'minions': '16'}, {'kills': 12, 'gold': '2701(12780)', 'level': 16, 'deaths': 3, 'kda': ['12', '3', '8'], 'dead': False, 'assists': 8, 'total_gold': 12780, 'current_gold': 2701, 'minions': '172'}, {'kills': 5, 'gold': '1295(10680)', 'level': 0, 'deaths': 3, 'kda': ['5', '3', '14'], 'dead': False, 'assists': 14, 'total_gold': 10680, 'current_gold': 1295, 'minions': '150'}, {'kills': 8, 'gold': '1052(12539)', 'level': 18, 'deaths': 5, 'kda': ['8', '5', '13'], 'dead': False, 'assists': 13, 'total_gold': 12539, 'current_gold': 1052, 'minions': '200'}, {'kills': 5, 'gold': '1570(11237)', 'level': 17, 'deaths': 2, 'kda': ['5', '2', '14'], 'dead': False, 'assists': 14, 'total_gold': 11237, 'current_gold': 1570, 'minions': '162'}]], 'game_finished': False, 'time': 2095, 'item_data_available': False, 'speed': 1},
        {'loading': True},
        False,
        {'loading': False, 'gold_data_available': False, 'teams': [{'kills': 18, 'gold': None}, {'kills': 10, 'gold': None}], 'players': [[{'kills': 0, 'gold': None, 'level': 0, 'deaths': 3, 'kda': ['0', '3', '8'], 'dead': False, 'assists': 8, 'minions': '2'}, {'kills': 3, 'gold': None, 'level': 0, 'deaths': 1, 'kda': ['3', '1', '1'], 'dead': False, 'assists': 1, 'minions': '133'}, {'kills': 0, 'gold': None, 'level': 12, 'deaths': 0, 'kda': ['0', '0', '5'], 'dead': False, 'assists': 5, 'minions': '99'}, {'kills': 8, 'gold': None, 'level': 14, 'deaths': 1, 'kda': ['8', '1', '2'], 'dead': False, 'assists': 2, 'minions': '204'}, {'kills': 7, 'gold': None, 'level': 15, 'deaths': 5, 'kda': ['7', '5', '3'], 'dead': False, 'assists': 3, 'minions': '152'}], [{'kills': 0, 'gold': None, 'level': 0, 'deaths': 4, 'kda': ['0', '4', '5'], 'dead': False, 'assists': 5, 'minions': '125'}, {'kills': 1, 'gold': None, 'level': 0, 'deaths': 3, 'kda': ['1', '3', '2'], 'dead': False, 'assists': 2, 'minions': '108'}, {'kills': 3, 'gold': None, 'level': 0, 'deaths': 3, 'kda': ['3', '3', '2'], 'dead': False, 'assists': 2, 'minions': '125'}, {'kills': 6, 'gold': None, 'level': 13, 'deaths': 4, 'kda': ['6', '4', '0'], 'dead': False, 'assists': 0, 'minions': '79'}, {'kills': 0, 'gold': None, 'level': 10, 'deaths': 4, 'kda': ['0', '4', '4'], 'dead': False, 'assists': 4, 'minions': '16'}]], 'game_finished': True, 'time': 1441, 'item_data_available': True, 'speed': 1},
        {'loading': False, 'gold_data_available': True, 'teams': [{'kills': 8, 'gold': 23293}, {'kills': 7, 'gold': 20523}], 'players': [[{'kills': 0, 'gold': '1031(3467)', 'level': 9, 'deaths': 2, 'kda': ['0', '2', '3'], 'dead': True, 'assists': 3, 'total_gold': 3467, 'current_gold': 1031, 'minions': '2'}, {'kills': 1, 'gold': '774(4739)', 'level': 0, 'deaths': 0, 'kda': ['1', '0', '0'], 'dead': False, 'assists': 0, 'total_gold': 4739, 'current_gold': 774, 'minions': '108'}, {'kills': 0, 'gold': '1480(3656)', 'level': 0, 'deaths': 0, 'kda': ['0', '0', '2'], 'dead': False, 'assists': 2, 'total_gold': 3656, 'current_gold': 1480, 'minions': '68'}, {'kills': 3, 'gold': '1918(5940)', 'level': 0, 'deaths': 1, 'kda': ['3', '1', '0'], 'dead': False, 'assists': 0, 'total_gold': 5940, 'current_gold': 1918, 'minions': '145'}, {'kills': 4, 'gold': '781(5491)', 'level': 12, 'deaths': 4, 'kda': ['4', '4', '0'], 'dead': False, 'assists': 0, 'total_gold': 5491, 'current_gold': 781, 'minions': '109'}], [{'kills': 0, 'gold': '1108(4333)', 'level': 10, 'deaths': 2, 'kda': ['0', '2', '2'], 'dead': True, 'assists': 2, 'total_gold': 4333, 'current_gold': 1108, 'minions': '103'}, {'kills': 0, 'gold': '895(3911)', 'level': 10, 'deaths': 2, 'kda': ['0', '2', '2'], 'dead': False, 'assists': 2, 'total_gold': 3911, 'current_gold': 895, 'minions': '75'}, {'kills': 3, 'gold': '531(4697)', 'level': 11, 'deaths': 1, 'kda': ['3', '1', '0'], 'dead': False, 'assists': 0, 'total_gold': 4697, 'current_gold': 531, 'minions': '89'}, {'kills': 4, 'gold': '49(4420)', 'level': 11, 'deaths': 2, 'kda': ['4', '2', '0'], 'dead': False, 'assists': 0, 'total_gold': 4420, 'current_gold': 49, 'minions': '51'}, {'kills': 0, 'gold': '916(3162)', 'level': 9, 'deaths': 1, 'kda': ['0', '1', '2'], 'dead': False, 'assists': 2, 'total_gold': 3162, 'current_gold': 916, 'minions': '15'}]], 'game_finished': False, 'time': 1051, 'item_data_available': False, 'speed': 8},
        {'loading': False, 'gold_data_available': True, 'teams': [{'kills': 34, 'gold': 53916}, {'kills': 13, 'gold': 38738}], 'players': [[{'kills': 7, 'gold': '878(10543)', 'level': 0, 'deaths': 3, 'kda': ['7', '3', '18'], 'dead': False, 'assists': 18, 'total_gold': 10543, 'current_gold': 878, 'minions': '119'}, {'kills': 6, 'gold': '1187(10652)', 'level': 17, 'deaths': 5, 'kda': ['6', '5', '6'], 'dead': False, 'assists': 6, 'total_gold': 10652, 'current_gold': 1187, 'minions': '168'}, {'kills': 9, 'gold': '1180(11670)', 'level': 0, 'deaths': 3, 'kda': ['9', '3', '3'], 'dead': False, 'assists': 3, 'total_gold': 11670, 'current_gold': 1180, 'minions': '183'}, {'kills': 9, 'gold': '859(11284)', 'level': 15, 'deaths': 2, 'kda': ['9', '2', '10'], 'dead': False, 'assists': 10, 'total_gold': 11284, 'current_gold': 859, 'minions': '164'}, {'kills': 3, 'gold': '993(9767)', 'level': 14, 'deaths': 1, 'kda': ['3', '1', '21'], 'dead': False, 'assists': 21, 'total_gold': 9767, 'current_gold': 993, 'minions': '23'}], [{'kills': 7, 'gold': '1243(10155)', 'level': 17, 'deaths': 1, 'kda': ['7', '1', '1'], 'dead': False, 'assists': 1, 'total_gold': 10155, 'current_gold': 1243, 'minions': '191'}, {'kills': 0, 'gold': '465(7368)', 'level': 15, 'deaths': 6, 'kda': ['0', '6', '7'], 'dead': False, 'assists': 7, 'total_gold': 7368, 'current_gold': 465, 'minions': '133'}, {'kills': 5, 'gold': '1038(8683)', 'level': 15, 'deaths': 7, 'kda': ['5', '7', '4'], 'dead': False, 'assists': 4, 'total_gold': 8683, 'current_gold': 1038, 'minions': '114'}, {'kills': 1, 'gold': '135(6220)', 'level': 12, 'deaths': 10, 'kda': ['1', '10', '2'], 'dead': False, 'assists': 2, 'total_gold': 6220, 'current_gold': 135, 'minions': '17'}, {'kills': 0, 'gold': '207(6312)', 'level': 13, 'deaths': 10, 'kda': ['0', '10', '3'], 'dead': False, 'assists': 3, 'total_gold': 6312, 'current_gold': 207, 'minions': '122'}]], 'game_finished': False, 'time': 1873, 'item_data_available': False, 'speed': 4},
        {'loading': False, 'gold_data_available': True, 'teams': [{'kills': 29, 'gold': 64732}, {'kills': 35, 'gold': 65045}], 'players': [[{'kills': 1, 'gold': '1282(10931)', 'level': 18, 'deaths': 11, 'kda': ['1', '11', '11'], 'dead': True, 'assists': 11, 'total_gold': 10931, 'current_gold': 1282, 'minions': '169'}, {'kills': 2, 'gold': '310(12979)', 'level': 18, 'deaths': 8, 'kda': ['2', '8', '10'], 'dead': False, 'assists': 10, 'total_gold': 12979, 'current_gold': 310, 'minions': '247'}, {'kills': 7, 'gold': '1073(11302)', 'level': 17, 'deaths': 7, 'kda': ['7', '7', '18'], 'dead': True, 'assists': 18, 'total_gold': 11302, 'current_gold': 1073, 'minions': '86'}, {'kills': 9, 'gold': '101(16951)', 'level': 18, 'deaths': 3, 'kda': ['9', '3', '16'], 'dead': False, 'assists': 16, 'total_gold': 16951, 'current_gold': 101, 'minions': '304'}, {'kills': 10, 'gold': '1319(12569)', 'level': 16, 'deaths': 6, 'kda': ['10', '6', '18'], 'dead': True, 'assists': 18, 'total_gold': 12569, 'current_gold': 1319, 'minions': '25'}], [{'kills': 7, 'gold': '621(12672)', 'level': 18, 'deaths': 9, 'kda': ['7', '9', '16'], 'dead': False, 'assists': 16, 'total_gold': 12672, 'current_gold': 621, 'minions': '146'}, {'kills': 1, 'gold': '1368(7348)', 'level': 16, 'deaths': 9, 'kda': ['1', '9', '13'], 'dead': False, 'assists': 13, 'total_gold': 7348, 'current_gold': 1368, 'minions': '13'}, {'kills': 7, 'gold': '1231(13070)', 'level': 18, 'deaths': 3, 'kda': ['7', '3', '9'], 'dead': False, 'assists': 9, 'total_gold': 13070, 'current_gold': 1231, 'minions': '222'}, {'kills': 11, 'gold': '1497(16662)', 'level': 18, 'deaths': 6, 'kda': ['11', '6', '15'], 'dead': False, 'assists': 15, 'total_gold': 16662, 'current_gold': 1497, 'minions': '310'}, {'kills': 9, 'gold': '1014(15293)', 'level': 18, 'deaths': 2, 'kda': ['9', '2', '7'], 'dead': False, 'assists': 7, 'total_gold': 15293, 'current_gold': 1014, 'minions': '288'}]], 'game_finished': False, 'time': 2540, 'item_data_available': False, 'speed': 1}
        ]
    """
    print "Running Screenshot tests..."
    fopentime = 0
    
    for i in range(1, 17):
        fopenstart = time.clock()
        im= Image.open("tests/screenshot"+str(i)+".png")
        fopentime += (time.clock() - fopenstart) * 1000
        data = (getScreenshotData(im, True))
        #print data['events'] if data and 'events' in data else None
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
        
        #if len(correct) < i:
        #    print "Test "+str(i)+" has no expected value. Returned value: '"+str(data)+"'."
        #elif data != correct[i-1]:
        #    print "Test "+str(i)+" failed. Expected: '"+str(correct[i-1])+"'. Actual: '"+str(data)+"'."
        #    print "Difference: "
        #    pp.pprint(dict_diff(correct[i-1], data))
        #print data['speed'] if data and 'speed' in data else None

start = time.clock()
runOCRTests()
print "Finished in " + str((time.clock() - start)*1000)+"ms ("+str(fopentime)+"ms spent opening files)"

start = time.clock()
runIconTests()
print "Finished in " + str((time.clock() - start)*1000)+"ms ("+str(fopentime)+"ms spent opening files)"

start = time.clock()
runScreenshotTests()
print "Finished in " + str((time.clock() - start)*1000)+"ms ("+str(fopentime)+"ms spent opening files)"
