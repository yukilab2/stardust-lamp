import copy, os
from sexp import parse, find, findall, Sym
LIBDIR = (os.environ.get('KICAD10_SYMBOL_DIR') or os.environ.get('KICAD_SYMBOL_DIR')
          or '/usr/share/kicad/symbols')
_cache = {}
def _libfile(lib):
    if lib not in _cache:
        _cache[lib] = parse(open(os.path.join(LIBDIR, lib + '.kicad_sym')).read())[0]
    return _cache[lib]
def get_symbol(lib_id):
    lib, name = lib_id.split(':')
    L = _libfile(lib)
    sym = None
    for e in findall(L, 'symbol'):
        if e[1] == name: sym = copy.deepcopy(e); break
    if sym is None: raise KeyError(lib_id)
    ext = find(sym, 'extends')
    if ext:
        parent = get_symbol(lib + ':' + ext[1])
        pname = parent[1].split(':')[1]
        # child props override parent props
        cprops = {p[1]: p for p in findall(sym, 'property')}
        new = [Sym('symbol'), lib_id]
        for e in parent[2:]:
            if isinstance(e, list) and e[0] == 'property' and e[1] in cprops:
                new.append(cprops.pop(e[1]))
            elif isinstance(e, list) and e[0] == 'symbol':
                e = copy.deepcopy(e); e[1] = e[1].replace(pname + '_', name + '_', 1); new.append(e)
            else:
                new.append(e)
        for p in cprops.values(): new.insert(len(new), p)
        return new
    sym[1] = lib_id
    # rename unit names to plain name prefix
    return sym
def pins(sym):
    """return list of dict(number,name,x,y,angle,length,type,unit,hidden)"""
    out = []
    base = sym[1].split(':')[1]
    for u in findall(sym, 'symbol'):
        un = u[1].rsplit('_', 2)
        unit = int(un[-2])
        for p in findall(u, 'pin'):
            at = find(p, 'at'); ln = find(p, 'length')
            out.append(dict(number=find(p, 'number')[1], name=find(p, 'name')[1], x=float(at[1]), y=float(at[2]),
                            angle=float(at[3]) if len(at) > 3 else 0, length=float(ln[1]) if ln else 0,
                            type=str(p[1]), unit=unit, hidden=any(isinstance(e, Sym) and e == 'hide' for e in p) or (find(p,'hide') is not None and find(p,'hide')[1]=='yes')))
    return out
if __name__ == '__main__':
    import sys
    for lid in sys.argv[1:]:
        s = get_symbol(lid)
        print('==', lid)
        for p in pins(s): print('  ', p)
