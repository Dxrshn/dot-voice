import threading
import pyttsx3


class Speaker:
    def __init__(self):
        self._lock = threading.Lock()
        self._thread = None
        self._last_spoken = None

    def speak(self, text):
        if text == self._last_spoken:
            return
        self._last_spoken = text
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._say, args=(text,), daemon=True)
        self._thread.start()

    def _say(self, text):
        with self._lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 160)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception:
                pass