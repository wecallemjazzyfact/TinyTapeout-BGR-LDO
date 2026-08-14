"""
gm/Id 사이징 헬퍼 — lookup.py 위의 설계 계층

lookup.py가 "바이어스 -> 소자 파라미터" 정방향 조회라면, 이 모듈은 설계에 필요한
"성능 요구 -> 소자 치수" 역방향을 제공한다.

    curves()   : 한 (L, VDS, VSB)에서 VGS 축 전체의 설계 곡선 세트
    vgs_at()   : 목표 gm/Id 또는 ID/W 에 해당하는 VGS (역조회)
    size()     : gm/Id 와 목표 전류 -> W, m, VGS, 부산물(gm, gds, cgg, fT, vdsat)
    charts()   : Murmann 4-패널 설계 차트 PNG

전형적 사용 (folded cascode 입력쌍 예):
    import design as d
    r = d.size('nfet', L=2e-6, gm_id=15, ID_total=2.5e-6, VDS=1.0, VSB=0.3)
    # -> W_total, m, VGS, gm, gds, cgg, fT, vdsat, gm_gds

주의 (lut/README.md §9, 02_LUT_앵커.md §5)
    * 유닛 핑거 W >= 5 um (권장 10). size()는 W_unit=10 기본, m 정수화까지 해준다.
    * L 은 격자값만: {0.5, 1, 2, 4, 8, 20} um
    * gds 정확도는 -3.2 ~ +9.6% -> 이득 예측은 +/-10~20% 전제, 확정은 회로 시뮬
    * 결과는 '제안'이며 확정은 회로 시뮬 검증 후
"""

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import lookup as lut

__all__ = ['curves', 'vgs_at', 'size', 'charts', 'report']

_VARS = ('ID', 'GM', 'GDS', 'CGG', 'VDSAT', 'VT')


def curves(dev, L, VDS, VSB=0.0, vgs_min=0.3, vgs_max=3.0):
    """
    한 (L, VDS, VSB) 단면에서 VGS 격자 전체의 설계 곡선.

    반환 dict (모두 W = 10 um, m = 1 기준):
        VGS, ID, GM, GDS, CGG, VDSAT, VT   -- 원 파라미터
        GM_ID   [1/V]   gm/Id, 반전 정도의 척도
        ID_W    [A/um]  전류 밀도 -> W 산출에 사용
        GM_GDS  [-]     intrinsic gain
        FT      [Hz]    gm / (2 pi Cgg)
        VOV     [V]     VGS - VT (참고용. [vth]는 zero-bias 계열이므로 정밀 판단은 VDSAT로)
    """
    vg = lut.axes(dev)['VGS']
    vg = vg[(vg >= vgs_min) & (vg <= vgs_max)]
    out = {'VGS': vg, '_L': L, '_VDS': VDS, '_VSB': VSB, '_dev': dev}
    for k in _VARS:
        out[k] = np.array([float(lut.lookup(dev, k, L=L, VGS=float(v),
                                            VDS=VDS, VSB=VSB)) for v in vg])
    out['GM_ID'] = out['GM'] / out['ID']
    out['ID_W'] = out['ID'] / lut.W_REF_UM          # A per um
    out['GM_GDS'] = out['GM'] / out['GDS']
    out['FT'] = out['GM'] / (2.0 * np.pi * out['CGG'])
    out['VOV'] = out['VGS'] - out['VT']
    return out


def vgs_at(dev, L, VDS, VSB=0.0, gm_id=None, id_w=None, **kw):
    """
    목표 gm/Id [1/V] 또는 ID/W [A/um] 에 해당하는 VGS 를 역조회한다.
    둘 중 하나만 지정할 것. ID/W 역조회는 log 도메인 보간을 쓴다.
    """
    if (gm_id is None) == (id_w is None):
        raise ValueError('gm_id 또는 id_w 중 정확히 하나만 지정하십시오.')
    c = curves(dev, L, VDS, VSB, **kw)

    if gm_id is not None:
        g, v = c['GM_ID'], c['VGS']
        if not (g.min() <= gm_id <= g.max()):
            raise ValueError('gm/Id = %.3g 는 이 단면의 범위 [%.2f, %.2f] 밖입니다.'
                             % (gm_id, g.min(), g.max()))
        o = np.argsort(g)                      # gm/Id 는 VGS 에 대해 감소 -> 정렬
        return float(np.interp(gm_id, g[o], v[o]))

    x, v = c['ID_W'], c['VGS']
    if not (x.min() <= id_w <= x.max()):
        raise ValueError('ID/W = %.3g A/um 는 이 단면의 범위 [%.3g, %.3g] 밖입니다.'
                         % (id_w, x.min(), x.max()))
    return float(np.interp(np.log(id_w), np.log(x), v))


def size(dev, L, ID_total, gm_id=None, VDS=1.0, VSB=0.0, W_unit=10.0,
         m=None, vgs=None):
    """
    사이징 1회. gm_id 또는 vgs 중 하나로 동작점을 지정한다.

    ID_total : 이 소자가 흘려야 하는 총 전류 [A] (m 포함한 실소자 기준)
    W_unit   : 유닛 핑거 폭 [um]. 기본 10 (LUT 기준폭). 5 미만 금지.
    m        : 지정하면 그 값으로 고정하고 유닛 폭을 역산. 미지정 시 m 을 정수로 올림.

    반환 dict: VGS, W_unit, m, W_total, ID_total, gm, gds, cgg, fT,
               vdsat, vth, gm_id, gm_gds, ID_W
    """
    if (gm_id is None) == (vgs is None):
        raise ValueError('gm_id 또는 vgs 중 정확히 하나만 지정하십시오.')
    if W_unit < lut.W_BIN_MIN_UM:
        raise ValueError('W_unit = %.3g um 는 모델 bin 경계(%.3g um) 아래입니다. '
                         'gds 가 유효하지 않습니다.' % (W_unit, lut.W_BIN_MIN_UM))

    if vgs is None:
        vgs = vgs_at(dev, L, VDS, VSB, gm_id=gm_id)

    b = dict(L=L, VGS=vgs, VDS=VDS, VSB=VSB)
    id10 = float(lut.lookup(dev, 'ID', **b))        # W = 10 um 기준
    id_w = id10 / lut.W_REF_UM                      # A/um
    W_total = ID_total / id_w                       # um

    if m is None:
        m = max(1, int(np.ceil(W_total / W_unit)))
        W_unit_eff = W_total / m
    else:
        m = int(m)
        W_unit_eff = W_total / m
    if W_unit_eff < lut.W_BIN_MIN_UM:
        sys.stderr.write('Warning: 유닛 폭 %.3g um 가 bin 경계 아래입니다. '
                         'm 을 줄이거나 W_unit 을 키우십시오.\n' % W_unit_eff)

    scale = W_total / lut.W_REF_UM                  # = (W/10) * m 과 동일
    gm = float(lut.lookup(dev, 'GM', **b)) * scale
    gds = float(lut.lookup(dev, 'GDS', **b)) * scale
    cgg = float(lut.lookup(dev, 'CGG', **b)) * scale

    return {
        'dev': dev, 'L_um': L * 1e6, 'VGS': vgs, 'VDS': VDS, 'VSB': VSB,
        'W_unit_um': W_unit_eff, 'm': m, 'W_total_um': W_total,
        'ID_total': ID_total, 'ID_W_uA_per_um': id_w * 1e6,
        'gm': gm, 'gds': gds, 'cgg': cgg,
        'gm_id': gm / ID_total, 'gm_gds': gm / gds,
        'fT_Hz': gm / (2.0 * np.pi * cgg),
        'vdsat': float(lut.lookup(dev, 'VDSAT', **b)),
        'vth': float(lut.lookup(dev, 'VT', **b)),
    }


def report(r):
    """size() 결과를 사람이 읽는 형태로."""
    print('  %s  L=%.2fum  W=%.3gum (=%.3gum x m%d)  VGS=%.4fV  VDS=%.3fV  VSB=%.3fV'
          % (r['dev'], r['L_um'], r['W_total_um'], r['W_unit_um'], r['m'],
             r['VGS'], r['VDS'], r['VSB']))
    print('    ID=%.4g A   gm=%.4g S   gds=%.4g S   cgg=%.4g F'
          % (r['ID_total'], r['gm'], r['gds'], r['cgg']))
    print('    gm/Id=%.2f 1/V   gm/gds=%.1f   fT=%.4g Hz   vdsat=%.4f V   vth=%.4f V'
          % (r['gm_id'], r['gm_gds'], r['fT_Hz'], r['vdsat'], r['vth']))
    print('    ID/W=%.4f uA/um   (gds 는 +/-10~20%% 오차 전제 — 이득 확정은 회로 시뮬)'
          % r['ID_W_uA_per_um'])


def charts(dev, L_list=(0.5e-6, 1e-6, 2e-6, 4e-6, 8e-6), VDS=1.0, VSB=0.0,
           out_png=None, gm_id_range=(3.0, 25.0)):
    """
    Murmann 4-패널 설계 차트를 PNG 로 저장한다. x축은 모두 gm/Id.
      (1) ID/W  [A/um]  로그축 -- 전류 밀도, W 산출
      (2) gm/gds        로그축 -- intrinsic gain
      (3) fT    [Hz]    로그축 -- 속도
      (4) vdsat [V]            -- 헤드룸
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    if out_png is None:
        out_png = os.path.join(_HERE, 'data',
                               'gmid_charts_%s_VDS%.2f_VSB%.2f.png' % (dev, VDS, VSB))

    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    panels = [('ID_W', 'ID/W  [A/um]', True),
              ('GM_GDS', 'gm/gds  (intrinsic gain)', True),
              ('FT', 'fT  [Hz]', True),
              ('VDSAT', 'vdsat  [V]', False)]

    for L in L_list:
        c = curves(dev, L, VDS, VSB)
        g = c['GM_ID']
        sel = (g >= gm_id_range[0]) & (g <= gm_id_range[1])
        lbl = 'L=%.2gum' % (L * 1e6)
        for a, (key, ylab, logy) in zip(ax.ravel(), panels):
            a.plot(g[sel], c[key][sel], label=lbl)
            a.set_xlabel('gm/Id  [1/V]')
            a.set_ylabel(ylab)
            if logy:
                a.set_yscale('log')
            a.grid(True, which='both', alpha=0.3)

    ax.ravel()[0].legend(fontsize=8)
    fig.suptitle('%s  gm/Id design charts   (tt/27C, W=10um, VDS=%.2fV, VSB=%.2fV)'
                 % (dev, VDS, VSB))
    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    print('saved: %s' % out_png)
    return out_png


if __name__ == '__main__':
    print('=== gm/Id design charts ===')
    charts('nfet', VDS=1.0, VSB=0.0)
    charts('pfet', VDS=1.0, VSB=0.0)
    print('\n=== sanity: A1b 조건을 size() 로 재현 ===')
    # A1b: nfet L=2, W=10, VGS=0.92, VDS=1.0, VSB=0 -> ID = 5.345498 uA
    report(size('nfet', L=2e-6, ID_total=5.345498e-6, vgs=0.92,
                VDS=1.0, VSB=0.0, m=1))
    print('    기대: W_total=10um, gm=62.917uS, gds=71.206nS, cgg=41.798fF')
