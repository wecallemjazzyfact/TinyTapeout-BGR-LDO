gds maskhints yes
gds read ldo_top_fixed.gds
load ldo_top
select top cell
expand
drc style drc(full)
drc euclidean on
drc check
set r [drc listall why]
set n 0
foreach {e c} $r { puts "  [llength $c]  $e" ; incr n [llength $c] }
puts "TOTAL $n"
quit -noprompt
