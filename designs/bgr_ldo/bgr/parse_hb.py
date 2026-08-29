import re

content = open("hb_out.txt").read()
rows = sorted((int(m.group(1)), float(m.group(2))) for m in re.finditer(r'===HB(\d+)===\s*\n[^\n]*v\(vref_low\)\s*=\s*([0-9.eE+-]+)', content))
vs = [v for c, v in rows]

print('=' * 60)
print('수집 코드 개수: %d / 64' % len(vs))
print('=' * 60)

if len(vs) == 64:
    mono = all(vs[i] > vs[i + 1] for i in range(63))
    print('단조성 (Monotonicity): %s' % ('OK (전 구간 완벽 단조 감소)' if mono else 'FAIL (단조 위반)'))
    if not mono:
        for i in range(63):
            if vs[i] <= vs[i + 1]:
                print('  위반: code%d(%.5f) <= code%d(%.5f)' % (i, vs[i], i + 1, vs[i + 1]))
    print()
    print('Vout(code 0)  = %.5f V  (Vref = %.5f V)' % (vs[0] * 1.5, vs[0]))
    print('Vout(code 63) = %.5f V  (Vref = %.5f V)' % (vs[-1] * 1.5, vs[-1]))
    print('트림 전압 가변 스팬 = %.2f mV' % ((vs[0] - vs[-1]) * 1500))
    print('중앙코드(31~32) Vout 평균 = %.5f V' % ((vs[31] + vs[32]) / 2 * 1.5))
    
    lsb = [(vs[i] - vs[i + 1]) * 1500 for i in range(63)]
    a = sum(lsb) / 63
    print('LSB 평균 = %.3f mV (min %.3f mV, max %.3f mV)' % (a, min(lsb), max(lsb)))
    imax = lsb.index(max(lsb))
    print('최대 LSB = %.3f mV, 위치 code%d->%d (Vout %.4fV -> %.4fV)' % (max(lsb), imax, imax + 1, vs[imax] * 1.5, vs[imax + 1] * 1.5))
    print('DNL (max-min)/avg = %.3f LSB' % ((max(lsb) - min(lsb)) / a))
    print()
    print('1.800 V 근접 코드 (±10 mV 이내):', [(f'code{i}', '%.4f V' % (x * 1.5)) for i, x in enumerate(vs) if abs(x * 1.5 - 1.800) < 0.010])
print('=' * 60)
