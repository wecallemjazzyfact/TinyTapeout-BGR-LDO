#!/usr/bin/env bash
# ==============================================================================
# extract_pdk_temp.sh
# Sky130A PDK 온도 관련 정밀 파라미터 덤프 스크립트
# 규칙: grep 결과를 파싱하지 않고 원문 그대로 출력
# ==============================================================================

PDK_ROOT="/foss/pdks/sky130A"

echo "=================================================================="
echo "1. PNP BJT (sky130_fd_pr__pnp_05v5_W0p68L0p68) 모델 및 온도 파라미터"
echo "=================================================================="
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/models_bjt.spice"
grep -n -C 30 "sky130_fd_pr__pnp_05v5_W0p68L0p68" "${PDK_ROOT}/libs.tech/combined/continuous/models_bjt.spice"

echo ""
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/parameters_fet_tt.spice (sw_nw_rs_mult)"
grep -n "sw_nw_rs_mult" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_fet_tt.spice"
grep -n "sw_nw_rs_mult" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_fet_ss.spice"
grep -n "sw_nw_rs_mult" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_fet_ff.spice"

echo ""
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_nom.spice (sw_rdp)"
grep -n "sw_rdp" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_nom.spice"
grep -n "sw_rdp" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_high.spice"
grep -n "sw_rdp" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_low.spice"

echo ""
echo "=================================================================="
echo "2. 고저항 폴리 (sky130_fd_pr__res_high_po_0p69) 및 온도계수"
echo "=================================================================="
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/models_resistors.spice"
grep -n -C 20 "sky130_fd_pr__res_high_po" "${PDK_ROOT}/libs.tech/combined/continuous/models_resistors.spice"

echo ""
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/models_global.spice (tc1/tc2)"
grep -n "tc1sky130_fd_pr__res_generic_pobody" "${PDK_ROOT}/libs.tech/combined/continuous/models_global.spice"
grep -n "tc2sky130_fd_pr__res_generic_pobody" "${PDK_ROOT}/libs.tech/combined/continuous/models_global.spice"

echo ""
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_nom.spice (sw_sky130_fd_pr__res_high_po_rs)"
grep -n "sw_sky130_fd_pr__res_high_po_rs" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_nom.spice"
grep -n "sw_sky130_fd_pr__res_high_po_rs" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_high.spice"
grep -n "sw_sky130_fd_pr__res_high_po_rs" "${PDK_ROOT}/libs.tech/combined/continuous/parameters_res_low.spice"

echo ""
echo "[경로] ${PDK_ROOT}/libs.tech/magic/sky130A.tech (xhrpoly 시트저항)"
grep -n "resist xhrpoly" "${PDK_ROOT}/libs.tech/magic/sky130A.tech"

echo ""
echo "=================================================================="
echo "3. 컨택 저항 온도계수 검증"
echo "=================================================================="
echo "[경로] ${PDK_ROOT}/libs.tech/combined/continuous/models_resistors.spice (rhead_model 검사)"
grep -n -A 10 "model rhead_model r" "${PDK_ROOT}/libs.tech/combined/continuous/models_resistors.spice"

echo ""
echo "=================================================================="
echo "4. 트림 스위치 (sky130_fd_pr__nfet_01v8) BSIM4 온도 파라미터"
echo "=================================================================="
echo "[경로] ${PDK_ROOT}/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8.pm3.spice"
grep -n -E "(tnom|ute|kt1|kt2|kt1l|ua|ub|uc|ua1|ub1|uc1) =" "${PDK_ROOT}/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8.pm3.spice" | head -30

echo ""
echo "=================================================================="
echo "추출 완료."
