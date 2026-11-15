# KiCad 回路図（配線版）

[回路図 PDF（EasyEDA）](../schematic.pdf) は、部品どうしをネットラベルだけで
つないでいます。ここにあるのは、同じ回路を KiCad 10 で描き直し、
部品の間をワイヤーでつないだものです。

- 回路図: [schematic_kicad.pdf](schematic_kicad.pdf)（A3 × 3 枚）
- KiCad プロジェクト: [hosikuzu.kicad_pro](hosikuzu.kicad_pro)

## シートの分け方

| ページ | ファイル | 中身 |
| --- | --- | --- |
| 1 | `hosikuzu.kicad_sch` | マイコン、残光、LED の定電流、ボタン、外部出力 |
| 2 | `power.kicad_sch` | USB 入力、USB シリアル、電池入力と TPS63070 |
| 3 | `hv.kicad_sch` | 高圧電源、帰還の分圧、GM 管 2 本と検出、J13、J14 |

- 1 ページ目に 2 つの下位シートを箱で置き、マイコンのピンから箱まで
  ワイヤーで引いています
- ラベルを使うのは、シートをまたぐ信号（階層ラベル）と、ネット名を
  付けたい配線（1 本に 1 個）だけです
- 電源（V5、VIN）と GND は電源記号です

## 元回路図との違い

回路・定数・部品番号は元回路図と同じです。描き方の都合で次だけ変えています。

- USB-C（J1）は KiCad の `USB_C_Receptacle_USB2.0_16P` で描きました。
  元の A1B12 は A1 と B12、A4B9 は A4 と B9 のように 2 本のピンに分かれます。
  シールド（EH 13、14）は SH の 1 本です
- S8550（Q6、Q7）は SOT-23 の並び（1 = B、2 = E、3 = C）で描きました
- TPS63070（U3）は KiCad の公式ライブラリに無いので、専用シンボルを
  [hosikuzu.kicad_sym](hosikuzu.kicad_sym) に置きました
- ネットラベルを付けたのは主なネットだけです。
  残り 31 本は KiCad の自動名（`Net-(Q2-B)` など）です

## 注意

- TPS63070 の 8 番（VOUT）と 13 番（VIN）は、元回路図のシンボルに無いので
  未接続のままです。データシートでは 7 と 8 が VOUT、12 と 13 が VIN で、
  どちらもつなぐ前提です。基板を起こすときは確認してください
- フットプリントは、公式ライブラリで既定値があるシンボル（IC、トランジスタ、
  ダイオードなど）だけに入っています。抵抗・コンデンサと U3 は未設定です

## 検証

- ERC（`kicad-cli sch erc --severity-all`）: エラー 0、警告 0
- ネットリスト: 元回路図から起こした接続表
  [gen/intended_netlist.json](gen/intended_netlist.json)（100 部品、65 ネット）と
  完全に一致。未接続にするピンはすべて NC マーク付き
- T 字（配線の途中に別の端点やピン）: 0
- 線の交差: 3 か所（すべて意図したもの）
  - 2 ページ目: USB の D+ と D−。USB-C 側は D− が上、CH340N 側は UD+ が上で、
    並びが逆のため
  - 1 ページ目: KICK と UPDI。KICK は ATtiny1614 の左上（PB0）から、
    UPDI は右上（PA0）から出て、どちらもマイコンの上を通るため
  - 1 ページ目: PULSE_B の分岐と PULSE_A。PULSE_A と PULSE_B は
    マイコン、残光の回路、高圧シートの 3 か所をつなぐため

## 作り直し方

回路図は [gen/build.py](gen/build.py) から生成しています。
接続表は [gen/netlist.py](gen/netlist.py) です。

```sh
cd hardware/kicad/gen
./run_all.sh
```

`run_all.sh` は回路図を生成し、ERC、ネットリスト照合、T 字チェックを実行して、
このフォルダのファイルを上書きします。KiCad 10 の `kicad-cli` と
公式シンボルライブラリが必要です（macOS の設定例はスクリプトの先頭）。
