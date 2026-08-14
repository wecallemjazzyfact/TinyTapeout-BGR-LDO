import subprocess

tcl_code = """
puts "=== REAL MAGIC VERSION REPORT ==="
puts "VERSION: [version]"
puts "REVISION: [version revision]"
exit
"""

with open("/tmp/ver_real.tcl", "w") as f:
    f.write(tcl_code)

res = subprocess.run(["/headless/.local/bin/magic", "-dnull", "-noconsole", "/tmp/ver_real.tcl"], capture_output=True, text=True)
print(res.stdout)
