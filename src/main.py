import cv2
from PIL import Image

import auto_crop
import pytesseract
from id_tabs import id_tabs
from normalize_training_image import normalize_training_image
from postprocess import proofread


def main():
    disp = False
    # img = cv2.imread(sys.argv[1:],0 # read in image from console
    img = cv2.imread('../images/training/training1.jpg', 0)         # read in image
    img = auto_crop.crop_to_bounding_box(img, disp)  # crop image
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
    # print(tabs)

    # something with Tebbe
    cv2.imwrite("text.png", img)
    pil_img = Image.open("text.png")
    # pil_img.show()
    translation = pytesseract.image_to_string(pil_img, 'hww')
    print translation

    # something with post processing
    # foo = proofread(translation.split('\n'))
    # print foo

if __name__ == '__main__':
    main()
