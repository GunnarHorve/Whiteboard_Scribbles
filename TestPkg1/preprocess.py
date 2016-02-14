import cv2
import sys
import TabID
import auto_crop
from normalize_training_image import normalize_training_image
import glob
import shutil
import os
import cv2

# def main():
#     #img = cv2.imread(sys.argv[1:],0)                               #read in image from console
#     img = cv2.imread('../images/training/training1.jpg',0)         #read in image
#     img = auto_crop.crop_to_bounding_box(img)                       #crop image
#     _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)    #binarize image
#     img = normalize_training_image(255 - img, 50)                   #normalize image height
#     tabs = TabID.run(255-img,50)                                    #identify indent levels
#     print(tabs)
#     cv2.imshow("TEST", img)
#     cv2.waitKey(0)

#something with Tebbe
#something with post processing

def main():
    auto_crop.crop_to_bounding_boxes(glob.glob('../images/training/*training*'))
    listing = os.listdir("../images/temp/")
    for file in listing:
        img = cv2.imread("../images/temp/" + file,0)
        if file != "training":
            if "training" in file and "cropped" in file:
                _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                img = normalize_training_image(img, 30)
                tabs = TabID.run(255-img,50)                                 #identify indent levels
                print(tabs)
                cv2.imwrite("../images/preprocessed/" + file, img)

    # cleanup: remove temp folder
    if os.path.exists('../images/temp'):
        shutil.rmtree('../images/temp')

if __name__ == '__main__':
    print 'hi'
    main()
