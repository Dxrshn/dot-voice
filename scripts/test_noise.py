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


def test_noise(text, noise_sd):
    img = render(text).astype(np.float32)
    noise = np.random.normal(0, noise_sd, img.shape).astype(np.float32)
    noisy = np.clip(img + noise, 0, 255).astype(np.uint8)
    gray = preprocess(noisy)
    dots = detect_dots(gray)
    angle = estimate_rotation(dots)
    dots_aligned = rotate_dots(dots, angle)
    cells = segment_grid(dots_aligned)
    result = decode_cells(cells)
    status = 'PASS' if result == text else 'FAIL'
    print(f'noise_sd={noise_sd:3d}  dots={len(dots):3d}  got={repr(result):20s}  [{status}]')


np.random.seed(42)
for sd in [0, 5, 10, 15, 25]:
    test_noise('braille', sd)
