from dotvoice.preprocess import preprocess, to_gray
from dotvoice.detect import detect_dots, draw_debug
from dotvoice.grid import segment_grid
from dotvoice.decode import decode_cells
from dotvoice.quality import blur_score, coverage, quality_report


def read_braille(image):
    gray = to_gray(image)
    processed = preprocess(gray)
    quality = quality_report(processed)
    quality['blur_raw'] = blur_score(gray)
    dots = detect_dots(processed)
    cells = segment_grid(dots)
    text = decode_cells(cells)
    overlay = draw_debug(processed, dots)
    return {
        'text': text,
        'cells': cells,
        'dots': dots,
        'quality': quality,
        'overlay': overlay,
        'processed': processed,
    }