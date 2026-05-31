from dotvoice.decode import decode_cells
from dotvoice.mapping import NUMBER_SIGN, CAPITAL_SIGN


def test_hello():
    hello_cells = [
        (1, 2, 5), (1, 5), (1, 2, 3), (1, 2, 3), (1, 3, 5)
    ]
    assert decode_cells(hello_cells) == 'hello'


def test_abc_123():
    cells = [
        (1,), (1, 2), (1, 4),
        (),
        NUMBER_SIGN, (1,), (1, 2), (1, 4)
    ]
    assert decode_cells(cells) == 'abc 123'


def test_capital():
    cells = [CAPITAL_SIGN, (1,), (1, 2), (1, 4)]
    assert decode_cells(cells) == 'Abc'


def test_space():
    cells = [()]
    assert decode_cells(cells) == ' '