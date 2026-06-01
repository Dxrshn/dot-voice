import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from dotvoice.synth import render
from dotvoice.pipeline import read_braille, reset

np.random.seed(42)

REAL_WORDS = ['hello', 'hi', 'cat', 'dog', 'yes', 'no', 'read', 'abc', 'dots', 'world']


def make_junk_frame(shape=(220, 400)):
    img = np.random.randint(80, 200, shape, dtype=np.uint8)
    for _ in range(np.random.randint(5, 30)):
        x, y = np.random.randint(0, shape[1]), np.random.randint(0, shape[0])
        r = np.random.randint(2, 20)
        cv2.circle(img, (x, y), r, int(np.random.randint(0, 80)), -1)
    return img


def run(img):
    reset()
    result = read_braille(img)
    return result['text'].strip()


real_pass = 0
real_total = len(REAL_WORDS)
junk_silent = 0
junk_total = 10

print("=== REAL WORD RECALL ===")
for word in REAL_WORDS:
    img = render(word)
    got = run(img)
    passed = got == word
    real_pass += int(passed)
    print(f"  {'PASS' if passed else 'FAIL'}  expected={word!r:10s} got={got!r}")

print(f"\nRecall: {real_pass}/{real_total} ({100*real_pass/real_total:.0f}%)")

print("\n=== JUNK REJECTION ===")
for i in range(junk_total):
    img = make_junk_frame()
    got = run(img)
    silent = got == '' or got.strip() == ''
    junk_silent += int(silent)
    print(f"  {'SILENT' if silent else 'SPOKE ':6s}  got={got!r}")

print(f"\nRejection: {junk_silent}/{junk_total} ({100*junk_silent/junk_total:.0f}%)")

recall_pct = 100 * real_pass / real_total
rejection_pct = 100 * junk_silent / junk_total
gate_ok = recall_pct >= 90 and rejection_pct >= 90
print(f"\n{'GATE PASS' if gate_ok else 'GATE FAIL'}: recall={recall_pct:.0f}% rejection={rejection_pct:.0f}% (need both >=90%)")

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'scenario_results.md')
with open(OUT, 'a') as f:
    f.write(f'\n## Noise Gate: Recall + Rejection\n\n')
    f.write(f'| Metric | Result | Threshold |\n')
    f.write(f'|---|---|---|\n')
    f.write(f'| Real word recall | {recall_pct:.0f}% ({real_pass}/{real_total}) | ≥90% |\n')
    f.write(f'| Junk rejection | {rejection_pct:.0f}% ({junk_silent}/{junk_total}) | ≥90% |\n')
    f.write(f'| Gate | {"PASS" if gate_ok else "FAIL"} | Both must pass |\n')

print(f"\nAppended to docs/scenario_results.md")
