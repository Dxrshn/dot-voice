import cv2
import numpy as np


def _blob_detector():
    params = cv2.SimpleBlobDetector_Params()
    params.filterByColor = True
    params.blobColor = 0
    params.filterByArea = True
    params.minArea = 20
    params.maxArea = 2000
    params.filterByCircularity = True
    params.minCircularity = 0.5
    params.filterByConvexity = True
    params.minConvexity = 0.7
    params.filterByInertia = True
    params.minInertiaRatio = 0.3
    return cv2.SimpleBlobDetector_create(params)


def detect_dots(gray):
    detector = _blob_detector()
    keypoints = detector.detect(gray)

    if not keypoints:
        return _fallback_detect(gray)

    dots = [(kp.pt[0], kp.pt[1], kp.size / 2) for kp in keypoints]
    dots = _filter_by_size_consistency(dots)
    return dots


def _fallback_detect(gray):
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)

    dots = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        if area < 10 or area > 3000:
            continue
        if w == 0 or h == 0:
            continue
        circularity = area / (w * h)
        if circularity < 0.4:
            continue
        cx, cy = centroids[i]
        r = (w + h) / 4
        dots.append((cx, cy, r))

    return _filter_by_size_consistency(dots)


def _filter_by_size_consistency(dots, tolerance=0.6):
    if len(dots) < 3:
        return dots
    radii = [r for _, _, r in dots]
    median_r = np.median(radii)
    return [(x, y, r) for x, y, r in dots if abs(r - median_r) < tolerance * median_r]


def draw_debug(image, dots):
    out = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
    for x, y, r in dots:
        cv2.circle(out, (int(x), int(y)), int(r) + 2, (0, 0, 255), 2)
        cv2.circle(out, (int(x), int(y)), 2, (0, 255, 0), -1)
    return out
