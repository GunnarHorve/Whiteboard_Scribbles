import glob
import shutil
import os
import cv2

from blob_detector import find_connected_components
from bounding_box_finder import crop_to_bounding_boxes
import normalizeTraningImage


def preprocessor_main():
    crop_to_bounding_boxes(glob.glob('../images/training/*training*'))
    listing = os.listdir("../images/temp/")
    for file in listing:
        img = cv2.imread("../images/temp/" + file,0)
        if file != "training":
            if "training" in file and "cropped" in file:
                _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                img = normalizeTraningImage.normalizeTrainingImage(img, 30)
                # cv2.imshow('Preprocessed Image', img)
                # cv2.waitKey(0)
                cv2.imwrite("../images/preprocessed/" + file, img)

    # cleanup: remove temp folder
    if os.path.exists('../images/temp'):
        shutil.rmtree('../images/temp')


preprocessor_main()
