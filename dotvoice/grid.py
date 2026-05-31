import numpy as np
from scipy.spatial.distance import cdist


def _estimate_unit(dots):
    if len(dots) < 2:
        return 20.0
    pts = np.array([(x, y) for x, y, _ in dots])
    dists = cdist(pts, pts)
    np.fill_diagonal(dists, np.inf)
    nn_dists = dists.min(axis=1)
    nn_dists = nn_dists[nn_dists < np.percentile(nn_dists, 75)]
    return float(np.median(nn_dists)) if len(nn_dists) > 0 else 20.0


def _cluster_1d(values, gap_threshold):
    if not values:
        return []
    sorted_vals = sorted(values)
    clusters = [[sorted_vals[0]]]
    for v in sorted_vals[1:]:
        if v - clusters[-1][-1] < gap_threshold:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return [np.mean(c) for c in clusters]


def _assign_to_grid(dots, col_centers, row_centers, u):
    cells = {}
    for x, y, _ in dots:
        col = int(np.argmin([abs(x - c) for c in col_centers]))
        row = int(np.argmin([abs(y - r) for r in row_centers]))
        cells.setdefault((col, row), []).append((x, y))
    return cells


def _split_cols_into_cells(col_centers, u):
    if not col_centers:
        return []
    cell_groups = [[col_centers[0]]]
    for c in col_centers[1:]:
        gap = c - cell_groups[-1][-1]
        if gap > 1.6 * u:
            cell_groups.append([c])
        else:
            cell_groups[-1].append(c)
    return cell_groups


def _split_rows_into_lines(row_centers, u):
    if not row_centers:
        return []
    line_groups = [[row_centers[0]]]
    for r in row_centers[1:]:
        gap = r - line_groups[-1][-1]
        if gap > 2.5 * u:
            line_groups.append([r])
        else:
            line_groups[-1].append(r)
    return line_groups


def _dot_position_in_cell(dx, dy, u):
    col = 0 if dx < 0.5 * u else 1
    if dy < 0.8 * u:
        row = 0
    elif dy < 1.8 * u:
        row = 1
    else:
        row = 2
    return col * 3 + row + 1


def segment_grid(dots):
    if not dots:
        return []

    u = _estimate_unit(dots)

    col_centers = _cluster_1d([x for x, _, _ in dots], gap_threshold=0.8 * u)
    row_centers = _cluster_1d([y for _, y, _ in dots], gap_threshold=0.8 * u)

    cell_col_groups = _split_cols_into_cells(col_centers, u)
    line_row_groups = _split_rows_into_lines(row_centers, u)

    result = []

    for line_rows in line_row_groups:
        line_y_min = min(line_rows) - 1.5 * u
        line_y_max = max(line_rows) + 1.5 * u
        line_dots = [(x, y, r) for x, y, r in dots if line_y_min <= y <= line_y_max]

        for cell_cols in cell_col_groups:
            cell_x_min = min(cell_cols) - 0.8 * u
            cell_x_max = max(cell_cols) + 0.8 * u
            cell_dots = [(x, y, r) for x, y, r in line_dots if cell_x_min <= x <= cell_x_max]

            if not cell_dots:
                result.append(())
                continue

            origin_x = min(cell_cols)
            origin_y = min(line_rows)

            dot_positions = set()
            for x, y, _ in cell_dots:
                dx = x - origin_x
                dy = y - origin_y
                pos = _dot_position_in_cell(dx, dy, u)
                dot_positions.add(pos)

            result.append(tuple(sorted(dot_positions)))

    return result


def cell_confidence(dot_positions, u):
    if not dot_positions:
        return 0.0
    scores = []
    for x, y in dot_positions:
        snap_x = round(x / (u * 0.5)) * (u * 0.5)
        snap_y = round(y / u) * u
        dist = ((x - snap_x)**2 + (y - snap_y)**2) ** 0.5
        scores.append(max(0.0, 1.0 - dist / (0.5 * u)))
    return float(np.mean(scores))