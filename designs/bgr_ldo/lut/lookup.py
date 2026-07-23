"""
gm/Id LUT 조회 래퍼 — sky130 4소자

    thick-ox (3.3 V 도메인)   nfet       pfet         g5v0d10v5   4D
    thin-ox  (1.8 V 도메인)   nfet_01v8  pfet_01v8    01v8        5D

════════════════════════════════════════════════════════════════
★ 스케일 규칙이 소자군마다 다르다 — 가장 흔한 오용 지점
════════════════════════════════════════════════════════════════
    thick-ox :  실소자 = lookup(...) × (W_um / 10) × m      ← W 로 나눈다
    thin-ox  :  실소자 = lookup(W=격자값, ...) × m           ← W 로 나누지 않는다

thick-ox 는 W ≥ 5 µm 에서 gds/W 가 1.5% 이내로 평탄해 단일 기준폭(W=10 µm)
선형 스케일이 성립한다. **thin-ox 는 그 평탄역이 없다.**
실측 (L=0.15, VGS=VDS=0.9, tt/27):
    nfet_01v8  ID/W  30.85 → 48.95 µA/µm  (W 0.42→10 µm, +59% 단조)
    pfet_01v8  gds/W 3.92 → 7.58          (W 0.42→0.65 µm, +94%, bin 경계)

그래서 thin-ox 는 **W 를 L 과 동일한 이산 축**으로 두고 보간을 금지한다.
`predict()` 가 격자 밖 W 를 받으면 `LUTRangeError` 를 던진다 — 문서로만 적어두면
반드시 누군가 `/10` 을 곱하기 때문이다.

════════════════════════════════════════════════════════════════
저장 부호 규약 (4소자 공통, lut/README.md §4)
════════════════════════════════════════════════════════════════
    ID, VT, VDSAT, GM, GDS, CGG  →  양수 크기
    CGS, CGD, CGB                →  signed 유지
        CGD 는 포화에서 물리적으로 0 을 교차하므로 저장 시 abs() 를 걸면
        보간이 접힌 곡선을 지난다. CGG = CGS+CGD+CGB 전하보존이
        파싱·저장 전 경로의 체크섬으로 작동한다(실측 0.000%).
        abs() 는 **조회 반환 시점에만** 적용한다.

부호 검사는 잡음 허용 상대 임계다: `x < −1e-9 × max|x|` 만 위반으로 센다.
정상 테이블에도 VDS=0 열에 수치 먼지(~1e-35 A)가 남는다. "음수가 하나라도
있으면 오류" 로 판정하면 정상 테이블의 조회를 막는다(실제로 냈던 버그).

════════════════════════════════════════════════════════════════
용량은 intrinsic 전용 (4소자 공통)
════════════════════════════════════════════════════════════════
CGG/CGS/CGD 는 채널 고유 성분만 담으며 **게이트 오버랩을 포함하지 않는다.**
    실효 C_gg = LUT + W × (CGDO + CGSO) + 2 × W × CF
    실효 C_gd = LUT + W × CGDO + W × CF
pfet_g5v0d10v5 모델카드(tt): CGDO = CGSO = 0.194171 fF/µm, CF = 0.012 fF/µm
영향은 1/L 로 커진다 — L=0.5 µm 에서 +47.6%, L=2 µm 에서 +9.3%.
**용량 수치를 인용할 때는 intrinsic / 실효 중 어느 쪽인지 반드시 병기한다.**

════════════════════════════════════════════════════════════════
API
════════════════════════════════════════════════════════════════
    lookup(dev, var, **bias)              단위 소자 값 (thick-ox: W=10 기준)
    predict(dev, var, W_um, m=1, **bias)  실소자 값 (소자군별 스케일 규칙 적용)
    lookupVGS(dev, **kw)                  역조회 (thick-ox 전용)
    axes(dev) / table(dev) / audit(dev)   원시 접근·감사
    describe(dev)                         스케일 규칙과 격자를 사람이 읽는 형태로
"""

import os
import sys

import numpy as np

LUT_DIR = os.path.dirname(os.path.abspath(__file__))
if LUT_DIR not in sys.path:
    sys.path.insert(0, LUT_DIR)

__all__ = ['lookup', 'predict', 'lookupVGS', 'table', 'axes', 'audit',
           'describe', 'sign_violation', 'devices',
           'LUTSignError', 'LUTRangeError', 'DEVICES', 'SIGN_NOISE_REL']


class LUTSignError(ValueError):
    """저장 테이블이 부호 규약을 위반했다."""


class LUTRangeError(ValueError):
    """요청 좌표를 이 격자에서 쓸 수 없다."""


SIGN_NOISE_REL = 1e-9      # 이보다 작은 음수는 수치 먼지
_ZERO_FLOOR = 1e-30        # log 영역에서 0 을 대신하는 값
_CAP_VARS = ('CGS', 'CGD', 'CGB')

# ─────────────────────────── 소자 정의 ───────────────────────────
_L_THICK = (0.5e-6, 1.0e-6, 2.0e-6, 4.0e-6, 8.0e-6, 20.0e-6)
_L_THIN = (0.15e-6, 0.18e-6, 0.25e-6, 0.5e-6, 1.0e-6, 2.0e-6)
_W_THIN = (0.42e-6, 0.65e-6, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6)

DEVICES = {
    'nfet': dict(pkl='nfet_g5v0d10v5.pkl', kind='4d', L=_L_THICK,
                 w_ref_um=10.0, w_min_um=5.0, domain='3.3 V thick-ox'),
    'pfet': dict(pkl='pfet_g5v0d10v5.pkl', kind='4d', L=_L_THICK,
                 w_ref_um=10.0, w_min_um=5.0, domain='3.3 V thick-ox'),
    'nfet_01v8': dict(pkl='nfet_01v8.pkl', kind='5d', L=_L_THIN, W=_W_THIN,
                      domain='1.8 V thin-ox'),
    'pfet_01v8': dict(pkl='pfet_01v8.pkl', kind='5d', L=_L_THIN, W=_W_THIN,
                      domain='1.8 V thin-ox'),
}

_DATA_DIR = os.path.join(LUT_DIR, 'data')
_OBJ, _RAW, _ERR = {}, {}, {}


def _load(dev):
    """지연 로드. thick-ox 는 pygmid.Lookup, thin-ox 는 원시 dict."""
    cfg = DEVICES[dev]
    path = os.path.join(_DATA_DIR, cfg['pkl'])
    if not os.path.exists(path):
        _ERR[dev] = '파일 없음: %s' % path
        return False
    try:
        if cfg['kind'] == '4d':
            from pygmid import Lookup as lk
            _OBJ[dev] = lk(path)
            _RAW[dev] = _OBJ[dev]._Lookup__DATA
        else:
            import pickle
            with open(path, 'rb') as fh:
                _RAW[dev] = pickle.load(fh)
        return True
    except Exception as exc:                                   # noqa: BLE001
        _ERR[dev] = '%s: %s' % (type(exc).__name__, exc)
        return False


def _cfg(device):
    dev = str(device).lower()
    if dev not in DEVICES:
        raise ValueError("알 수 없는 소자 %r. 사용 가능: %s"
                         % (device, ', '.join(DEVICES)))
    if dev not in _RAW and not _load(dev):
        raise RuntimeError('%s 테이블 미로드 (%s). 해당 스윕을 먼저 실행하십시오.'
                           % (dev, _ERR.get(dev, '원인 불명')))
    return dev, DEVICES[dev]


def devices():
    """로드 가능한 소자 목록과 상태."""
    out = {}
    for dev in DEVICES:
        try:
            _cfg(dev)
            out[dev] = 'ok'
        except Exception as exc:                               # noqa: BLE001
            out[dev] = str(exc).split('\n')[0]
    return out


def table(device):
    """원시 저장 dict. 감사·게이트용이며 설계 조회에는 쓰지 않는다."""
    dev, _ = _cfg(device)
    return _RAW[dev]


def axes(device):
    """축 배열 dict. thin-ox 는 'W' 가 추가된다."""
    dev, cfg = _cfg(device)
    d = _RAW[dev]
    keys = ('L', 'VGS', 'VDS', 'VSB')
    if cfg['kind'] == '5d':
        keys = ('W',) + keys
    return {k: np.asarray(d[k], dtype=float) for k in keys}


def sign_violation(arr):
    """(유의미 음수 개수, 최솟값, 임계값). 잡음은 세지 않는다."""
    a = np.asarray(arr, dtype=float)
    if a.size == 0:
        return 0, 0.0, 0.0
    thr = -SIGN_NOISE_REL * float(np.max(np.abs(a)))
    return int((a < thr).sum()), float(np.min(a)), thr


def audit(device):
    """변수별 건강 리포트. 나쁜 데이터에도 예외를 던지지 않는다."""
    dev, cfg = _cfg(device)
    d = _RAW[dev]
    rep = {}
    for k in ('ID', 'VT', 'VDSAT', 'GM', 'GDS', 'CGG', 'CGS', 'CGD', 'CGB'):
        if k not in d:
            continue
        a = np.asarray(d[k], dtype=float)
        n_sig, mn, thr = sign_violation(a)
        rep[k] = dict(min=mn, max=float(np.nanmax(a)),
                      n_neg=int((a < 0).sum()), n_sig_neg=n_sig, thr=thr,
                      n_nan=int(np.isnan(a).sum()), size=int(a.size))
    ax = axes(dev)
    rep['_axis_len'] = {k: int(v.size) for k, v in ax.items()}
    rep['_shape'] = tuple(np.asarray(d['ID']).shape)
    rep['_kind'] = cfg['kind']
    return rep


def describe(device):
    """스케일 규칙과 격자를 출력한다. 오용 방지용."""
    dev, cfg = _cfg(device)
    ax = axes(dev)
    print('%s  (%s, %s)' % (dev, cfg['domain'], cfg['kind'].upper()))
    if cfg['kind'] == '4d':
        print('  스케일: lookup(...) × (W_um / %.0f) × m' % cfg['w_ref_um'])
        print('  유닛 핑거 W ≥ %.0f µm (권장 %.0f). 그 아래는 gds 무효.'
              % (cfg['w_min_um'], cfg['w_ref_um']))
    else:
        print('  스케일: lookup(W=격자값, ...) × m      ← W 로 나누지 않는다')
        print('  W 격자 (보간 금지): %s µm'
              % np.array2string(ax['W'] * 1e6, precision=2))
    print('  L 격자 (보간 금지): %s µm'
          % np.array2string(ax['L'] * 1e6, precision=2))
    print('  VGS %.3f..%.3f (%d) / VDS %.3f..%.3f (%d) / VSB %s'
          % (ax['VGS'].min(), ax['VGS'].max(), ax['VGS'].size,
             ax['VDS'].min(), ax['VDS'].max(), ax['VDS'].size,
             np.array2string(ax['VSB'], precision=2)))
    meta = _RAW[dev].get('_META')
    if meta:
        print('  meta: %s | %s' % (meta.get('version', '?'),
                                   meta.get('generated', '?')))


# ─────────────────────────── 격자 강제 ───────────────────────────
def _grid_index(dev, name, value):
    """격자 정점이 아니면 예외. L 과 (thin-ox 의) W 에 적용된다."""
    grid = np.asarray(DEVICES[dev][name], dtype=float)
    v = float(value)
    hit = np.isclose(grid, v, rtol=0.0, atol=1e-12)
    if not hit.any():
        raise LUTRangeError(
            '%s = %.4g µm 는 %s 격자점이 아닙니다 (%s µm). '
            '보간이 금지된 축입니다 — %s.'
            % (name, v * 1e6, dev,
               np.array2string(grid * 1e6, precision=2),
               'RSCE 로 L 에 비단조' if name == 'L'
               else 'thin-ox 는 폭 평탄역이 없다'))
    return int(np.argmax(hit))


def _check_L(dev, kwargs):
    L = kwargs.get('L', kwargs.get('l'))
    if L is None:
        return
    for v in np.atleast_1d(L):
        _grid_index(dev, 'L', v)


# ─────────────────────────── 조회 ───────────────────────────
def _lookup_4d(dev, var, log_id, kwargs):
    obj = _OBJ[dev]
    if var == 'ID' and log_id:
        data = _RAW[dev]
        orig = data['ID']
        n_bad, mn, thr = sign_violation(orig)
        if n_bad:
            raise LUTSignError(
                '%s ID 테이블에 %.3e A 미만인 항목이 %d/%d 개 (최솟값 %.4e A) 있어 '
                '수치 잡음 범위를 크게 벗어납니다. 저장 규약은 양수 크기이므로 '
                'log 보간을 거부합니다. gen/run_sweep.py 의 부호를 고쳐 재스윕하십시오 '
                '— 여기서 우회하지 마십시오.' % (dev, thr, n_bad, orig.size, mn))
        data['ID'] = np.log(np.where(orig > 0.0, orig, _ZERO_FLOOR))
        try:
            res = np.exp(obj.look_up('ID', **kwargs))
        finally:
            data['ID'] = orig
        return res
    return obj.look_up(var, **kwargs)


def _lookup_5d(dev, var, log_id, W, kwargs):
    from scipy.interpolate import interpn
    d = _RAW[dev]
    if W is None:
        raise LUTRangeError(
            '%s 는 W 가 이산 축이므로 W 인자가 필수입니다. '
            '예: lookup("%s", "ID", W=1e-6, L=0.15e-6, VGS=.9, VDS=.9, VSB=0)'
            % (dev, dev))
    iW = _grid_index(dev, 'W', W)

    arr = np.asarray(d[var], dtype=float)[iW]          # (L, VGS, VDS, VSB)
    if var == 'ID' and log_id:
        n_bad, mn, thr = sign_violation(d['ID'])
        if n_bad:
            raise LUTSignError(
                '%s ID 테이블에 %.3e A 미만인 항목이 %d 개 (최솟값 %.4e A) 있습니다. '
                'gen/run_sweep_01v8.py 의 부호를 고쳐 재스윕하십시오.'
                % (dev, thr, n_bad, mn))
        arr = np.log(np.where(arr > 0.0, arr, _ZERO_FLOOR))

    pts = tuple(np.asarray(d[k], dtype=float) for k in ('L', 'VGS', 'VDS', 'VSB'))
    q = [np.atleast_1d(np.asarray(kwargs[k], dtype=float)).ravel()
         for k in ('L', 'VGS', 'VDS', 'VSB')]
    n = max(len(x) for x in q)
    q = [np.repeat(x, n) if len(x) == 1 else x for x in q]
    if any(len(x) != n for x in q):
        raise ValueError('VGS/VDS/VSB 길이가 서로 맞지 않습니다.')

    res = interpn(pts, arr, np.column_stack(q), method='linear',
                  bounds_error=False, fill_value=None)
    if var == 'ID' and log_id:
        res = np.exp(res)
    return res[0] if n == 1 else res


def lookup(device, outvar, log_id=True, W=None, **kwargs):
    """
    한 바이어스 점의 저장량을 조회한다.

    device  : 'nfet' | 'pfet' | 'nfet_01v8' | 'pfet_01v8'
    outvar  : 'ID','VT','VDSAT','GM','GDS','CGG','CGS','CGD','CGB'
    log_id  : ID 를 log 영역에서 보간 (기본 True). 약반전에서 필수.
              False 는 원시 테이블 확인용이며 설계 수치에는 쓰지 않는다.
    W       : **thin-ox 전용, 필수.** 격자값만 허용 (미터 단위).
    kwargs  : L (미터, 격자값만), VGS, VDS, VSB (볼트, 크기)

    반환은 thick-ox 면 W=10 µm / m=1 기준값, thin-ox 면 그 W 의 m=1 값이다.
    실소자로 스케일하려면 predict() 를 쓸 것.
    """
    dev, cfg = _cfg(device)
    var = str(outvar).upper()
    _check_L(dev, kwargs)

    if cfg['kind'] == '4d':
        if W is not None:
            sys.stderr.write(
                '경고: %s 는 4D 테이블이라 W 인자를 무시합니다. '
                '폭 스케일은 predict() 가 처리합니다.\n' % dev)
        res = _lookup_4d(dev, var, log_id, kwargs)
    else:
        res = _lookup_5d(dev, var, log_id, W, kwargs)

    if var in _CAP_VARS:
        res = np.abs(res)
    return res


def predict(device, outvar, W_um, m=1, log_id=True, **kwargs):
    """
    실소자 값으로 스케일한다. **규칙이 소자군마다 다르다.**

        thick-ox : lookup(...) × (W_um / 10) × m
        thin-ox  : lookup(W=W_um, ...) × m        ← W 는 격자값이어야 한다

    강도량(VT, VDSAT, 비율)은 스케일하지 않는다.
    ngspice `@m.x<inst>.<model>[...]` 는 이미 m 을 포함하므로 결과와 직접 비교한다.
    """
    dev, cfg = _cfg(device)
    var = str(outvar).upper()
    intensive = var in ('VT', 'VDSAT', 'VGS', 'VDS', 'VSB') or '_' in var

    if cfg['kind'] == '4d':
        if float(W_um) < cfg['w_min_um']:
            sys.stderr.write(
                '경고: 유닛 폭 %.3g µm 가 bin 경계 %.3g µm 아래입니다. '
                '이 테이블의 gds 는 그 아래에서 유효하지 않습니다 '
                '(실측: W=4 µm 에서 gds/W 가 +72%% 이탈). '
                'm × (W≥10 µm 핑거) 로 나누십시오.\n'
                % (float(W_um), cfg['w_min_um']))
        val = lookup(dev, var, log_id=log_id, **kwargs)
        if intensive:
            return val
        return val * (float(W_um) / cfg['w_ref_um']) * float(m)

    # thin-ox: W 는 축이다. 나누지 않는다.
    val = lookup(dev, var, log_id=log_id, W=float(W_um) * 1e-6, **kwargs)
    if intensive:
        return val
    return val * float(m)


def lookupVGS(device, **kwargs):
    """
    GM_ID 또는 ID_W 로부터 VGS 역조회 (pygmid look_upVGS).
    thin-ox 는 pygmid 를 쓰지 않으므로 design.vgs_at() 을 사용할 것.
    """
    dev, cfg = _cfg(device)
    if cfg['kind'] != '4d':
        raise NotImplementedError(
            '%s 는 5D 테이블이라 pygmid look_upVGS 를 쓸 수 없습니다. '
            'design.vgs_at(dev, L, VDS, VSB, W=..., gm_id=...) 를 사용하십시오.' % dev)
    _check_L(dev, kwargs)
    return _OBJ[dev].look_upVGS(**kwargs)


if __name__ == '__main__':
    print('=== 로드 상태 ===')
    for k, v in devices().items():
        print('  %-12s %s' % (k, v))
    print()
    for dev in DEVICES:
        try:
            describe(dev)
            print()
        except Exception as exc:                               # noqa: BLE001
            print('%s: %s\n' % (dev, str(exc).split('\n')[0]))
