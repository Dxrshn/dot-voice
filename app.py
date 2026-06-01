import threading
import time
import cv2
from flask import Flask, Response, render_template, stream_with_context
from dotvoice.capture import Camera
from dotvoice.pipeline import read_braille
from dotvoice.guidance import GuidanceEngine

app = Flask(__name__)

_state = {
    'frame': None,
    'text': '',
    'guidance': 'Starting...',
    'dots': 0,
    'blur': 0.0,
    'fps': 0.0,
    'confidence': 0.0,
    'speak': False,
    'lock': threading.Lock(),
}

PROCESS_EVERY_N = 4
MIN_DOTS = 3


def _camera_loop():
    import time
    guidance_engine = GuidanceEngine()
    frame_count = 0
    fps_counter = 0
    fps_start = time.time()

    with Camera() as cam:
        while True:
            frame = cam.read()
            if frame is None:
                time.sleep(0.05)
                continue

            frame_count += 1
            fps_counter += 1
            elapsed = time.time() - fps_start
            if elapsed >= 1.0:
                with _state['lock']:
                    _state['fps'] = fps_counter / elapsed
                fps_counter = 0
                fps_start = time.time()

            if frame_count % PROCESS_EVERY_N == 0:
                result = read_braille(frame)
                dots = result['dots']
                blur = result['quality'].get('blur', 0.0)
                text = result['text'] if len(dots) >= MIN_DOTS else ''
                confidence = result.get('confidence', 1.0)
                action, payload = guidance_engine.evaluate(result['quality'], dots, text, confidence)

                overlay = result['overlay']
                overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_GRAY2BGR) if len(overlay.shape) == 2 else overlay
                h, w = overlay_bgr.shape[:2]
                fh, fw = frame.shape[:2]
                annotated = frame.copy()
                annotated[0:min(h,fh), 0:min(w,fw)] = overlay_bgr[0:min(h,fh), 0:min(w,fw)]

                for x, y, r in dots:
                    cv2.circle(frame, (int(x), int(y)), int(r)+3, (0,0,255), 2)

                if action == 'read':
                    guidance_msg = f"Reading: {payload}"
                    display_text = payload
                    speak_now = True
                elif action == 'guide':
                    guidance_msg = payload
                    display_text = ''
                    speak_now = False
                else:
                    guidance_msg = "Stabilizing..."
                    display_text = ''
                    speak_now = False

                with _state['lock']:
                    _state['text'] = display_text
                    _state['guidance'] = guidance_msg
                    _state['dots'] = len(dots)
                    _state['blur'] = blur
                    _state['confidence'] = confidence
                    _state['speak'] = speak_now

            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            with _state['lock']:
                _state['frame'] = jpeg.tobytes()

            time.sleep(0.01)


threading.Thread(target=_camera_loop, daemon=True).start()


def _gen_frames():
    while True:
        with _state['lock']:
            frame = _state['frame']
        if frame:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)


@app.route('/video_feed')
def video_feed():
    return Response(_gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/events')
def events():
    def generate():
        last_text = ''
        last_guidance = ''
        while True:
            with _state['lock']:
                text = _state['text']
                guidance = _state['guidance']
                dots = _state['dots']
                blur = _state['blur']
                fps = _state['fps']
                confidence = _state['confidence']
                speak = _state['speak']
                if speak:
                    _state['speak'] = False
            if text != last_text or guidance != last_guidance:
                last_text = text
                last_guidance = guidance
                data = f"data: {text}||{guidance}||{dots}||{blur:.1f}||{fps:.1f}||{confidence:.2f}||{'1' if speak else '0'}\n\n"
                yield data
            time.sleep(0.2)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, threaded=True, port=5001)