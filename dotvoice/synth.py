import numpy as np
import cv2
from dotvoice.mapping import BRAILLE_MAP, NUMBER_SIGN, CAPITAL_SIGN, NUMBER_MAP

UNIT = 20
DOT_RADIUS = 6
CELL_COLS = 2
CELL_ROWS = 3
INTER_DOT_X = UNIT
INTER_DOT_Y = UNIT
INTER_CELL_X = int(2.4 * UNIT)
INTER_CELL_Y = int(4.0 * UNIT)
MARGIN = 40

_REVERSE_MAP = {v: k for k, v in BRAILLE_MAP.items() if v not in (' ', ',', '.', '?', ';', ':', "'", '-')}
_REVERSE_MAP[' '] = ()
_PUNCT_MAP = {',': (2,), '.': (2,5,6), '?': (2,3,6), ';': (2,3), ':': (2,5), "'": (3,), '-': (3,6)}
_REVERSE_NUMBER = {v: k for k, v in NUMBER_MAP.items()}


def _string_to_cellsets(text):
    cells = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.upper() != ch.lower() and ch.isupper():
            cells.append(CAPITAL_SIGN)
            cells.append(_REVERSE_MAP.get(ch.lower(), ()))
        elif ch.isdigit():
            if not cells or cells[-1] != NUMBER_SIGN:
                cells.append(NUMBER_SIGN)
            cells.append(_REVERSE_NUMBER.get(ch, ()))
        elif ch == ' ':
            cells.append(())
        elif ch in _PUNCT_MAP:
            cells.append(_PUNCT_MAP[ch])
        else:
            cells.append(_REVERSE_MAP.get(ch, ()))
        i += 1
    return cells


def _dot_positions(col_idx, row_idx):
    positions = []
    for dot_num in range(1, 7):
        dc = (dot_num - 1) // 3
        dr = (dot_num - 1) % 3
        x = MARGIN + col_idx * (CELL_COLS * INTER_DOT_X + INTER_CELL_X) + dc * INTER_DOT_X
        y = MARGIN + row_idx * (CELL_ROWS * INTER_DOT_Y + INTER_CELL_Y) + dr * INTER_DOT_Y
        positions.append((dot_num, x, y))
    return positions


def render(text, bg=255, fg=0):
    cellsets = _string_to_cellsets(text)
    n_cells = len(cellsets)
    if n_cells == 0:
        n_cells = 1

    width = MARGIN * 2 + n_cells * (CELL_COLS * INTER_DOT_X + INTER_CELL_X)
    height = MARGIN * 2 + CELL_ROWS * INTER_DOT_Y + INTER_CELL_Y

    img = np.full((height, width), bg, dtype=np.uint8)

    for ci, dotset in enumerate(cellsets):
        for dot_num, x, y in _dot_positions(ci, 0):
            if dot_num in dotset:
                cv2.circle(img, (x, y), DOT_RADIUS, fg, -1)

    return img