MIN_BLUR = 15.0
MIN_COVERAGE = 0.005
MAX_COVERAGE = 0.6
MIN_DOTS = 3
STABILITY_K = 4


class GuidanceEngine:
    def __init__(self):
        self._history = []

    def evaluate(self, quality, dots, text):
        blur = quality.get('blur', 0)
        cov = quality.get('coverage', 0)
        n_dots = len(dots)

        if cov < MIN_COVERAGE:
            self._history.clear()
            return 'guide', "No Braille detected. Move the camera over the page."

        if blur < MIN_BLUR:
            self._history.clear()
            return 'guide', "Hold steady."

        if n_dots < MIN_DOTS:
            self._history.clear()
            return 'guide', "Move closer."

        if cov > MAX_COVERAGE:
            self._history.clear()
            return 'guide', "Move back."

        if not text or text.strip() == '':
            self._history.clear()
            return 'guide', "Move closer."

        self._history.append(text)
        if len(self._history) > STABILITY_K:
            self._history.pop(0)

        if len(self._history) == STABILITY_K and len(set(self._history)) == 1:
            self._history.clear()
            return 'read', text

        if len(self._history) == STABILITY_K:
            self._history.clear()
            return 'guide', "Adjust camera for clearer Braille."

        return 'waiting', None