import os, re

def_file = '/foss/designs/tt/tech/sky130A/def/analog/tt_analog_1x2_3v3.def'

def parse_def_pins(def_path):
    units_re = re.compile(r'UNITS DISTANCE MICRONS (\S+) ;')
    diearea_re = re.compile(r'DIEAREA \( (\S+) (\S+) \) \( (\S+) (\S+) \) ;')
    pins_re = re.compile(r'PINS (\d+) ;')
    pin_re = re.compile(r' *- (\S+) \+ NET (\S+) \+ DIRECTION (\S+) \+ USE (\S+)')
    layer_re = re.compile(r' *\+ LAYER (\S+) \( (\S+) (\S+) \) \( (\S+) (\S+) \)')
    placed_re = re.compile(r' *\+ PLACED \( (\S+) (\S+) \) (\S+) ;')

    dbu = 1000
    pins = {}

    with open(def_path) as f:
        lines = [line.strip() for line in f]

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('UNITS '):
            m = units_re.match(line)
            if m: dbu = int(m.group(1))
        elif line.startswith('PINS '):
            m = pins_re.match(line)
            count = int(m.group(1))
            i += 1
            for _ in range(count):
                m_pin = pin_re.match(lines[i])
                pname, net, direction, use = m_pin.groups()
                i += 2 # skip PORT line
                m_layer = layer_re.match(lines[i])
                layer, lx, by, rx, ty = m_layer.groups()
                i += 1
                m_placed = placed_re.match(lines[i])
                ox, oy, _ = m_placed.groups()
                i += 1
                
                ox, oy = float(ox)/dbu, float(oy)/dbu
                lx, by, rx, ty = float(lx)/dbu, float(by)/dbu, float(rx)/dbu, float(ty)/dbu
                
                pins[pname] = {
                    'layer': layer,
                    'rect': (ox+lx, oy+by, ox+rx, oy+ty),
                    'use': use,
                    'direction': direction
                }
            break
        i += 1
    return pins

pins = parse_def_pins(def_file)

# Update power pins with layout verified coordinates
pins['VAPWR'] = {'layer': 'met4', 'rect': (0.420, 5.000, 2.920, 225.760), 'use': 'POWER', 'direction': 'INOUT'}
pins['VDPWR'] = {'layer': 'met4', 'rect': (3.920, 5.000, 5.920, 220.760), 'use': 'POWER', 'direction': 'INOUT'}
pins['VGND']  = {'layer': 'met4', 'rect': (6.920, 5.000, 9.420, 218.060), 'use': 'GROUND', 'direction': 'INOUT'}

out = []
out.append('VERSION 5.7 ;')
out.append('  NOWIREEXTENSIONATPIN ON ;')
out.append('  DIVIDERCHAR "/" ;')
out.append('  BUSBITCHARS "[]" ;')
out.append('MACRO tt_um_wecallemjazzyfact_bgr_ldo')
out.append('  CLASS BLOCK ;')
out.append('  ORIGIN 0.000 0.000 ;')
out.append('  SIZE 145.360 BY 225.760 ;')

for pname, pdata in sorted(pins.items()):
    out.append(f'  PIN {pname}')
    out.append(f'    DIRECTION {pdata["direction"]} ;')
    out.append(f'    USE {pdata["use"]} ;')
    out.append(f'    PORT')
    out.append(f'      LAYER {pdata["layer"]} ;')
    r = pdata['rect']
    out.append(f'        RECT {r[0]:.3f} {r[1]:.3f} {r[2]:.3f} {r[3]:.3f} ;')
    out.append(f'    END')
    out.append(f'  END {pname}')

out.append('END tt_um_wecallemjazzyfact_bgr_ldo')
out.append('END LIBRARY')

text = '\n'.join(out) + '\n'

os.makedirs('/foss/designs/lef', exist_ok=True)
os.makedirs('/foss/designs/gds', exist_ok=True)

with open('/foss/designs/lef/tt_um_wecallemjazzyfact_bgr_ldo.lef', 'w') as f:
    f.write(text)
with open('/foss/designs/gds/tt_um_wecallemjazzyfact_bgr_ldo.lef', 'w') as f:
    f.write(text)

print('Generated LEF cleanly!')
