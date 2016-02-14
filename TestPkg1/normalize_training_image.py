from __future__ import division
import cv2
import numpy as np


def normalize_training_image(img, threshold_height):
    """ Takes in a binary image and normalizes the text within the image to the given height. """
    img = _remove_circles(img)
    cc = _horizontally_blur_image(img)
    _, cc = cv2.threshold(cc, 1, 255, cv2.THRESH_BINARY)
    _, contours, hierarchy = cv2.findContours(cc, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    avg_height = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        avg_height += h
    avg_height = avg_height / len(contours)

    parsed_contours = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h >= avg_height / 2:
            parsed_contours.append(cnt)

    new_avg_height = 0
    for cnt in parsed_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        new_avg_height += h
    new_avg_height = new_avg_height / len(parsed_contours)

    # minHeight = float("inf")
    # maxHeight = 0
    # for cnt in parsed_contours:
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     maxHeight = max(maxHeight, h)
    #     minHeight = min(minHeight, h)
    #
    # avg_height = 0
    # for cnt in parsed_contours:
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     newHeight = (h - minHeight) * (thresholdHeight / (maxHeight - minHeight))
    #     avg_height += newHeight
    # avg_height = avg_height / len(contours)

    p = threshold_height / new_avg_height

    height, width = img.shape
    dim = (int(width * p), int(height * p))
    return cv2.resize(img, dim)


def _horizontally_blur_image(img):
    r, c = len(img), len(img[0])
    horizontal_size = c // 25
    horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    inverted = (255 - img)
    img = cv2.filter2D(inverted, -1, horizontal_structure)

    _, regions = _find_connected_components(img)
    return regions


def _remove_circles(img):
    n, regions = _find_connected_components((255 - img))
    x, y, w, h = cv2.boundingRect(regions)
    for i in range(1, n):
        idx = np.where(regions[x, :] == i)
        if len(idx[0]) > 0:
            # print idx
            regions[np.where(regions == i)] = 0

        idx = np.where(regions[:, y] == i)
        if len(idx[0]) > 0:
            # print idx
            regions[np.where(regions == i)] = 0

        idx = np.where(regions[h - 1, :] == i)
        if len(idx[0]) > 0:
            # print idx
            regions[np.where(regions == i)] = 0

        idx = np.where(regions[:, w - 1] == i)
        if len(idx[0]) > 0:
            # print idx
            regions[np.where(regions == i)] = 0
    _, regions = cv2.threshold(regions, 1, 255, cv2.THRESH_BINARY)
    return 255 - regions


def _find_connected_components(img):
    n, regions = cv2.connectedComponents(img)
    regions = np.uint8(regions)
    return n, regions


def main():
    img = cv2.imread('../images/training/training1.jpg', 0)
    _, img = cv2.threshold(255 - img, 127, 255, cv2.THRESH_BINARY_INV)
    # img = cv2.imread('test2.png', 0)
    cv2.imshow('Original', img)
    cv2.waitKey(0)
    img = normalize_training_image(img, 20)
    cv2.imshow('Resize', img)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
