import glob
import os
import shutil

import cv2
from PIL import Image

import auto_crop
import pytesseract
from id_tabs import id_tabs
from normalize_training_image import normalize_training_image
from postprocess import proofread


def main():
    disp = False                                                    # Set to true to view pre-processing of the images.
    img = cv2.imread('../images/training/training1.jpg', 0)         # read in image
    img = auto_crop.crop_to_bounding_box(img, disp)                 # crop image
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)    # binarize image
    if disp:
        vis_img, _ = auto_crop.reduce_image(img.copy())
        cv2.imshow('Binary Image', vis_img)
        cv2.waitKey(0)
    img = 255 - img
    if disp:
        vis_img, _ = auto_crop.reduce_image(img.copy())
        cv2.imshow('Inverted', vis_img)
        cv2.waitKey(0)
    img = normalize_training_image(img, 30, disp)  # normalize image height

    if disp:
        cv2.imshow('Normalized', img)
        cv2.waitKey(0)
    cv2.waitKey(0)

    tabs = id_tabs(255 - img, 50, 12, 2)  # identify indent levels
    # print tabs
    cv2.imwrite("text.png", img)
    pil_img = Image.open("text.png")
    translation = pytesseract.image_to_string(pil_img, 'hww')
    # print translation

    foo = proofread(translation.split('\n'), tabs)
    print foo

if __name__ == '__main__':
    main()

def preprocess_images():
    auto_crop.crop_to_bounding_boxes(glob.glob('../images/training/*training*'))
    listing = os.listdir("../images/temp/")
    for file in listing:
        img = cv2.imread("../images/temp/" + file,0)
        if file != "training":
            if "training" in file and "cropped" in file:
                _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                img = normalize_training_image(img, 30)
                tabs = id_tabs.run(255-img,50)
                print(tabs)
                cv2.imwrite("../images/preprocessed/" + file, img)

    # cleanup: remove temp folder
    if os.path.exists('../images/temp'):
        shutil.rmtree('../images/temp')
