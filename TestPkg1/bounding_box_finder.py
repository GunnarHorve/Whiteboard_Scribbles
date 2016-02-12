import glob
import os

import cv2
import numpy as np


def main():
    # reducePhotos(5, glob.glob('../images/GunnarHandwriting/*'))
    crop_to_bounding_boxes(glob.glob('../images/GunnarHandwriting/*Front*'), False)


def reduce_photos(reduction, image_path_list):
    for photo_path in image_path_list:
        img = cv2.imread(photo_path)
        height, width, channels = img.shape
        img = cv2.resize(img, (width / reduction, height / reduction))
        cv2.imwrite(photo_path, img)


def crop_to_bounding_boxes(image_path_list, disp=False):
    """
    Attempts to crop all of the images in the given list of file paths.
    If an image cannot be cropped properly, an Exception is logged and the image is ignored.
    :param image_path_list: A list of paths for the images to crop
    :param disp: Whether to display intermediate results
    :return: None
    """
    if not os.path.exists("../images/temp"):
        os.makedirs("../images/temp")
    for image_path in image_path_list:
        img = cv2.imread(image_path, 0)
        split_path = os.path.splitext(image_path)[0]
        filename = split_path[split_path.index('\\') + 1:]
        filename = '../images/temp/' + filename + '_cropped.png'
        try:
            cropped_img = crop_to_bounding_box(img, disp)
            print('writing image: ' + filename)
            cv2.imwrite(filename, cropped_img)
        except Exception as e:
            print 'Caught Exception: ' + str(e)
            continue


def crop_to_bounding_box(img, disp=False):
    """
    Attempts to find the bounding box for an image and crop it to that box.
    Throws an exception if one of the cropped image's dimensions is 0.
    :param img: The image to crop
    :param disp: Whether to display intermediate results
    :return: the cropped image, if it is valid.
    :raises Exception: If one of the cropped image's dimensions is 0, or if there is an error in _find_bounding_box
    """
    try:
        mean_min, mean_max = _find_bounding_box(img, disp)
        if mean_min is not None and mean_max is not None:
            cropped_img = img[mean_min[1]:mean_max[1], mean_min[0]:mean_max[0]]
            if cropped_img.shape[0] != 0 and cropped_img.shape[1] != 0:
                if disp:
                    cv2.imshow('Cropped', cropped_img)
                    cv2.waitKey(0)
                return cropped_img
            else:
                raise Exception('Unable to crop image: one or more dimensions are 0')
        else:
            raise Exception('One or more bounding circles does not exist')
    except Exception as e:
        raise Exception('Unable to crop image', e)


def _find_bounding_box(img, disp=False):
    """
    Finds the bounding box for the given image, denoted by two sets of concentric circles,
        using OpenCV's HoughCircles detector.
    :param img: The image to find a bounding box for
    :param disp: Whether to display intermediate results
    :return: a pair of circles which identify the corners of the image's bounding box.
    """
    gray_img = cv2.medianBlur(img, 5).copy()
    gray_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

    '''
    http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#houghcircles
    cv2.HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]])
    http://stackoverflow.com/questions/13952659/detecting-concentric-circles-with-hough-circle-transform
    '''
    dp = 1
    min_dist = 50
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
        raise Exception('No circles detected; no cropping performed')
    if len(circles[0]) == 1:
        raise Exception('Only one circle detected; no cropping performed')

    circles = np.uint32(np.around(circles))

    mean_min, mean_max = _find_mean_bounding_circles(circles, gray_img, disp)

    if disp:
        cimg2 = gray_img.copy()
        for circ in circles[0]:
            cv2.circle(cimg2, (circ[0], circ[1]), 3, (0, 0, 255), 3)
            cv2.circle(cimg2, (circ[0], circ[1]), circ[2], (0, 255, 0), 2)
        cv2.imshow("Detected circles", cimg2)

        # min bounding point
        cv2.circle(gray_img, (mean_min[0], mean_min[1]), 3, (0, 0, 255), 3)
        # max bounding point
        cv2.circle(gray_img, (mean_max[0], mean_max[1]), 3, (0, 0, 255), 3)
        # Bounding Box
        cv2.rectangle(gray_img, (mean_min[0], mean_min[1]), (mean_max[0], mean_max[1]), (255, 0, 0), 2)

        cv2.imshow('Bounding Points and Box', gray_img)
        # cv2.waitKey(0)

    return mean_min, mean_max


def _find_mean_bounding_circles(circles, gray_img=None, disp=False):
    """
    Given a set of Hough-detected circles for the given image,
        attempts to find the circles which best define the image's bounding box.
    :param circles: The list of circles from which to find the min and max circles
    :param gray_img: The image to display. Defaults to None
    :param disp: Whether to display intermediate results
    :return: Two circles which denote the upper-left and lower-right corners of the image's bounding box.
    """
    # Find min and max circle for each axis
    min_circle_x = circles[0, np.where(circles[0, :, 0] == np.amin(circles[0, :, 0]))][0][0]
    min_circle_y = circles[0, np.where(circles[0, :, 1] == np.amin(circles[0, :, 1]))][0][0]
    max_circle_x = circles[0, np.where(circles[0, :, 0] == np.amax(circles[0, :, 0]))][0][0]
    max_circle_y = circles[0, np.where(circles[0, :, 1] == np.amax(circles[0, :, 1]))][0][0]

    # find mean center between min pair and max pair of circles
    min_x, min_y, min_rad = np.mean(np.vstack((min_circle_x, min_circle_y)), axis=0, dtype=int)
    max_x, max_y, max_rad = np.mean(np.vstack((max_circle_x, max_circle_y)), axis=0, dtype=int)

    # Find all circles within a radius of tol
    tol = 30
    dist_to_min = np.sqrt(((circles[0, :, 0] - min_x) ** 2) + ((circles[0, :, 1] - min_y) ** 2))
    dist_to_max = np.sqrt(((circles[0, :, 0] - max_x) ** 2) + ((circles[0, :, 1] - max_y) ** 2))

    min_list = circles[0, np.where((dist_to_min <= tol))][0]
    max_list = circles[0, np.where((dist_to_max <= tol))][0]

    # CONSIDER taking whichever of the min (max) circles minimizes its distance to the mean
    #     (i.e. the x_min circle if its x-distance is closer, the y_min circle if its y-distance is closer
    # If we don't find any circles in range, use the mean as the circle.
    if len(min_list) == 0:
        min_list = np.zeros(shape=(1, 3), dtype=np.uint32)
        min_list[0] = np.array([min_x, min_y, min_rad])

    if len(max_list) == 0:
        max_list = np.zeros(shape=(1, 3), dtype=np.uint32)
        max_list[0] = np.array([max_x, max_y, max_rad])

    if disp and gray_img:
        gray_img2 = gray_img.copy()
        for circ in np.vstack((min_list, max_list)):
            cv2.circle(gray_img2, (circ[0], circ[1]), 3, (0, 0, 255), 3)
            cv2.circle(gray_img2, (circ[0], circ[1]), circ[2], (0, 255, 0), 2)
        cv2.imshow('Min and Max circles', gray_img2)

    # Take the mean of those
    mean_min = np.mean(min_list, axis=0, dtype=int)
    mean_max = np.mean(max_list, axis=0, dtype=int)

    return mean_min, mean_max


if __name__ == '__main__':
    main()