"""星屑灯 (GM_hosikuzu) の回路図を、部品間をワイヤーでつないで描き直す (KiCad 10, A3 x 3 枚)。

- ルート: マイコン・残光 LED (hosikuzu.kicad_sch)
- 下位: 電源・USB (power.kicad_sch), 高圧・GM 管 (hv.kicad_sch)
シートをまたぐ信号だけ階層ラベル。ほかはすべてワイヤー。
"""
import sys, json, os
import schgen
from schgen import Sch, g, r4

COMMENTS = ('元回路図: monoradio102/stardust-lamp hardware/schematic.pdf (EasyEDA, 5 ページ)',
            'ラベル接続を部品間のワイヤーに描き直したもの。回路・定数は元回路図と同じ')
P = {}
CUR = [None]


def S():
    return CUR[0]


def add(ref, x, y, rot=0, mirror=None):
    P[ref] = S().add(ref, x, y, rot, mirror)
    return P[ref]


def pin(ref, n):
    return P[ref].pin(n)


def W(*pts):
    return S().wire(*pts)


def X(pt):
    return pt[0]


def Y(pt):
    return pt[1]


def gnd(pt, drop=0):
    if drop:
        W(pt, (pt[0], pt[1] + drop))
    S().pwr('GND', (pt[0], pt[1] + drop))


def pwr(pt, rise=0, name='V5'):
    if rise:
        W(pt, (pt[0], pt[1] - rise))
    S().pwr(name, (pt[0], pt[1] - rise))


def flag(pt, rot=0):
    S().pwr('PWR_FLAG', pt, rot)


def text(s, pt, size=2.54, bold=True):
    S().text(s, pt, size, bold)

PAPER = 'A4'


# =====================================================================================
# 電源・USB シート
# =====================================================================================
def sheet_power():
    s = Sch('星屑灯 GM_hosikuzu  電源・USB', PAPER, COMMENTS, name='power', file='power.kicad_sch')
    CUR[0] = s
    # ---------------- USB 入力 ----------------
    text('USB 入力', (g(12), g(16)))
    J1 = add('J1', g(20), g(44))
    J1.place('Value', -10.16, 26.67, 'L')
    xp = X(J1.pin('A4'))
    yb = Y(J1.pin('A4')) - g(4)
    add('F1', xp + g(12), yb, 90)
    add('D2', xp + g(27), yb, 180)
    W(J1.pin('A4'), (xp + g(2), Y(J1.pin('A4'))), (xp + g(2), yb), pin('F1', '1'))
    s.label('VBUS', (xp + g(2), yb))
    W(pin('F1', '2'), pin('D2', '2'))
    s.label('VUSB', (X(pin('F1', '2')) + g(2), yb))
    add('C1', xp + g(36), yb + g(3))
    add('C2', xp + g(44), yb + g(3))
    W(pin('D2', '1'), pin('C1', '1'), pin('C2', '1'), (xp + g(52), yb))
    pwr((xp + g(52), yb))
    gnd(pin('C1', '2')); gnd(pin('C2', '2'))
    add('R2', xp + g(10), Y(J1.pin('B5')) + g(3))
    add('R1', xp + g(18), Y(J1.pin('A5')) + g(3))
    W(J1.pin('A5'), pin('R1', '1'))
    W(J1.pin('B5'), pin('R2', '1'))
    gnd(pin('R1', '2')); gnd(pin('R2', '2'))
    gnd(J1.pin('SH'))
    gnd(J1.pin('A1'))
    s.nc(J1.pin('A8')); s.nc(J1.pin('B8'))

    # ---------------- USB シリアル ----------------
    text('USB シリアル', (g(12), g(70)))
    U1 = add('U1', g(62), g(86))
    U1.place('Value', 3.81, 13.97, 'L')
    xD_p, xD_m = xp + g(2), xp + g(4)
    W(J1.pin('A7'), (xD_m, Y(J1.pin('A7'))))
    W(J1.pin('B7'), (xD_m, Y(J1.pin('B7'))))
    W((xD_m, Y(J1.pin('A7'))), (xD_m, Y(U1.pin('2'))), U1.pin('2'))
    W(J1.pin('A6'), (xD_p, Y(J1.pin('A6'))))
    W(J1.pin('B6'), (xD_p, Y(J1.pin('B6'))))
    W((xD_p, Y(J1.pin('A6'))), (xD_p, Y(U1.pin('1'))), U1.pin('1'))
    s.label('USB_DP', (xD_m + g(3), Y(U1.pin('1'))))
    s.label('USB_DN', (xD_m + g(3), Y(U1.pin('2'))))
    v3 = U1.pin('8')
    add('C3', X(v3) - g(11), Y(v3) - g(12))
    W(v3, (X(v3) - g(2), Y(v3)), (X(v3) - g(2), Y(pin('C3', '1')) - g(2)),
      (X(pin('C3', '1')), Y(pin('C3', '1')) - g(2)), pin('C3', '1'))
    gnd(pin('C3', '2'))
    vcc = U1.pin('5')
    add('C4', X(vcc) + g(6), Y(vcc) - g(8) + g(3))
    W(vcc, (X(vcc), Y(vcc) - g(8)), (X(pin('C4', '1')), Y(vcc) - g(8)), pin('C4', '1'))
    pwr((X(vcc), Y(vcc) - g(8)))
    gnd(pin('C4', '2'))
    gnd(U1.pin('3'))
    s.nc(U1.pin('4'))
    tx = U1.pin('6')
    add('D1', X(tx) + g(7), Y(tx))
    W(tx, pin('D1', '1'))
    add('R4', X(pin('D1', '2')) + g(4), Y(tx) + g(3), 180)
    W(pin('D1', '2'), pin('R4', '2'))
    rx = U1.pin('7')
    yrx = Y(pin('R4', '1')) + g(2)
    W(pin('R4', '1'), (X(pin('R4', '1')), yrx))
    add('SW1', X(pin('R4', '1')) + g(14), yrx)
    P['SW1'].place('Reference', -2.54, -8.89, 'L').place('Value', -2.54, -6.35, 'L')
    W(rx, (X(rx) + g(3), Y(rx)), (X(rx) + g(3), yrx), (X(pin('R4', '1')), yrx), pin('SW1', '2'))
    text('PROG', (X(pin('SW1', '1')) + g(2), Y(pin('SW1', '1')) - g(1)), 1.27, False)
    text('RUN', (X(pin('SW1', '3')) + g(2), Y(pin('SW1', '3')) + g(3)), 1.27, False)
    text('SW1: PROG = 書き込み (UPDI) / RUN = ログ (TXD)', (X(pin('SW1', '2')) - g(4), Y(pin('SW1', '2')) + g(9)), 1.27, False)
    add('R3', X(pin('SW1', '1')) + g(10), Y(pin('SW1', '1')), 90)
    W(pin('SW1', '1'), pin('R3', '1'))
    xo = X(pin('R3', '2')) + g(6)
    W(pin('R3', '2'), (xo, Y(pin('R3', '2'))))
    s.hlabel('UPDI', (xo, Y(pin('R3', '2'))), 0, 'bidirectional')
    W(pin('SW1', '3'), (xo, Y(pin('SW1', '3'))))
    s.hlabel('TXD', (xo, Y(pin('SW1', '3'))), 0, 'bidirectional')

    # ---------------- 電池入力と昇降圧 ----------------
    text('電池入力 (2〜12V) と昇降圧 TPS63070', (g(92), g(16)))
    text('SW2 が切るのは電池側だけ。USB をつなぐと SW2 に関係なく USB から動く', (g(92), g(18.5)), 1.27, False)
    ybat = g(30)
    J15 = add('J15', g(94), ybat, 0, 'y')
    J15.place('Reference', -2.54, -3.81, 'R').place('Value', g(84) - g(94), g(10), 'L')
    text('BAT+ / BAT-', (g(84), ybat + g(8)), 1.27, False)
    Q5 = add('Q5', g(110), ybat + g(2), 90)
    Q5.place('Reference', 3.81, 8.89, 'L').place('Value', 3.81, 11.43, 'L')
    W(J15.pin('1'), Q5.pin('3'))
    s.label('BAT_IN', (X(J15.pin('1')) + g(1), ybat))
    p2 = J15.pin('2')
    W(p2, (X(p2) + g(2), Y(p2)))
    gnd((X(p2) + g(2), Y(p2)), g(3))
    gnd(Q5.pin('1'))
    text('逆接保護', (X(Q5.pin('3')) + g(1), ybat - g(5)), 1.27, False)
    U3 = add('U3', g(163), ybat + g(6))
    U3.place('Reference', -15.24, -19.05, 'L').place('Value', 2.54, 21.59, 'L')
    assert abs(Y(U3.pin('12')) - ybat) < 1e-6
    add('C30', g(118), ybat + g(3))
    add('C31', g(126), ybat + g(3))
    xr60 = g(135)
    add('R60', xr60, ybat + g(3))
    W(Q5.pin('2'), pin('C30', '1'), pin('C31', '1'), pin('R60', '1'), U3.pin('12'))
    gnd(pin('C30', '2')); gnd(pin('C31', '2'))
    pwr((g(131), ybat), name='VIN')
    s.nc(U3.pin('13'))
    en = U3.pin('14')
    ps = U3.pin('1')
    assert abs(Y(pin('R60', '2')) - Y(en)) < 1e-6
    xj = X(en) - g(4)
    W(pin('R60', '2'), en)
    W((xj, Y(en)), (xj, Y(ps)), ps)
    SW2 = add('SW2', xr60 - g(4), Y(en) + g(10), 0, 'y')
    SW2.place('Reference', -6.35, -3.81, 'R').place('Value', 0, 10.16, 'C')
    W(pin('R60', '2'), (xr60, Y(pin('SW2', '2'))), pin('SW2', '2'))
    s.nc(pin('SW2', '1'))
    p3 = pin('SW2', '3')
    W(p3, (X(p3) - g(2), Y(p3)))
    gnd((X(p3) - g(2), Y(p3)), g(2))
    text('ON', (X(pin('SW2', '1')) + g(1), Y(pin('SW2', '1')) - g(2)), 1.27, False)
    text('OFF', (X(p3) - g(6), Y(p3) - g(1)), 1.27, False)
    vs = U3.pin('15')
    W(vs, (X(vs) - g(2), Y(vs)))
    gnd((X(vs) - g(2), Y(vs)), g(2))
    l1, l2 = U3.pin('11'), U3.pin('9')
    add('L2', U3.x, Y(l1) - g(4), 90)
    P['L2'].place('Reference', -6.35, -1.27, 'R').place('Value', 6.35, -1.27, 'L')
    W(l1, pin('L2', '1'))
    W(l2, pin('L2', '2'))
    va = U3.pin('3')
    add('C32', X(va), Y(va) + g(5))
    P['C32'].place('Reference', -2.54, -1.27, 'R').place('Value', -2.54, 1.27, 'R')
    W(va, pin('C32', '1'))
    gnd(pin('C32', '2'))
    gnd(U3.pin('4'))
    gnd(U3.pin('10'))
    s.nc(U3.pin('2'))
    s.nc(U3.pin('8'))
    vo = U3.pin('7')
    fb = U3.pin('5')
    xr61 = X(vo) + g(6)
    add('R61', xr61, Y(vo) + g(3))
    assert abs(Y(pin('R61', '2')) - Y(fb)) < 1e-6
    add('R62', xr61, Y(fb) + g(3))
    W(fb, pin('R61', '2'))
    W(pin('R61', '2'), pin('R62', '1'))
    gnd(pin('R62', '2'))
    f2 = U3.pin('6')
    W(f2, (X(f2) + g(2), Y(f2)))
    gnd((X(f2) + g(2), Y(f2)), g(2))
    xc = [xr61 + g(9), xr61 + g(17), xr61 + g(25)]
    for ref, x in zip(('C33', 'C34', 'C35'), xc):
        add(ref, x, Y(vo) + g(3))
        gnd(pin(ref, '2'))
    D3 = add('D3', xc[-1] + g(10), Y(vo), 180)
    W(vo, pin('R61', '1'), pin('C33', '1'), pin('C34', '1'), pin('C35', '1'), D3.pin('2'))
    s.label('VBOOST', (X(vo) + g(1), Y(vo)))
    pwr(D3.pin('1'))
    text('出力 4.68V (FB 分圧 330k / 68k)', (X(fb) + g(5), Y(pin('R62', '2')) + g(6)), 1.27, False)
    text('8 番 (VOUT) と 13 番 (VIN) は元回路図どおり未接続', (X(U3.pin('15')), Y(U3.pin('4')) + g(13)), 1.27, False)
    text('データシートでは 7/8 が VOUT、12/13 が VIN', (X(U3.pin('15')), Y(U3.pin('4')) + g(15)), 1.27, False)

    # ---------------- 電源フラグ (ERC 用) ----------------
    text('電源フラグ (ERC 用)', (g(14), g(118)), 1.27, False)
    for i, name in enumerate(('V5', 'VIN', 'GND')):
        x = g(16 + 10 * i)
        y = g(124)
        flag((x, y))
        W((x, y), (x, y + g(3)))
        if name == 'GND':
            S().pwr('GND', (x, y + g(3)))
        else:
            W((x, y + g(3)), (x + g(4), y + g(3)))
            S().pwr(name, (x + g(4), y + g(3)))
    return s


# =====================================================================================
# 高圧・GM 管 シート
# =====================================================================================
def sheet_hv():
    s = Sch('星屑灯 GM_hosikuzu  高圧・GM 管', PAPER, COMMENTS, name='hv', file='hv.kicad_sch')
    CUR[0] = s
    yr = g(32)
    text('高圧電源 (約 200V を倍圧して約 400V)', (g(12), g(16)))
    text('マイコンが HV_FB を読みながら Q1 をスイッチングする。止めると約 10 秒で 10V 未満', (g(12), g(18.5)), 1.27, False)
    x0 = g(14)
    W((x0, yr), (x0 + g(3), yr))
    pwr((x0, yr))
    add('R10', x0 + g(6), yr, 90)
    W((x0 + g(3), yr), pin('R10', '1'))
    add('C10', x0 + g(14), yr + g(3))
    add('C11', x0 + g(21), yr + g(3))
    add('L1', x0 + g(31), yr, 90)
    W(pin('R10', '2'), pin('C10', '1'), pin('C11', '1'), pin('L1', '1'))
    s.label('V5_HV', (X(pin('R10', '2')) + g(1), yr))
    gnd(pin('C10', '2')); gnd(pin('C11', '2'))
    xs = X(pin('L1', '2')) + g(4)
    Q1 = add('Q1', xs - g(2), yr + g(13))
    Q1.place('Reference', 6.35, 1.27, 'L').place('Value', 6.35, 3.81, 'L')
    W(Q1.pin('2'), (xs, yr))
    W(Q1.pin('4'), (X(Q1.pin('4')), yr))
    gnd(Q1.pin('3'))
    gate = Q1.pin('1')
    add('R11', X(gate) - g(9), Y(gate), 90)
    W(pin('R11', '2'), gate)
    xg = X(gate) - g(3)
    add('R12', xg, Y(gate) + g(5))
    W((xg, Y(gate)), pin('R12', '1'))
    gnd(pin('R12', '2'))
    xhl = X(pin('R11', '1')) - g(4)
    W((xhl, Y(gate)), pin('R11', '1'))
    s.hlabel('HV_DRV', (xhl, Y(gate)), 180, 'input')
    xb = X(Q1.pin('4')) + g(9)
    add('C13', xb + g(9), yr, 90)
    W(pin('L1', '2'), (xs, yr), (X(Q1.pin('4')), yr), (xb, yr), pin('C13', '1'))
    s.label('SW', (xs + g(2), yr))
    yl = yr + g(16)
    add('D10', xb + g(9), yl, 180)
    W((xb, yr), (xb, yl), pin('D10', '2'))
    xh1 = X(pin('D10', '1')) + g(5)
    add('C12', xh1 + g(5), yl + g(3))
    W(pin('D10', '1'), (xh1, yl), (X(pin('C12', '1')), yl), pin('C12', '1'))
    gnd(pin('C12', '2'))
    s.label('HV1', (X(pin('D10', '1')) + g(1), yl))
    add('D11', xh1, (yr + yl) / 2, 270)
    P['D11'].place('Reference', 2.54, -1.27, 'L').place('Value', 2.54, 1.27, 'L')
    W(pin('D11', '2'), (xh1, yl))
    xpump = xh1
    W(pin('C13', '2'), (xpump, yr))
    W((xpump, yr), pin('D11', '1'))
    add('D12', xpump + g(10), yr, 180)
    W((xpump, yr), pin('D12', '2'))
    s.label('PUMP', (xpump + g(1), yr))
    xhv = X(pin('D12', '1')) + g(5)
    add('C14', xhv + g(4), yr + g(3))
    add('D13', xhv + g(13), yr + g(3), 270)
    W(pin('D12', '1'), (xhv, yr), pin('C14', '1'))
    W(pin('C14', '1'), (X(pin('D13', '1')), yr), pin('D13', '1'))
    gnd(pin('C14', '2')); gnd(pin('D13', '2'))
    text('D13: 約 500V で頭打ち', (X(pin('D13', '1')) - g(10), yr + g(13)), 1.27, False)

    # ---------------- 帰還の分圧 ----------------
    xd = X(pin('D13', '1')) + g(13)
    W((X(pin('D13', '1')), yr), (xd, yr))
    s.label('HV', (X(pin('D13', '1')) + g(2), yr))
    text('! HV ZONE  約 400V  動作中と停止後 10 秒は触らない', (xhv - g(8), yr - g(7)), 1.5, True)
    y = yr + g(2)
    W((xd, yr), (xd, y))
    for i in range(8):
        ref = 'R2%d' % i
        add(ref, xd, y + g(3))
        W((xd, y), pin(ref, '1'))
        y = Y(pin(ref, '2')) + g(2)
        W(pin(ref, '2'), (xd, y))
    yfb = y
    text('帰還の分圧 10MΩ × 8 + 220k', (xd - g(30), yr + g(36)), 1.27, False)
    text('(放電抵抗も兼ねる)', (xd - g(30), yr + g(38)), 1.27, False)
    add('R28', xd, yfb + g(5))
    W((xd, yfb), pin('R28', '1'))
    gnd(pin('R28', '2'))
    add('C15', xd + g(8), yfb + g(3))
    W((xd, yfb), pin('C15', '1'))
    gnd(pin('C15', '2'))
    W((xd, yfb), (xd - g(5), yfb))
    s.hlabel('HV_FB', (xd - g(5), yfb), 180, 'output')
    text('HV = HV_FB × 365', (xd - g(22), yfb + g(3)), 1.27, False)

    # ---------------- GM 管と検出 (A: 上 / B: 下) ----------------
    xa = xd + g(14)
    W((xd, yr), (xa, yr))
    text('GM 管と検出 (管 A を上、管 B を下に重ねる)', (xa - g(4), g(16)))
    text('反応中はパルスが LOW。マイコンに高圧は来ない', (xa - g(4), g(18.5)), 1.27, False)
    outs = {}
    for ch, y0, rr, j, q, c in (('A', yr, 30, 'J10', 'Q2', 'C16'), ('B', yr + g(44), 40, 'J11', 'Q3', 'C17')):
        if ch == 'B':
            W((xa, yr), (xa, y0))
        add('R%d' % rr, xa + g(6), y0, 90)
        W((xa, y0), pin('R%d' % rr, '1'))
        J = add(j, xa + g(23), y0)
        J.place('Reference', 2.54, -3.81, 'L').place('Value', g(3), g(4), 'L')
        W(pin('R%d' % rr, '2'), J.pin('1'))
        s.label('ANODE_' + ch, (X(pin('R%d' % rr, '2')) + g(1), y0))
        text('← 管 %s (J321)' % ch, (J.x + g(3), y0 + g(2)), 1.27, False)
        k = J.pin('2')
        xk = X(k) - g(3)
        yk = y0 + g(10)
        W(k, (xk, Y(k)), (xk, yk))
        add('R%d' % (rr + 1), xk, yk + g(3))
        W((xk, yk), pin('R%d' % (rr + 1), '1'))
        gnd(pin('R%d' % (rr + 1), '2'))
        add('R%d' % (rr + 2), xk + g(13), yk, 90)
        W((xk, yk), pin('R%d' % (rr + 2), '1'))
        s.label('CATH_' + ch, (xk + g(1), yk))
        Q = add(q, X(pin('R%d' % (rr + 2), '2')) + g(15), yk)
        xbase = X(pin('R%d' % (rr + 2), '2')) + g(4)
        add(c, xbase, yk + g(3))
        W(pin('R%d' % (rr + 2), '2'), (xbase, yk), Q.pin('1'))
        W((xbase, yk), pin(c, '1'))
        gnd(pin(c, '2'))
        gnd(Q.pin('2'))
        col = Q.pin('3')
        add('R%d' % (rr + 3), X(col), Y(col) - g(5))
        W(col, pin('R%d' % (rr + 3), '2'))
        pwr(pin('R%d' % (rr + 3), '1'))
        outs[ch] = col
    # J13: 1 GND, 2 V5, 3 UPDI, 4 TXD, 5 PULSE_A, 6 PULSE_B
    xj13 = g(216)
    J13 = add('J13', xj13, g(round(((Y(outs['A']) + Y(outs['B'])) / 2) / 1.27)))
    J13.place('Reference', 0, -10.16, 'C').place('Value', -1.27, 10.16 + 2.54, 'C')
    p1, p2 = J13.pin('1'), J13.pin('2')
    W(p1, (X(p1) - g(3), Y(p1)))
    S().pwr('GND', (X(p1) - g(3), Y(p1)), 270)
    W(p2, (X(p2) - g(3), Y(p2)))
    S().pwr('V5', (X(p2) - g(3), Y(p2)), 90)
    for n, name in (('3', 'UPDI'), ('4', 'TXD')):
        p = J13.pin(n)
        W(p, (X(p) - g(3), Y(p)))
        s.hlabel(name, (X(p) - g(3), Y(p)), 180, 'bidirectional')
    for ch, n in (('A', '5'), ('B', '6')):
        col = outs[ch]
        p = J13.pin(n)
        xc = X(p) - g(12) if ch == 'A' else X(p) - g(8)
        W(col, (xc, Y(col)), (xc, Y(p)), p)
        W((xc, Y(col)), (xc + g(5), Y(col)))
        s.hlabel('PULSE_' + ch, (xc + g(5), Y(col)), 0, 'output')
    # J14: 1 HV_FB, 2 BTN, 3 GLOW (分圧の下)
    J14 = add('J14', xd + g(28), yfb + g(14))
    J14.place('Reference', 2.54, -6.35, 'L').place('Value', 2.54, 6.35, 'L')
    xv = xd + g(16)
    W((X(pin('C15', '1')), yfb), (xv, yfb), (xv, Y(J14.pin('1'))), J14.pin('1'))
    for n, name in (('2', 'BTN'), ('3', 'GLOW')):
        p = J14.pin(n)
        W(p, (X(p) - g(3), Y(p)))
        s.hlabel(name, (X(p) - g(3), Y(p)), 180, 'bidirectional')
    text('J14: 高圧の測定 (HVF)、ボタン、残光', (J14.x - g(12), Y(J14.pin('3')) + g(6)), 1.27, False)
    return s


# =====================================================================================
# ルートシート: マイコン・残光 LED
# =====================================================================================
def sheet_root():
    s = Sch('星屑灯 GM_hosikuzu  マイコン・残光 LED', PAPER, COMMENTS, name='root', file='hosikuzu.kicad_sch')
    CUR[0] = s
    U2 = add('U2', g(72), g(101))
    U2.place('Reference', -12.7, -19.05, 'L').place('Value', -12.7, 22.86, 'L')
    pa = {n: U2.pin(n) for n in ('10', '11', '12', '13', '2', '3', '4', '5')}
    pb = {n: U2.pin(n) for n in ('9', '8', '7', '6')}
    xr = X(pa['10'])
    yu, yg = g(20), g(24)
    yk, ya, yb = g(69), g(81), g(85)
    x1, x2, x3 = xr + g(2), xr + g(4), xr + g(6)
    yt = g(126)
    hv = s.sheet('高圧・GM 管', 'hv.kicad_sch', g(204), g(16), g(18), yt + g(2) - g(16))
    hv.page, hv.ns = '3', 'hv'
    pw = s.sheet('電源・USB', 'power.kicad_sch', g(12), g(16), g(10), Y(pb['7']) + g(3) - g(16))
    pw.page, pw.ns = '2', 'power'
    text('残光: Q6・Q7 が同時に通った間だけ C40 に電荷が入る。FADE = 残光の長さ、BRIGHT = 明るさ', (g(92), g(18.5)), 1.27, True)

    # ---------------- マイコン右側 ----------------
    W(pa['10'], (x1, Y(pa['10'])), (x1, yu))
    W((X(pw.pin('UPDI', 'R', yu - pw.y, 'bidirectional')), yu), (x1, yu),
      (X(hv.pin('UPDI', 'L', yu - hv.y, 'bidirectional')), yu))
    s.label('UPDI', (x1 + g(2), yu))
    W(pa['11'], (x2, Y(pa['11'])), (x2, ya), hv.pin('PULSE_A', 'L', ya - hv.y, 'output'))
    W(pa['12'], (x3, Y(pa['12'])), (x3, yb), hv.pin('PULSE_B', 'L', yb - hv.y, 'output'))
    s.label('PULSE_A', (x3 + g(3), ya))
    s.label('PULSE_B', (x3 + g(3), yb))
    ybtn = Y(pa['13'])
    W(pa['13'], hv.pin('BTN', 'L', ybtn - hv.y, 'bidirectional'))
    s.label('BTN', (xr + g(2), ybtn))
    xf, xv = xr + g(2), xr + g(8)
    xhd = xv + g(29)
    y1, y2 = g(113), g(122)
    W(pa['2'], (xhd, Y(pa['2'])), (xhd, y1), hv.pin('HV_DRV', 'L', y1 - hv.y, 'input'))
    s.label('HV_DRV', (xhd + g(2), y1))
    s.nc(pa['3'])
    W(pa['5'], (xf, Y(pa['5'])), (xf, y2), hv.pin('HV_FB', 'L', y2 - hv.y, 'output'))
    s.label('HV_FB', (xhd + g(2), y2))
    yn = g(112)
    W(pa['4'], (xv, Y(pa['4'])), (xv, yn))
    add('R64', xv, yn + g(3))
    add('C36', xv + g(8), yn + g(3))
    add('R63', xv + g(20), yn - g(3))
    W((xv, yn), pin('R64', '1'))
    W((xv, yn), (X(pin('C36', '1')), yn), pin('C36', '1'))
    W((X(pin('C36', '1')), yn), (X(pin('R63', '2')), yn), pin('R63', '2'))
    pwr(pin('R63', '1'), name='VIN')
    gnd(pin('R64', '2')); gnd(pin('C36', '2'))
    s.label('VBAT_ADC', (xv + g(9), yn))
    text('電池電圧 (1M / 330k)', (xv + g(11), yn + g(8)), 1.27, False)
    SW3 = add('SW3', xhd + g(14), ybtn + g(6))
    SW3.place('Reference', -6.35, -1.27, 'R').place('Value', 6.35, -1.27, 'L')
    for n, dx in (('1', -g(2)), ('2', g(2))):
        p = SW3.pin(n)
        W(p, (X(p) + dx, Y(p)), (X(p) + dx, ybtn))
    for n, dx in (('3', -g(2)), ('4', g(2))):
        p = SW3.pin(n)
        W(p, (X(p) + dx, Y(p)))
        gnd((X(p) + dx, Y(p)), g(2))
    text('MODE ボタン', (SW3.x - g(4), ybtn - g(1)), 1.27, False)

    # ---------------- マイコン左側 ----------------
    xl = X(pb['9'])
    xk, xo, xtj = xl - g(2), xl - g(4), xl - g(8)
    W(pb['7'], (xtj, Y(pb['7'])), pw.pin('TXD', 'R', Y(pb['7']) - pw.y, 'bidirectional'))
    W((xtj, Y(pb['7'])), (xtj, yt), hv.pin('TXD', 'L', yt - hv.y, 'bidirectional'))
    s.label('TXD', (xtj + g(10), yt))
    s.nc(pb['6'])
    vcc = U2.pin('1')
    yc = Y(vcc) - g(10)
    W(vcc, (X(vcc), yc))
    pwr((X(vcc), yc - g(2)))
    W((X(vcc), yc), (X(vcc), yc - g(2)))
    add('C20', X(vcc) + g(5), yc + g(3))
    add('C21', X(vcc) - g(5), yc + g(3))
    P['C21'].place('Reference', -2.54, -1.27, 'R').place('Value', -2.54, 1.27, 'R')
    W(pin('C21', '1'), (X(vcc), yc), pin('C20', '1'))
    W(pin('C20', '1'), (X(pin('C20', '1')), yc))
    gnd(pin('C20', '2')); gnd(pin('C21', '2'))
    gnd(U2.pin('14'))

    # ---------------- OUT (Q9) ----------------
    pb1 = pb['8']
    Q9 = add('Q9', xo - g(8) - 5.08, g(80), 0, 'y')     # G 右, D 上, S 下
    Q9.place('Reference', -5.08, -1.27, 'R').place('Value', -5.08, 1.27, 'R')
    gq = Q9.pin('1')
    W(pb1, (xo, Y(pb1)), (xo, Y(gq)), gq)
    s.label('OUT_DRV', (X(gq) + g(1), Y(gq)))
    add('R80', xo - g(3), Y(gq) + g(3))
    P['R80'].place('Reference', -2.54, -1.27, 'R').place('Value', -2.54, 1.27, 'R')
    W((X(pin('R80', '1')), Y(gq)), pin('R80', '1'))
    gnd(pin('R80', '2'))
    gnd(Q9.pin('2'))
    d = Q9.pin('3')
    add('R81', X(d), Y(d) - g(5), 180)
    P['R81'].place('Reference', 2.54, -1.27, 'L').place('Value', 2.54, 1.27, 'L')
    W(d, pin('R81', '1'))
    J16 = add('J16', X(d) - g(10), Y(pin('R81', '2')) - g(2), 0, 'y')    # ピンが右向き
    J16.place('Reference', 0, -5.08, 'C').place('Value', 0, 10.16, 'C')
    W(pin('R81', '2'), (X(pin('R81', '2')), Y(J16.pin('2'))), J16.pin('2'))
    j1, j3 = J16.pin('1'), J16.pin('3')
    W(j1, (X(j1) + g(2), Y(j1)))
    pwr((X(j1) + g(2), Y(j1)), g(2))
    W(j3, (X(j3) + g(2), Y(j3)))
    gnd((X(j3) + g(2), Y(j3)), g(2))
    text('外部出力 OUT (オープンドレイン)', (J16.x - g(2), Y(j1) - g(7)), 1.27, True)
    text('KICK (マイコンから点灯)', (xk + g(2), yk - g(1)), 1.27, False)

    # ---------------- 残光 (Q6/Q7 の同時計数と C40) ----------------
    xgl = g(92)
    ybus = g(60)
    xqe = g(120)
    Q6 = add('Q6', xqe + 2.54, g(34), 180)
    Q7 = add('Q7', xqe + 2.54, g(46), 180)
    for q in (Q6, Q7):
        q.place('Reference', -5.08, -1.27, 'R').place('Value', -5.08, 1.27, 'R')
    pwr(Q6.pin('2'), g(1))
    W(Q6.pin('3'), Q7.pin('2'))
    add('R72', xqe, Y(Q7.pin('3')) + g(5))
    P['R72'].place('Reference', -2.54, -1.27, 'R').place('Value', -2.54, 1.27, 'R')
    W(Q7.pin('3'), pin('R72', '1'))
    W(pin('R72', '2'), (xqe, ybus), (xgl, ybus), (xgl, yg), hv.pin('GLOW', 'L', yg - hv.y, 'bidirectional'))
    s.label('GLOW', (xgl + g(2), ybus))
    bA, bB = Q6.pin('1'), Q7.pin('1')
    add('R70', X(bA) + g(4), Y(bA), 270)
    add('R71', X(bB) + g(4), Y(bB), 270)
    W(bA, pin('R70', '2'))
    W(bB, pin('R71', '2'))
    xdb, xda = X(pin('R71', '1')) + g(2), X(pin('R70', '1')) + g(5)
    W(pin('R71', '1'), (xdb, Y(bB)), (xdb, yb))
    W(pin('R70', '1'), (xda, Y(bA)), (xda, ya))
    add('R75', xgl + g(5), ybus + 3.81, 180)
    add('C40', xgl + g(12), ybus + 3.81)
    gnd(pin('C40', '2'))
    pk = pin('R75', '1')
    W(pk, (X(pk), yk), (xk, yk), (xk, Y(pb['9'])), pb['9'])
    s.label('KICK', (X(pk) - g(8), yk))
    add('R78', xgl + g(20), ybus + 3.81)
    V2 = add('VR2', X(pin('R78', '2')), Y(pin('R78', '2')) + g(5))
    V2.place('Reference', -2.54, -1.27, 'R').place('Value', -2.54, 1.27, 'R')
    W(pin('R78', '2'), V2.pin('1'))
    gnd(V2.pin('3'))
    w2 = V2.pin('2')
    W(w2, (X(w2) + g(2), Y(w2)))
    gnd((X(w2) + g(2), Y(w2)), g(3))
    xr73 = xda + g(9)
    add('R73', xr73, yg + g(5))
    W((xr73, yg), pin('R73', '1'))
    V1 = add('VR1', xr73, Y(pin('R73', '2')) + g(5), 0, 'y')
    V1.place('Reference', 2.54, -1.27, 'L').place('Value', 2.54, 1.27, 'L')
    W(pin('R73', '2'), V1.pin('1'))
    gnd(V1.pin('3'))

    # ---------------- LED の定電流 (U4, Q8) ----------------
    tap = V1.pin('2')
    xt = X(tap) - g(2)
    U4 = add('U4', xr73 + g(14), g(54))
    U4.place('Reference', 2.54, 8.89, 'L').place('Value', 2.54, 11.43, 'L')
    pin_p, pin_n, pout = U4.pin('1'), U4.pin('3'), U4.pin('4')
    W(tap, (xt, Y(tap)), (xt, Y(pin_p)), pin_p)
    s.label('GLOW_TAP', (xt + g(1), Y(pin_p)))
    add('C42', xt + g(3), Y(pin_p) + g(3))
    P['C42'].place('Reference', 2.54, -1.27 + 1.27, 'L').place('Value', 2.54, 1.27 + 1.27, 'L')
    gnd(pin('C42', '2'))
    vp, vn = U4.pin('5'), U4.pin('2')
    W(vp, (X(vp), Y(vp) - g(3)))
    pwr((X(vp), Y(vp) - g(3)), g(1))
    add('C41', X(vp) + g(5), Y(vp) - g(3) + g(3))
    W((X(vp), Y(vp) - g(3)), (X(pin('C41', '1')), Y(vp) - g(3)), pin('C41', '1'))
    gnd(pin('C41', '2'))
    gnd(vn)
    add('R76', X(pout) + g(5), Y(pout), 90)
    W(pout, pin('R76', '1'))
    Q8 = add('Q8', X(pin('R76', '2')) + g(7), Y(pout))
    Q8.place('Reference', -5.08, 6.35, 'R').place('Value', -5.08, 8.89, 'R')
    W(pin('R76', '2'), Q8.pin('1'))
    e8, c8 = Q8.pin('2'), Q8.pin('3')
    yfb = Y(vn) + g(7)
    add('R77', X(e8), yfb + g(5))
    W(e8, (X(e8), yfb), pin('R77', '1'))
    gnd(pin('R77', '2'))
    W((X(e8), yfb), (X(pin_n) - g(2), yfb), (X(pin_n) - g(2), Y(pin_n)), pin_n)
    s.label('LED_SENSE', (X(e8) - g(10), yfb))
    yledk = Y(c8) - g(2)
    LED = add('LED1', X(c8), yledk - g(2) - 3.81, 90)
    LED.place('Reference', -3.81, -1.27, 'R').place('Value', -3.81, 1.27, 'R')
    W(c8, LED.pin('1'))
    add('JP1', X(c8), Y(LED.pin('2')) - g(5))
    P['JP1'].place('Reference', -2.54, -1.27, 'R').place('Value', -2.54, 1.27, 'R')
    W(LED.pin('2'), pin('JP1', '2'))
    pwr(pin('JP1', '1'))
    J12 = add('J12', X(c8) + g(11), yledk - 2.54)
    J12.place('Reference', 0, -5.08, 'C').place('Value', -1.27, 7.62, 'C')
    W((X(c8), yledk), J12.pin('2'))
    jp = J12.pin('1')
    W(jp, (X(jp) - g(2), Y(jp)))
    pwr((X(jp) - g(2), Y(jp)), g(2))
    s.label('LED_K', (X(c8) + g(2), yledk))
    text('J12: 外付け LED (L+ / L-)', (X(e8) - g(28), yfb + g(7)), 1.27, False)
    text('JP1 を外すと基板の LED が切れる', (X(e8) - g(28), yfb + g(9)), 1.27, False)
    return s, dict(hv=hv, pw=pw)


# =====================================================================================
if __name__ == '__main__':
    power = sheet_power()
    hvs = sheet_hv()
    rs, ctx = sheet_root()
    subs = {'電源・USB': power, '高圧・GM 管': hvs}
    out = sys.argv[1] if len(sys.argv) > 1 else 'out/proj'
    os.makedirs(out, exist_ok=True)
    report = {}
    for sh in (rs, power, hvs):
        sh.finalize()
        report[sh.name] = dict(junctions=len(sh.junctions), crossings=sh.crossings, errors=sh.errors,
                               tsplit=sh.tsplit, text=sh.check_text())
        print('==', sh.name, 'junctions', len(sh.junctions), 'crossings', sh.crossings, 'errors', sh.errors)
        for i in report[sh.name]['text']:
            print('  TXT', i)
    chk = rs.check_netlist([power, hvs])
    print('NETLIST', {k: v for k, v in chk.items()})
    report['netlist'] = chk
    rs.write(os.path.join(out, 'hosikuzu.kicad_sch'))
    for sym in rs.sheets:
        sub = subs[sym.name]
        sub.write(os.path.join(out, sym.file), inst_path='/' + rs.root + '/' + sym.uuid)
    json.dump(report, open(os.path.join(out, 'build_report.json'), 'w'), ensure_ascii=False, indent=1, default=str)
