import cv2
import os

def main():
    listing = os.listdir("images/")
    for file in listing:
        img = cv2.imread("images/" + file,0)
        if file != "training":
            if "Front" in file:
                generateTrainingSet(img, file)

def generateTrainingSet(img, file):
    saveLocation = "images/training/"
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    _, regions = cv2.connectedComponents(img, img)

    if not os.path.exists("../images/cc"):
        os.makedirs("../images/cc")

    cv2.imwrite("../images/cc/cc.png", regions)
    cc = cv2.imread("../images/cc/cc.png", 0)
    _, cc_vis = cv2.threshold(cc, 1, 255, cv2.THRESH_BINARY)

    _,contours,hierarchy = cv2.findContours(cc_vis,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    idx = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50 or area > 1000:
            continue
        if len(cnt) < 5:
            continue
        idx += 1
        x, y, w, h = cv2.boundingRect(cnt)
        roi = img[y: y + h, x: x + w]
        name = file.split('.')[0]
        inverted = (255 - roi)
        cv2.imwrite(saveLocation + name + str(idx) + '.jpg', inverted)
    cv2.waitKey(0)

main()