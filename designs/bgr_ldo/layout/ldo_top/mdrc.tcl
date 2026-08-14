gds maskhints yes
gds read ldo_top_fixed.gds
load ldo_top
select top cell
expand
drc euclidean on
drc style drc(full)
drc check
set r [drc listall why]
set n 0
foreach {e c} $r {
  puts "== $e  ([llength $c])"
  set i 0
  foreach k $c {
    if {$i<3} { puts "     $k" }
    incr i; incr n
  }
}
puts "TOTAL $n"
quit -noprompt
