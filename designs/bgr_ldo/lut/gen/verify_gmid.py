#!/usr/bin/env python3
"""
gm/Id LUT verification -- pipeline integrity and accuracy.

Pure python: reads data/*.pkl through lookup.py. No ngspice, no PATH dependency.
Designed to stay useful on a BROKEN table: every check reports rather than crashes,
so one run tells you exactly which run_sweep.py lines need patching.

v2 change: the sign gate is noise-tolerant. A correct table still holds numerical
dust at VDS = 0 (nfet ID ~ -7e-22 A against 3.4e-3 A full scale); v1 flagged that
as a sign error. Only negatives past 1e-9 x full scale count now -- which is still
far below the real failure that was found (pfet ID, 99.7% negative at full scale).

SECTIONS
  [0] Grid inventory      -- axis lengths and shape, per device. Grid drift and
                             nfet/pfet asymmetry show up here first.
  [1] Sign audit          -- per-variable min/max, raw negatives vs significant
                             negatives. Names the exact columns to patch.
  [2] Integrity gates     -- charge conservation, ID positivity, monotonicity.
  [3] Grid anchors        -- A1b/A2b (nfet, W=10) and A3 (pfet, W=10). Each bias
                             coordinate is annotated on / interp / EXTRAP so an
                             "impossibly good" result cannot pass unnoticed.
  [4] Real-circuit anchors-- XM3, XM3c, XMtop1 measured on the finished BGR at
                             arbitrary off-grid bias. This is the test that says
                             whether the table can predict a real circuit.
  [5] Reference           -- probe2 pfet, informational only (W=400, default
                             geometry, so a few percent offset is expected).

Every expected value carries its measurement conditions, per project rule 5.
Exit code 0 only if all gating checks pass.
"""

import os
import sys

import numpy as np

GEN_DIR = os.path.dirname(os.path.abspath(__file__))
LUT_DIR = os.path.dirname(GEN_DIR)
if LUT_DIR not in sys.path:
    sys.path.insert(0, LUT_DIR)

import lookup as lut                                            # noqa: E402

FAILURES = []
NOTES = []


# ----------------------------------------------------------------------------
# expected values -- all tt / 27 C
# ----------------------------------------------------------------------------
# A1b / A2b : nfet L=2 um, W=10 um. ID/GM/GDS independently re-measured with
#             wscale.sp (W = 4/10/20/40 at the same bias). VT/VDSAT/ID(A2b) come
#             from the W=10 characterisation run and are marked [unconfirmed]
#             until re-measured -- see gen/a1b_remeasure.sp.
# NOTE      : 02_LUT_anchor.md A1 is the SAME bias at W = 4 um. Its gds
#             (12.238 nS/um) differs by ~42% because W = 4 sits in a different
#             model bin (edge near W ~ 5 um, measured). Both numbers are correct
#             for their own width; do not "reconcile" them.
A1B = dict(dev='nfet', L=2e-6, VGS=0.92, VDS=1.0, VSB=0.0, W=10.0,
           ID=5.345498e-06, GM=6.291698e-05, GDS=7.120622e-08,
           VT=0.79761, VDSAT=0.12069)
A2B = dict(dev='nfet', L=2e-6, VGS=0.92, VDS=1.0, VSB=0.78, W=10.0,
           ID=4.1130e-08, VT=1.06896, DVT=0.27135)

# A3 : pfet L=2 um, W=10 um -- 02_LUT_anchor.md / bgr/anchor_p1.spice.
#      Same width as the table, so this is the strictest direct anchor.
A3 = dict(dev='pfet', L=2e-6, VGS=1.176, VDS=1.0, VSB=0.0, W=10.0,
          ID=3.0009e-06, GM=30.312e-06, GDS=172.18e-09,
          VT=1.02434, VDSAT=0.15956)

# Real-circuit anchors: ngspice .op on the finished BGR (bgr_core_tb.spice,
# VAPWR = 3.3 V, tt, 27 C). Bias values are the solved operating point, so every
# coordinate is off-grid -- this measures interpolation quality in real use.
# ngspice [id] already includes m, hence scale = (W/10) * m.
BGR = [
    dict(tag='XM3    nfet W20/L4 m2', dev='nfet', L=4e-6, W=20.0, m=2,
         VGS=1.190078, VDS=0.4381737, VSB=0.778899,
         ID=1.025296e-05, GM=1.304483e-04, GDS=5.977988e-07, CGG=3.355136e-13),
    dict(tag='XM3c   nfet W10/L2 m2', dev='nfet', L=2e-6, W=10.0, m=2,
         VGS=1.299742, VDS=0.7517368, VSB=1.21717,
         ID=1.025296e-05, GM=1.327897e-04, GDS=2.174945e-07, CGG=8.026672e-14),
    dict(tag='XMtop1 pfet W20/L4 m4', dev='pfet', L=4e-6, W=20.0, m=4,
         VGS=1.176203, VDS=0.3011255, VSB=5.60124e-05,
         ID=1.025294e-05, GM=1.126772e-04, GDS=9.622210e-07, CGG=5.127140e-13),
]

# probe2: pfet W=400/L=0.5, DEFAULT geometry, normalised per um. Informational:
# both width and geometry differ from the sweep deck, so a few percent offset is
# expected. pfraw.sp at the same bias but W=10 gave 7.7878 uA/um / 37.024 uS/um /
# 1.4345 uS/um / 0.81772 fF/um / vdsat 0.28969 -- closer to the table, as it should be.
PROBE2 = dict(dev='pfet', L=0.5e-6, VGS=1.3, VDS=1.5, VSB=0.0,
              ID_W=7.646, GM_W=37.18, GDS_W=1.4537, CGG_W=0.8154, VDSAT=0.2825)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def hdr(text):
    print('\n' + '=' * 74)
    print(text)
    print('=' * 74)


def sub(text):
    print('\n--- %s ---' % text)


def where(dev, **bias):
    """Annotate each bias coordinate as on-grid / interpolated / extrapolated."""
    try:
        ax = lut.axes(dev)
    except Exception:                                           # noqa: BLE001
        return '(axes unavailable)'
    out = []
    for name in ('L', 'VGS', 'VDS', 'VSB'):
        if name not in bias:
            continue
        g = ax[name]
        v = float(bias[name])
        if v < g.min() - 1e-12 or v > g.max() + 1e-12:
            tag = 'EXTRAP'
        elif np.any(np.isclose(g, v, rtol=0.0, atol=1e-9)):
            tag = 'on'
        else:
            tag = 'interp'
        out.append('%s=%g[%s]' % (name, v, tag))
    return '  '.join(out)


def idx(dev, axis, value):
    g = lut.axes(dev)[axis]
    return int(np.argmin(np.abs(g - value)))


def chk(name, got, exp, tol_pct=2.0, tol_abs=None, unit='', gate=True, extra=''):
    """Compare and record. got=None means the lookup itself failed."""
    if got is None:
        print('  %-26s | %-30s | %s' % (name, 'LOOKUP FAILED', extra))
        if gate:
            FAILURES.append(name)
        return False
    got = float(np.asarray(got).ravel()[0])
    err = got - exp
    pct = (err / exp * 100.0) if exp != 0 else float('nan')
    ok = abs(pct) <= tol_pct
    if tol_abs is not None and abs(err) <= tol_abs:
        ok = True
    if ok:
        status = 'PASS'
    elif gate:
        status = 'FAIL'
        FAILURES.append(name)
    else:
        status = 'note'
        NOTES.append(name)
    print('  %-26s | got %12.5g | exp %12.5g | %+8.2f%% | %-4s %s%s'
          % (name, got, exp, pct, status, unit, extra))
    return ok


def get(dev, var, **bias):
    """lookup() that returns None instead of raising, printing the reason once."""
    try:
        return lut.lookup(dev, var, **bias)
    except Exception as exc:                                    # noqa: BLE001
        msg = str(exc).split('\n')[0]
        if len(msg) > 96:
            msg = msg[:96] + '...'
        print('    ! %s %s -> %s: %s' % (dev, var, type(exc).__name__, msg))
        return None


# ----------------------------------------------------------------------------
# [0] grid inventory
# ----------------------------------------------------------------------------
hdr('gm/Id LUT verification  (tt, 27 C, tables characterised at W = 10 um)')

sub('[0] grid inventory')
shapes = {}
for dev in ('nfet', 'pfet'):
    try:
        rep = lut.audit(dev)
    except Exception as exc:                                    # noqa: BLE001
        print('  %s: NOT LOADED -- %s' % (dev, exc))
        FAILURES.append('%s table load' % dev)
        continue
    ax = lut.axes(dev)
    n = rep['_axis_len']
    expect = n['L'] * n['VGS'] * n['VDS'] * n['VSB']
    shape = rep['_shape']
    size = int(np.prod(shape))
    shapes[dev] = shape
    print('  %s  shape=%s  elements=%d  (L*VGS*VDS*VSB=%d) %s'
          % (dev, shape, size, expect, 'OK' if size == expect else 'MISMATCH'))
    print('       L   (%2d): %s' % (n['L'], np.array2string(ax['L'] * 1e6, precision=2)))
    print('       VSB (%2d): %s' % (n['VSB'], np.array2string(ax['VSB'], precision=3)))
    print('       VDS (%2d): %.3f .. %.3f  step~%.4f'
          % (n['VDS'], ax['VDS'].min(), ax['VDS'].max(),
             np.median(np.diff(ax['VDS'])) if n['VDS'] > 1 else 0.0))
    print('       VGS (%2d): %.3f .. %.3f  step~%.4f'
          % (n['VGS'], ax['VGS'].min(), ax['VGS'].max(),
             np.median(np.diff(ax['VGS'])) if n['VGS'] > 1 else 0.0))
    if size != expect:
        FAILURES.append('%s shape' % dev)

if len(shapes) < 2:
    print('\nTables missing -- run gen/run_sweep.py first. Aborting.')
    sys.exit(1)

if shapes['nfet'] != shapes['pfet']:
    print('\n  note: nfet and pfet grids differ %s vs %s. Not an error -- anchor '
          'points were inserted for one device only. Off-grid anchors below will '
          'show [interp]; judge them on their measured error, not on grid parity.'
          % (shapes['nfet'], shapes['pfet']))


# ----------------------------------------------------------------------------
# [1] sign audit -- names the broken columns
# ----------------------------------------------------------------------------
sub('[1] sign audit  (ID/VT/VDSAT/GM/GDS/CGG >= 0 ; caps stay signed ; '
    'dust below %g x full scale ignored)' % lut.SIGN_NOISE_REL)
SHOULD_BE_POS = ('ID', 'VT', 'VDSAT', 'GM', 'GDS', 'CGG')
patch_hint = []
for dev in ('nfet', 'pfet'):
    rep = lut.audit(dev)
    print('  [%s]' % dev)
    for key in ('ID', 'VT', 'VDSAT', 'GM', 'GDS', 'CGG', 'CGS', 'CGD', 'CGB'):
        if key not in rep:
            continue
        r = rep[key]
        flag = ''
        if key in SHOULD_BE_POS and r['n_sig_neg'] > 0:
            flag = '  <== SIGN ERROR'
            patch_hint.append((dev, key, 100.0 * r['n_sig_neg'] / r['size']))
        elif key in SHOULD_BE_POS and r['n_neg'] > 0:
            flag = '  (dust only, ok)'
        print('    %-6s min=%12.4e  max=%12.4e  neg=%7d  significant=%7d%s'
              % (key, r['min'], r['max'], r['n_neg'], r['n_sig_neg'], flag))

if patch_hint:
    print('\n  >> patch gen/run_sweep.py -- flip sign_factor for:')
    for dev, key, frac in patch_hint:
        arr = 'pch' if dev == 'pfet' else 'nch'
        print("       %s %-6s (%.1f%% significant)   %s['%s'] sign_factor 1.0 -> -1.0"
              % (dev, key, frac, arr, key))
    FAILURES.append('sign convention')


# ----------------------------------------------------------------------------
# [2] integrity gates
# ----------------------------------------------------------------------------
sub('[2] integrity gates')

for dev, bias in (('nfet', dict(L=2e-6, VGS=0.925, VDS=1.0, VSB=0.0)),
                  ('pfet', dict(L=2e-6, VGS=1.175, VDS=1.0, VSB=0.0))):
    d = lut.table(dev)
    i = idx(dev, 'L', bias['L'])
    j = idx(dev, 'VGS', bias['VGS'])
    k = idx(dev, 'VDS', bias['VDS'])
    b = idx(dev, 'VSB', bias['VSB'])
    ax = lut.axes(dev)
    cgg = float(d['CGG'][i, j, k, b])
    tot = float(d['CGS'][i, j, k, b] + d['CGD'][i, j, k, b] + d['CGB'][i, j, k, b])
    err = abs(cgg - tot) / abs(cgg) if cgg else float('inf')
    ok = err < 0.03
    if not ok:
        FAILURES.append('%s charge conservation' % dev)
    print('  %s charge conservation  L=%.1fu VGS=%.3f VDS=%.2f VSB=%.2f -> %.3f%%  %s'
          % (dev, ax['L'][i] * 1e6, ax['VGS'][j], ax['VDS'][k], ax['VSB'][b],
             err * 100.0, 'PASS' if ok else 'FAIL'))

for dev in ('nfet', 'pfet'):
    a = np.asarray(lut.table(dev)['ID'], dtype=float)
    vds = lut.axes(dev)['VDS']
    k0 = 1 if abs(vds[0]) < 1e-12 else 0
    sub_a = a[:, :, k0:, :]
    n_bad, mn, thr = lut.sign_violation(sub_a)
    ok = n_bad == 0
    if not ok:
        FAILURES.append('%s ID positive' % dev)
    print('  %s ID positive (VDS>0)                              -> %s  (min %.3e)'
          % (dev, 'PASS' if ok else 'FAIL', mn))

for dev in ('nfet', 'pfet'):
    a = np.asarray(lut.table(dev)['ID'], dtype=float)
    dif = np.diff(a, axis=1)
    tol = -lut.SIGN_NOISE_REL * float(np.max(np.abs(a)))
    ok = bool(np.all(dif >= tol))
    if not ok:
        FAILURES.append('%s ID monotonic in VGS' % dev)
    frac = 100.0 * float((dif < tol).sum()) / dif.size
    print('  %s ID increasing with VGS                           -> %s  (%.2f%% violate)'
          % (dev, 'PASS' if ok else 'FAIL', frac))

for dev in ('nfet', 'pfet'):
    a = np.asarray(lut.table(dev)['VT'], dtype=float)
    dif = np.diff(a, axis=3)
    ok = bool(np.all(dif >= -1e-9))
    if not ok:
        FAILURES.append('%s VT monotonic in VSB' % dev)
    print('  %s VT increasing with VSB (body effect)             -> %s'
          % (dev, 'PASS' if ok else 'FAIL'))


# ----------------------------------------------------------------------------
# [3] grid anchors
# ----------------------------------------------------------------------------
sub('[3] grid anchors  (values are for W = 10 um, m = 1)')

a = A1B
print('\n [A1b] nfet L=2u W=10u  %s' % where('nfet', L=a['L'], VGS=a['VGS'],
                                             VDS=a['VDS'], VSB=a['VSB']))
bias = dict(L=a['L'], VGS=a['VGS'], VDS=a['VDS'], VSB=a['VSB'])
a1_id = get('nfet', 'ID', **bias)
a1_gm = get('nfet', 'GM', **bias)
a1_gds = get('nfet', 'GDS', **bias)
a1_vt = get('nfet', 'VT', **bias)
chk('ID   (A)', a1_id, a['ID'], 2.0)
chk('GM   (S)', a1_gm, a['GM'], 2.0)
chk('GDS  (S)', a1_gds, a['GDS'], 2.0)
if a1_gm is not None and a1_id not in (None, 0):
    chk('gm/Id (1/V)', float(a1_gm) / float(a1_id), a['GM'] / a['ID'], 2.0)
if a1_gm is not None and a1_gds not in (None, 0):
    chk('gm/gds', float(a1_gm) / float(a1_gds), a['GM'] / a['GDS'], 2.0)
chk('VT   (V)', a1_vt, a['VT'], 2.0, tol_abs=0.010, extra='[unconfirmed]')
chk('VDSAT(V)', get('nfet', 'VDSAT', **bias), a['VDSAT'], 2.0, tol_abs=0.010,
    extra='[unconfirmed]')

a = A2B
print('\n [A2b] nfet L=2u W=10u VSB=0.78 (body-effect axis)  %s'
      % where('nfet', L=a['L'], VGS=a['VGS'], VDS=a['VDS'], VSB=a['VSB']))
bias = dict(L=a['L'], VGS=a['VGS'], VDS=a['VDS'], VSB=a['VSB'])
a2_id = get('nfet', 'ID', **bias)
a2_vt = get('nfet', 'VT', **bias)
chk('ID   (A) [log-interp]', a2_id, a['ID'], 3.0, extra='[unconfirmed]')
chk('VT   (V)', a2_vt, a['VT'], 2.0, tol_abs=0.010, extra='[unconfirmed]')
if a2_vt is not None and a1_vt is not None:
    chk('dVT A1b->A2b (V)', float(a2_vt) - float(a1_vt), a['DVT'], 5.0, tol_abs=0.015)

a = A3
print('\n [A3 ] pfet L=2u W=10u  (same width as the table -> strictest anchor)  %s'
      % where('pfet', L=a['L'], VGS=a['VGS'], VDS=a['VDS'], VSB=a['VSB']))
bias = dict(L=a['L'], VGS=a['VGS'], VDS=a['VDS'], VSB=a['VSB'])
a3_id = get('pfet', 'ID', **bias)
a3_gm = get('pfet', 'GM', **bias)
a3_gds = get('pfet', 'GDS', **bias)
chk('ID   (A)', a3_id, a['ID'], 2.0)
chk('GM   (S)', a3_gm, a['GM'], 2.0)
chk('GDS  (S)', a3_gds, a['GDS'], 2.0)
if a3_gm is not None and a3_id not in (None, 0):
    chk('gm/Id (1/V)', float(a3_gm) / float(a3_id), a['GM'] / a['ID'], 2.0)
if a3_gm is not None and a3_gds not in (None, 0):
    chk('gm/gds', float(a3_gm) / float(a3_gds), a['GM'] / a['GDS'], 2.0)
chk('VT   (V)', get('pfet', 'VT', **bias), a['VT'], 2.0, tol_abs=0.010)
chk('VDSAT(V)', get('pfet', 'VDSAT', **bias), a['VDSAT'], 2.0, tol_abs=0.010)


# ----------------------------------------------------------------------------
# [4] real-circuit anchors
# ----------------------------------------------------------------------------
sub('[4] real-circuit anchors  (BGR .op, tt/27, VAPWR=3.3 -- all bias off-grid)')
print('    predicted = lookup * (W/10) * m ; ngspice [id] already includes m')

for c in BGR:
    scale = (c['W'] / 10.0) * c['m']
    print('\n [%s]  scale=%g' % (c['tag'], scale))
    print('    %s' % where(c['dev'], L=c['L'], VGS=c['VGS'], VDS=c['VDS'], VSB=c['VSB']))
    bias = dict(L=c['L'], VGS=c['VGS'], VDS=c['VDS'], VSB=c['VSB'])
    for var, tol, gate in (('ID', 5.0, True), ('GM', 5.0, True),
                           ('CGG', 10.0, True), ('GDS', 15.0, False)):
        v = get(c['dev'], var, **bias)
        chk('%-4s (scaled)' % var, None if v is None else float(v) * scale,
            c[var], tol, gate=gate)


# ----------------------------------------------------------------------------
# [5] reference anchor
# ----------------------------------------------------------------------------
sub('[5] reference anchor  (informational -- probe2 used W=400, default geometry)')
p = PROBE2
bias = dict(L=p['L'], VGS=p['VGS'], VDS=p['VDS'], VSB=p['VSB'])
print('    %s' % where('pfet', **bias))
for var, key, mul, unit in (('ID', 'ID_W', 1e6 / 10.0, 'uA/um'),
                            ('GM', 'GM_W', 1e6 / 10.0, 'uS/um'),
                            ('GDS', 'GDS_W', 1e6 / 10.0, 'uS/um'),
                            ('CGG', 'CGG_W', 1e15 / 10.0, 'fF/um')):
    v = get('pfet', var, **bias)
    chk('%s/W' % var, None if v is None else float(v) * mul, p[key],
        5.0, unit=unit, gate=False)
chk('VDSAT (V)', get('pfet', 'VDSAT', **bias), p['VDSAT'], 5.0, tol_abs=0.015,
    gate=False)


# ----------------------------------------------------------------------------
# summary
# ----------------------------------------------------------------------------
hdr('summary')
if NOTES:
    print('  non-gating deviations: %s' % ', '.join(sorted(set(NOTES))))
if FAILURES:
    print('  FAILED gates (%d):' % len(set(FAILURES)))
    for f in sorted(set(FAILURES)):
        print('    - %s' % f)
    print('\n>>> VERIFICATION: FAIL')
    sys.exit(1)

print('  all gating checks passed')
print('\n>>> VERIFICATION: PASS')
sys.exit(0)
