import json, glob, os, sys

base_dirs = [
    "designs/bgr_ldo/ldo/real_clamp_mc_ll_mm",
    "/foss/designs/designs/bgr_ldo/ldo/real_clamp_mc_ll_mm",
    "designs/bgr_ldo/ldo/real_clamp_trim_finalize",
    "/foss/designs/designs/bgr_ldo/ldo/real_clamp_trim_finalize",
    "designs/bgr_ldo/ldo/real_clamp_test",
    "/foss/designs/designs/bgr_ldo/ldo/real_clamp_test"
]

checked = set()
for folder in base_dirs:
    real_f = os.path.abspath(folder)
    if real_f in checked or not os.path.exists(folder):
        continue
    checked.add(real_f)
    files = sorted(glob.glob(os.path.join(folder, "seed_*", "selected.json")))
    print(f"\n[{folder}] found {len(files)} files")
    raws = []
    for p in files:
        d = json.load(open(p))
        # pre_trim_vddc 또는 raw_deviation_mV 또는 final_vddc_V
        val = d.get("pre_trim_vddc") or d.get("raw_deviation_mV") or d.get("pre_trim_dev_mV")
        if val is None and "final_vddc_V" in d:
            val = (d["final_vddc_V"] - 1.8) * 1000
        if val is not None:
            raws.append(val)
    print("  n =", len(raws))
    if raws:
        print("  min/max = %.3f / %.3f" % (min(raws), max(raws)))
        half_span = 131.6
        over = [r for r in raws if abs(r) > half_span]
        print("  스팬 이탈(>%.1f mV) 샘플 수 = %d" % (half_span, len(over)))
        print("  이탈 샘플:", sorted(over, key=abs, reverse=True)[:10])

    if files:
        sample = json.load(open(files[0]))
        print("  sample keys:", list(sample.keys()))
        if "final_vddc_V" in sample:
            devs = [(json.load(open(p))["final_vddc_V"] - 1.8) * 1000 for p in files if "final_vddc_V" in json.load(open(p))]
            print(f"  final_vddc deviation (mV): min={min(devs):.2f}, max={max(devs):.2f}")
            half_span = 131.6
            over = [r for r in devs if abs(r) > half_span]
            print(f"  스팬 이탈(>{half_span} mV) 샘플 수 = {len(over)}")
