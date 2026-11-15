import re
TOK = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)')
class Sym(str):
    """bare atom"""
    pass
def parse(text):
    pos = 0; stack = [[]]
    for m in TOK.finditer(text):
        t = m.group(1)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        elif t.startswith('"'):
            stack[-1].append(bytes(t[1:-1], 'utf-8').decode('unicode_escape') if '\\' in t else t[1:-1])
        else:
            stack[-1].append(Sym(t))
    return stack[0]
def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
def dump(x, ind=0):
    if isinstance(x, list):
        if not x: return '()'
        simple = all(not isinstance(e, list) for e in x)
        if simple:
            return '(' + ' '.join(dump(e) for e in x) + ')'
        parts = []
        head = []
        for e in x:
            if not isinstance(e, list) and not parts:
                head.append(dump(e))
            else:
                parts.append(e)
        s = '(' + ' '.join(head)
        for e in parts:
            s += '\n' + '\t' * (ind + 1) + dump(e, ind + 1)
        return s + '\n' + '\t' * ind + ')'
    if isinstance(x, Sym): return str(x)
    if isinstance(x, bool): return 'yes' if x else 'no'
    if isinstance(x, (int,)): return str(x)
    if isinstance(x, float):
        s = ('%.4f' % x).rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    return q(x)
def find(lst, key):
    for e in lst:
        if isinstance(e, list) and e and e[0] == key: return e
    return None
def findall(lst, key):
    return [e for e in lst if isinstance(e, list) and e and e[0] == key]
