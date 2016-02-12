from __future__ import division
import cv2
import os

def main():
    img = cv2.imread('test1.png',0)
    img = cv2.imread('test2.png',0)
    cv2.imshow('Original', img)
    cv2.waitKey(0)
    img = normalizeTrainingImage(img, 20)
    cv2.imshow('Resize', img)
    cv2.waitKey(0)

'''
Takes in a binary image and normalizes the text within the image to the given height.
'''
def normalizeTrainingImage(img, thresholdHeight):

    cc = horizontallyBlurImage(img)
    # _, cc = cv2.threshold(cc, 1, 255, cv2.THRESH_BINARY)
    _,contours,hierarchy = cv2.findContours(cc, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    avgHeight = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        avgHeight += h
    avgHeight = avgHeight / len(contours)

    parsedContours = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h >= avgHeight / 2:
            parsedContours.append(cnt)

    newAvgHeight = 0;
    for cnt in parsedContours:
        x, y, w, h = cv2.boundingRect(cnt)
        newAvgHeight += h
    newAvgHeight = newAvgHeight / len(parsedContours)

    # minHeight = float("inf")
    # maxHeight = 0
    # for cnt in parsedContours:
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     maxHeight = max(maxHeight, h)
    #     minHeight = min(minHeight, h)
    #
    # avgHeight = 0
    # for cnt in parsedContours:
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     newHeight = (h - minHeight) * (thresholdHeight / (maxHeight - minHeight))
    #     avgHeight += newHeight
    # avgHeight = avgHeight / len(contours)

    p = thresholdHeight / newAvgHeight

    height, width = img.shape
    dim = (int(width * p), int(height * p))
    return cv2.resize(img,dim)

def horizontallyBlurImage(img):
    r, c = len(img), len(img[0])
    horizontalSize = c // 25
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalSize, 1))
    inverted = (255 - img)
    img = cv2.filter2D(inverted, -1, horizontalStructure)

    n, regions = cv2.connectedComponents(img, img)
    img = ccVisualization(regions, img)
    return img

'''
This function writes an image to a file and re-loads it so it can be visualized
(done b/c of a bug from cv2.connectedComponents?)
'''
def ccVisualization(regions, img):
    if not os.path.exists("../images/cc"):
        os.makedirs("../images/cc")

    cv2.imwrite("../images/cc/cc.png", regions) # when we write out, we have the right data
    return cv2.imread("../images/cc/cc.png", 0)

if __name__ == '__main__':
    main()


