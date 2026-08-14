# ---- MiM 단위셀 레이아웃 (평탄) ----
drc off
load mim_flat -silent

# 하판 met3
box 0 0 20um 20um
paint m3

# MiM 유전체 capm (met3 안쪽)
box 0.2um 0.2um 18.5147um 18.5147um
paint capm

# 상판 met4 (capm 위)
box 0.2um 0.2um 18.5147um 18.5147um
paint m4

# 포트 라벨: BOT = 하판 met3 (오른쪽 여백)
box 19um 1um 19.8um 2um
label BOT
port make

# 포트 라벨: TOP = 상판 met4 (중앙)
box 9um 9um 10um 10um
label TOP
port make

save mim_flat

# ---- DRC ----
drc on
select top cell
drc check
drc catchup
puts "DRC_COUNT [drc list count total]"

# ---- 추출 ----
extract all
ext2spice lvs
ext2spice -o mim_flat_lay.spice
puts "EXTRACT_DONE"
quit -noprompt
