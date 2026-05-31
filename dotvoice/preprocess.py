import cv2
import numpy as np


def to_gray(image):
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(gray):
    return cv2.GaussianBlur(gray, (5, 5), 0)


def enhance(gray):
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


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


def preprocess(image):
    gray = to_gray(image)
    gray = normalize_lighting(gray)
    gray = denoise(gray)
    gray = enhance(gray)
    return gray