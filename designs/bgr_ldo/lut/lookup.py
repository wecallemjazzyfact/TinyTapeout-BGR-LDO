"""
gm/Id LUT lookup wrapper -- sky130 g5v0d10v5 (TinyTapeout bgr_ldo project)

STORED SIGN CONVENTION (data/*.pkl), identical for nfet and pfet
    ID, VT, VDSAT, GM, GDS, CGG : positive magnitudes
    CGS, CGD, CGB               : SIGNED (raw ngspice value negated once)
        Keeping the caps signed preserves the CGD zero-crossing (CGD legitimately
        changes sign in saturation) and makes CGG == CGS + CGD + CGB usable as a
        checksum on the whole parse/store path.

SIGN CHECKING IS NOISE-TOLERANT (v2)
    A correct table still contains a handful of tiny negatives: at VDS = 0 the
    current is zero and ngspice returns numerical dust (measured: nfet ID has 170
    entries at ~-7e-22 A against a 3.4e-3 A full scale; GM likewise at ~-3e-33 S).
    Those are NOT sign errors. A real sign error looks completely different -- the
    pfet table had 99.7% of ID negative with min = -1.6e-3 A, i.e. full scale.
    So the test is relative: a value only counts as a violation when it is more
    negative than 1e-9 x the largest magnitude in the same array. v1 used
    "any negative at all" and wrongly blocked every nfet ID lookup.

WHAT THIS WRAPPER ADDS ON TOP OF pygmid.Lookup
    * L-axis guard   : interpolating across the non-uniform L grid is refused.
    * log-domain ID  : ID is interpolated as log(ID) and exponentiated back, which
                       is what makes weak/moderate inversion usable at all.
    * NO SILENT REPAIR : a table with a genuine sign violation raises LUTSignError.
                       An earlier version clipped negatives with
                       np.maximum(ID, 1e-25), which turned the pfet sign bug into a
                       plausible-looking 8e-25 and cost a full debug cycle.
    * abs() on caps  : CGS/CGD/CGB are returned as magnitudes AFTER interpolation.

SCALING RULE (validated against the BGR netlist, 2026-07)
    real_device = lookup(...) * (W_um / 10) * m
    ngspice's @m.x<inst>.<model>[id] already includes m, so compare against that.
    Measured agreement on the finished BGR (all bias points off-grid):
        GM  -0.03 .. +0.64 %,  CGG +0.01 .. +0.57 %,  GDS -3.2 .. +9.6 %

DEVICE GEOMETRY LIMIT (measured, tt/27, L=2, VGS=0.92, VDS=1.0)
    gds/W is flat within 1.5% for W >= 5 um but jumps at W = 4 and W = 3
    (12.24 and 19.68 nS/um vs 7.12 at W >= 5) -- a model bin edge near W ~ 5 um.
    Use unit fingers of W >= 5 um, preferably W = 10 um (the table's own width),
    and get area from m. predict() warns when this is violated.

PROJECT RULE: any number out of this module is quotable only together with its
conditions (corner / temp / L / VGS / VDS / VSB / W-normalisation).
"""

import os
import sys

import numpy as np

LUT_DIR = os.path.dirname(os.path.abspath(__file__))
if LUT_DIR not in sys.path:
    sys.path.insert(0, LUT_DIR)

from pygmid import Lookup as lk

__all__ = ['lookup', 'lookupVGS', 'predict', 'table', 'axes', 'audit',
           'sign_violation', 'LUTSignError', 'LUTRangeError',
           'L_GRID', 'W_REF_UM', 'SIGN_NOISE_REL']


class LUTSignError(ValueError):
    """Stored table violates the documented sign convention."""


class LUTRangeError(ValueError):
    """Requested coordinate is not usable on the stored grid."""


L_GRID = (0.5e-6, 1.0e-6, 2.0e-6, 4.0e-6, 8.0e-6, 20.0e-6)
W_REF_UM = 10.0          # every table is characterised at W = 10 um
W_BIN_MIN_UM = 5.0       # below this the gds bin edge makes the table invalid
SIGN_NOISE_REL = 1e-9    # negatives below this x full scale are numerical dust
_ZERO_FLOOR = 1e-18      # stands in for zeros / dust (the VDS = 0 row) in log space

_PKL = {
    'nfet': os.path.join(LUT_DIR, 'data', 'nfet_g5v0d10v5.pkl'),
    'pfet': os.path.join(LUT_DIR, 'data', 'pfet_g5v0d10v5.pkl'),
}
_OBJ = {}
_LOAD_ERR = {}

for _dev, _path in _PKL.items():
    if not os.path.exists(_path):
        _LOAD_ERR[_dev] = 'file not found: %s' % _path
        continue
    try:
        _OBJ[_dev] = lk(_path)
    except Exception as _exc:                                   # noqa: BLE001
        _LOAD_ERR[_dev] = '%s: %s' % (type(_exc).__name__, _exc)


def _obj(device):
    dev = str(device).lower()
    if dev not in _PKL:
        raise ValueError("unknown device %r (expected 'nfet' or 'pfet')" % device)
    if dev not in _OBJ:
        raise RuntimeError('%s table not loaded (%s). Run gen/run_sweep.py first.'
                           % (dev, _LOAD_ERR.get(dev, 'unknown reason')))
    return _OBJ[dev]


def table(device):
    """Raw stored dict (axes + 4-D arrays). For audits and gates, not design use."""
    return _obj(device)._Lookup__DATA


def axes(device):
    """{'L','VGS','VDS','VSB'} -> 1-D numpy arrays, as actually stored."""
    d = table(device)
    return {k: np.asarray(d[k], dtype=float) for k in ('L', 'VGS', 'VDS', 'VSB')}


def sign_violation(arr):
    """
    Count negatives too large to be numerical noise.

    Returns (n_significant, min_value, threshold). A value counts only when it is
    below -SIGN_NOISE_REL * max|arr|, so dust near zero is ignored while a flipped
    array (negatives at full scale) is caught.
    """
    a = np.asarray(arr, dtype=float)
    if a.size == 0:
        return 0, 0.0, 0.0
    thr = -SIGN_NOISE_REL * float(np.max(np.abs(a)))
    return int((a < thr).sum()), float(np.min(a)), thr


def _check_L(kwargs):
    L = kwargs.get('L', kwargs.get('l'))
    if L is None:
        return
    for val in np.atleast_1d(L):
        if not any(np.isclose(val, g, rtol=0.0, atol=1e-9) for g in L_GRID):
            raise LUTRangeError(
                'L = %.4g um is not a grid point (%s um). L interpolation is '
                'prohibited: the L axis is non-uniform and short-channel behaviour '
                'is not linear in L.'
                % (float(val) * 1e6, [g * 1e6 for g in L_GRID]))


def audit(device):
    """Per-variable health report of the stored table. Never raises on bad data."""
    d = table(device)
    rep = {}
    for key in ('ID', 'VT', 'VDSAT', 'GM', 'GDS', 'CGG', 'CGS', 'CGD', 'CGB'):
        if key not in d:
            continue
        a = np.asarray(d[key], dtype=float)
        n_sig, mn, thr = sign_violation(a)
        rep[key] = {
            'min': mn, 'max': float(np.nanmax(a)),
            'n_neg': int((a < 0).sum()), 'n_sig_neg': n_sig, 'thr': thr,
            'n_zero': int((a == 0).sum()), 'n_nan': int(np.isnan(a).sum()),
            'size': int(a.size),
        }
    ax = axes(device)
    rep['_axis_len'] = {k: int(v.size) for k, v in ax.items()}
    rep['_shape'] = tuple(np.asarray(d['ID']).shape)
    return rep


def lookup(device, outvar, log_id=True, **kwargs):
    """
    Interpolate one stored quantity at a bias point.

    device  : 'nfet' | 'pfet'
    outvar  : 'ID','VT','VDSAT','GM','GDS','CGG','CGS','CGD','CGB' (or a pygmid ratio)
    log_id  : interpolate ID in log space (default True). Set False only to inspect
              the raw table -- design numbers should always use the log path.
    kwargs  : L (metres, grid value only), VGS, VDS, VSB (volts, magnitudes)

    Returns the value for a W = 10 um device with m = 1. Use predict() to scale.
    """
    _check_L(kwargs)
    obj = _obj(device)
    var = str(outvar).upper()

    if var == 'ID' and log_id:
        data = table(device)
        orig = data['ID']
        n_bad, mn, thr = sign_violation(orig)
        if n_bad:
            raise LUTSignError(
                '%s ID table holds %d/%d entries below %.3e A (min = %.4e A), far '
                'past numerical noise. The stored convention is positive-magnitude '
                'ID for both devices, so log-domain interpolation is refused. Fix '
                'the sign in gen/run_sweep.py and re-sweep -- do not work around it '
                'here. Pass log_id=False to read the raw table for debugging.'
                % (str(device).lower(), n_bad, orig.size, thr, mn))
        data['ID'] = np.log(np.where(orig > 0.0, orig, _ZERO_FLOOR))
        try:
            res = np.exp(obj.look_up('ID', **kwargs))
        finally:
            data['ID'] = orig
        if np.any(np.asarray(res, dtype=float) <= _ZERO_FLOOR * 10.0):
            sys.stderr.write(
                'Warning: %s ID lookup hit the zero floor at %s -- the point is at '
                'or below VDS = 0.\n' % (device, kwargs))
    else:
        res = obj.look_up(var, **kwargs)

    if var in ('CGS', 'CGD', 'CGB'):
        res = np.abs(res)
    return res


def predict(device, outvar, W_um, m=1, log_id=True, **kwargs):
    """
    Scale a table entry to a real device: value * (W_um / 10) * m.

    Intensive quantities (VT, VDSAT and any ratio containing '_') are returned
    unscaled. Compare the result directly against ngspice
    @m.x<inst>.<model>[...], which already includes m.
    """
    var = str(outvar).upper()
    val = lookup(device, var, log_id=log_id, **kwargs)

    if float(W_um) < W_BIN_MIN_UM:
        sys.stderr.write(
            'Warning: unit W = %.3g um is below the %.3g um bin edge; gds from this '
            'table is not valid there (measured: gds/W jumps ~72%% at W = 4 um). '
            'Split the device into m fingers of W >= 10 um instead.\n'
            % (float(W_um), W_BIN_MIN_UM))

    if var in ('VT', 'VDSAT', 'VGS', 'VDS', 'VSB') or '_' in var:
        return val
    return val * (float(W_um) / W_REF_UM) * float(m)


def lookupVGS(device, **kwargs):
    """VGS for a given GM_ID or ID_W (pygmid look_upVGS)."""
    _check_L(kwargs)
    return _obj(device).look_upVGS(**kwargs)
