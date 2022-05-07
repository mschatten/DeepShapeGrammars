import sys
import cv2 as cv
import numpy as np

_SIMILARITY_THRESHOLD = 0.8
_MIN_PIXEL_DISTANCE_BETWEEN_POINTS = 10.0


def _get_distance_between_points(point1: list[int], point2: list[int]):
    return np.linalg.norm(np.array(point1) - np.array(point2))


def match_template(source_image_path: str, template_image_path: str):
    img_rgb = cv.imread(source_image_path)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    template = cv.imread(template_image_path, 0)
    w, h = template.shape[::-1]

    res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= _SIMILARITY_THRESHOLD)
    bboxes = []
    for pt in zip(*loc[::-1]):
        bbox = [list(pt), [pt[0] + w, pt[1] + h]]

        # OpenCV may generate bboxes where one compared to another is only 1px
        # away which gives the same exact result from human standpoint
        # thus we wish to filter out bboxes where distance between bboxes is
        # not at least 10px
        if all(
            [
                _get_distance_between_points(b[0], bbox[0])
                > _MIN_PIXEL_DISTANCE_BETWEEN_POINTS
                for b in bboxes
            ]
        ):
            bboxes.append(bbox)

    return bboxes


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("Must provide path to source image & template image!")

    source_image_path = sys.argv[1]
    template_image_path = sys.argv[2]

    bboxes = match_template(source_image_path, template_image_path)
    print(bboxes)
