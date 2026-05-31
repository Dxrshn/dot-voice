from dotvoice.mapping import BRAILLE_MAP, NUMBER_SIGN, CAPITAL_SIGN, NUMBER_MAP


def cell_to_dots(bitmask):
    return tuple(i + 1 for i in range(6) if bitmask & (1 << i))


def decode_cells(cell_dotsets):
    result = []
    number_mode = False
    capital_next = False

    for dots in cell_dotsets:
        key = tuple(sorted(dots))

        if key == NUMBER_SIGN:
            number_mode = True
            continue

        if key == CAPITAL_SIGN:
            capital_next = True
            continue

        if key == ():
            number_mode = False
            result.append(' ')
            continue

        if number_mode:
            char = NUMBER_MAP.get(key, '?')
        else:
            char = BRAILLE_MAP.get(key, '?')
            if capital_next:
                char = char.upper()
                capital_next = False

        result.append(char)

    return ''.join(result)