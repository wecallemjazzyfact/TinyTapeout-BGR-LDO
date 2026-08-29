#!/usr/bin/env python3
"""CJPTEX_2/_3 출력 met4 세로가 VDDC 와 어디서 만나는지 특정.

출력 met4:  x 115.790..116.250 (CJPTEX_2),  x 116.880..117.340 (CJPTEX_3)
            y -5.0 .. 66.1
이 두 기둥과 겹치는 via3 를 찾고, 그 via3 에 닿는 met3 를 나열한다.
"""
import gdstk

lib = gdstk.read_gds("ldo_top_chk.gds")
top = [c for c in lib.cells if c.name == "ldo_top"][0].copy("_f")
top.flatten()

def lay(l, d=20):
    return [p for p in top.polygons if (p.layer, p.datatype) == (l, d)]

m3, m4 = lay(70), lay(71)
v3 = [p for p in top.polygons if (p.layer, p.datatype) == (70, 44)]

COLS = [("CJPTEX_2 out", 115.79, 116.25), ("CJPTEX_3 out", 116.88, 117.34)]

for name, x0, x1 in COLS:
    print(f"=== {name}  x {x0}..{x1} ===")
    # 그 x 범위의 met4 기둥
    cols = [p for p in m4
            if p.bounding_box()[0][0] >= x0-0.2 and p.bounding_box()[1][0] <= x1+0.2
            and p.bounding_box()[1][1] > 50]
    for c in cols:
        b = c.bounding_box()
        print("  met4 x %.3f..%.3f y %.3f..%.3f" % (b[0][0], b[1][0], b[0][1], b[1][1]))
        hits = [v for v in v3 if gdstk.boolean([c], [v], "and")]
        print("    닿는 via3 %d개" % len(hits))
        for v in hits[:12]:
            vb = v.bounding_box()
            print("      via3 x %.3f..%.3f y %.3f..%.3f" % (vb[0][0], vb[1][0], vb[0][1], vb[1][1]))
            for m in m3:
                if gdstk.boolean([m], [v], "and"):
                    mb = m.bounding_box()
                    w = mb[1][0] - mb[0][0]
                    tag = "  <== 광역 met3 (VDDC 의심)" if w > 10 else ""
                    print("         met3 x %.3f..%.3f y %.3f..%.3f  폭 %.2f%s"
                          % (mb[0][0], mb[1][0], mb[0][1], mb[1][1], w, tag))
        if len(hits) > 12:
            print("      ... (%d개 더)" % (len(hits)-12))
    print()
