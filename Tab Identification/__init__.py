import cv2
import os

averageLineHeight = 20  #this value is used to kill questionable lines that are too thin (the dots of i's, for example)
lineBlur = 20           #if lines aren't fully connecting to themselves, lower this number.
tabWiggleRoom = 5       #this value is how many pixels an indent is allowed to very to still be the same tab level.

def main():
    #load image as grayscale
    img = cv2.imread('../images/Test/tab_testing.png',0)
    _, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)

    #aggressively horizontally blur the image
    r, c = len(img), len(img[0])
    horizontalSize = c / lineBlur
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalSize, 1))
    img = cv2.filter2D(img, -1, horizontalStructure)

    #Identify connected components & generate bounding boxes
    n, regions = cv2.connectedComponents(img, img)
    img = ccVisualization(regions, img)
    bbs = generateBoundingBoxes(img,n)

    print analyzeBBS(bbs)

'''
This function writes an image to a file and re-loads it so it can be visualized
(done b/c of a bug from cv2.connectedComponents?)
'''
def ccVisualization(regions, img):
    if not os.path.exists("../images/cc"):
        os.makedirs("../images/cc")

    cv2.imwrite("../images/cc/cc.png", regions) # when we write out, we have the right data
    return cv2.imread("../images/cc/cc.png", 0)

'''
This function takes an image that has been parsed into regions and creates/stores bounding box
information for every region
'''
def generateBoundingBoxes(img,n):
    boundingBoxStorage = [[], [], [], []] #stored as [[x][y][w][h]]
    for region in range(n):
        #imgCpy = cv2.inRange(img, n-region, n-region)
        imgCpy = cv2.inRange(img, region, region)

        x,y,w,h = cv2.boundingRect(imgCpy)
        if (h > averageLineHeight/2 and h < averageLineHeight*2):  #only keep things that are actually lines
            boundingBoxStorage[0].append(x)
            boundingBoxStorage[1].append(y)
            boundingBoxStorage[2].append(w)
            boundingBoxStorage[3].append(h)
    return boundingBoxStorage


'''
This function takes in ordered bounding box data of an image's lines and computes the indentation
level of each line based on the bounding box for each line.  The data input should look like...
    [ [x1, x2, x3, ... , xN],
      [y1, y2, y3, ... , yN],
      [w1, w2, w3, ... , wN],
      [h1, h2, h3, ... , hN]]
Line indentation levels ordered from top line to bottom line are returned.
(P.S., this is a relatively inefficient function.  Don't try to use it for an image with 1,000+ lines)
'''
def analyzeBBS(bbs):
    ranges = []
    for x in bbs[0]:
        ranges += [(x-tabWiggleRoom, x+tabWiggleRoom)]

    changed = True
    while(changed): #combine ranges until there is nothing left to combine.
        changed = False
        for i in range(len(ranges)): #try to conbine at every index
            prevLen = len(ranges)
            ranges = combineAtRange(i, ranges)
            changed = prevLen != len(ranges)
            if (changed):
                break

    tabLevels = []
    for i in range(len(ranges)): #create tab levels
        tabLevels.append(sum(ranges[i])/2)

    tabLevels = sorted(tabLevels)
    orderedTabLevels = []
    for x in bbs[0]: #loop over every line and assign it a tab position.
        for i in range(len(tabLevels)):
            if(tabLevels[i] - tabWiggleRoom <= x and tabLevels[i] + tabWiggleRoom >= x):
                #we've found the correct assignment, move on to next line
                orderedTabLevels.append(i)
                break

    return orderedTabLevels


'''
This function takes a list of ranges [(min1,max1),(min2,max2), ... , (minN, maxN)]
and merges ranges that intersect the given index together.  That is, if index = 1,
[(4, 10), (2,4), (20,25),(18,21)] --> [(2,10), (20,25), (18,21)]
'''
def combineAtRange(index,ranges):
    curRange = ranges[index]
    killIndicies = []
    minn = min(curRange)
    maxx = max(curRange)
    for i in range(len(ranges)):
        if i == index:
            continue
        minIn = curRange[0] >= ranges[i][0] and curRange[0] <= ranges[i][1]
        maxIn = curRange[1] <= ranges[i][1] and curRange[1] >= ranges[i][0]
        if(minIn or maxIn):
            killIndicies.append(i)
            minn = min(minn,ranges[i][0])
            maxx = max(maxx,ranges[i][1])

    ranges[index] = (minn,maxx)
    for offset, index in enumerate(killIndicies):
        index -= offset
        del ranges[index]
    return ranges

main()
