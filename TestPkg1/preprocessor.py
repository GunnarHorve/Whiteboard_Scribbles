import glob
import shutil
import os

from blob_detector import find_connected_components
from bounding_box_finder import crop_to_bounding_boxes


def preprocessor_main():
    crop_to_bounding_boxes(glob.glob('../images/GunnarHandwriting/*Front*'))
    find_connected_components(glob.glob('../images/temp/*Front*'))

    # cleanup: remove temp folder
    if os.path.exists('../images/temp'):
        shutil.rmtree('../images/temp')


preprocessor_main()
