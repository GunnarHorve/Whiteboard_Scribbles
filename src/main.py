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
    disp = False  # Set to true to view pre-processing of the images.
    img = cv2.imread('../images/training/training3.jpg', 0)
    img = auto_crop.crop_to_bounding_box(img, disp=disp)
    # binarize image
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    if disp:
        vis_img, _ = auto_crop.reduce_image(img.copy())
        cv2.imshow('Binary Image', vis_img)
        cv2.waitKey(0)

    img = 255 - img
    if disp:
        vis_img, _ = auto_crop.reduce_image(img.copy())
        cv2.imshow('Inverted', vis_img)
        cv2.waitKey(0)

    # normalize image height
    img, avg_line_height = normalize_training_image(img, 30, disp=disp)

    if disp:
        cv2.imshow('Normalized', img)
        cv2.waitKey(0)
    cv2.waitKey(0)

    # identify indent levels
    tabs = id_tabs(255 - img,
                   avg_line_height=avg_line_height,
                   line_blur=20,
                   tab_wiggle_room=2,
                   disp=True)
    print tabs
    cv2.imwrite("text.png", img)
    pil_img = Image.open("text.png")
    translation = pytesseract.image_to_string(pil_img, 'hww')
    print "TESSERACT RESULTS: "
    print translation

    print "\n\nPROOFREAD: "
    print proofread(translation.split('\n'), tabs)


def preprocess_images():
    auto_crop.crop_to_bounding_boxes(glob.glob('../images/training/*training*'))
    listing = os.listdir("../images/temp/")
    for file in listing:
        img = cv2.imread("../images/temp/" + file, 0)
        if file != "training":
            if "training" in file and "cropped" in file:
                _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                img = normalize_training_image(img, 30)
                tabs = id_tabs(255 - img, 50)
                print(tabs)
                cv2.imwrite("../images/preprocessed/" + file, img)

    # cleanup: remove temp folder
    if os.path.exists('../images/temp'):
        shutil.rmtree('../images/temp')


if __name__ == '__main__':
    main()
