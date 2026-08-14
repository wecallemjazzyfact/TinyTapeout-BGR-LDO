#!/usr/bin/env python3
"""
thin-ox (1.8 V) gm/Id LUT 생성기 — sky130_fd_pr__{nfet,pfet}_01v8

thick-ox용 `run_sweep.py`는 건드리지 않는다 (검증 통과 상태).
산출물: data/nfet_01v8.pkl / data/pfet_01v8.pkl

════════════════════════════════════════════════════════════════
★ v4 — `.save` 누락 수정 (v3 데이터는 전량 폐기)
════════════════════════════════════════════════════════════════
ngspice는 전압원 분기 전류 `i(Vm)` 는 기본 저장하지만
**소자 내부 파라미터 `@m.x<inst>.<model>[param]` 은 `save` 없이는
스윕 중에 기록하지 않는다.** v3는 이걸 빠뜨려서 wrdata가 `.op` 종료 시점의
**스칼라 하나를 열 전체에 브로드캐스트**했다.

증거 (v3 산출물, nfet W=1 L=0.15 VGS=VDS=0.9 격자점):
    VDSAT  저장 0.331 V  vs  실측 0.128 V   ← VGS=1.8 종점의 값
    GM     저장 531 µS   vs  실측 277 µS    ← 〃
    GDS    저장 51.5 µS  vs  실측 16.1 µS   ← 〃
    ID     저장 = 실측 (0.0000%)            ← 분기 전류라 기본 저장됨

컬럼 매핑·reshape·부호 규약은 전부 정상이었고 데이터가 애초에 없었다.
부호 감사가 통과한 것도 당연하다 — 상수라도 부호는 맞기 때문이다.
그래서 v4는 **"VGS 축을 따라 변하는가"** 게이트를 추가한다(§audit).

════════════════════════════════════════════════════════════════
W가 5번째 이산 축이다
════════════════════════════════════════════════════════════════
thick-ox는 W≥5 µm에서 gds/W가 1.5% 이내로 평탄해 단일 기준폭 선형 스케일이
성립했으나 **thin-ox는 그 평탄역이 없다** (L=0.15, VGS=VDS=0.9, tt/27 실측):
    nfet  ID/W  30.85 → 48.95 µA/µm (W 0.42→10, +59% 단조), gm/gds 16.5~17.6 (평탄)
    pfet  gds/W 3.92 → 7.58 (W 0.42→0.65, +94% = bin 경계)
→ **W 보간 금지.** L과 동일하게 격자값만 사용한다.

저장 형식: ID.shape == (W, L, VGS, VDS, VSB)
스케일 규칙: 실소자 = LUT(W_grid, ...) × m   ← W 나눗셈 없음

════════════════════════════════════════════════════════════════
W/L 단위 — 접미사 없는 마이크로미터
════════════════════════════════════════════════════════════════
    W=1 L=0.15   ✔       W=1u L=0.15u ✘ (1 fm)
근거: `run_sweep.py` L106/L247 이 `W=10` 형식이고 검증을 통과했다.

부호 규약은 thick-ox와 동일 (lut/README.md §4). 가정하지 않고 감사한다.

════════════════════════════════════════════════════════════════
사용법  (ngspice 호출 → 반드시 `bash -l -c`)
════════════════════════════════════════════════════════════════
  python3 run_sweep_01v8.py --preflight     # ★ 먼저. 벡터가 실제로 변하는지 (1분)
  python3 run_sweep_01v8.py --probe-bins    # (W,L) 유효성
  python3 run_sweep_01v8.py                 # 본 스윕 (약 40분)
"""

import argparse
import os
import pickle
import re
import subprocess
import time

import numpy as np

# ────────────────────────── 설정 ──────────────────────────
LIB = "/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice"
CORNER = "tt"
TEMP_C = 27
VDD = 1.8

W_GRID_UM = [0.42, 0.65, 1.0, 2.0, 5.0, 10.0]   # ★ 이산 축. 보간 금지
L_GRID_UM = [0.15, 0.18, 0.25, 0.50, 1.00, 2.00]
VSB_GRID = [0.0, 0.2, 0.4, 0.8, 1.2]
VGS_STEP = 0.025
VDS_STEP = 0.050

GEN_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(GEN_DIR), "data")

DEVICES = {
    "nfet_01v8": dict(model="sky130_fd_pr__nfet_01v8", pol=+1.0),
    "pfet_01v8": dict(model="sky130_fd_pr__pfet_01v8", pol=-1.0),
}

VARS = ["ID", "GM", "GDS", "CGG", "CGS", "CGD", "CGB", "VT", "VDSAT"]
PROBE_KEYS = ["gm", "gds", "cgg", "cgs", "cgd", "cgb", "vth", "vdsat"]

SIGN = {
    "nfet_01v8": {"ID": -1.0, "GM": +1.0, "GDS": +1.0, "CGG": +1.0,
                  "CGS": -1.0, "CGD": -1.0, "CGB": -1.0,
                  "VT": +1.0, "VDSAT": +1.0},
    "pfet_01v8": {"ID": +1.0, "GM": +1.0, "GDS": +1.0, "CGG": +1.0,
                  "CGS": -1.0, "CGD": -1.0, "CGB": -1.0,
                  "VT": +1.0, "VDSAT": +1.0},
}

MUST_BE_POSITIVE = ("ID", "VT", "VDSAT", "GM", "GDS", "CGG")
SIGN_NOISE_REL = 1e-9


def make_axes():
    return dict(
        W=np.array(W_GRID_UM) * 1e-6,
        L=np.array(L_GRID_UM) * 1e-6,
        VGS=np.round(np.arange(int(round(VDD / VGS_STEP)) + 1) * VGS_STEP, 6),
        VDS=np.round(np.arange(int(round(VDD / VDS_STEP)) + 1) * VDS_STEP, 6),
        VSB=np.array(VSB_GRID, dtype=float),
    )


def run_ngspice(deck_text, stem):
    path = os.path.join(GEN_DIR, stem + ".sp")
    with open(path, "w") as fh:
        fh.write(deck_text)
    r = subprocess.run(["ngspice", "-b", os.path.basename(path)],
                       cwd=GEN_DIR, capture_output=True, text=True)
    return r, (r.stdout or "") + (r.stderr or "")


def detect_inner(dev, w_um=1.0, L_um=0.5):
    model = DEVICES[dev]["model"]
    deck = f""".title inner name probe
.lib {LIB} {CORNER}
.temp {TEMP_C}
Vd d 0 0.9
Vg g 0 0.9
XM1 d g 0 0 {model} W={w_um:g} L={L_um:g} nf=1
.control
op
listing e
.endc
.end
"""
    _, txt = run_ngspice(deck, "_inner")
    m = re.search(r"\bm\.xm1\.(\S+)", txt, flags=re.IGNORECASE)
    return m.group(1) if m else None


def multi_L_deck(dev, w_um, vsb, inner, mode, out_name=None):
    """
    한 (W, VSB) 에서 L 6종 동시 인스턴스화. 0 V 전압원을 전류계로 사용.
    nfet: 소스 0 / 벌크 −VSB / 게이트·드레인 0→+1.8
    pfet: 소스 0 / 벌크 +VSB / 게이트·드레인 0→−1.8
    """
    d = DEVICES[dev]
    model, s = d["model"], d["pol"]
    out = [f".title thin-ox {mode} {dev} W={w_um} VSB={vsb}",
           f".lib {LIB} {CORNER}", f".temp {TEMP_C}",
           "Vd dc 0 0", "Vg g 0 0", f"Vb b 0 {-s * vsb:g}"]
    for i, Lu in enumerate(L_GRID_UM):
        out.append(f"Vm{i} d{i} dc 0")
        out.append(f"XM{i} d{i} g 0 b {model} W={w_um:g} L={Lu:g} nf=1")

    # ★ v4 핵심: 소자 내부 파라미터는 .save 가 있어야 스윕 중 벡터로 기록된다.
    #   없으면 wrdata 가 종점 스칼라를 열 전체에 브로드캐스트한다.
    #   .save 는 누적되므로 인스턴스별로 나눠 써도 된다(라인 길이 안전).
    if mode == "dc":
        for i in range(len(L_GRID_UM)):
            vecs = [f"i(Vm{i})"] + [f"@m.xm{i}.{inner}[{k}]" for k in PROBE_KEYS]
            out.append(".save " + " ".join(vecs))

    out.append(".control")
    if mode == "op":
        out += [f"alter Vg dc = {s * 0.9:g}", f"alter Vd dc = {s * 0.9:g}", "op"]
        for i in range(len(L_GRID_UM)):
            out.append(f"print i(Vm{i})")
    else:
        out.append(f"dc Vg 0 {s * VDD:g} {s * VGS_STEP:g} "
                   f"Vd 0 {s * VDD:g} {s * VDS_STEP:g}")
        probes = []
        for i in range(len(L_GRID_UM)):
            probes.append(f"i(Vm{i})")
            probes += [f"@m.xm{i}.{inner}[{k}]" for k in PROBE_KEYS]
        out.append("wrdata " + out_name + " " + " ".join(probes))
    out += [".endc", ".end"]
    return "\n".join(out) + "\n"


def parse_wrdata(path, n_vec):
    arr = np.loadtxt(path)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    n = arr.shape[1]
    if n == n_vec + 1:
        return arr
    if n == 2 * n_vec:
        out = np.empty((arr.shape[0], n_vec + 1))
        out[:, 0] = arr[:, 0]
        for i in range(n_vec):
            out[:, i + 1] = arr[:, 2 * i + 1]
        return out
    raise ValueError(f"wrdata 컬럼 {n} 해석 불가 (기대 {n_vec+1} 또는 {2*n_vec})")


# ────────────────────────── preflight ──────────────────────────
def preflight(dev="nfet_01v8", w_um=1.0, vsb=0.0):
    """
    덱 하나만 돌려 각 컬럼이 실제로 변하는지 본다.
    v3 사고(스칼라 브로드캐스트)를 30초에 잡아내는 게이트다.
    """
    inner = detect_inner(dev) or ("m" + DEVICES[dev]["model"])
    n_vec = len(L_GRID_UM) * (1 + len(PROBE_KEYS))
    out_n, out_p = "_pf.txt", os.path.join(GEN_DIR, "_pf.txt")
    if os.path.exists(out_p):
        os.remove(out_p)

    print("=" * 72)
    print(f"preflight  dev={dev} W={w_um} VSB={vsb}  내부명={inner}")
    print("=" * 72)
    _, txt = run_ngspice(multi_L_deck(dev, w_um, vsb, inner, "dc", out_n), "_pf")
    if not os.path.exists(out_p):
        print("wrdata 미생성:\n" + txt[-1500:])
        return False

    raw = parse_wrdata(out_p, n_vec)
    nG = int(round(VDD / VGS_STEP)) + 1
    nD = int(round(VDD / VDS_STEP)) + 1
    print(f"  행 {raw.shape[0]} (기대 {nG*nD})   열 {raw.shape[1]} (기대 {n_vec+1})")
    print(f"\n  {'L(um)':>7} " + "".join("%9s" % v for v in VARS))
    print("  " + "-" * 88)
    ok = True
    for i, Lu in enumerate(L_GRID_UM):
        base = 1 + i * (1 + len(PROBE_KEYS))
        row = "  %7g " % Lu
        for c, k in enumerate(VARS):
            col = raw[:, base + c]
            span = float(np.ptp(col))
            const = span == 0.0
            if const and k in ("GM", "GDS", "CGG", "VDSAT"):
                ok = False
            row += "%9s" % ("상수!" if const else "변함")
        print(row)
    os.remove(out_p)

    if ok:
        print("\n  → 통과. 모든 파라미터가 벡터로 기록되고 있다.")
    else:
        print("\n  ★ 실패: 상수 열이 있다 = `.save` 가 먹지 않았다.")
        print("    ngspice 버전에 따라 `.save` 대신 `.control` 안의 `save` 가 필요할 수 있다.")
        print("    본 스윕을 돌리지 말 것.")
    return ok


# ────────────────────────── 프로브 ──────────────────────────
def probe_bins():
    print("=" * 72)
    print(f"L × W 유효성   {CORNER}/{TEMP_C} C, VGS=VDS=0.9")
    print("=" * 72)
    ok_all = True
    for dev in DEVICES:
        inner = detect_inner(dev) or ("m" + DEVICES[dev]["model"])
        print(f"\n[{dev}]  내부 인스턴스명: {inner}")
        print("   %-7s" % "W\\L" + "".join("%11s" % L for L in L_GRID_UM))
        for w in W_GRID_UM:
            _, txt = run_ngspice(multi_L_deck(dev, w, 0.0, inner, "op"), "_probe")
            ids = {}
            for ln in txt.splitlines():
                m = re.search(r"i\(vm(\d+)\)\s*=\s*([-\d.eE+]+)", ln, re.I)
                if m:
                    ids[int(m.group(1))] = abs(float(m.group(2)))
            row = "   %-7g" % w
            for i in range(len(L_GRID_UM)):
                v = ids.get(i)
                if v is None or v < 1e-12:
                    row += "%11s" % "✗"
                    ok_all = False
                else:
                    row += "%10.2fu" % (v * 1e6)
            print(row)
    print("\n판정:", "전 (W,L) 유효" if ok_all else "★ ✗ 조합을 격자에서 제외할 것")
    return ok_all


# ────────────────────────── 감사 ──────────────────────────
def audit(dev, tables, ax):
    bad = []
    print("\n  [부호 감사]")
    for k in VARS:
        a = tables[k]
        thr = -SIGN_NOISE_REL * float(np.max(np.abs(a))) if a.size else 0.0
        n_sig, n_neg = int((a < thr).sum()), int((a < 0).sum())
        flag = ""
        if k in MUST_BE_POSITIVE and n_sig > 0:
            flag = "  ← 부호 오류"
            bad.append(k)
        elif k in MUST_BE_POSITIVE and n_neg > 0:
            flag = "  (먼지, 정상)"
        print("    %-6s min=%12.4e max=%12.4e  neg=%8d  유의미=%8d%s"
              % (k, a.min(), a.max(), n_neg, n_sig, flag))

    cgg, tot = tables["CGG"], tables["CGS"] + tables["CGD"] + tables["CGB"]
    with np.errstate(divide="ignore", invalid="ignore"):
        err = np.abs(cgg - tot) / np.where(cgg > 0, cgg, np.nan)
    worst = float(np.nanmax(err)) * 100.0
    print("    전하보존 최대 오차 = %.4f %%" % worst)
    if worst > 3.0:
        bad.append("charge")

    # ★ v4 신설: 스칼라 브로드캐스트 검출.
    #   전하보존은 상수여도 통과하므로 이 게이트가 따로 있어야 한다.
    print("\n  [변동성 감사]  VDS≈0.9 단면에서 VGS 축을 따라 변해야 한다")
    iD = int(np.argmin(np.abs(ax["VDS"] - 0.9)))
    for k in ("GM", "GDS", "CGG", "VDSAT"):
        span = np.ptp(tables[k][:, :, :, iD, :], axis=2)     # (W,L,VSB)
        n_flat = int((span == 0).sum())
        print("    %-6s 상수 단면 %d / %d" % (k, n_flat, span.size))
        if n_flat:
            bad.append(k + "(상수)")

    if bad:
        print("\n  ★ 감사 실패: %s" % ", ".join(bad))
        print("    상수 항목이 있으면 `.save` 가 먹지 않은 것이다 — --preflight 로 확인.")
        print("    부호 항목이면 SIGN['%s'] 계수를 뒤집을 것." % dev)
        print("    (자동 보정하지 않는다 — 조용한 보정이 과거 사고의 원인이었다)")
        raise SystemExit(1)
    print("    → 통과")


# ────────────────────────── 본 스윕 ──────────────────────────
def sweep(dev):
    ax = make_axes()
    nW, nL, nG, nD, nB = (len(ax["W"]), len(ax["L"]), len(ax["VGS"]),
                          len(ax["VDS"]), len(ax["VSB"]))
    inner = detect_inner(dev) or ("m" + DEVICES[dev]["model"])

    print("=" * 72)
    print("%s  스윕   형상 (W,L,VGS,VDS,VSB) = (%d,%d,%d,%d,%d) = %s 점"
          % (dev, nW, nL, nG, nD, nB, f"{nW*nL*nG*nD*nB:,}"))
    print("  nf=1, m=1, %s/%d C, geometry 생략(PDK 기본값)" % (CORNER, TEMP_C))
    print("  내부 인스턴스명: %s   ngspice 호출 %d 회" % (inner, nW * nB))
    print("=" * 72)

    tables = {k: np.zeros((nW, nL, nG, nD, nB)) for k in VARS}
    n_vec = nL * (1 + len(PROBE_KEYS))
    out_n = "_sw_%s.txt" % dev
    out_p = os.path.join(GEN_DIR, out_n)
    t0, step, total = time.time(), 0, nW * nB

    for iw, w_m in enumerate(ax["W"]):
        w_um = round(w_m * 1e6, 4)
        for j, vsb in enumerate(ax["VSB"]):
            step += 1
            if os.path.exists(out_p):
                os.remove(out_p)
            _, txt = run_ngspice(
                multi_L_deck(dev, w_um, vsb, inner, "dc", out_n), "_sw_%s" % dev)
            if not os.path.exists(out_p):
                print("\n실패: W=%s VSB=%s 에서 wrdata 미생성" % (w_um, vsb))
                print(txt[-2000:])
                raise SystemExit(1)

            raw = parse_wrdata(out_p, n_vec)
            if raw.shape[0] != nG * nD:
                print("\n실패: 행 %d ≠ 기대 %d (W=%s VSB=%s)"
                      % (raw.shape[0], nG * nD, w_um, vsb))
                raise SystemExit(1)

            for i in range(nL):
                base = 1 + i * (1 + len(PROBE_KEYS))
                for c, k in enumerate(VARS):
                    blk = raw[:, base + c].reshape(nD, nG) * SIGN[dev][k]
                    tables[k][iw, i, :, :, j] = blk.T

            el = time.time() - t0
            pct = 100.0 * step / total
            print("\r  [%-20s] %5.1f%%  W=%-6s VSB=%-4s  경과 %02dm%02ds"
                  % ("█" * int(pct / 5), pct, w_um, vsb, el // 60, el % 60),
                  end="", flush=True)
    print()

    audit(dev, tables, ax)

    data = {a: ax[a] for a in ("W", "L", "VGS", "VDS", "VSB")}
    data.update(tables)
    data["_META"] = dict(
        device=DEVICES[dev]["model"], corner=CORNER, temp_C=TEMP_C,
        nf=1, m=1, vdd=VDD, inner=inner, dims="(W, L, VGS, VDS, VSB)",
        scale_rule="실소자 = LUT(W_grid, ...) × m   (W 나눗셈 없음 — W는 축이다)",
        w_interp="금지. W는 이산 축이다 (thin-ox는 폭 평탄역이 없다)",
        geometry="ad/as/pd/ps/nrd/nrs 생략 (PDK 기본값)",
        cap_note="용량은 intrinsic 전용. 실효값 = LUT + W*CGDO (+ 프린지)",
        generated=time.strftime("%Y-%m-%d %H:%M:%S"),
        script=os.path.basename(__file__), version="v4 (.save fix)")

    os.makedirs(DATA_DIR, exist_ok=True)
    pkl = os.path.join(DATA_DIR, "%s.pkl" % dev)
    with open(pkl, "wb") as fh:
        pickle.dump(data, fh)
    for f in os.listdir(GEN_DIR):
        if f.startswith(("_sw_", "_probe", "_inner", "_pf")):
            os.remove(os.path.join(GEN_DIR, f))

    el = time.time() - t0
    print("  저장: %s  (%.1f MB, %02dm%02ds)"
          % (pkl, os.path.getsize(pkl) / 1e6, el // 60, el % 60))
    return pkl


def main():
    ap = argparse.ArgumentParser(description="thin-ox 01v8 gm/Id LUT 생성기 v4")
    ap.add_argument("--device", choices=list(DEVICES) + ["both"], default="both")
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--probe-bins", action="store_true")
    a = ap.parse_args()

    if a.preflight:
        ok = True
        for dev in (list(DEVICES) if a.device == "both" else [a.device]):
            ok &= preflight(dev)
            print()
        raise SystemExit(0 if ok else 1)
    if a.probe_bins:
        raise SystemExit(0 if probe_bins() else 1)
    for dev in (list(DEVICES) if a.device == "both" else [a.device]):
        sweep(dev)
        print()
    print("완료. 다음: lookup.py 5D 확장 → 앵커 대조 검증")


if __name__ == "__main__":
    main()
