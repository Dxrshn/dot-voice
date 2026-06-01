from collections import Counter
from dotvoice.preprocess import preprocess, to_gray
from dotvoice.detect import detect_dots, draw_debug, draw_debug_confidence
from dotvoice.grid import segment_grid, cell_confidence, _estimate_unit
from dotvoice.decode import decode_cells
from dotvoice.quality import blur_score, quality_report

_vote_buffer = []
VOTE_WINDOW = 5


def _text_plausible(text):
    if not text or not text.strip():
        return False
    junk_chars = sum(1 for c in text if c in '?')
    return junk_chars / len(text) < 0.4


def reset():
    global _vote_buffer
    _vote_buffer = []


def read_braille(image):
    global _vote_buffer
    gray = to_gray(image)
    processed = preprocess(gray)
    quality = quality_report(processed)
    quality['blur_raw'] = blur_score(gray)
    dots = detect_dots(processed)

    cells = segment_grid(dots)
    text = decode_cells(cells)

    u = _estimate_unit(dots) if dots else 20.0
    dot_positions = [(x, y) for x, y, _ in dots]
    confidence = cell_confidence(dot_positions, u) if dot_positions else 0.0
    quality['confidence'] = confidence

    if text and text.strip() and confidence > 0.3 and _text_plausible(text):
        _vote_buffer.append(text)
        if len(_vote_buffer) > VOTE_WINDOW:
            _vote_buffer.pop(0)
        if _vote_buffer:
            text = Counter(_vote_buffer).most_common(1)[0][0]
    else:
        _vote_buffer.clear()
        if confidence <= 0.3:
            text = ''

    overlay = draw_debug_confidence(processed, dots, confidence)
    return {
        'text': text,
        'cells': cells,
        'dots': dots,
        'quality': quality,
        'overlay': overlay,
        'processed': processed,
        'confidence': confidence,
    }
