import cv2
import sys
import TabID
import auto_crop
from normalize_training_image import normalize_training_image
import glob
import shutil
import os
import cv2

def main():
    disp = True
    #img = cv2.imread(sys.argv[1:],0)                               #read in image from console
    img = cv2.imread('../images/training/training1.jpg',0)         #read in image
    img = auto_crop.crop_to_bounding_box(img, disp)                       #crop image
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)    #binarize image
    if disp == True:
        vis_img, _ = auto_crop._reduce_image(img.copy())
        cv2.imshow('Binary Image', vis_img)
        cv2.waitKey(0)
    img = 255 - img
    if disp == True:
        vis_img, _ = auto_crop._reduce_image(img.copy())
        cv2.imshow('Inverted', vis_img)
        cv2.waitKey(0)
    img = normalize_training_image(img, 50, disp)                   #normalize image height

    if disp == True:
        cv2.imshow('Normalized', img)
        cv2.waitKey(0)
    cv2.waitKey(0)

    tabs = TabID.run(255-img,50, True, 12, 2)                                    #identify indent levels
    print(tabs)

#something with Tebbe
#something with post processing

# def main():
#     auto_crop.crop_to_bounding_boxes(glob.glob('../images/training/*training*'))
#     listing = os.listdir("../images/temp/")
#     for file in listing:
#         img = cv2.imread("../images/temp/" + file,0)
#         if file != "training":
#             if "training" in file and "cropped" in file:
#                 _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
#                 img = normalize_training_image(img, 30)
#                 tabs = TabID.run(255-img,50)                                 #identify indent levels
#                 print(tabs)
#                 cv2.imwrite("../images/preprocessed/" + file, img)
#
#     # cleanup: remove temp folder
#     if os.path.exists('../images/temp'):
#         shutil.rmtree('../images/temp')

if __name__ == '__main__':
    print 'hi'
    main()
