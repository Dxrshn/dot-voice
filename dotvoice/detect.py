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
        dots = _fallback_detect(gray)
    else:
        dots = [(kp.pt[0], kp.pt[1], kp.size / 2) for kp in keypoints]
        dots = _filter_by_size_consistency(dots)

    max_plausible = int(gray.shape[0] * gray.shape[1] / 400)
    if len(dots) > max_plausible:
        return []

    if len(dots) > 30:
        dots = _filter_by_spacing(dots)

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

    dots = _filter_by_size_consistency(dots)
    return dots


def _filter_by_size_consistency(dots, tolerance=0.5):
    if len(dots) < 3:
        return dots
    radii = [r for _, _, r in dots]
    median_r = np.median(radii)
    return [(x, y, r) for x, y, r in dots if abs(r - median_r) < tolerance * median_r]


def _filter_by_spacing(dots, tolerance=3.0):
    if len(dots) < 3:
        return dots
    pts = np.array([(x, y) for x, y, _ in dots])
    from scipy.spatial.distance import cdist
    dists = cdist(pts, pts)
    np.fill_diagonal(dists, np.inf)
    nn_dists = dists.min(axis=1)
    median_nn = np.median(nn_dists)
    if median_nn == 0:
        return dots
    return [dots[i] for i in range(len(dots)) if nn_dists[i] < tolerance * median_nn]


def draw_debug(image, dots):
    out = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
    for x, y, r in dots:
        cv2.circle(out, (int(x), int(y)), int(r) + 2, (0, 0, 255), 2)
        cv2.circle(out, (int(x), int(y)), 2, (0, 255, 0), -1)
    return out
