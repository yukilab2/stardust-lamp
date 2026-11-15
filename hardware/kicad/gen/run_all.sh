#!/bin/bash
# 回路図を生成し直して検証する。KiCad 10 の kicad-cli と公式シンボルライブラリが必要。
#   macOS の例: export PATH=/Applications/KiCad/KiCad.app/Contents/MacOS:$PATH
#               export KICAD10_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols
set -e
cd "$(dirname "$0")"
TMP=$(mktemp -d)
python3 netlist.py
python3 build.py "$TMP" | grep -v TXT
python3 mkproj.py "$TMP"
kicad-cli sch upgrade --force "$TMP/hosikuzu.kicad_sch" >/dev/null 2>&1
kicad-cli sch erc --severity-all -o "$TMP/erc.rpt" "$TMP/hosikuzu.kicad_sch" >/dev/null 2>&1 || true
grep "ERC messages" "$TMP/erc.rpt"
python3 compare_netlist.py "$TMP/hosikuzu.kicad_sch" "$TMP/hosikuzu.net"
python3 tcheck.py "$TMP/hosikuzu.kicad_sch" "$TMP/power.kicad_sch" "$TMP/hv.kicad_sch"
kicad-cli sch export pdf -o "$TMP/schematic_kicad.pdf" "$TMP/hosikuzu.kicad_sch" >/dev/null 2>&1
cp "$TMP"/hosikuzu.kicad_pro "$TMP"/hosikuzu.kicad_sch "$TMP"/power.kicad_sch "$TMP"/hv.kicad_sch \
   "$TMP"/hosikuzu.kicad_sym "$TMP"/sym-lib-table "$TMP"/schematic_kicad.pdf ..
echo "updated: $(cd .. && pwd)"
