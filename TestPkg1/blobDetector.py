import cv2
import os
import numpy as np
from matplotlib import pyplot as plt

# TODO: change me for your system
img = cv2.imread("../images/GunnarHandwriting/a_Front.jpg", 0)
cv2.imshow('Original Image', img)
cv2.waitKey(0)
# We want the blobs that we want to detect to be white, so we'll inversely threshold the image
_, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
_, regions = cv2.connectedComponents(img, img)

if not os.path.exists("../images/cc"):
    os.makedirs("../images/cc")

cv2.imshow('Thresholded Image', img)
cv2.waitKey(0)
cv2.imwrite("../images/cc/thresholded.png", img)

# when we write out, we have the right data
cv2.imwrite("../images/cc/cc.png", regions)

# read it back in so we can visualize it
cc = cv2.imread("../images/cc/cc.png", 0)
cv2.imshow('Connected Components', cc)
cv2.waitKey(0)

# Binarize the image for visualization
_, cc_vis = cv2.threshold(cc, 1, 255, cv2.THRESH_BINARY)
cv2.imwrite("../images/cc/binarized_cc.png", cc_vis)
cv2.imshow('Binarized Connected Components', cc_vis)
cv2.waitKey(0)
