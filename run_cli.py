import time
import cv2
from dotvoice.capture import Camera
from dotvoice.pipeline import read_braille
from dotvoice.tts import Speaker
from dotvoice.guidance import GuidanceEngine

PROCESS_EVERY_N = 5
MIN_DOTS_FOR_READ = 3


def draw_dots_on_frame(frame, dots):
    out = frame.copy()
    for x, y, r in dots:
        cv2.circle(out, (int(x), int(y)), int(r) + 3, (0, 0, 255), 2)
        cv2.circle(out, (int(x), int(y)), 2, (0, 255, 0), -1)
    return out


def main():
    speaker = Speaker()
    guidance = GuidanceEngine()

    frame_count = 0
    last_text = ''
    last_dots = []
    last_blur = 0.0
    status_line = 'Starting...'

    fps_counter = 0
    fps_start = time.time()
    fps = 0.0

    speaker.speak("DotVoice ready. Move camera over Braille.")

    with Camera() as cam:
        print("DotVoice running — press Q to quit")
        while True:
            frame = cam.read()
            if frame is None:
                break

            frame_count += 1
            fps_counter += 1
            fh, fw = frame.shape[:2]

            elapsed = time.time() - fps_start
            if elapsed >= 1.0:
                fps = fps_counter / elapsed
                fps_counter = 0
                fps_start = time.time()

            if frame_count % PROCESS_EVERY_N == 0:
                result = read_braille(frame)
                last_dots = result['dots']
                last_blur = result['quality'].get('blur', 0)
                text = result['text'] if len(last_dots) >= MIN_DOTS_FOR_READ else ''
                last_text = text

                action, payload = guidance.evaluate(result['quality'], last_dots, text)

                if action == 'guide':
                    status_line = payload
                    speaker.speak(payload)
                elif action == 'read':
                    status_line = f"Reading: {payload}"
                    speaker.speak(f"Braille detected. {payload}")
                else:
                    status_line = f"Stabilizing... ({text})"

            display = draw_dots_on_frame(frame, last_dots)

            cv2.rectangle(display, (0, fh - 90), (fw, fh), (0, 0, 0), -1)
            cv2.putText(display, f"Text: {last_text if last_text else '---'}",
                        (10, fh - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(display, status_line,
                        (10, fh - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 255), 2)
            cv2.putText(display, f"FPS: {fps:.1f}  Blur: {last_blur:.1f}  Dots: {len(last_dots)}",
                        (fw - 280, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

            cv2.imshow('DotVoice', display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
