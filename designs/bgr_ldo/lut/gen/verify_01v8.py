#!/usr/bin/env python3
"""
thin-ox (01v8) gm/Id LUT 검증 — 5D 테이블 무결성 및 앵커 대조

순수 python. `lookup.py` 를 거치지 않고 `.pkl` 을 직접 읽는다.
조회 계층의 버그가 검증을 통과시키는 일이 없도록 경로를 분리한 것이다.

앵커는 전부 **당세션 독립 덱 실측**이며 **전부 격자 정점**이다.
보간이 개입하지 않으므로 **0.00% 를 기대**한다. 어긋나면 파이프라인 문제다.

────────────────────────────────────────────────────────────────
★ 앵커 정밀도 규율 (v2에서 추가된 규칙)
────────────────────────────────────────────────────────────────
**게이트는 기준값 자신의 정밀도보다 좁을 수 없다.**

v1은 `--probe-bins` 의 `%9.3f` 표시값(`0.022 uA`, 유효숫자 2자리, ±2.3%)을
`2.200000e-08` 로 옮겨 적고 허용오차 1%를 걸어 **정상 테이블을 FAIL 처리**했다.
같은 인덱스의 VT/VDSAT 는 표시 자릿수가 많아 0.005% 로 통과했으므로
인덱싱은 처음부터 정상이었다.

→ 앵커는 반드시 **전정밀도 출력(`print`)에서** 가져오고,
   출처 덱과 유효숫자를 주석에 병기한다. 표시용 반올림값은 앵커가 아니다.

────────────────────────────────────────────────────────────────
검사 순서
────────────────────────────────────────────────────────────────
  [0] 격자 인벤토리        형상·축·메타
  [1] 부호 감사            잡음 허용 상대 임계 (1e-9 × full scale)
  [2] 무결성 게이트        전하보존 / ID>0 / ID 단조 / VT 단조 / 변동성
  [3] W 축 앵커            6폭 × {ID, GM, GDS}
  [4] L 축 앵커            6길이 × {ID, VT, VDSAT}
  [5] VT vs W 앵커         협폭 거동
  [6] 물리 정합            gm/Id 상한, vdsat, CGD 0교차

exit 0 은 모든 게이트 통과일 때만.
"""

import os
import pickle
import sys

import numpy as np

GEN_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(GEN_DIR), "data")
SIGN_NOISE_REL = 1e-9

FAIL, NOTE = [], []

# ─────────────────── 앵커 (조건·출처·정밀도 병기) ───────────────────
# 전부 tt / 27 °C / nf=1 / m=1 / geometry 생략(PDK 기본값)

# [3] gen/wscan01v8.sp   L=0.15 µm, VGS=VDS=0.9 V (pfet 는 VSG=VSD=0.9), VSB=0
#     `print` 전정밀도 (6~7 유효숫자).  pfet GM 은 해당 덱 미출력 → None
ANCHOR_W = {
    "nfet_01v8": {
        0.42: (1.29586e-05, 1.102320e-04, 6.540512e-06),
        0.65: (2.09145e-05, 1.728041e-04, 1.032637e-05),
        1.0:  (3.28893e-05, 2.769877e-04, 1.612391e-05),
        2.0:  (8.17677e-05, 6.409327e-04, 3.731305e-05),
        5.0:  (2.32222e-04, 1.788517e-03, 1.015138e-04),
        10.0: (4.89503e-04, 3.465026e-03, 2.100083e-04),
    },
    "pfet_01v8": {
        0.42: (3.885319e-06, None, 1.644469e-06),
        0.65: (7.437728e-06, None, 4.925872e-06),
        1.0:  (1.162163e-05, None, 9.529040e-06),
        2.0:  (2.057998e-05, None, 1.907185e-05),
        5.0:  (4.384712e-05, None, 4.159855e-05),
        10.0: (9.063351e-05, None, 9.294781e-05),
    },
}

# [4] W=1 µm, VGS=VDS=0.9 V, VSB=0
#     ID    : gen/lanchor01v8.sp  `print` 전정밀도 (nfet 6자리 / pfet 7자리)
#     VT    : --probe-bins 표시값 (5자리, ±0.001%)
#     VDSAT : --probe-bins 표시값 (4~5자리, ±0.009%)
ANCHOR_L = {
    "nfet_01v8": {
        0.15: (3.28893e-05, 0.76988, 0.12755),
        0.18: (2.86005e-05, 0.74265, 0.14484),
        0.25: (2.21810e-05, 0.71278, 0.16401),
        0.50: (1.67797e-05, 0.63809, 0.21678),
        1.00: (1.10228e-05, 0.61542, 0.26527),
        2.00: (6.22835e-06, 0.57745, 0.28606),
    },
    "pfet_01v8": {
        0.15: (1.162163e-05, 0.62595, 0.26087),
        0.18: (4.886722e-06, 0.73360, 0.17843),
        0.25: (1.477295e-06, 0.84414, 0.11420),
        0.50: (2.010925e-07, 0.92011, 0.07258),
        1.00: (5.820021e-08, 0.96014, 0.06556),
        2.00: (2.157893e-08, 0.96899, 0.05692),
    },
}

# [5] gen/wvth.sp   VT, VGS=VDS=0.9 V, VSB=0.  `print` 전정밀도 (7자리)
ANCHOR_VT = {
    "nfet_01v8": {(0.42, 0.15): 0.7750921, (1.0, 0.15): 0.7698823,
                  (2.0, 0.15): 0.7402045, (5.0, 0.15): 0.7082454,
                  (10.0, 0.15): 0.7266931, (10.0, 2.0): 0.5488605},
    "pfet_01v8": {(0.42, 0.15): 0.6896867, (1.0, 0.15): 0.6259541,
                  (2.0, 0.15): 0.6618696, (5.0, 0.15): 0.6962064,
                  (10.0, 0.15): 0.6924177, (10.0, 2.0): 1.046557},
}

# 허용오차 — 각 앵커의 유효숫자에서 역산한 값보다 넉넉하되 의미는 남게
TOL = dict(W_ID=0.01, W_GM=0.01, W_GDS=0.01,
           L_ID=0.02, L_VT=0.05, L_VDSAT=0.05, VT_W=0.01)

VARS = ["ID", "GM", "GDS", "CGG", "CGS", "CGD", "CGB", "VT", "VDSAT"]
MUST_POS = ("ID", "VT", "VDSAT", "GM", "GDS", "CGG")


# ─────────────────── 헬퍼 ───────────────────
def hdr(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)


def sub(t):
    print("\n--- %s ---" % t)


def load(dev):
    p = os.path.join(DATA_DIR, "%s.pkl" % dev)
    if not os.path.exists(p):
        print("  %s: 파일 없음 (%s)" % (dev, p))
        FAIL.append("%s load" % dev)
        return None
    with open(p, "rb") as fh:
        return pickle.load(fh)


def idx(ax, v):
    return int(np.argmin(np.abs(np.asarray(ax) - v)))


def chk(name, got, exp, tol, tol_abs=None, gate=True):
    if got is None or exp is None:
        return True
    err = got - exp
    pct = err / exp * 100.0 if exp else float("nan")
    ok = abs(pct) <= tol or (tol_abs is not None and abs(err) <= tol_abs)
    tag = "PASS" if ok else ("FAIL" if gate else "note")
    if not ok:
        (FAIL if gate else NOTE).append(name)
    print("    %-22s lut=%12.6e  meas=%12.6e  %+9.4f%%  %s"
          % (name, got, exp, pct, tag))
    return ok


def sign_violation(a):
    a = np.asarray(a, float)
    thr = -SIGN_NOISE_REL * float(np.max(np.abs(a)))
    return int((a < thr).sum()), float(a.min()), thr


# ─────────────────── 실행 ───────────────────
hdr("thin-ox (01v8) LUT 검증   tt / 27 °C / nf=1 / m=1 / geometry 생략")

DATA = {}
for dev in ("nfet_01v8", "pfet_01v8"):
    d = load(dev)
    if d is not None:
        DATA[dev] = d
if len(DATA) < 2:
    print("\n테이블이 없습니다. run_sweep_01v8.py 를 먼저 실행하십시오.")
    sys.exit(1)

# [0]
sub("[0] 격자 인벤토리")
for dev, d in DATA.items():
    sh = d["ID"].shape
    exp = tuple(len(d[a]) for a in ("W", "L", "VGS", "VDS", "VSB"))
    ok = sh == exp
    if not ok:
        FAIL.append("%s shape" % dev)
    print("  %s  shape=%s %s" % (dev, sh, "OK" if ok else "MISMATCH %s" % (exp,)))
    print("      W  (%d): %s um" % (len(d["W"]), np.array2string(d["W"] * 1e6, precision=2)))
    print("      L  (%d): %s um" % (len(d["L"]), np.array2string(d["L"] * 1e6, precision=2)))
    print("      VSB(%d): %s" % (len(d["VSB"]), np.array2string(d["VSB"], precision=2)))
    print("      VGS(%d): %.3f..%.3f step %.4f   VDS(%d): %.3f..%.3f step %.4f"
          % (len(d["VGS"]), d["VGS"].min(), d["VGS"].max(), np.median(np.diff(d["VGS"])),
             len(d["VDS"]), d["VDS"].min(), d["VDS"].max(), np.median(np.diff(d["VDS"]))))
    m = d.get("_META", {})
    print("      meta: %s | %s" % (m.get("version", "?"), m.get("generated", "?")))

# [1]
sub("[1] 부호 감사  (ID/VT/VDSAT/GM/GDS/CGG ≥ 0 ; 캡은 signed 유지)")
for dev, d in DATA.items():
    print("  [%s]" % dev)
    for k in VARS:
        n_sig, mn, _ = sign_violation(d[k])
        n_neg = int((np.asarray(d[k]) < 0).sum())
        flag = ""
        if k in MUST_POS and n_sig:
            flag = "  ← 부호 오류"
            FAIL.append("%s %s sign" % (dev, k))
        elif k in MUST_POS and n_neg:
            flag = "  (먼지, 정상)"
        print("    %-6s min=%12.4e max=%12.4e  neg=%8d 유의미=%8d%s"
              % (k, mn, float(np.max(d[k])), n_neg, n_sig, flag))

# [2]
sub("[2] 무결성 게이트")
for dev, d in DATA.items():
    cgg = d["CGG"]
    tot = d["CGS"] + d["CGD"] + d["CGB"]
    with np.errstate(divide="ignore", invalid="ignore"):
        e = np.abs(cgg - tot) / np.where(cgg > 0, cgg, np.nan)
    w = float(np.nanmax(e)) * 100
    ok = w < 3.0
    if not ok:
        FAIL.append("%s charge" % dev)
    print("  %-10s 전하보존 최대오차 %.4f %%   %s" % (dev, w, "PASS" if ok else "FAIL"))

    k0 = 1 if abs(d["VDS"][0]) < 1e-12 else 0
    n_sig, mn, _ = sign_violation(d["ID"][:, :, :, k0:, :])
    ok = n_sig == 0
    if not ok:
        FAIL.append("%s ID>0" % dev)
    print("  %-10s ID > 0 (VDS>0)          min %.3e   %s" % (dev, mn, "PASS" if ok else "FAIL"))

    dif = np.diff(d["ID"], axis=2)
    tol = -SIGN_NOISE_REL * float(np.max(np.abs(d["ID"])))
    frac = 100.0 * float((dif < tol).sum()) / dif.size
    ok = frac == 0.0
    if not ok:
        FAIL.append("%s ID monotonic" % dev)
    print("  %-10s ID ↑ with VGS           위반 %.3f %%   %s" % (dev, frac, "PASS" if ok else "FAIL"))

    dif = np.diff(d["VT"], axis=4)
    ok = bool(np.all(dif >= -1e-9))
    if not ok:
        FAIL.append("%s VT monotonic" % dev)
    print("  %-10s VT ↑ with VSB           %s" % (dev, "PASS" if ok else "FAIL"))

    iD = idx(d["VDS"], 0.9)
    flat = int((np.ptp(d["GM"][:, :, :, iD, :], axis=2) == 0).sum())
    ok = flat == 0
    if not ok:
        FAIL.append("%s GM constant" % dev)
    print("  %-10s GM 변동성 (상수 단면)     %d 개   %s" % (dev, flat, "PASS" if ok else "FAIL"))

# [3]
sub("[3] W 축 앵커   L=0.15 µm, VGS=VDS=0.9 V, VSB=0   (gen/wscan01v8.sp, 전정밀도)")
for dev, d in DATA.items():
    print("  [%s]" % dev)
    iL, iG, iD, iB = (idx(d["L"], 0.15e-6), idx(d["VGS"], 0.9),
                      idx(d["VDS"], 0.9), idx(d["VSB"], 0.0))
    for w, (rid, rgm, rgds) in ANCHOR_W[dev].items():
        iW = idx(d["W"], w * 1e-6)
        chk("W=%-5g ID" % w, float(d["ID"][iW, iL, iG, iD, iB]), rid, TOL["W_ID"])
        chk("W=%-5g GM" % w, float(d["GM"][iW, iL, iG, iD, iB]), rgm, TOL["W_GM"])
        chk("W=%-5g GDS" % w, float(d["GDS"][iW, iL, iG, iD, iB]), rgds, TOL["W_GDS"])

# [4]
sub("[4] L 축 앵커   W=1 µm, VGS=VDS=0.9 V, VSB=0   (ID: gen/lanchor01v8.sp 전정밀도)")
for dev, d in DATA.items():
    print("  [%s]" % dev)
    iW, iG, iD, iB = (idx(d["W"], 1e-6), idx(d["VGS"], 0.9),
                      idx(d["VDS"], 0.9), idx(d["VSB"], 0.0))
    for L, (rid, rvt, rvd) in ANCHOR_L[dev].items():
        iL = idx(d["L"], L * 1e-6)
        chk("L=%-5g ID" % L, float(d["ID"][iW, iL, iG, iD, iB]), rid, TOL["L_ID"])
        chk("L=%-5g VT" % L, float(d["VT"][iW, iL, iG, iD, iB]), rvt,
            TOL["L_VT"], tol_abs=1e-5)
        chk("L=%-5g VDSAT" % L, float(d["VDSAT"][iW, iL, iG, iD, iB]), rvd,
            TOL["L_VDSAT"], tol_abs=1e-5)

# [5]
sub("[5] VT vs W 앵커   VGS=VDS=0.9 V, VSB=0   (gen/wvth.sp, 전정밀도)")
for dev, d in DATA.items():
    print("  [%s]" % dev)
    iG, iD, iB = idx(d["VGS"], 0.9), idx(d["VDS"], 0.9), idx(d["VSB"], 0.0)
    for (w, L), rv in ANCHOR_VT[dev].items():
        iW, iL = idx(d["W"], w * 1e-6), idx(d["L"], L * 1e-6)
        chk("W=%-5g L=%-5g VT" % (w, L), float(d["VT"][iW, iL, iG, iD, iB]),
            rv, TOL["VT_W"], tol_abs=1e-5)

# [6]
sub("[6] 물리 정합  (정보용 — 게이트 아님)")
for dev, d in DATA.items():
    sat = d["VDS"] >= 0.4
    with np.errstate(divide="ignore", invalid="ignore"):
        gm_id = np.where(d["ID"] > 1e-12, d["GM"] / np.maximum(d["ID"], 1e-30), np.nan)
    mx = float(np.nanmax(gm_id[:, :, :, sat, :]))
    n_eff = 1.0 / (mx * 0.02585)
    print("  %-10s gm/Id 최대 %6.2f V⁻¹  → n=%.2f, S=%.0f mV/dec  %s"
          % (dev, mx, n_eff, n_eff * 59.5, "정합" if 1.0 <= n_eff <= 2.0 else "★ 확인"))
    nc = int((np.asarray(d["CGD"]) < 0).sum())
    print("  %-10s CGD 음수 %d / %d (%.1f%%) — 포화에서 0 교차하는 물리"
          % (dev, nc, d["CGD"].size, 100.0 * nc / d["CGD"].size))
    print("  %-10s VDSAT 범위 %.4f ~ %.4f V" % (dev, float(d["VDSAT"].min()),
                                                float(d["VDSAT"].max())))

# 요약
hdr("요약")
if NOTE:
    print("  비게이팅 편차: %s" % ", ".join(sorted(set(NOTE))))
if FAIL:
    print("  실패 게이트 (%d):" % len(set(FAIL)))
    for f in sorted(set(FAIL)):
        print("    - %s" % f)
    print("\n>>> VERIFICATION: FAIL")
    sys.exit(1)
print("  모든 게이트 통과")
print("\n>>> VERIFICATION: PASS")
sys.exit(0)
