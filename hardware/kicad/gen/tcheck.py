"""保存済み .kicad_sch で T 字 (配線の途中に別の端点) と、3 本以上集まる点のジャンクション有無を確かめる。"""
import sys, itertools
from sexp import parse, find, findall
for f in sys.argv[1:]:
    r = parse(open(f).read())[0]
    segs = []
    for w in findall(r, 'wire'):
        pts = findall(find(w, 'pts'), 'xy')
        a = (round(float(pts[0][1]), 3), round(float(pts[0][2]), 3)); b = (round(float(pts[1][1]), 3), round(float(pts[1][2]), 3))
        segs.append((a, b))
    juncs = {(round(float(find(j, 'at')[1]), 3), round(float(find(j, 'at')[2]), 3)) for j in findall(r, 'junction')}
    ends = {}
    for a, b in segs:
        ends[a] = ends.get(a, 0) + 1; ends[b] = ends.get(b, 0) + 1
    def interior(c, s):
        (x1, y1), (x2, y2) = s
        if x1 == x2 == c[0]: return min(y1, y2) < c[1] < max(y1, y2)
        if y1 == y2 == c[1]: return min(x1, x2) < c[0] < max(x1, x2)
        return False
    t = [(c, s) for c in ends for s in segs if interior(c, s)]
    nojunc = [p for p, n in ends.items() if n >= 3 and p not in juncs]
    cross = 0
    for s1, s2 in itertools.combinations(segs, 2):
        (a1, b1), (a2, b2) = s1, s2
        if a1[0] == b1[0] and a2[1] == b2[1]:
            v, h = s1, s2
        elif a1[1] == b1[1] and a2[0] == b2[0]:
            v, h = s2, s1
        else:
            continue
        x, y = v[0][0], h[0][1]
        if min(h[0][0], h[1][0]) < x < max(h[0][0], h[1][0]) and min(v[0][1], v[1][1]) < y < max(v[0][1], v[1][1]):
            cross += 1
    print(f.split('/')[-1], 'wires', len(segs), 'junctions', len(juncs), 'T-violations', len(t), '3+ends-without-junction', len(nojunc), 'crossings', cross)
