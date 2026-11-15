"""kicad-cli でネットリストを書き出し、netlist.py の意図した接続表と照合する。"""
import sys, subprocess, json
from sexp import parse, find, findall
import netlist as NL

sch = sys.argv[1]
out = sys.argv[2]
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', out, sch], check=True,
               capture_output=True)
root = parse(open(out).read())[0]
nets = find(root, 'nets')
got = {}
for n in findall(nets, 'net'):
    name = find(n, 'name')[1]
    nodes = ['%s.%s' % (find(x, 'ref')[1], find(x, 'pin')[1]) for x in findall(n, 'node')]
    nodes = [x for x in nodes if not x.startswith('#')]
    got[name] = sorted(nodes)
want = NL.nets()
nc = {'%s.%s' % (r, p) for r, d in NL.PARTS.items() for p, v in d['pins'].items() if v == 'NC'}
gs = {frozenset(v): k for k, v in got.items() if len(v) > 1}
ws = {frozenset(v): k for k, v in want.items()}
missing = [(ws[s], sorted(s)) for s in ws if s not in gs]
extra = [(gs[s], sorted(s)) for s in gs if s not in ws]
singles = sorted(v[0] for k, v in got.items() if len(v) == 1 and v[0] not in nc)
nc_connected = sorted(x for k, v in got.items() if len(v) > 1 for x in v if x in nc)
# 部品の一覧
comps = findall(find(root, 'components'), 'comp')
refs = sorted(find(c, 'ref')[1] for c in comps)
vals = {find(c, 'ref')[1]: find(c, 'value')[1] for c in comps}
absent = sorted(set(NL.PARTS) - set(refs))
extra_parts = sorted(set(refs) - set(NL.PARTS))
badval = sorted((r, vals[r], NL.PARTS[r]['value']) for r in refs if r in NL.PARTS and vals[r] != NL.PARTS[r]['value'])
# 名前の対応 (意図したネット名と KiCad のネット名)
names = []
for s, k in ws.items():
    if s in gs:
        names.append((k, gs[s]))
res = dict(parts=len(refs), nets_kicad=len([1 for v in got.values() if len(v) > 1]), nets_intended=len(want),
           missing=missing, extra=extra, single_pin_nets=singles, nc_pins_connected=nc_connected,
           absent_parts=absent, extra_parts=extra_parts, value_mismatch=badval)
print(json.dumps(res, ensure_ascii=False, indent=1))
unnamed = [(k, g) for k, g in names if not g.lstrip('/').split('/')[-1] == k]
print('net names differing from intended (auto names etc):', len(unnamed))
for k, gname in sorted(unnamed):
    print('  ', k, '->', gname)
