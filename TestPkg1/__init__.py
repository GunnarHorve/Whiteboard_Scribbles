import cv2

def main():
    img = cv2.imread("../images/Score.png",cv2.IMREAD_COLOR )
    cv2.imshow('window title',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

main()