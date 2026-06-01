import threading
import time
import cv2
import numpy as np
from flask import Flask, Response, render_template, stream_with_context, request, jsonify
from dotvoice.capture import Camera
from dotvoice.pipeline import read_braille
from dotvoice.guidance import GuidanceEngine

app = Flask(__name__)

_state = {
    'frame': None,
    'text': '',
    'guidance': 'Live scan is OFF',
    'dots': 0,
    'blur': 0.0,
    'fps': 0.0,
    'confidence': 0.0,
    'speak': False,
    'speak_text': '',
    'live_scan': False,
    'lock': threading.Lock(),
}

PROCESS_EVERY_N = 4
MIN_DOTS = 3


def _camera_loop():
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

            with _state['lock']:
                scanning = _state['live_scan']

            if scanning and frame_count % PROCESS_EVERY_N == 0:
                result = read_braille(frame)
                dots = result['dots']
                blur = result['quality'].get('blur', 0.0)
                text = result['text'] if len(dots) >= MIN_DOTS else ''
                confidence = result.get('confidence', 1.0)
                action, payload = guidance_engine.evaluate(result['quality'], dots, text, confidence)

                for x, y, r in dots:
                    cv2.circle(frame, (int(x), int(y)), int(r) + 3, (0, 0, 255), 2)

                if action == 'read':
                    guidance_msg = f"Captured: {payload}. Scan stopped. Press L to read again."
                    display_text = payload
                    speak_text = f"{payload}. Captured. Press L to read again."
                    speak_now = True
                    with _state['lock']:
                        _state['live_scan'] = False
                elif action == 'guide':
                    guidance_msg = payload
                    display_text = ''
                    speak_text = payload
                    speak_now = (payload != _state['guidance'])
                else:
                    guidance_msg = "Stabilizing..."
                    display_text = ''
                    speak_text = ''
                    speak_now = False

                with _state['lock']:
                    _state['text'] = display_text
                    _state['guidance'] = guidance_msg
                    _state['speak_text'] = speak_text
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


def _read_image_file(img):
    from dotvoice.preprocess import to_gray, preprocess
    from dotvoice.detect import detect_dots
    from dotvoice.grid import segment_grid
    from dotvoice.decode import decode_cells
    proc = preprocess(to_gray(img))
    dots = detect_dots(proc)
    text = decode_cells(segment_grid(dots)).strip()
    return text, len(dots)


@app.route('/video_feed')
def video_feed():
    return Response(_gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/toggle_scan', methods=['POST'])
def toggle_scan():
    with _state['lock']:
        _state['live_scan'] = not _state['live_scan']
        on = _state['live_scan']
        if not on:
            _state['text'] = ''
            _state['guidance'] = 'Live scan is OFF'
            _state['speak'] = False
            _state['speak_text'] = ''
    return jsonify({'live_scan': on})


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
                speak_text = _state.get('speak_text', '')
                if speak:
                    _state['speak'] = False
            if text != last_text or guidance != last_guidance:
                last_text = text
                last_guidance = guidance
                data = f"data: {text}||{guidance}||{dots}||{blur:.1f}||{fps:.1f}||{confidence:.2f}||{'1' if speak else '0'}||{speak_text}\n\n"
                yield data
            time.sleep(0.2)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    if file is None:
        return jsonify({'error': 'no file'}), 400
    data = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'bad image'}), 400
    text, n = _read_image_file(img)
    return jsonify({'text': text, 'dots': n, 'confidence': 1.0})


@app.route('/sample', methods=['POST'])
def sample():
    img = cv2.imread('data/real/joel.png')
    if img is None:
        return jsonify({'error': 'sample not found'}), 404
    text, n = _read_image_file(img)
    return jsonify({'text': text, 'dots': n, 'confidence': 1.0})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, threaded=True, port=5001)