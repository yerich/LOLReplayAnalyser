import ocr
import time
import Image

correct = ["", '106    2/6/3', '87    3/3/4', '121    2/2/2', '92    0/3/2', '5    3/3/4', '2/2/7    131', '2/2/6    78', 
           '3/3/6    15', '7/1/4    155', '3/2/2    119', '3/3/11    177', '2/2/6    78', '3/3/6    15', '9/2/5    180', '7/2/4    171', 
           '126    3/5/7', '129    3/7/7', '160    4/4/4', '130    2/4/3', '7    3/5/7', '1,118(7,654)      4/3/1    141', 
           '540(6,399)      3/3/1    95', '311(5,451)      0/4/2    96', '545(6,980)      2/6/3    121', '1,112(5,673)      1/2/3    30', 
           '15    2/1/16        844(7,839)', '157    9/3/7        516(10,594)', '119   4/3/12       1,009(8,794)', 
           '178   8/4/10       1,815(11,000)', '137   5/2/13       1,549(9,664)', '31,01', '25,45', '28,39', "25,45/35,57", 
           "28,39/32,24", "3   5   5   3", "5   3   5   3", "0    1   0   0", "4   2    1    1", '5   4   3   2',
           '14', '12', '16', '13', '14', '13', '8', '9', '7', '4', '5', '6', '17', '18', '15']

print "Running tests..."
start = time.clock()
fopentime = 0
for i in range(1, 56):
    fopenstart = time.clock()
    im = Image.open('tests/image'+str(i)+'.png')
    fopentime += (time.clock() - fopenstart) * 1000
    result = ocr.imagetostring(im)
    if result != correct[i]:
        print "Test "+str(i)+" failed. Expected: '"+correct[i]+"'. Actual: '"+result+"'."
    
print "Finished in " + str((time.clock() - start)*1000)+"ms ("+str(fopentime)+"ms spent opening files)"