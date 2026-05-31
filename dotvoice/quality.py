import cv2
import numpy as np


def blur_score(gray):
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def coverage(gray, threshold=127):
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    return np.count_nonzero(mask) / mask.size


def skew_angle(points):
    if len(points) < 2:
        return 0.0
    pts = np.array(points, dtype=np.float32)
    _, _, angle = cv2.fitEllipse(pts) if len(pts) >= 5 else (None, None, 0.0)
    if len(pts) < 5:
        vx, vy, _, _ = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01)
        angle = float(np.degrees(np.arctan2(vy, vx)))
    if angle > 45:
        angle -= 90
    return angle


def quality_report(gray):
    return {
        'blur': blur_score(gray),
        'coverage': coverage(gray),
    }