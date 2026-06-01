import numpy as np

MIN_BLUR = 15.0
MIN_COVERAGE = 0.02
MAX_COVERAGE = 0.6
MIN_DOTS = 4
MAX_DOTS = 400
STABILITY_K = 2
MIN_CONFIDENCE = 0.35
MAX_RADIUS_CV = 0.55


def _looks_like_braille(dots):
    n = len(dots)
    if n < MIN_DOTS or n > MAX_DOTS:
        return False
    radii = np.array([d[2] for d in dots], dtype=float)
    if radii.mean() <= 0:
        return False
    if np.std(radii) / (np.mean(radii) + 1e-6) > MAX_RADIUS_CV:
        return False
    return True


class GuidanceEngine:
    def __init__(self):
        self._history = []

    def evaluate(self, quality, dots, text, confidence=1.0):
        blur = quality.get('blur', 0)
        cov = quality.get('coverage', 0)
        n_dots = len(dots)

        if cov < MIN_COVERAGE or n_dots < MIN_DOTS:
            self._history.clear()
            return 'guide', "No Braille detected. Move the camera over the page."

        if cov > MAX_COVERAGE:
            self._history.clear()
            return 'guide', "Move back."

        if blur < MIN_BLUR:
            self._history.clear()
            return 'guide', "Hold steady."

        if not _looks_like_braille(dots):
            self._history.clear()
            return 'guide', "Point the camera at Braille text."

        if not text or text.strip() == '':
            self._history.clear()
            return 'guide', "Move closer."

        if confidence < MIN_CONFIDENCE:
            self._history.clear()
            return 'guide', "Adjust the camera angle."

        self._history.append(text)
        if len(self._history) > STABILITY_K:
            self._history.pop(0)

        if len(self._history) == STABILITY_K and len(set(self._history)) == 1:
            confirmed = text
            self._history.clear()
            return 'read', confirmed

        return 'waiting', None