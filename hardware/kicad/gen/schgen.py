"""KiCad 10 回路図を Python から生成する小さなライブラリ。

座標は mm、回路図座標 (Y 下向き)。接続グリッドは 1.27 mm。
- ライブラリ座標 (Y 上向き) のピン (px, py) は、mirror -> 回転 (反時計回り) した (rx, ry) を使って
  回路図上では (X + rx, Y - ry)
- 配線は直交線のみ。finalize() で T 字を分割し、3 本以上が集まる点にジャンクションを打つ
"""
import math, uuid, copy, json, itertools
from sexp import dump, Sym as S, find, findall
from lib import get_symbol, pins as lib_pins
import netlist as NL

U = 1.27
NS = uuid.UUID('6f1c3a52-9d0e-4c1a-8f0e-5b7f2c1d9e01')
PROJECT = 'hosikuzu'


def uid(*k):
    return str(uuid.uuid5(NS, '/'.join(str(x) for x in k)))


def r4(v):
    v = round(v, 4)
    return 0.0 if v == 0 else v


def on_grid(v):
    return abs(v / U - round(v / U)) < 1e-6


def g(n):
    """グリッド数 -> mm"""
    return r4(n * U)


def xf(px, py, rot, mirror):
    if mirror == 'y':
        px = -px
    elif mirror == 'x':
        py = -py
    a = math.radians(rot)
    c, s = round(math.cos(a)), round(math.sin(a))
    return px * c - py * s, px * s + py * c


# ------------------------------------------------------------------ custom symbols
def _pin(num, name, x, y, ang, typ='passive', length=2.54, hide=False):
    p = [S('pin'), S(typ), S('line'), [S('at'), x, y, ang], [S('length'), length]]
    if hide:
        p.append([S('hide'), S('yes')])
    p += [[S('name'), name, [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]],
          [S('number'), num, [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]]]
    return p


def _prop(k, v, x, y, hide=False):
    p = [S('property'), k, v, [S('at'), x, y, 0]]
    if hide:
        p.append([S('hide'), S('yes')])
    p.append([S('effects'), [S('font'), [S('size'), 1.27, 1.27]]])
    return p


def tps63070():
    name = 'TPS63070RNM'
    body = [S('symbol'), name + '_0_1',
            [S('rectangle'), [S('start'), -15.24, 12.7], [S('end'), 15.24, -12.7],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]]
    pins = [S('symbol'), name + '_1_1',
            _pin('11', 'L1', -3.81, 15.24, 270),
            _pin('9', 'L2', 3.81, 15.24, 270),
            _pin('12', 'VIN', -17.78, 7.62, 0, 'power_in'),
            _pin('13', 'VIN', -17.78, 5.08, 0, 'power_in'),
            _pin('14', 'EN', -17.78, 0, 0, 'input'),
            _pin('1', 'PS/SYNC', -17.78, -2.54, 0, 'input'),
            _pin('15', 'VSEL', -17.78, -7.62, 0, 'input'),
            _pin('2', 'PG', 17.78, 7.62, 180, 'open_collector'),
            _pin('7', 'VOUT', 17.78, 5.08, 180, 'power_out'),
            _pin('8', 'VOUT', 17.78, 2.54, 180, 'power_out'),
            _pin('5', 'FB', 17.78, -2.54, 180, 'input'),
            _pin('6', 'FB2', 17.78, -7.62, 180, 'passive'),
            _pin('3', 'VAUX', -7.62, -15.24, 90),
            _pin('4', 'GND', 0, -15.24, 90, 'power_in'),
            _pin('10', 'PGND', 5.08, -15.24, 90, 'power_in')]
    return [S('symbol'), 'hosikuzu:' + name,
            [S('pin_names'), [S('offset'), 1.016]],
            [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
            _prop('Reference', 'U', -15.24, 13.97),
            _prop('Value', name, -15.24, -13.97),
            _prop('Footprint', '', 0, -15.24, True),
            _prop('Datasheet', 'https://www.ti.com/lit/ds/symlink/tps63070.pdf', 0, -17.78, True),
            _prop('Description', 'Buck-boost converter 2-16V in, 2A, VQFN-HR-15', 0, 0, True),
            body, pins, [S('embedded_fonts'), S('no')]]


CUSTOM = {'hosikuzu:TPS63070RNM': tps63070}


# ------------------------------------------------------------------ geometry of lib symbols
def sym_graphics_bbox(sym, unit, rot, mirror, X, Y):
    xs, ys = [], []

    def add(px, py):
        rx, ry = xf(px, py, rot, mirror)
        xs.append(X + rx)
        ys.append(Y - ry)

    for u in findall(sym, 'symbol'):
        un = int(u[1].rsplit('_', 2)[-2])
        if un not in (0, unit):
            continue
        for e in u[2:]:
            if not isinstance(e, list):
                continue
            if e[0] == 'rectangle':
                a, b = find(e, 'start'), find(e, 'end')
                add(float(a[1]), float(a[2])); add(float(b[1]), float(b[2]))
            elif e[0] == 'polyline' or e[0] == 'bezier':
                for xy in findall(find(e, 'pts'), 'xy'):
                    add(float(xy[1]), float(xy[2]))
            elif e[0] == 'circle':
                c, r = find(e, 'center'), float(find(e, 'radius')[1])
                add(float(c[1]) - r, float(c[2]) - r); add(float(c[1]) + r, float(c[2]) + r)
            elif e[0] == 'arc':
                for k in ('start', 'mid', 'end'):
                    a = find(e, k)
                    add(float(a[1]), float(a[2]))
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


# ------------------------------------------------------------------ parts
class Part:
    def __init__(self, sch, ref, lib_id, value, x, y, rot=0, mirror=None, unit=1, power=False, fp=''):
        assert on_grid(x) and on_grid(y), (ref, x, y)
        self.sch, self.ref, self.lib_id, self.value = sch, ref, lib_id, value
        self.x, self.y, self.rot, self.mirror, self.unit, self.power = r4(x), r4(y), rot, mirror, unit, power
        self.sym = sch.libsym(lib_id)
        self.fp = fp or self._lib_prop('Footprint')
        self.pins = {}
        for p in lib_pins(self.sym):
            if p['unit'] in (0, unit):
                self.pins.setdefault(p['number'], p)
        self.fields = {}   # name -> (x, y, just, hidden)
        self.extra = {}

    def _lib_prop(self, k):
        for p in findall(self.sym, 'property'):
            if p[1] == k:
                return p[2]
        return ''

    def pin(self, n):
        p = self.pins[str(n)]
        rx, ry = xf(p['x'], p['y'], self.rot, self.mirror)
        return (r4(self.x + rx), r4(self.y - ry))

    def out(self, n):
        """ピンの外向き方向 (回路図座標の単位ベクトル)"""
        p = self.pins[str(n)]
        a = math.radians(p['angle'] + 180)
        dx, dy = round(math.cos(a)), round(math.sin(a))
        rx, ry = xf(dx, dy, self.rot, self.mirror)
        return (rx, -ry)

    def bbox(self):
        return sym_graphics_bbox(self.sym, self.unit, self.rot, self.mirror, self.x, self.y)

    # field placement helpers. just: 'L' (left aligned), 'R', 'C'
    def place(self, which, dx, dy, just='L', hide=False):
        self.fields[which] = (r4(self.x + dx), r4(self.y + dy), just, hide)
        return self


# ------------------------------------------------------------------ schematic
_CNT = {'pwr': 0, 'flg': 0}


class SheetSym:
    def __init__(self, sch, name, file, x, y, w, h):
        self.sch, self.name, self.file = sch, name, file
        self.x, self.y, self.w, self.h = r4(x), r4(y), r4(w), r4(h)
        assert all(on_grid(v) for v in (x, y, w, h)), (name, x, y, w, h)
        self.pins = {}   # name -> (pt, side, shape)
        self.uuid = uid('sheet', name)
        self.page = None

    def pin(self, name, side, pos, shape='output'):
        """side: L/R/T/B, pos: 辺の始点 (上 or 左) からの距離 (mm)"""
        if side == 'L':
            pt = (self.x, self.y + pos)
        elif side == 'R':
            pt = (self.x + self.w, self.y + pos)
        elif side == 'T':
            pt = (self.x + pos, self.y)
        else:
            pt = (self.x + pos, self.y + self.h)
        pt = (r4(pt[0]), r4(pt[1]))
        assert on_grid(pt[0]) and on_grid(pt[1])
        self.pins[name] = (pt, side, shape)
        return pt

    def bbox(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


class Sch:
    def __init__(self, title, paper='A2', comments=(), name='root', file='hosikuzu.kicad_sch'):
        self.title, self.paper, self.comments = title, paper, comments
        self.name, self.file = name, file
        self.hlabels = []
        self.sheets = []
        self.root_uuid = None
        self.parts = {}
        self.order = []
        self.wires = []
        self.labels = []
        self.ncs = []
        self.texts = []
        self.libsyms = {}
        self.npwr = 0
        self.nflg = 0
        self.root = uid('root') if name == 'root' else uid('sheetfile', name)
        self.junctions = []

    def libsym(self, lib_id):
        if lib_id not in self.libsyms:
            self.libsyms[lib_id] = CUSTOM[lib_id]() if lib_id in CUSTOM else get_symbol(lib_id)
        return self.libsyms[lib_id]

    # -- placement
    def add(self, ref, x, y, rot=0, mirror=None, fp=''):
        d = NL.PARTS[ref]
        p = Part(self, ref, d['lib_id'], d['value'], x, y, rot, mirror, fp=fp or d.get('fp', ''))
        assert ref not in self.parts, ref
        self.parts[ref] = p
        self.order.append(ref)
        auto_fields(p)
        return p

    def pwr(self, name, pt, rot=0):
        if name == 'PWR_FLAG':
            _CNT['flg'] += 1
            ref, lib = '#FLG%02d' % _CNT['flg'], 'power:PWR_FLAG'
        else:
            _CNT['pwr'] += 1
            ref = '#PWR%03d' % _CNT['pwr']
            lib = 'power:GND' if name == 'GND' else 'power:VCC'
        p = Part(self, ref, lib, name, pt[0], pt[1], rot, power=True)
        self.parts[ref] = p
        self.order.append(ref)
        # value text
        if name == 'GND':
            off = {0: (0, 6.35), 180: (0, -6.35), 90: (-6.35, 0), 270: (6.35, 0)}[rot]
        elif name == 'PWR_FLAG':
            off = {0: (0, -5.08), 180: (0, 5.08), 90: (5.08, 0), 270: (-5.08, 0)}[rot]
        else:
            off = {0: (0, -3.81), 180: (0, 3.81), 90: (-4.45, 0), 270: (4.45, 0)}[rot]
        just = 'C'
        if rot == 90:
            just = 'R'
        if rot == 270:
            just = 'L'
        if name == 'GND':
            p.place('Value', off[0], off[1], 'C', hide=True)   # GND 記号は文字なし
        else:
            p.place('Value', off[0], off[1], just)
        p.place('Reference', 0, 0, 'C', hide=True)
        return p

    # -- wires
    def wire(self, *pts):
        pts = [(r4(a), r4(b)) for a, b in pts]
        for a, b in zip(pts, pts[1:]):
            assert a[0] == b[0] or a[1] == b[1], ('not orthogonal', a, b)
            assert on_grid(a[0]) and on_grid(a[1]) and on_grid(b[0]) and on_grid(b[1]), ('off grid', a, b)
            if a != b:
                self.wires.append((a, b))
        return pts[-1]

    def label(self, name, pt, rot=0):
        self.labels.append((name, (r4(pt[0]), r4(pt[1])), rot))

    def hlabel(self, name, pt, rot=0, shape='output'):
        """rot 0: 接続点が左、文字が右へ伸びる / rot 180: 接続点が右、文字が左へ"""
        self.hlabels.append((name, (r4(pt[0]), r4(pt[1])), rot, shape))

    def sheet(self, name, file, x, y, w, h):
        sh = SheetSym(self, name, file, x, y, w, h)
        self.sheets.append(sh)
        return sh

    def conn_points(self):
        pts = set(pt for pt, _, _ in self.pin_points())
        pts |= set(h[1] for h in self.hlabels)
        for sh in self.sheets:
            pts |= set(v[0] for v in sh.pins.values())
        return pts

    def nc(self, pt):
        self.ncs.append((r4(pt[0]), r4(pt[1])))

    def text(self, s, pt, size=2.54, bold=True):
        self.texts.append((s, pt, size, bold))

    # ---------------------------------------------------------------- analysis
    def pin_points(self):
        """[(point, ref, pin)] ; スタックピンは 1 つにまとめない (接続判定用)"""
        out = []
        for ref, p in self.parts.items():
            for n in p.pins:
                out.append((p.pin(n), ref, n))
        return out

    def finalize(self):
        pinpts = self.conn_points()
        # 1) 重なり (同一直線上で区間が重なる) チェック
        segs = [tuple(sorted(s)) for s in self.wires]
        errs = []
        for i, a in enumerate(segs):
            for b in segs[i + 1:]:
                if _overlap(a, b):
                    errs.append(('overlap', a, b))
        # 2) T 字分割
        ends = set()
        for a, b in segs:
            ends.add(a); ends.add(b)
        lblpts = set(l[1] for l in self.labels)
        cut = ends | pinpts | lblpts
        out = []
        for a, b in segs:
            pts = [a, b]
            for c in cut:
                if _interior(c, (a, b)):
                    pts.append(c)
            pts = sorted(set(pts))
            for u, v in zip(pts, pts[1:]):
                out.append((u, v))
        self.tsplit = len(out) - len(segs)
        self.segs = sorted(set(out))
        # 3) ジャンクション: 線の端点の数 + その点にピンを持つ部品の数 >= 3
        cnt = {}
        for a, b in self.segs:
            cnt[a] = cnt.get(a, 0) + 1
            cnt[b] = cnt.get(b, 0) + 1
        partat = {}
        for pt, ref, n in self.pin_points():
            partat.setdefault(pt, set()).add(ref)
        for h in self.hlabels:
            partat.setdefault(h[1], set()).add('HL:' + h[0])
        for sh in self.sheets:
            for nm, v in sh.pins.items():
                partat.setdefault(v[0], set()).add('SP:' + sh.name + nm)
        self.junctions = sorted(pt for pt, c in cnt.items() if c + len(partat.get(pt, ())) >= 3)
        # 4) 交差
        self.crossings = []
        for a, b in itertools.combinations(self.segs, 2):
            x = _cross(a, b)
            if x:
                self.crossings.append(x)
        # 5) 線の端点がどこにもつながっていない (ダングリング)
        dang = []
        for pt, c in cnt.items():
            if c == 1 and pt not in pinpts and pt not in lblpts:
                dang.append(pt)
        segpts = set()
        for a, bb in self.segs:
            segpts.add(a); segpts.add(bb)
        badlbl = [('label-off-wire', l[0], l[1]) for l in self.labels if l[1] not in segpts]
        self.errors = errs + [('dangling', d) for d in dang] + badlbl
        return self

    def connectivity(self, uf=None):
        """uf: 共有する union-find (dict)。キーはシート名で名前空間を分ける"""
        parent = uf if uf is not None else {}
        ns = self.name

        def f(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def u(a, b):
            parent[f(a)] = f(b)

        for a, b in self.segs:
            u((ns, 'P', a), (ns, 'P', b))
        for pt, ref, n in self.pin_points():
            u(('PIN', ref, n), (ns, 'P', pt))
            p = self.parts[ref]
            if p.power and p.value != 'PWR_FLAG':
                u(('PIN', ref, n), ('NET', p.value))
        for name, pt, rot in self.labels:
            u((ns, 'P', pt), (ns, 'LBL', name))
        for name, pt, rot, shape in self.hlabels:
            u((ns, 'P', pt), (ns, 'HL', name))
        for sh in self.sheets:
            for nm, v in sh.pins.items():
                u((ns, 'P', v[0]), (getattr(sh, 'ns', sh.name), 'HL', nm))
        return parent, f

    def check_netlist(self, subs=()):
        """subs: このシートから下の Sch (ルートで呼ぶ)"""
        want = NL.nets()
        parent = {}
        sheets = [self] + list(subs)
        f = None
        for s in sheets:
            parent, f = s.connectivity(parent)
        groups = {}
        allparts = {}
        for s in sheets:
            allparts.update(s.parts)
        for ref, p in allparts.items():
            if p.power:
                continue
            for n in p.pins:
                groups.setdefault(f(('PIN', ref, n)), []).append('%s.%s' % (ref, n))
        got = [sorted(v) for v in groups.values()]
        gotset = {frozenset(v) for v in got if len(v) > 1}
        wantset = {frozenset(v) for v in want.values()}
        nc_pins = {'%s.%s' % (r, pn) for r, d in NL.PARTS.items() for pn, n in d['pins'].items() if n == 'NC'}
        lonely = sorted(v[0] for v in got if len(v) == 1 and v[0] not in nc_pins)
        missing = [sorted(s) for s in wantset - gotset]
        extra = [sorted(s) for s in gotset - wantset]
        ncpts = {}
        for s in sheets:
            for n in s.ncs:
                ncpts[(s.name, n)] = 1
        nc_missing = []
        for s in sheets:
            for x in nc_pins:
                r, pn = x.split('.')
                if r in s.parts and (s.name, s.parts[r].pin(pn)) not in ncpts:
                    nc_missing.append(x)
        absent = sorted(set(NL.PARTS) - set(r for r in allparts if not allparts[r].power))
        # ラベル (ネット名) が付いているネットの名前と、意図した名前の一致
        names = {}
        for s in sheets:
            for name, pt, rot in s.labels:
                names.setdefault(f((s.name, 'P', pt)), set()).add(name)
            for name, pt, rot, shape in s.hlabels:
                names.setdefault(f((s.name, 'P', pt)), set()).add(name)
        badname = []
        inv = {}
        for k, v in want.items():
            inv[frozenset(v)] = k
        for root, ns in names.items():
            members = frozenset(groups.get(root, []))
            if len(ns) > 1 or (members in inv and inv[members] not in ns):
                badname.append((sorted(ns), inv.get(members)))
        return dict(missing=missing, extra=extra, lonely=lonely, nc_missing=nc_missing, absent=absent,
                    badname=badname)

    # ---------------------------------------------------------------- text overlap check (概算)
    def text_boxes(self):
        boxes = []
        for ref, p in self.parts.items():
            for k, (x, y, just, hide) in p.fields.items():
                if hide:
                    continue
                s = p.ref if k == 'Reference' else p.value
                boxes.append((ref + ':' + k, _tbox(s, x, y, just, 1.27)))
        for name, pt, rot in self.labels:
            w = len(name) * 1.27 + 0.6
            if rot == 0:
                boxes.append(('label:' + name, (pt[0] + 0.3, pt[1] - 1.6, pt[0] + w, pt[1] - 0.3)))
            elif rot == 180:
                boxes.append(('label:' + name, (pt[0] - w, pt[1] - 1.6, pt[0] - 0.3, pt[1] - 0.3)))
            else:
                boxes.append(('label:' + name, (pt[0] - 1.6, pt[1] - w, pt[0] - 0.3, pt[1] - 0.3)))
        for name, pt, rot, shape in self.hlabels:
            w = len(name) * 1.27 + 2.5
            if rot == 0:
                boxes.append(('hlabel:' + name, (pt[0] + 0.3, pt[1] - 0.8, pt[0] + w, pt[1] + 0.8)))
            elif rot == 180:
                boxes.append(('hlabel:' + name, (pt[0] - w, pt[1] - 0.8, pt[0] - 0.3, pt[1] + 0.8)))
            elif rot == 90:
                boxes.append(('hlabel:' + name, (pt[0] - 0.8, pt[1] - w, pt[0] + 0.8, pt[1] - 0.3)))
            else:
                boxes.append(('hlabel:' + name, (pt[0] - 0.8, pt[1] + 0.3, pt[0] + 0.8, pt[1] + w)))
        for s, pt, size, bold in self.texts:
            boxes.append(('text:' + s, (pt[0], pt[1] - size, pt[0] + len(s) * size * (1.0 if s.isascii() else 1.6), pt[1])))
        return boxes

    def check_text(self):
        issues = []
        boxes = self.text_boxes()
        for (n1, b1), (n2, b2) in itertools.combinations(boxes, 2):
            if _bb_overlap(b1, b2):
                issues.append(('text-text', n1, n2))
        for n, b in boxes:
            for s in self.segs:
                if _seg_hits_box(s, b):
                    issues.append(('text-wire', n, s))
                    break
            for ref, p in self.parts.items():
                if p.power:
                    continue
                bb = p.bbox()
                if bb and _bb_overlap(b, _shrink(bb, 0.2)):
                    issues.append(('text-body', n, ref))
            for sh in self.sheets:
                if _bb_overlap(b, _shrink(sh.bbox(), 0.2)):
                    issues.append(('text-body', n, 'sheet:' + sh.name))
        # 部品の本体同士 / 本体と線
        bodies = [(r, _shrink(p.bbox(), 0.1)) for r, p in self.parts.items() if not p.power and p.bbox()]
        bodies += [('sheet:' + sh.name, _shrink(sh.bbox(), 0.1)) for sh in self.sheets]
        for (r1, b1), (r2, b2) in itertools.combinations(bodies, 2):
            if _bb_overlap(b1, b2):
                issues.append(('body-body', r1, r2))
        for r, b in bodies:
            for s in self.segs:
                if _seg_hits_box(s, _shrink(b, 0.3)):
                    issues.append(('wire-body', r, s))
        return issues

    # ---------------------------------------------------------------- output
    def write(self, path, inst_path=None, page=None):
        """inst_path: このシートのインスタンスパス ('/' + root uuid [+ '/' + sheet uuid])"""
        root = self.root
        self.inst_path = inst_path or ('/' + root)
        out = [S('kicad_sch'), [S('version'), 20260306], [S('generator'), 'eeschema'],
               [S('generator_version'), '10.0'], [S('uuid'), root], [S('paper'), self.paper]]
        tb = [S('title_block'), [S('title'), self.title], [S('date'), '2026-11-15'], [S('rev'), '1.0']]
        for i, c in enumerate(self.comments):
            tb.append([S('comment'), i + 1, c])
        out.append(tb)
        ls = [S('lib_symbols')]
        for lid in sorted(self.libsyms):
            ls.append(self.libsyms[lid])
        out.append(ls)
        for j in self.junctions:
            out.append([S('junction'), [S('at'), j[0], j[1]], [S('diameter'), 0], [S('color'), 0, 0, 0, 0],
                        [S('uuid'), uid('j', j)]])
        for n in self.ncs:
            out.append([S('no_connect'), [S('at'), n[0], n[1]], [S('uuid'), uid('nc', n)]])
        for a, b in self.segs:
            out.append([S('wire'), [S('pts'), [S('xy'), a[0], a[1]], [S('xy'), b[0], b[1]]],
                        [S('stroke'), [S('width'), 0], [S('type'), S('default')]], [S('uuid'), uid('w', a, b)]])
        for name, pt, rot in self.labels:
            just = {0: [S('justify'), S('left'), S('bottom')], 180: [S('justify'), S('right'), S('bottom')],
                    90: [S('justify'), S('left'), S('bottom')], 270: [S('justify'), S('right'), S('bottom')]}[rot]
            out.append([S('label'), name, [S('at'), pt[0], pt[1], rot],
                        [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], just], [S('uuid'), uid('l', name, pt)]])
        for s, pt, size, bold in self.texts:
            font = [S('font'), [S('size'), size, size]]
            if bold:
                font += [[S('thickness'), round(size * 0.2, 3)], [S('bold'), S('yes')]]
            out.append([S('text'), s, [S('exclude_from_sim'), S('no')], [S('at'), pt[0], pt[1], 0],
                        [S('effects'), font, [S('justify'), S('left'), S('bottom')]], [S('uuid'), uid('t', s, pt)]])
        for name, pt, rot, shape in self.hlabels:
            just = [S('justify'), S('left')] if rot in (0, 270) else [S('justify'), S('right')]
            out.append([S('hierarchical_label'), name, [S('shape'), S(shape)], [S('at'), pt[0], pt[1], rot],
                        [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], just], [S('uuid'), uid('hl', self.name, name)]])
        for ref in self.order:
            out.append(self._symbol(self.parts[ref]))
        for sh in self.sheets:
            out.append(self._sheet(sh))
        if inst_path is None:
            out.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
        out.append([S('embedded_fonts'), S('no')])
        open(path, 'w').write(dump(out) + '\n')

    def _symbol(self, p):
        e = [S('symbol'), [S('lib_id'), p.lib_id], [S('at'), p.x, p.y, p.rot]]
        if p.mirror:
            e.append([S('mirror'), S(p.mirror)])
        e += [[S('unit'), p.unit], [S('exclude_from_sim'), S('no')], [S('in_bom'), S('no' if p.power else 'yes')],
              [S('on_board'), S('no' if p.power else 'yes')], [S('dnp'), S('no')], [S('uuid'), uid('s', p.ref)]]
        fa = p.rot % 180
        for k, val in (('Reference', p.ref), ('Value', p.value)):
            x, y, just, hide = p.fields.get(k, (p.x, p.y, 'C', True))
            e.append(_field(k, val, x, y, fa, just, hide, p))
        e.append(_field('Footprint', p.fp, p.x, p.y, fa, 'C', True, p))
        e.append(_field('Datasheet', '', p.x, p.y, fa, 'C', True, p))
        e.append(_field('Description', '', p.x, p.y, fa, 'C', True, p))
        for k, v in p.extra.items():
            e.append(_field(k, v, p.x, p.y, fa, 'C', True, p))
        for n in sorted(p.pins):
            e.append([S('pin'), n, [S('uuid'), uid('pin', p.ref, n)]])
        e.append([S('instances'), [S('project'), PROJECT,
                                   [S('path'), self.inst_path, [S('reference'), p.ref], [S('unit'), p.unit]]]])
        return e

    def _sheet(self, sh):
        e = [S('sheet'), [S('at'), sh.x, sh.y], [S('size'), sh.w, sh.h], [S('exclude_from_sim'), S('no')],
             [S('in_bom'), S('yes')], [S('on_board'), S('yes')], [S('dnp'), S('no')],
             [S('stroke'), [S('width'), 0.3], [S('type'), S('solid')]],
             [S('fill'), [S('color'), 255, 255, 225, 1]], [S('uuid'), sh.uuid],
             [S('property'), 'Sheetname', sh.name, [S('at'), sh.x, r4(sh.y - 1.0), 0],
              [S('effects'), [S('font'), [S('size'), 2.0, 2.0], [S('bold'), S('yes')]], [S('justify'), S('left'), S('bottom')]]],
             [S('property'), 'Sheetfile', sh.file, [S('at'), sh.x, r4(sh.y + sh.h + 0.6), 0],
              [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], [S('justify'), S('left'), S('top')]]]]
        for nm, (pt, side, shape) in sh.pins.items():
            ang = {'L': 180, 'R': 0, 'T': 90, 'B': 270}[side]
            just = {'L': 'left', 'R': 'right', 'T': 'right', 'B': 'left'}[side]
            e.append([S('pin'), nm, S(shape), [S('at'), pt[0], pt[1], ang], [S('uuid'), uid('sp', sh.name, nm)],
                      [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], [S('justify'), S(just)]]])
        e.append([S('instances'), [S('project'), PROJECT, [S('path'), '/' + self.root, [S('page'), sh.page]]]])
        return e


def _field(k, v, x, y, angle, just, hide, p):
    f = [S('property'), k, v, [S('at'), x, y, angle]]
    if hide:
        f.append([S('hide'), S('yes')])
    eff = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]
    # 見た目の揃えを KiCad の justify に変換 (実測: rot 90 / 180 で左右が入れ替わる)
    j = {'L': 'left', 'R': 'right', 'C': None}[just]
    flip = p.rot in (90, 180)
    if p.mirror == 'y':
        flip = not flip
    if j and flip:
        j = {'left': 'right', 'right': 'left'}[j]
    if j:
        eff.append([S('justify'), S(j)])
    f.append(eff)
    return f


def _tbox(s, x, y, just, size):
    w = len(s) * size * 1.0 + 0.2
    h = size
    if just == 'L':
        return (x, y - h / 2, x + w, y + h / 2)
    if just == 'R':
        return (x - w, y - h / 2, x, y + h / 2)
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def _shrink(b, d):
    return (b[0] + d, b[1] + d, b[2] - d, b[3] - d)


def _bb_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _seg_hits_box(s, b):
    (x1, y1), (x2, y2) = s
    if x1 == x2:
        return b[0] < x1 < b[2] and min(y1, y2) < b[3] and max(y1, y2) > b[1]
    return b[1] < y1 < b[3] and min(x1, x2) < b[2] and max(x1, x2) > b[0]


def _interior(c, s):
    (x1, y1), (x2, y2) = s
    if x1 == x2 == c[0]:
        return min(y1, y2) < c[1] < max(y1, y2)
    if y1 == y2 == c[1]:
        return min(x1, x2) < c[0] < max(x1, x2)
    return False


def _overlap(a, b):
    (ax1, ay1), (ax2, ay2) = a
    (bx1, by1), (bx2, by2) = b
    if ax1 == ax2 == bx1 == bx2:
        return max(min(ay1, ay2), min(by1, by2)) < min(max(ay1, ay2), max(by1, by2))
    if ay1 == ay2 == by1 == by2:
        return max(min(ax1, ax2), min(bx1, bx2)) < min(max(ax1, ax2), max(bx1, bx2))
    return False


def _cross(a, b):
    (ax1, ay1), (ax2, ay2) = a
    (bx1, by1), (bx2, by2) = b
    if ax1 == ax2 and by1 == by2:
        v, h = a, b
    elif ay1 == ay2 and bx1 == bx2:
        v, h = b, a
    else:
        return None
    x = v[0][0]
    y = h[0][1]
    if min(h[0][0], h[1][0]) < x < max(h[0][0], h[1][0]) and min(v[0][1], v[1][1]) < y < max(v[0][1], v[1][1]):
        return (x, y)
    return None


# ------------------------------------------------------------------ default field placement
def auto_fields(p):
    lid = p.lib_id
    two = lid in ('Device:R', 'Device:C', 'Device:L', 'Device:Polyfuse')
    diode = lid in ('Device:D_Schottky', 'Diode:US1M', 'Diode:SMAJ440A', 'Device:LED')
    if two:
        if p.rot in (0, 180):          # 縦置き: 右に Ref / Value
            p.place('Reference', 2.54, -1.27, 'L').place('Value', 2.54, 1.27, 'L')
        else:                           # 横置き: 上に Ref, 下に Value
            p.place('Reference', 0, -2.54, 'C').place('Value', 0, 2.54, 'C')
    elif diode:
        if p.rot in (0, 180):          # 横置き
            p.place('Reference', 0, -3.81 + (0 if lid != 'Device:LED' else -1.27), 'C').place('Value', 0, 3.81, 'C')
        else:
            p.place('Reference', 2.54, -1.27, 'L').place('Value', 2.54, 1.27, 'L')
    elif lid.startswith('Transistor'):
        p.place('Reference', 5.08, -1.27, 'L').place('Value', 5.08, 1.27, 'L')
    else:
        bb = p.bbox()
        if bb:
            p.place('Reference', bb[0] - p.x, bb[1] - p.y - 1.27, 'L')
            p.place('Value', bb[0] - p.x, bb[3] - p.y + 1.27, 'L')
