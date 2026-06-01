import numpy as np
from scipy.spatial.distance import cdist

def estimate_rotation(dots):
    if len(dots) < 4:
        return 0.0
    pts = np.array([(x, y) for x, y, _ in dots])
    dists = cdist(pts, pts); np.fill_diagonal(dists, np.inf)
    angles = []
    for i in range(len(pts)):
        j = np.argmin(dists[i])
        dx = pts[j][0]-pts[i][0]; dy = pts[j][1]-pts[i][1]
        a = np.degrees(np.arctan2(dy, dx)) % 90
        if a > 45: a -= 90
        angles.append(a)
    angles = np.array(angles); angles = angles[np.abs(angles) < 30]
    return float(np.median(angles)) if len(angles) else 0.0

def rotate_dots(dots, angle_deg):
    if abs(angle_deg) < 0.5: return dots
    th = np.radians(-angle_deg); c, s = np.cos(th), np.sin(th)
    xs = np.array([x for x,_,_ in dots]); ys = np.array([y for _,y,_ in dots])
    cx, cy = xs.mean(), ys.mean()
    xr = c*(xs-cx)-s*(ys-cy)+cx; yr = s*(xs-cx)+c*(ys-cy)+cy
    return [(float(xr[i]), float(yr[i]), dots[i][2]) for i in range(len(dots))]

def _estimate_unit(dots):
    if len(dots) < 2: return 20.0
    pts = np.array([(x, y) for x, y, _ in dots])
    dists = cdist(pts, pts); np.fill_diagonal(dists, np.inf)
    nn = dists.min(axis=1); nn = nn[nn < np.percentile(nn, 75)]
    return float(np.median(nn)) if len(nn) else 20.0

def _cluster_1d(values, gap_threshold):
    if not values: return []
    sv = sorted(values); clusters = [[sv[0]]]
    for v in sv[1:]:
        if v - clusters[-1][-1] < gap_threshold: clusters[-1].append(v)
        else: clusters.append([v])
    return [float(np.mean(c)) for c in clusters]

def _group_into_lines(dots, u):
    if not dots: return []
    ds = sorted(dots, key=lambda d: d[1])
    lines = [[ds[0]]]; band_max = ds[0][1]
    for d in ds[1:]:
        if d[1] - band_max > 1.2 * u and (d[1] - lines[-1][0][1]) > 2.0 * u:
            lines.append([d]); band_max = d[1]
        else:
            lines[-1].append(d); band_max = max(band_max, d[1])
    return lines

def _decode_line(line_dots, u):
    if not line_dots:
        return []
    xs = np.array([d[0] for d in line_dots]); ys = np.array([d[1] for d in line_dots])
    if len(line_dots) >= 3:
        slope = np.polyfit(xs, ys, 1)[0]
        ys = ys - slope * (xs - xs.mean())
    pts = [(xs[i], ys[i]) for i in range(len(line_dots))]
    y_min, y_max = ys.min(), ys.max()
    span = max(y_max - y_min, 1e-6)
    def row_of(y):
        f = (y - y_min) / span
        if span < 1.2 * u:
            return 0 if f < 0.5 else 1
        return 0 if f < 0.33 else (1 if f < 0.67 else 2)
    col_centers = sorted(_cluster_1d([p[0] for p in pts], gap_threshold=0.6 * u))
    if not col_centers:
        return []
    col_gaps = [col_centers[i+1]-col_centers[i] for i in range(len(col_centers)-1)]
    cell_split = 1.3 * u
    inter_cell = [g for g in col_gaps if g > cell_split]
    space_thr = (np.median(inter_cell) * 1.8) if inter_cell else (5.0 * u)
    groups = [[col_centers[0]]]
    for c in col_centers[1:]:
        if c - groups[-1][-1] > cell_split:
            groups.append([c])
        else:
            groups[-1].append(c)
    result = []
    prev_x = None
    for g in groups:
        if prev_x is not None and (min(g) - prev_x) > space_thr:
            result.append(())
        cell_xmin, cell_xmax = min(g) - 0.6*u, max(g) + 0.6*u
        cx0 = min(g)
        cell_dots = [(px, py) for px, py in pts if cell_xmin <= px <= cell_xmax]
        positions = set()
        for px, py in cell_dots:
            col = 0 if (px - cx0) < 0.5 * u else 1
            positions.add(col * 3 + row_of(py) + 1)
        result.append(tuple(sorted(positions)))
        prev_x = max(g)
    return result

def segment_grid(dots):
    if not dots: return []
    u = _estimate_unit(dots)
    ang = estimate_rotation(dots)
    dots = rotate_dots(dots, ang)
    lines = _group_into_lines(dots, u)
    result = []
    for li, line in enumerate(lines):
        result.extend(_decode_line(line, u))
        if li < len(lines) - 1:
            result.append(())
    return result

def cell_confidence(dot_positions, u):
    if not dot_positions: return 0.0
    scores = []
    for x, y in dot_positions:
        sx = round(x/(u*0.5))*(u*0.5); sy = round(y/u)*u
        d = ((x-sx)**2+(y-sy)**2)**0.5
        scores.append(max(0.0, 1.0 - d/(0.5*u)))
    return float(np.mean(scores))