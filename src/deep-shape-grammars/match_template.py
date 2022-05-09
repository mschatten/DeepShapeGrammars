import sys
from typing import Optional
import cv2 as cv
import numpy as np

_SIMILARITY_THRESHOLD = 0.8
_MIN_PIXEL_DISTANCE_BETWEEN_POINTS = 10.0


def _get_distance_between_points(point1: list[int], point2: list[int]):
    return np.linalg.norm(np.array(point1) - np.array(point2))


def _rotate_image(mat, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """

    height, width = mat.shape[:2]  # image shape has 3 dimensions
    image_center = (
        width / 2,
        height / 2,
    )  # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv.getRotationMatrix2D(image_center, angle, 1.0)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv.warpAffine(mat, rotation_mat, (bound_w, bound_h))

    return rotated_mat


def generate_similar_bboxes_matching_template(
    source_image_path: str,
    template_image_path: str,
    output_image_path: Optional[str] = None,
    similarity_threshold: float = _SIMILARITY_THRESHOLD,
):
    # we may as well accept here numpy list of RGB pixels (matrix)
    img_rgb = cv.imread(source_image_path)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    template = cv.imread(template_image_path, 0)
    w, h = template.shape[::-1]

    bboxes = []
    for degree in [0, 90, 180, 270]:
        rotated_template = _rotate_image(template, degree)

        res = cv.matchTemplate(img_gray, rotated_template, cv.TM_CCOEFF_NORMED)
        loc = np.where(res >= similarity_threshold)

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
                if output_image_path:
                    cv.rectangle(img_rgb, bbox[0], bbox[1], (0, 0, 255), 2)

    if output_image_path:
        cv.imwrite(output_image_path, img_rgb)

    return bboxes


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        raise ValueError(
            "Valid args are: path to source image, path to template image, path to output & similarity threshold!"
        )

    source_image_path = sys.argv[1]
    template_image_path = sys.argv[2]
    output_image_path = sys.argv[3] if len(sys.argv) == 4 else None
    similarity_threshold = (
        float(sys.argv[4]) if len(sys.argv) == 5 else _SIMILARITY_THRESHOLD
    )

    bboxes = generate_similar_bboxes_matching_template(
        source_image_path, template_image_path, output_image_path, similarity_threshold
    )
    print(bboxes)
