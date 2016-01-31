import cv2
import numpy as np
import glob

def main():
    #reducePhotos(5, glob.glob('../images/GunnarHandwriting/*'))
    circleDetect(glob.glob('../images/GunnarHandwriting/*'))

def reducePhotos(reduction,imagePathList):
    for photoPath in imagePathList:
        img = cv2.imread(photoPath)
        height, width, channels = img.shape
        img = cv2.resize(img, (width/reduction, height/reduction))
        cv2.imwrite(photoPath, img)

def circleDetect(imagePathList):
    for photoPath in imagePathList:
        img = cv2.imread(photoPath,0)
        img = cv2.medianBlur(img,5)
        # cv2.imshow('pre',img)
        # cv2.waitKey(0)

        cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,70,100,50,10)

        if not circles == None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2) # draw the outer circle
                cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)    # draw the center of the circle

            cv2.imshow('detected circles',cimg)
            cv2.waitKey(0)

main()