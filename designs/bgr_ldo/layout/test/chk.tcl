puts "=== tech 로드 상태 ==="
puts "tech: [tech name]"
puts ""
puts "=== cap 관련 레이어 전부 ==="
foreach l [tech layers] {
    if {[string match "*cap*" $l] || [string match "*mim*" $l] || [string match "met*" $l]} {
        puts "  $l"
    }
}
quit -noprompt
