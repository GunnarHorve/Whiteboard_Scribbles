import os

import cv2
import numpy as np


def main():
    # TODO: change me for your system
    img = cv2.imread("../images/GunnarHandwriting/a_Front.jpg", 0)
    cv2.imshow('Original Image', img)
    cv2.waitKey(0)


def find_connected_components(image_path_list, disp=False):
    """
    Finds all connected components for each image denoted by image_path_list
    :param image_path_list: a list of file paths denoting the images to find connected components for
    :param disp: Whether to display intermediate results
    :return: None
    """
    if not os.path.exists("../images/connected_components"):
        os.makedirs("../images/connected_components")
    for image_path in image_path_list:
        img = cv2.imread(image_path, 0)
        cc_img = _find_connected_components(img, disp)

        split_path = os.path.splitext(image_path)[0]
        filename = split_path[split_path.index('\\') + 1:]
        filename = '../images/connected_components/' + filename + '_cc.png'
        print('writing image: ' + filename)
        cv2.imwrite(filename, cc_img)


def _find_connected_components(img, disp=False):
    """
    Finds the connected components for the given image.
    :param img: The image to find connected components for
    :param disp: Whether to display intermediate results
    :return: a grayscale image that shows all connected components for the given image
    """
    # We want the blobs that we want to detect to be white, so we'll inversely threshold the image
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    _, regions = cv2.connectedComponents(img, img)

    cc = np.uint8(regions)

    if disp:
        cv2.imshow('Thresholded Image', img)
        # cv2.waitKey(0)
        # cv2.imwrite("../images/connected_components/thresholded.png", img)

        # when we write out, we have the right data

        # read it back in so we can visualize it
        cv2.imshow('Connected Components', cc)
        cv2.waitKey(0)

        # Binarize the image for visualization
        _, cc_vis = cv2.threshold(cc, 1, 255, cv2.THRESH_BINARY)
        cv2.imshow('Binarized Connected Components', cc_vis)
        cv2.waitKey(0)

    return cc


if __name__ == '__main__':
    main()
