import cv2
import os

import numpy as np
import matplotlib.pyplot as plt

def main():
    #load image as grayscale
    img = cv2.imread('../images/Test/tab_testing.png',0)
    _, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow('pre-processed', img)
    cv2.waitKey(0)

    #aggressively horizontally blur the image
    r, c = len(img), len(img[0])
    horizontalSize = c / 25
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalSize, 1))
    img = cv2.filter2D(img, -1, horizontalStructure)
    cv2.imshow('blurred', img)
    cv2.waitKey(0)

    #Identify connected components & generate bounding boxes
    n, regions = cv2.connectedComponents(img, img)
    img = ccVisualization(regions, img)
    bbs = generateBoundingBoxes(img,n)
    cv2.imshow('Connected Components', img)
    cv2.waitKey(0)

    analyzeBBS(bbs)

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
        imgCpy = cv2.inRange(img, n-region, n-region)
        x,y,w,h = cv2.boundingRect(imgCpy)
        cv2.imshow('region ' + str(region), imgCpy)
        cv2.waitKey(0)
        boundingBoxStorage[0].append(x)
        boundingBoxStorage[1].append(y)
        boundingBoxStorage[2].append(w)
        boundingBoxStorage[3].append(h)
    return boundingBoxStorage

def analyzeBBS(bbs):
    for item in bbs: #items are in order x,y,w,h
        print len(item), item

main()