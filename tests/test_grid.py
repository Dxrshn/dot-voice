from dotvoice.synth import render, _string_to_cellsets
from dotvoice.preprocess import preprocess
from dotvoice.detect import detect_dots
from dotvoice.grid import segment_grid
from dotvoice.decode import decode_cells


def _pipeline(text):
    img = render(text)
    gray = preprocess(img)
    dots = detect_dots(gray)
    cells = segment_grid(dots)
    return decode_cells(cells)


def test_single_word():
    assert _pipeline('hi') == 'hi'


def test_hello():
    assert _pipeline('hello') == 'hello'


def test_abc():
    assert _pipeline('abc') == 'abc'