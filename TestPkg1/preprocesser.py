import cv2
import sys
import TabID
import autoCrop
import normalizeTraningImage

def main():
    #img = cv2.imread(sys.argv[1:],0)                            #read in image from console
    img = cv2.imread('test.png',0)                               #read in image
    img = autoCrop.crop_to_bounding_box(img)                     #crop image
    _, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV) #binarize image
    img = normalizeTraningImage(img,40)                          #normalize image height
    tabs = TabID.run(img,40)                                     #identify indent levels
    print(tabs)

if __name__ == '__main__':
    print 'hi'
    main()

#something with Tebbe
#something with post processing

# import glob
# import shutil
# import os
# import cv2
#
# from blob_detector import find_connected_components
# from bounding_box_finder import crop_to_bounding_boxes
# import normalizeTraningImage
#
#
# def preprocessor_main():
#     crop_to_bounding_boxes(glob.glob('../images/training/*training*'))
#     listing = os.listdir("../images/temp/")
#     for file in listing:
#         img = cv2.imread("../images/temp/" + file,0)
#         if file != "training":
#             if "training" in file and "cropped" in file:
#                 _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
#                 img = normalizeTraningImage.normalizeTrainingImage(img, 30)
#                 # cv2.imshow('Preprocessed Image', img)
#                 # cv2.waitKey(0)
#                 cv2.imwrite("../images/preprocessed/" + file, img)
#
#     # cleanup: remove temp folder
#     if os.path.exists('../images/temp'):
#         shutil.rmtree('../images/temp')
#
#
# preprocessor_main()
