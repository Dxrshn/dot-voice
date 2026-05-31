import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from dotvoice.synth import render
from dotvoice.preprocess import preprocess
from dotvoice.detect import detect_dots
from dotvoice.grid import segment_grid, estimate_rotation, rotate_dots
from dotvoice.decode import decode_cells


def test_rotation(text, angle_deg):
    img = render(text)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle_deg, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), borderValue=255)
    gray = preprocess(rotated)
    dots = detect_dots(gray)
    angle = estimate_rotation(dots)
    dots_aligned = rotate_dots(dots, angle)
    cells = segment_grid(dots_aligned)
    result = decode_cells(cells)
    status = 'PASS' if result == text else 'FAIL'
    print(f'rot={angle_deg:3d}deg  dots={len(dots):2d}  got={result!r:15s}  [{status}]')


for deg in [0, 2, 4, 7, 10]:
    test_rotation('braille', deg)
