import cv2
import numpy as np
import glob
import math


def main():
    # reducePhotos(5, glob.glob('../images/GunnarHandwriting/*'))
    find_bounding_box(glob.glob('../images/GunnarHandwriting/*Front*'))


def reduce_photos(reduction, image_path_list):
    for photo_path in image_path_list:
        img = cv2.imread(photo_path)
        height, width, channels = img.shape
        img = cv2.resize(img, (width / reduction, height / reduction))
        cv2.imwrite(photo_path, img)


def find_bounding_box(image_path_list):
    for photo_path in image_path_list:
        img = cv2.imread(photo_path, 0)
        img = cv2.medianBlur(img, 5)
        # cv2.imshow('pre',img)
        # cv2.waitKey(0)

        cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        '''
        http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#houghcircles
        cv2.HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]])
        http://stackoverflow.com/questions/13952659/detecting-concentric-circles-with-hough-circle-transform
        '''
        dp = 1
        min_dist = 1
        canny_threshold = 70
        accum_threshold = 200
        min_radius = 50
        radius_range = 10
        circles = cv2.HoughCircles(img,
                                   cv2.HOUGH_GRADIENT,
                                   dp,
                                   min_dist,
                                   canny_threshold,
                                   accum_threshold,
                                   min_radius,
                                   radius_range)

        if circles is None:
            return
        circles = np.uint16(np.around(circles))
        mean_max, mean_min = find_mean_bounding_circles(circles)

        # min bounding point
        cv2.circle(cimg, (mean_min[0], mean_min[1]), 3, (0, 0, 255), 3)
        # max bounding point
        cv2.circle(cimg, (mean_max[0], mean_max[1]), 3, (0, 0, 255), 3)
        # Bounding Box
        cv2.rectangle(cimg, (mean_min[0], mean_min[1]), (mean_max[0], mean_max[1]), (255, 0, 0), 2)

        cv2.imshow('Bounding Points and Box', cimg)
        cv2.waitKey(0)


def find_mean_bounding_circles(circles):
    # Find min and max circle for each axis
    min_circle_x = circles[0, np.where(circles[0, :, 0] == np.amin(circles[0, :, 0]))][0][0]
    min_circle_y = circles[0, np.where(circles[0, :, 1] == np.amin(circles[0, :, 1]))][0][0]
    max_circle_x = circles[0, np.where(circles[0, :, 0] == np.amax(circles[0, :, 0]))][0][0]
    max_circle_y = circles[0, np.where(circles[0, :, 1] == np.amax(circles[0, :, 1]))][0][0]

    # find mean center between min pair and max pair of circles
    min_x, min_y, _ = np.mean(np.vstack((min_circle_x, min_circle_y)), axis=0, dtype=int)
    max_x, max_y, _ = np.mean(np.vstack((max_circle_x, max_circle_y)), axis=0, dtype=int)

    # Find all circles within a box of radius tol
    tol = 10
    min_list = np.where((abs(circles[0, :, 0] - min_x) < tol) - (abs(circles[0, :, 1] - min_y) < tol).all())
    max_list = np.where((abs(circles[0, :, 0] - max_x) < tol) - (abs(circles[0, :, 1] - max_y) < tol).all())

    # Take the mean of those
    mean_min = np.mean(circles[0, min_list][0], axis=0, dtype=int)
    mean_max = np.mean(circles[0, max_list][0], axis=0, dtype=int)

    return mean_max, mean_min


main()
