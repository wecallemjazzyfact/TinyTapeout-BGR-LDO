# MiM 적층(capm + cap2m) DRC 검증
drc off
tech load sky130A
snap internal

# --- 셀 1: 단층 (capm only) ---
load mim_single -silent
box 0 0 10um 10um
paint met3
box 0.2um 0.2um 9.8um 9.8um
paint capm
box 0 0 10um 10um
paint met4          ;# capm 상판 = met4
save

# --- 셀 2: 적층 (capm + cap2m) ---
load mim_stack -silent
box 0 0 10um 10um
paint met3
box 0.2um 0.2um 9.8um 9.8um
paint capm
box 0 0 10um 10um
paint met4
box 0.2um 0.2um 9.8um 9.8um
paint cap2m
box 0 0 10um 10um
paint met5          ;# cap2m 상판 = met5  <-- TT 금지층!
save

# --- DRC ---
drc on
foreach c {mim_single mim_stack} {
    load $c -silent
    select top cell
    drc check
    drc catchup
    set n [drc list count total]
    puts "=== $c : DRC 위반 $n 건 ==="
    if {$n > 0} { puts [drc listall why] }
}
quit -noprompt
