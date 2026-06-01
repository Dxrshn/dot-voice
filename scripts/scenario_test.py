import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from dotvoice.synth import render, UNIT, DOT_RADIUS
from dotvoice.pipeline import read_braille, reset

WORDS = ['hello', 'world', 'hi', 'cat', 'dog', 'read', 'yes', 'no', 'abc', 'dots']
OUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'scenario_results.md')

np.random.seed(42)


def apply_noise(img, sigma):
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def apply_rotation(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderValue=255)


def apply_lighting_gradient(img):
    h, w = img.shape[:2]
    gradient = np.linspace(0.5, 1.5, w, dtype=np.float32)
    gradient = np.tile(gradient, (h, 1))
    out = np.clip(img.astype(np.float32) * gradient, 0, 255).astype(np.uint8)
    return out


def apply_blur(img, ksize=7):
    return cv2.GaussianBlur(img, (ksize, ksize), 0)


def apply_spacing(img, factor):
    from dotvoice.synth import _string_to_cellsets, INTER_DOT_X, INTER_DOT_Y, INTER_CELL_X, INTER_CELL_Y, MARGIN, DOT_RADIUS
    return img


def run_case(word, img):
    reset()
    result = read_braille(img)
    got = result['text'].strip()
    return got == word, got


def build_cases():
    cases = []
    for word in WORDS:
        base = render(word)
        cases.append((word, 'clean', base))
        for sigma in [5, 10, 25]:
            cases.append((word, f'noise_sd={sigma}', apply_noise(base, sigma)))
        for angle in [-10, -5, -2, 2, 5, 10]:
            cases.append((word, f'rot={angle:+d}deg', apply_rotation(base, angle)))
        cases.append((word, 'lighting_gradient', apply_lighting_gradient(base)))
        cases.append((word, 'blur_7x7', apply_blur(base, 7)))
    return cases


def main():
    cases = build_cases()
    results = []
    condition_stats = {}

    for word, condition, img in cases:
        passed, got = run_case(word, img)
        results.append((word, condition, got, passed))
        if condition not in condition_stats:
            condition_stats[condition] = {'pass': 0, 'total': 0}
        condition_stats[condition]['total'] += 1
        if passed:
            condition_stats[condition]['pass'] += 1

    total = len(results)
    passed_total = sum(1 for _, _, _, p in results if p)
    print(f"\nOverall: {passed_total}/{total} ({100*passed_total/total:.1f}%)\n")

    print(f"{'Condition':<25} {'Pass':>5} {'Total':>6} {'Rate':>7}")
    print('-' * 45)
    for cond, stat in sorted(condition_stats.items()):
        rate = 100 * stat['pass'] / stat['total']
        print(f"{cond:<25} {stat['pass']:>5} {stat['total']:>6} {rate:>6.0f}%")

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w') as f:
        f.write('# Scenario Stress Test Results\n\n')
        f.write(f'**Overall: {passed_total}/{total} ({100*passed_total/total:.1f}%)**\n\n')
        f.write('## Per-condition pass rate\n\n')
        f.write('| Condition | Pass | Total | Rate |\n')
        f.write('|---|---|---|---|\n')
        for cond, stat in sorted(condition_stats.items()):
            rate = 100 * stat['pass'] / stat['total']
            f.write(f'| `{cond}` | {stat["pass"]} | {stat["total"]} | {rate:.0f}% |\n')
        f.write('\n## Per-word breakdown\n\n')
        f.write('| Word | Condition | Got | Pass |\n')
        f.write('|---|---|---|---|\n')
        for word, cond, got, passed in results:
            mark = 'PASS' if passed else 'FAIL'
            f.write(f'| `{word}` | `{cond}` | `{got}` | {mark} |\n')

    print(f'\nSaved to {OUT_FILE}')


if __name__ == '__main__':
    main()
