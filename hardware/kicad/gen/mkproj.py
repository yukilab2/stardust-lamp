import json, os, sys
from sexp import dump, Sym as S
from schgen import tps63070
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
pro = {"meta": {"filename": "hosikuzu.kicad_pro", "version": 3}, "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
       "sheets": [], "boards": [], "text_variables": {}}
json.dump(pro, open(os.path.join(out, 'hosikuzu.kicad_pro'), 'w'), indent=2)
sym = tps63070()
sym[1] = 'TPS63070RNM'
lib = [S('kicad_symbol_lib'), [S('version'), 20251024], [S('generator'), 'kicad_symbol_editor'], [S('generator_version'), '10.0'], sym]
open(os.path.join(out, 'hosikuzu.kicad_sym'), 'w').write(dump(lib) + '\n')
open(os.path.join(out, 'sym-lib-table'), 'w').write('(sym_lib_table\n\t(version 7)\n\t(lib (name "hosikuzu") (type "KiCad") (uri "${KIPRJMOD}/hosikuzu.kicad_sym") (options "") (descr "星屑灯 専用シンボル"))\n)\n')
