import cv2
from dotvoice.capture import Camera
from dotvoice.pipeline import read_braille

PROCESS_EVERY_N = 5
MIN_DOTS_FOR_READ = 3


def draw_dots_on_frame(frame, dots):
    out = frame.copy()
    for x, y, r in dots:
        cv2.circle(out, (int(x), int(y)), int(r) + 3, (0, 0, 255), 2)
        cv2.circle(out, (int(x), int(y)), 2, (0, 255, 0), -1)
    return out


def main():
    frame_count = 0
    last_text = ''
    last_dots = []
    last_blur = 0.0

    with Camera() as cam:
        print("DotVoice running — press Q to quit")
        while True:
            frame = cam.read()
            if frame is None:
                break

            frame_count += 1
            fh, fw = frame.shape[:2]

            if frame_count % PROCESS_EVERY_N == 0:
                result = read_braille(frame)
                last_dots = result['dots']
                last_blur = result['quality'].get('blur', 0)
                if len(last_dots) >= MIN_DOTS_FOR_READ:
                    last_text = result['text']
                else:
                    last_text = ''

            display = draw_dots_on_frame(frame, last_dots)

            cv2.rectangle(display, (0, fh - 80), (fw, fh), (0, 0, 0), -1)
            cv2.putText(display, f"Text: {last_text if last_text else '(no braille detected)'}",
                        (10, fh - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(display, f"Blur: {last_blur:.1f}  Dots: {len(last_dots)}",
                        (10, fh - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            cv2.imshow('DotVoice', display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
