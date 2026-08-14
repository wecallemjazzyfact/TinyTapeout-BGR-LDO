drc style drc(full)
drc euclidean on
load ldo_top
select top cell
expand
drc check
set r [drc listall why]
set f [open cur.txt w]
foreach {e c} $r { foreach k $c { puts $f "$e|$k" } }
close $f
quit -noprompt
