# Benchmark Results

## Synthetic validation (decoder + grid correctness)

These results prove the full logic pipeline — dot detection → grid segmentation → decode — is correct on known-good input. They do **not** measure real-world camera recognition accuracy.

| Expected | Got | Char Accuracy | Status |
|---|---|---|---|
| `a` | `a` | 100% | PASS |
| `b` | `b` | 100% | PASS |
| `c` | `c` | 100% | PASS |
| `hello` | `hello` | 100% | PASS |
| `world` | `world` | 100% | PASS |
| `hi` | `hi` | 100% | PASS |
| `yes` | `yes` | 100% | PASS |
| `no` | `no` | 100% | PASS |
| `cat` | `cat` | 100% | PASS |
| `dog` | `dog` | 100% | PASS |
| `abc` | `abc` | 100% | PASS |
| `braille` | `braille` | 100% | PASS |
| `read` | `read` | 100% | PASS |
| `text` | `text` | 100% | PASS |
| `dots` | `dots` | 100% | PASS |

**Overall synthetic character accuracy: 100.0%** on 15 synthetic test images.

## Real-camera samples

To be populated after physical Braille testing. Results will reflect recognition accuracy on real raised-dot Braille photographed under real-world lighting conditions.
