#!/usr/bin/env python3
"""
ldo_top GDS 후처리 — RPM(86/20) 국소 보정

배경 (핸드오프 §2.22):
  RPM = (xhrpoly + xpc) grow 620 shrink 420  =  순확장 +0.200, 갭 1.24 이내 병합
  res_high_po_0p69 단일 바 -> RPM 1.090 < 1.270 (rpm.1a)
  배열 내부는 병합되고 **끝단 핑거만** 노출된다

보정 원리:
  magic drc(full) 의 rpm.1 에러 타일 = 부족분 영역 그 자체
  -> 그 사각형을 그대로 RPM 으로 추가하면 1.090 -> 1.270
  전 사각형이 해당 저항 셀 bbox 안이므로 rpm.2(0.84) 도 안전
  전역 grow/closing 없음 -> rpm.3 계열 감쌈(0.200) 불변

사용:
  magic:  load ldo_top ; drc style drc(full) ; drc euclidean on ; gds write ldo_top.gds
  shell:  python3 fix_rpm.py
  제출/검증은 모두 ldo_top_fixed.gds 기준
"""
import gdstk

SRC, DST, TOP = "ldo_top.gds", "ldo_top_fixed.gds", "ldo_top"

FIX = [  # (x0, y0, x1, y1, 설명)   layer 86/20
    (  0.300,  -5.420,   4.500,  -5.240, "EA 저항 스택 상단"),
    ( 68.960,  39.800,  70.230,  42.480, "BGR GHYW6X_0 (6bit 신규)"),
    (114.770,  39.800, 116.040,  42.480, "BGR GHYW6X_1 (6bit 신규)"),
    (109.610,   2.800, 110.880,   5.480, "BGR UKBC2Q_1 (6bit 신규)"),
    (  0.300, -34.880,   4.500, -34.700, "EA 저항 스택 하단"),
    (136.390, -93.200, 136.570, -73.160, "XRz 우측 (고립 1.09)"),
    (103.620,-115.520, 103.800,-114.250, "분압 서단"),
    (104.890,-118.200, 105.070,-115.520, "분압 서단2"),
    (133.080,-118.200, 133.260,-114.250, "분압 동단"),
    (  1.800,-119.920,   4.480,-119.740, "XR_slew1 상"),
    (  4.480,-119.920,   5.750,-119.740, "XR_slew1 상2"),
    (  1.800,-128.110,   4.480,-127.930, "XR_slew1 하"),
    (  1.800,-130.920,   4.480,-130.740, "XR_slew2 상"),
    (  4.480,-130.920,   5.750,-130.740, "XR_slew2 상2"),
    (  1.800,-139.110,   4.480,-138.930, "XR_slew2 하"),
]

lib = gdstk.read_gds(SRC)
top = [c for c in lib.cells if c.name == TOP][0]
fx = lib.new_cell("RPM_FIX")
for x0, y0, x1, y1, _ in FIX:
    fx.add(gdstk.rectangle((x0, y0), (x1, y1), layer=86, datatype=20))
top.add(gdstk.Reference(fx))
lib.write_gds(DST)
print("RPM_FIX %d개 -> %s" % (len(fx.polygons), DST))
for x0, y0, x1, y1, d in FIX:
    print("   %-22s x %8.3f..%8.3f  y %9.3f..%9.3f" % (d, x0, x1, y0, y1))
