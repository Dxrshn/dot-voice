import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
from dotvoice.synth import render

TEST_WORDS = [
    'a', 'b', 'c', 'hello', 'world', 'hi', 'yes', 'no',
    'cat', 'dog', 'abc', 'braille', 'read', 'text', 'dots',
]

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets')
os.makedirs(OUT_DIR, exist_ok=True)

for word in TEST_WORDS:
    img = render(word)
    path = os.path.join(OUT_DIR, f'{word}.png')
    cv2.imwrite(path, img)
    print(f'saved {path}')

print(f'\nGenerated {len(TEST_WORDS)} synthetic test images.')