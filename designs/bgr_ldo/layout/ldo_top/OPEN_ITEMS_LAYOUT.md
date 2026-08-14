# ldo_top 레이아웃 미결 항목  (갱신: LU 조사 완료 시점)

## A. 블로커 — 반드시 처리
- [ ] A1 안테나 다이오드 2개 배치 (SNK_EN, RO_EN)
      골든 144 vs 추출 142. 배치 전까지 LVS 실패.
      셀 sky130_fd_sc_hd__diode_2, 포트 DIODE VGND VNB VPB VPWR
      결선 DIODE=신호, VGND/VNB=VGND, VPB/VPWR=VDPWR
- [ ] A2 LU.2 88건 : BGR 트림 N확산(y -16.870) <-> p-tap(y -1.500) = 15.370 (0.37 초과)
      해결안: p-tap 바 신설  x 85.0..143.4, y -20.100..-17.200
      빈 밴드 y -20.430..-16.870 (3.560) 확인됨. met1 은 관통 있음.
- [ ] A3 LU.3 32건 : BGR PNP(y 56.760~) / y41-51 배열, n-tap 거리 초과
      해결안: n-tap 바 신설  x 0.0..64.0, y 52.500..55.500
      빈 밴드 y 51.760..56.260 (4.500) 확인됨. met1 세로 관통 있음.
      넷: 전역 nwell 과 동일 노드(기존 좌우/상단 n-tap 과 같은 넷)
- [ ] A4 LU 27건 : div16 (x 98.9..104.2), 탭이 x 83.9/119.2 양끝뿐 (17.7)
      해결안: y -138.850..-135.000 밴드에 tap 배치. **금속 없음, 자유**
      LU.3 분은 div16 nwell(y -140.455..-138.850) 안에 n-tap 필요 -> nwell 확장 검토
- [ ] A5 LU.3 1건 : 클램프 x 139.7..140.7, y -73.5
      해결안 확정: n-tap 139.400..141.200, y -74.200..-73.800
      (nwell 139.070..141.560 안, 확산 없는 0.660 밴드)
- [ ] A6 diff/tap.18 1건 : p-tap(65.800) vs nwell(65.600) = 0.200 < 0.430
      해결안: p-tap 서단을 66.030 으로 절단

## B. 미실행 검증
- [ ] B1 precheck 전체 (pin_check / analog_pin_check / urpm_nwell_check / power_pin_check)
- [ ] B2 밀도 룰
- [ ] B3 전류 넷 전수 — 실제 DC 전류값 미확보 (회로 채팅 요청 필요)
- [ ] B4 PEX + post-layout AC 3조건
- [ ] B5 tt_um_bgr_ldo_shuttle 조립
- [ ] B6 fix_masks.py 를 최종 GDS 에 적용

## C. 검증 조건 (인용 시 반드시 병기)
- magic DRC : `drc euclidean on` + `drc style drc(full)`  <- 이것만 유효
              (기본 style 은 LU.2/LU.3 를 검사하지 않음)
- KLayout   : feol / beol / offgrid
- LVS       : netgen + dfxbp/diode blackbox stub 양쪽 로드

## D. 완료 (조건 명기)
- via 확대 전수 : 감쌈 0.090 균일 기준, 확대 여지 0
- 부유 노드 0 (다이오드 배치 전 기준)
- LVS match uniquely : 소자 96/96, 넷 63/63 (다이오드 배치 전 기준)
- KLayout feol/beol/offgrid 0/0/0 : ldo_top_fixed.gds (fix_masks.py 적용본)
  * RPM  grow 0.095 -> closing 0.425
  * PSDM closing 0.195

## E. LU 룰 기전 (2차 조사 완료)
- ptap_reach = psc,mvpsc -> grow 840 x18, 매회 and-not nwell   (기판에서만 전파)
- ntap_reach = nsc,mvnsc -> grow 1270 x12, 매회 and nwell,pnp  (nwell 안에서만 전파)
- ptap_missing = *ndiff,*mvndiff  and-not ptap_reach
- ntap_missing = *pdiff,*mvpdiff  and-not ntap_reach
- licon.16 : 모든 탭은 licon 필수. 탭 확산만으로는 LU 인정 안 됨
- 거리 기준점 = tap LICON center

### 설계 함의
- n-tap 은 대상 p-diff 와 **같은 nwell** 안에 있어야 함
- p-tap 은 대상 n-diff 와의 사이에 nwell 이 없어야 함
- magic 에서 psubdiffcont / mvnsubdiffcont 로 칠하면 확산+licon+li 동시 생성
- hvi(75/20) 영역이면 mv* 계열 사용

### A5 재검토 결과
- 클램프 nwell 하단 여유 0.660 < 필요 0.74 -> 하단 배치 불가
- 같은 nwell 내 y -60~-70 구간에 배치 필요 (빈자리 조사 중)

## F. BGR rev5 반영 (2026-08-11)
- BGR 이 latch-up 탭 신설로 LU 120건 + diff/tap.18 1건 해결
  - trim p-tap : psubdiff+locali 85.00-143.40 x y -19.90..-18.90
  - 채널 n-tap : mvnsubdiff+locali 0.15-63.65 x y 54.60..55.50
  - 행B 하부   : n-tap 0.30-63.50 x y 39.80..40.50
- ★ ldo_top/ 에 bgr_mos.mag 사본(05:59 중간본)이 있어 magic 이 그걸 읽었음
  -> BGR 이 _stale/ 로 격리, ldo_top/.magicrc 에 addpath bgr_core 추가
  -> **정본은 layout/bgr_core/bgr_mos.mag 하나. 사본 금지**
- ldo_top/.magicrc 신설 (기존 260B 파일 덮어씀 - 내용 미확인)
  source PDK rc / addpath bgr_core / drc style drc(full) / drc euclidean on

## G. 남은 LU (우리 몫 29건)
- [ ] G1 div16 LU.2 14 : 행 아래 y -142.6..-142.2 에 p-tap
      기존 p-tap x 83.9/119.2 에서 15um 가 x 98.9/104.2 에서 끊김
- [ ] G2 div16 LU.3 13 : nwell 을 y -138.850 -> -137.5 확장 후 n-tap
      nwell 내 여유 0.430 < 필요 0.600 (LV 감쌈 0.180+폭 0.150+이격 0.270)
      y -138.85..-136.5 는 **비어 있음** 확인됨
- [ ] G3 싱크 LU.2 1 : x 90.030..90.320, y -113.870..-110.370
      p-tap 바(y -95.72) 까지 18.15. y -119 근처에 p-tap 필요
- [ ] G4 클램프 LU.3 1 : nwell+hvi 를 y -75.170 까지 확장 후 MV n-tap
      하단 여유 0.660 < 필요 0.850 (MV 감쌈 0.330+폭 0.150+이격 0.370)

## H. rpm.1 (우리 저항)
- RF1/RF2 x 0.300..2.980, 세로 간격 1.81 > 1.24 -> 병합 안 됨
- XR_slew x 1.800..5.750
- 분압 x 103.62..133.26 (열 양끝)
- XRz  x 136.39
- 해법 후보: (a) 간격 1.24 이내로 배치 조정  (b) 더미 저항  (c) GDS 마스크 보정
- BGR 권고는 (a). fix_masks.py 는 검증 기준 이원화 문제로 보류
