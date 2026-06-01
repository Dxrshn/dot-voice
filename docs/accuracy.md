# DotVoice — Accuracy & Validation

DotVoice uses a classical, deterministic CV pipeline — no trained model or weights required —
so all results are fully reproducible.

## 1. Unit tests (logic correctness)
7/7 passing (`pytest`). Covers decoder, capital/number state machine, and synthetic grid round-trips.

## 2. Synthetic robustness harness (`scripts/scenario_test.py`)
120 scenarios = 10 words x 12 conditions. **Overall: 91/120 (75.8%).**

| Condition          | Pass/Total |
|--------------------|------------|
| clean              | 8/10       |
| blur 7x7           | 8/10       |
| lighting gradient  | 8/10       |
| noise sd=5/10/25   | 8/10 each  |
| rotation +/-2deg   | 8/10 each  |
| rotation +/-5deg   | 8/10 each  |
| rotation +/-10deg  | 3-4/10     |

Weakest point is large rotation (>=10deg); small tilts and lighting/noise are handled well.

## 3. Real handwritten Braille (judge test image, `data/real/joel.png`)
Input: handwritten Braille, 5 lines, photographed under side-lighting.
**Result: 5/5 lines located, 4/7 words exact** (jaihind, india, visually, great).
Two single-dot row slips remain (saiobraille, impailed) and one first-cell error (mr?ject vs project).
"sciobraille" may use a Grade-2 contraction, which this Grade-1 pipeline does not target.

Reproduce:
```bash
python -c "import cv2; from dotvoice.pipeline import read_braille,reset; reset(); print(read_braille(cv2.imread('data/real/joel.png'))['text'])"
```
