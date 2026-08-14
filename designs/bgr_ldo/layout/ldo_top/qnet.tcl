gds maskhints yes
gds read ldo_top_fixed.gds
load ldo_top
select top cell
expand
foreach p {{-0.7 60.0} {64.4 60.0} {30.0 77.85} {70.0 -1.25} {100.0 -33.85}} {
  set x [lindex $p 0]; set y [lindex $p 1]
  box [expr {$x-0.01}]um [expr {$y-0.01}]um [expr {$x+0.01}]um [expr {$y+0.01}]um
  select clear
  select area
  puts "POINT $x $y  ->  [what -list]"
}
quit -noprompt
