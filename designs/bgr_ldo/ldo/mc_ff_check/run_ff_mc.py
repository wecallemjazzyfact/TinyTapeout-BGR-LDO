#!/usr/bin/env python3
"""ff_mm/27C VDDC saturation check.
N개 샘플, 코드 0/15(극단)만 돌려 스팬 밖으로 나가는 샘플 비율을 본다.
목적: A안(스팬 불변) vs B안(스팬 확장) 판단용 스크리닝. DNL/정밀 sigma 는 아님.
"""
import subprocess, re, json, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

PDK_LIB = Path("/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice")
LDO_PEX = Path("/foss/designs/designs/bgr_ldo/layout/ldo_top/ldo_top_pex_rc_safe.spice")  # 실제 경로로 교체
OUT = Path("/foss/designs/designs/bgr_ldo/ldo/mc_ff_check")
CORNER = "ff_mm"
TEMP_C = 27.0
N = 60
SEED_START = 5001

# TRIM 값 (BGR 내부 정의, code=15-ui_in). code0/15 만 본다.
CODES = {0: [0,0,0,0], 15: [1,1,1,1]}   # bit0..3, TRIM=1 -> segment shorted

def build_deck(code_bits, seed):
    t0,t1,t2,t3 = [1.8 if b else 0.0 for b in code_bits]
    return f"""* ff_mm VDDC saturation check  seed={seed} code_bits={code_bits}
.include {LDO_PEX}
.lib {PDK_LIB} {CORNER}

.temp {TEMP_C:g}
VAPWR VAPWR 0 3.3
VTRIM0 TRIM0 0 {t0:g}
VTRIM1 TRIM1 0 {t1:g}
VTRIM2 TRIM2 0 {t2:g}
VTRIM3 TRIM3 0 {t3:g}
* SNK_EN / RO_EN / 부하 등 실제 ldo_top TB 조건에 맞춰 추가할 것
VSNK SNK_EN 0 1.8
VRO  RO_EN  0 0

.op
.control
setseed {seed}
option seedinfo
run
echo RESULT {{v(vddc)}}
.endc
.end
"""

def run_one(seed):
    row = {"seed": seed}
    for label, bits in CODES.items():
        case_dir = OUT / f"s{seed:05d}_c{label:02d}"
        case_dir.mkdir(parents=True, exist_ok=True)
        deck = case_dir / "run.spice"
        deck.write_text(build_deck(bits, seed))
        try:
            r = subprocess.run(["ngspice", "-b", str(deck)],
                                capture_output=True, text=True, timeout=120)
            m = re.search(r"RESULT\s+([-\d.eE+]+)", r.stdout)
            row[f"vddc_code{label}"] = float(m.group(1)) if m else None
            if m is None:
                row.setdefault("errors", []).append(f"code{label}: no match")
        except Exception as e:
            row[f"vddc_code{label}"] = None
            row.setdefault("errors", []).append(f"code{label}: {e}")
    return row

def main():
    seeds = list(range(SEED_START, SEED_START + N))
    rows = []
    with ProcessPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(run_one, s): s for s in seeds}
        for i, f in enumerate(as_completed(futs), 1):
            row = f.result()
            rows.append(row)
            print(f"[{i}/{N}] seed={row[\x27seed\x27]} "
                  f"code0={row.get(\x27vddc_code0\x27)} code15={row.get(\x27vddc_code15\x27)}",
                  flush=True)

    (OUT / "raw.json").write_text(json.dumps(rows, indent=2))

    lo, hi = 1.671, 1.929  # 4-bit 스팬 (code15 / code0 실측으로 교체 권장)
    sat_hi = sum(1 for r in rows if r.get("vddc_code0") is not None and r["vddc_code0"] < 1.800 - 0.036)
    sat_lo = sum(1 for r in rows if r.get("vddc_code15") is not None and r["vddc_code15"] > 1.800 + 0.036)
    fail = [r for r in rows if r.get("vddc_code0") is None or r.get("vddc_code15") is None]

    print("\\n=== ff_mm/27C 스크리닝 요약 ===")
    print(f"  N = {len(rows)} (요청 {N})")
    print(f"  code0(TRIM=0000, V최대)이 1.764V 미달 (하단 포화 의심): {sat_hi}")
    print(f"  code15(TRIM=1111, V최소)이 1.836V 초과 (상단 포화 의심): {sat_lo}")
    print(f"  시뮬 실패: {len(fail)}")
    if rows:
        v0 = [r["vddc_code0"] for r in rows if r.get("vddc_code0") is not None]
        v15 = [r["vddc_code15"] for r in rows if r.get("vddc_code15") is not None]
        if v0: print(f"  code0  range: {min(v0):.4f} .. {max(v0):.4f}")
        if v15: print(f"  code15 range: {min(v15):.4f} .. {max(v15):.4f}")

if __name__ == "__main__":
    main()
