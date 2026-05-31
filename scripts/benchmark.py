import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
from dotvoice.pipeline import read_braille

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets')
OUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'accuracy.md')

TEST_WORDS = [
    'a', 'b', 'c', 'hello', 'world', 'hi', 'yes', 'no',
    'cat', 'dog', 'abc', 'braille', 'read', 'text', 'dots',
]


def char_accuracy(expected, got):
    if not expected:
        return 1.0
    matches = sum(a == b for a, b in zip(expected, got))
    return matches / max(len(expected), len(got))


rows = []
total_chars = 0
correct_chars = 0

for word in TEST_WORDS:
    path = os.path.join(DATASET_DIR, f'{word}.png')
    if not os.path.exists(path):
        print(f'missing: {path}')
        continue
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    result = read_braille(img)
    got = result['text'].strip()
    acc = char_accuracy(word, got)
    total_chars += max(len(word), len(got))
    correct_chars += sum(a == b for a, b in zip(word, got))
    status = 'PASS' if got == word else 'FAIL'
    rows.append((word, got, f'{acc:.0%}', status))
    print(f'[{status}] expected={word!r:12} got={got!r:12} acc={acc:.0%}')

overall = correct_chars / total_chars if total_chars else 0
print(f'\nOverall character accuracy: {overall:.1%} on {len(rows)} images')

with open(OUT_FILE, 'w') as f:
    f.write('# Benchmark Results\n\n')
    f.write('| Expected | Got | Char Accuracy | Status |\n')
    f.write('|---|---|---|---|\n')
    for expected, got, acc, status in rows:
        f.write(f'| `{expected}` | `{got}` | {acc} | {status} |\n')
    f.write(f'\n**Overall character accuracy: {overall:.1%}** on {len(rows)} synthetic test images.\n')

print(f'\nResults saved to docs/accuracy.md')