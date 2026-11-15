# 元回路図 (monoradio102/stardust-lamp hardware/schematic.pdf, EasyEDA, 5 ページ) から起こした接続表。
# ピン番号は KiCad 側で使うシンボルのピン番号。元回路図のピン名との対応はコメントに書く。
# NC はどこにもつながないピン (no_connect を打つ)。

PARTS = {}


def P(ref, lib_id, value, pins, fp=''):
    PARTS[ref] = dict(lib_id=lib_id, value=value, pins=pins, fp=fp)


# ---------------- Page 1: Power (USB) ----------------
# J1 は EasyEDA の 16 ピン部品 (A1B12 などを 1 パッドにまとめた形)。KiCad の USB2.0 16P シンボルで描く。
P('J1', 'Connector:USB_C_Receptacle_USB2.0_16P', 'TYPE-C 16PIN 2MD(073)', {
    'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND',   # GND x2 + EH(13,14)
    'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
    'A5': 'CC1', 'B5': 'CC2',
    'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DN', 'B7': 'USB_DN',
    'A8': 'NC', 'B8': 'NC'})
P('F1', 'Device:Polyfuse', 'nSMD050-33V', {'1': 'VBUS', '2': 'VUSB'})
P('R1', 'Device:R', '5.1k', {'1': 'CC1', '2': 'GND'})
P('R2', 'Device:R', '5.1k', {'1': 'CC2', '2': 'GND'})
P('C1', 'Device:C', '10uF', {'1': 'V5', '2': 'GND'})
P('C2', 'Device:C', '100nF', {'1': 'V5', '2': 'GND'})
P('D2', 'Device:D_Schottky', 'B5819W', {'1': 'V5', '2': 'VUSB'})          # K=V5, A=VUSB
P('U1', 'Interface_USB:CH340N', 'CH340N', {
    '1': 'USB_DP', '2': 'USB_DN', '3': 'GND', '4': 'NC', '5': 'V5', '6': 'CH_TXD', '7': 'CH_RXD', '8': 'CH_V3'})
P('C3', 'Device:C', '100nF', {'1': 'CH_V3', '2': 'GND'})
P('C4', 'Device:C', '100nF', {'1': 'V5', '2': 'GND'})
P('D1', 'Device:D_Schottky', 'B5819W', {'1': 'CH_TXD', '2': 'SER_D'})     # K=CH_TXD, A=SER_D
P('R3', 'Device:R', '470', {'1': 'UPDI_SER', '2': 'UPDI'})
P('R4', 'Device:R', '1k', {'1': 'CH_RXD', '2': 'SER_D'})
# SW1: 2 (共通) = CH_RXD, 1 = UPDI_SER (PROG), 3 = TXD (RUN)
P('SW1', 'Switch:SW_SPDT', 'MST-12D18G4', {'1': 'UPDI_SER', '2': 'CH_RXD', '3': 'TXD'})

# ---------------- Page 2: HV ----------------
P('R10', 'Device:R', '10', {'1': 'V5', '2': 'V5_HV'})
P('C10', 'Device:C', '10uF', {'1': 'V5_HV', '2': 'GND'})
P('C11', 'Device:C', '100nF', {'1': 'V5_HV', '2': 'GND'})
P('R11', 'Device:R', '47', {'1': 'HV_DRV', '2': 'HV_GATE'})
P('R12', 'Device:R', '100k', {'1': 'HV_GATE', '2': 'GND'})
P('L1', 'Device:L', '1mH', {'1': 'V5_HV', '2': 'SW'})
P('Q1', 'Transistor_FET:Q_NMOS_GDSD', 'BSP125', {'1': 'HV_GATE', '2': 'SW', '3': 'GND', '4': 'SW'})
P('D10', 'Diode:US1M', 'US1M', {'1': 'HV1', '2': 'SW'})                  # K=HV1, A=SW
P('C12', 'Device:C', '10nF', {'1': 'HV1', '2': 'GND'})
P('C13', 'Device:C', '10nF', {'1': 'SW', '2': 'PUMP'})
P('D11', 'Diode:US1M', 'US1M', {'1': 'PUMP', '2': 'HV1'})                # K=PUMP, A=HV1
P('D12', 'Diode:US1M', 'US1M', {'1': 'HV', '2': 'PUMP'})                 # K=HV, A=PUMP
P('C14', 'Device:C', '10nF', {'1': 'HV', '2': 'GND'})
P('D13', 'Diode:SMAJ440A', 'SMAJ440A', {'1': 'HV', '2': 'GND'})          # 1=K(帯側)
chain = ['HV', 'DIV1', 'DIV2', 'DIV3', 'DIV4', 'DIV5', 'DIV6', 'DIV7', 'HV_FB']
for i in range(8):
    P('R%d' % (20 + i), 'Device:R', '10M', {'1': chain[i], '2': chain[i + 1]})
P('R28', 'Device:R', '220k', {'1': 'HV_FB', '2': 'GND'})
P('C15', 'Device:C', '10nF', {'1': 'HV_FB', '2': 'GND'})
for s, j, r0 in (('A', 'J10', 30), ('B', 'J11', 40)):
    q = 'Q2' if s == 'A' else 'Q3'
    c = 'C16' if s == 'A' else 'C17'
    P('R%d' % r0, 'Device:R', '4.7M', {'1': 'HV', '2': 'ANODE_' + s})
    P(j, 'Connector_Generic:Conn_01x02', 'TSM-102-01-L-SV', {'1': 'ANODE_' + s, '2': 'CATH_' + s})
    P('R%d' % (r0 + 1), 'Device:R', '100k', {'1': 'CATH_' + s, '2': 'GND'})
    P('R%d' % (r0 + 2), 'Device:R', '10k', {'1': 'CATH_' + s, '2': 'BASE_' + s})
    P(c, 'Device:C', '100pF', {'1': 'BASE_' + s, '2': 'GND'})
    P(q, 'Transistor_BJT:MMBT3904', 'MMBT3904', {'1': 'BASE_' + s, '2': 'GND', '3': 'PULSE_' + s})
    P('R%d' % (r0 + 3), 'Device:R', '10k', {'1': 'V5', '2': 'PULSE_' + s})

# ---------------- Page 3: Logic ----------------
P('C20', 'Device:C', '100nF', {'1': 'V5', '2': 'GND'})
P('C21', 'Device:C', '10uF', {'1': 'V5', '2': 'GND'})
P('U2', 'MCU_Microchip_ATtiny:ATtiny1614-SS', 'ATtiny1614-SSNR', {
    '1': 'V5', '2': 'HV_DRV', '3': 'NC', '4': 'VBAT_ADC', '5': 'HV_FB', '6': 'NC', '7': 'TXD',
    '8': 'OUT_DRV', '9': 'KICK', '10': 'UPDI', '11': 'PULSE_A', '12': 'PULSE_B', '13': 'BTN', '14': 'GND'})
# S8550 は SOT-23 (1=B, 2=E, 3=C) として Q_PNP_BEC で描く
P('R70', 'Device:R', '10k', {'1': 'PULSE_A', '2': 'GB_A'})
P('Q6', 'Transistor_BJT:Q_PNP_BEC', 'S8550', {'1': 'GB_A', '2': 'V5', '3': 'GLOW_MID'})
P('R71', 'Device:R', '10k', {'1': 'PULSE_B', '2': 'GB_B'})
P('Q7', 'Transistor_BJT:Q_PNP_BEC', 'S8550', {'1': 'GB_B', '2': 'GLOW_MID', '3': 'GLOW_CHG'})
P('R72', 'Device:R', '47', {'1': 'GLOW_CHG', '2': 'GLOW'})
P('R75', 'Device:R', '1k', {'1': 'KICK', '2': 'GLOW'})
P('C40', 'Device:C', '2.2uF', {'1': 'GLOW', '2': 'GND'})
P('R78', 'Device:R', '220k', {'1': 'GLOW', '2': 'TAU_ADJ'})
P('R73', 'Device:R', '4.7M', {'1': 'GLOW', '2': 'GLOW_DIV'})
# VR: 1,3 = 両端, 2 = ワイパー
P('VR1', 'Device:R_Potentiometer', '1M (BRIGHT)', {'1': 'GLOW_DIV', '2': 'GLOW_TAP', '3': 'GND'})
P('VR2', 'Device:R_Potentiometer', '1M (FADE)', {'1': 'TAU_ADJ', '2': 'GND', '3': 'GND'})
P('C42', 'Device:C', '10nF', {'1': 'GLOW_TAP', '2': 'GND'})
P('U4', 'Amplifier_Operational:LMV321', 'LMV321IDBVR', {
    '1': 'GLOW_TAP', '2': 'GND', '3': 'LED_SENSE', '4': 'OPA_OUT', '5': 'V5'})
P('C41', 'Device:C', '100nF', {'1': 'V5', '2': 'GND'})
P('R76', 'Device:R', '1k', {'1': 'OPA_OUT', '2': 'LED_BASE'})
P('Q8', 'Transistor_BJT:MMBT3904', 'MMBT3904', {'1': 'LED_BASE', '2': 'LED_SENSE', '3': 'LED_K'})
P('R77', 'Device:R', '47', {'1': 'LED_SENSE', '2': 'GND'})
P('LED1', 'Device:LED', 'KT-0805W', {'1': 'LED_K', '2': 'LED1_A'})
P('JP1', 'Device:R', '0', {'1': 'V5', '2': 'LED1_A'})
P('J12', 'Connector_Generic:Conn_01x02', 'TSM-102-01-L-SV', {'1': 'V5', '2': 'LED_K'})
P('J13', 'Connector_Generic:Conn_01x06', 'TSM-106-01-L-SV', {
    '1': 'GND', '2': 'V5', '3': 'UPDI', '4': 'TXD', '5': 'PULSE_A', '6': 'PULSE_B'})
P('J14', 'Connector_Generic:Conn_01x03', 'TSM-103-01-L-SV', {'1': 'HV_FB', '2': 'BTN', '3': 'GLOW'})

# ---------------- Page 4: Battery ----------------
P('J15', 'Connector_Generic:Conn_01x02', 'TSM-102-01-L-SV', {'1': 'BAT_IN', '2': 'GND'})
P('Q5', 'Transistor_FET:AO3401A', 'AO3401A', {'1': 'GND', '2': 'VIN', '3': 'BAT_IN'})   # G=GND, S=VIN, D=BAT_IN
P('C30', 'Device:C', '10uF', {'1': 'VIN', '2': 'GND'})
P('C31', 'Device:C', '10uF', {'1': 'VIN', '2': 'GND'})
P('R63', 'Device:R', '1M', {'1': 'VIN', '2': 'VBAT_ADC'})
P('R64', 'Device:R', '330k', {'1': 'VBAT_ADC', '2': 'GND'})
P('C36', 'Device:C', '100nF', {'1': 'VBAT_ADC', '2': 'GND'})
P('R60', 'Device:R', '1M', {'1': 'VIN', '2': 'BOOST_EN'})
P('SW2', 'Switch:SW_SPDT', 'MST-12D18G4', {'1': 'NC', '2': 'BOOST_EN', '3': 'GND'})
# TPS63070RNM: 8 (VOUT) と 13 (VIN) は元の EasyEDA シンボルに無いので、元回路図どおり未接続 (NC) にする。
# データシートでは 7/8 が VOUT、12/13 が VIN (どちらも接続が前提)
P('U3', 'hosikuzu:TPS63070RNM', 'TPS63070RNMR', {
    '1': 'BOOST_EN', '2': 'NC', '3': 'BOOST_VAUX', '4': 'GND', '5': 'BOOST_FB', '6': 'GND',
    '7': 'VBOOST', '8': 'NC', '9': 'BSW2', '10': 'GND', '11': 'BSW1', '12': 'VIN', '13': 'NC',
    '14': 'BOOST_EN', '15': 'GND'})
P('C32', 'Device:C', '100nF', {'1': 'BOOST_VAUX', '2': 'GND'})
P('R61', 'Device:R', '330k', {'1': 'VBOOST', '2': 'BOOST_FB'})
P('R62', 'Device:R', '68k', {'1': 'BOOST_FB', '2': 'GND'})
for c in ('C33', 'C34', 'C35'):
    P(c, 'Device:C', '22uF', {'1': 'VBOOST', '2': 'GND'})
P('L2', 'Device:L', '1.5uH', {'1': 'BSW1', '2': 'BSW2'})
P('D3', 'Device:D_Schottky', 'B5819W', {'1': 'V5', '2': 'VBOOST'})      # K=V5, A=VBOOST

# ---------------- Page 5: P1 ----------------
P('J16', 'Connector_Generic:Conn_01x03', 'TSM-103-01-L-SV', {'1': 'V5', '2': 'EXT_OUT', '3': 'GND'})
P('R81', 'Device:R', '100', {'1': 'OUT_D', '2': 'EXT_OUT'})
P('R80', 'Device:R', '100k', {'1': 'OUT_DRV', '2': 'GND'})
P('Q9', 'Transistor_FET:2N7002', '2N7002', {'1': 'OUT_DRV', '2': 'GND', '3': 'OUT_D'})
P('SW3', 'Switch:SW_Push_Dual', 'TS-1187A-B-A-B', {'1': 'BTN', '2': 'BTN', '3': 'GND', '4': 'GND'})


def nets():
    """net -> sorted list of 'REF.PIN' (NC は除く)"""
    out = {}
    for ref, p in PARTS.items():
        for pin, n in p['pins'].items():
            if n == 'NC':
                continue
            out.setdefault(n, []).append('%s.%s' % (ref, pin))
    return {k: sorted(v) for k, v in out.items()}


if __name__ == '__main__':
    import json
    n = nets()
    print(len(PARTS), 'parts,', len(n), 'nets')
    single = [k for k, v in n.items() if len(v) < 2]
    print('single-pin nets:', single)
    json.dump(n, open('intended_netlist.json', 'w'), indent=1, ensure_ascii=False, sort_keys=True)
