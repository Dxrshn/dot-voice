from collections import Counter
from dotvoice.preprocess import preprocess, to_gray
from dotvoice.detect import detect_dots, draw_debug
from dotvoice.grid import segment_grid
from dotvoice.decode import decode_cells
from dotvoice.quality import blur_score, coverage, quality_report

_vote_buffer = []
VOTE_WINDOW = 5


def read_braille(image):
    global _vote_buffer
    gray = to_gray(image)
    processed = preprocess(gray)
    quality = quality_report(processed)
    quality['blur_raw'] = blur_score(gray)
    dots = detect_dots(processed)
    cells = segment_grid(dots)
    text = decode_cells(cells)

    if text and text.strip():
        _vote_buffer.append(text)
        if len(_vote_buffer) > VOTE_WINDOW:
            _vote_buffer.pop(0)
        if _vote_buffer:
            text = Counter(_vote_buffer).most_common(1)[0][0]
    else:
        _vote_buffer.clear()

    overlay = draw_debug(processed, dots)
    return {
        'text': text,
        'cells': cells,
        'dots': dots,
        'quality': quality,
        'overlay': overlay,
        'processed': processed,
    }
