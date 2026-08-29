#!/usr/bin/env python3
"""두 라벨 사이 연결 경로 추적 (BFS).

VREF_LOW (140.140, -40.010)  ~  VDDC (116.000, -79.400)
met1/met2/met3/met4 + via1/via2/via3 를 그래프로 보고 최단 경로를 찾는다.
경로에 나오는 도형 목록이 곧 단락 경로다.
"""
import gdstk, collections, sys

GDS = "ldo_top_chk.gds"
SRC = (116.000, -79.400)
DST = (143.100, -8.800)

lib = gdstk.read_gds(GDS)
top = [c for c in lib.cells if c.name == "ldo_top"][0].copy("_f")
top.flatten()

LAY = {(68,20):"m1",(69,20):"m2",(70,20):"m3",(71,20):"m4",
       (68,44):"v1",(69,44):"v2",(70,44):"v3"}
P = []
for p in top.polygons:
    k = (p.layer, p.datatype)
    if k in LAY:
        b = p.bounding_box()
        P.append([LAY[k], b[0][0], b[1][0], b[0][1], b[1][1], p])
print("도형 수:", len(P))

# 인접: 같은 층끼리 겹침, 또는 via 를 통한 층간
CONN = {"m1":{"m1","v1"},"v1":{"m1","m2"},"m2":{"m2","v1","v2"},
        "v2":{"m2","m3"},"m3":{"m3","v2","v3"},"v3":{"m3","m4"},"m4":{"m4","v3"}}

def ov(a, b):
    return a[1] <= b[2] and a[2] >= b[1] and a[3] <= b[4] and a[4] >= b[3]

def find(pt, prefer=None):
    hits = [i for i,q in enumerate(P)
            if q[1]-0.01 <= pt[0] <= q[2]+0.01 and q[3]-0.01 <= pt[1] <= q[4]+0.01]
    if prefer:
        h2 = [i for i in hits if P[i][0] == prefer]
        if h2: return h2
    return hits

s = find(SRC); d = set(find(DST))
print("시작 후보:", [(P[i][0], round(P[i][1],2), round(P[i][3],2)) for i in s])
print("도착 후보:", [(P[i][0], round(P[i][1],2), round(P[i][3],2)) for i in d])
if not s or not d:
    sys.exit("좌표에 도형 없음")

# BFS
prev = {i: None for i in s}
Q = collections.deque(s)
hit = None
while Q:
    u = Q.popleft()
    if u in d:
        hit = u; break
    for v in range(len(P)):
        if v in prev: continue
        if P[v][0] not in CONN[P[u][0]]: continue
        if ov(P[u], P[v]):
            prev[v] = u; Q.append(v)

if hit is None:
    print("=> 연결 없음 (단락 아님)")
else:
    path = []
    x = hit
    while x is not None:
        path.append(x); x = prev[x]
    path.reverse()
    print("=> 연결됨. 경로 %d 단계" % len(path))
    for i in path:
        q = P[i]
        print("   %-3s x %8.3f..%8.3f  y %9.3f..%9.3f" % (q[0], q[1], q[2], q[3], q[4]))
