import os

import cv2
import numpy as np

import auto_crop


# averageLineHeight = 20 # this value is used to kill questionable lines that are too thin (e.g. the dots of i's)
# lineBlur = 20          # if lines aren't fully connecting to themselves, lower this number.
# tabWiggleRoom = 5      # this value is how many pixels an indent is allowed to very to still be the same tab level.
def id_tabs(img, avg_line_height=20, line_blur=20, tab_wiggle_room=5, disp=False):
    """
    Attempts to identify the indent level of each line of text, with the assumption that the first line is at level 0.

    :param img: the input image (should contain text)
    :param avg_line_height: the expected vertical height of a line of text
    :param line_blur: how far the image is blurred to extract features (img.width/line_blur)
    :param tab_wiggle_room: how far in pixels tabs are allowed to be from on another before they are considered distinct
    :param disp: whether to display intermediate results
    :return: An integer list representing the tab level for each line
    """
    # load image as grayscale
    # aggressively horizontally blur the image
    r, c = len(img), len(img[0])
    horizontal_size = c / line_blur
    horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    img = cv2.filter2D(img, -1, horizontal_structure)
    if disp:
        vis_img, _ = auto_crop.reduce_image(img.copy())
        cv2.imshow('Horizontally Blur', vis_img)
        cv2.waitKey(0)
    # Identify connected components & generate bounding boxes
    n, regions = cv2.connectedComponents(img, img)
    img = np.uint8(regions)
    bbs = _generate_bounding_boxes(img, n, avg_line_height)

    return _analyze_bounding_boxes(bbs, tab_wiggle_room)


def _generate_bounding_boxes(img, n, avg_line_height):
    """
    This function takes an image that has been parsed into regions and creates/stores bounding box
    information for every region
    """
    bounding_box_storage = [[], [], [], []]  # stored as [[x][y][w][h]]
    for region in range(1, n):
        # img_copy = cv2.inRange(img, n-region, n-region)
        img_copy = cv2.inRange(img, region, region)

        x, y, w, h = cv2.boundingRect(img_copy)
        if avg_line_height / 2 < h and h < avg_line_height * 2:  # only keep things that are actually lines
            bounding_box_storage[0].append(x)
            bounding_box_storage[1].append(y)
            bounding_box_storage[2].append(w)
            bounding_box_storage[3].append(h)
    return bounding_box_storage


def _analyze_bounding_boxes(bbs, tab_wiggle_room):
    """
    This function takes in ordered bounding box data of an image's lines and computes the indentation
    level of each line based on the bounding box for each line.  The data input should look like...
        [ [x1, x2, x3, ... , xN],
          [y1, y2, y3, ... , yN],
          [w1, w2, w3, ... , wN],
          [h1, h2, h3, ... , hN]]
    Line indentation levels ordered from top line to bottom line are returned.
    (P.S., this is a relatively inefficient function.  Don't try to use it for an image with 1,000+ lines)
    """
    ranges = []
    for x in bbs[0]:
        ranges += [(x - tab_wiggle_room, x + tab_wiggle_room)]

    changed = True
    while changed:  # combine ranges until there is nothing left to combine.
        changed = False
        for i in range(len(ranges)):  # try to combine at every index
            prev_len = len(ranges)
            ranges = _combine_at_range(i, ranges)
            changed = prev_len != len(ranges)
            if changed:
                break

    tab_levels = []
    for i in range(len(ranges)):  # create tab levels
        tab_levels.append(sum(ranges[i]) / 2)

    tab_levels = sorted(tab_levels)
    ordered_tab_levels = []
    for x in bbs[0]:  # loop over every line and assign it a tab position.
        for i in range(len(tab_levels)):
            if tab_levels[i] - tab_wiggle_room <= x and x <= tab_levels[i] + tab_wiggle_room:
                # we've found the correct assignment, move on to next line
                ordered_tab_levels.append(i)
                break

    return ordered_tab_levels


def _combine_at_range(index, ranges):
    """
    This function takes a list of ranges [(min1,max1),(min2,max2), ... , (minN, maxN)]
    and merges ranges that intersect the given index together.  That is, if index = 1,
    [(4, 10), (2,4), (20,25),(18,21)] --> [(2,10), (20,25), (18,21)]
    """
    cur_range = ranges[index]
    kill_indices = []
    range_min = min(cur_range)
    range_max = max(cur_range)
    for i in range(len(ranges)):
        if i == index:
            continue
        min_in = cur_range[0] >= ranges[i][0] and cur_range[0] <= ranges[i][1]
        max_in = cur_range[1] <= ranges[i][1] and cur_range[1] >= ranges[i][0]
        if min_in or max_in:
            kill_indices.append(i)
            range_min = min(range_min, ranges[i][0])
            range_max = max(range_max, ranges[i][1])

    ranges[index] = (range_min, range_max)
    for offset, index in enumerate(kill_indices):
        index -= offset
        del ranges[index]
    return ranges
