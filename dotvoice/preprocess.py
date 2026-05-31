import cv2
import numpy as np


def to_gray(image):
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(gray):
    return cv2.GaussianBlur(gray, (5, 5), 0)


def enhance(gray):
    clip = _auto_clip(gray)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _auto_clip(gray):
    std = gray.std()
    if std < 20:
        return 5.0
    if std < 40:
        return 3.0
    return 2.0


def normalize_lighting(gray):
    blur = cv2.GaussianBlur(gray, (61, 61), 0).astype(np.float32)
    norm = (gray.astype(np.float32) / (blur + 1e-6)) * 128
    return np.clip(norm, 0, 255).astype(np.uint8)


def deskew(image, angle):
    if abs(angle) < 0.5:
        return image
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def perspective_correct(gray):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return gray
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < 0.05 * gray.shape[0] * gray.shape[1]:
        return gray
    peri = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.02 * peri, True)
    if len(approx) != 4:
        return gray
    pts = approx.reshape(4, 2).astype(np.float32)
    rect = _order_points(pts)
    w = int(max(np.linalg.norm(rect[0]-rect[1]), np.linalg.norm(rect[2]-rect[3])))
    h = int(max(np.linalg.norm(rect[0]-rect[3]), np.linalg.norm(rect[1]-rect[2])))
    if w < 50 or h < 50:
        return gray
    dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(gray, M, (w, h))


def _order_points(pts):
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def preprocess(image):
    gray = to_gray(image)
    gray = perspective_correct(gray)
    gray = normalize_lighting(gray)
    gray = denoise(gray)
    gray = enhance(gray)
    return gray
