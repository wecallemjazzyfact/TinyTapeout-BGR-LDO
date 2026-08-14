import os, re, gdstk

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
                
                pins[pname] = (ox+lx, oy+by, ox+rx, oy+ty)
            break
        i += 1
    return pins

pins = parse_def_pins(def_file)
pins['VAPWR'] = (0.420, 5.000, 2.920, 225.760)
pins['VDPWR'] = (3.920, 5.000, 5.920, 220.760)
pins['VGND']  = (6.920, 5.000, 9.420, 218.060)

gds_in = '/foss/designs/designs/bgr_ldo/layout/ldo_top/ldo_top_fixed.gds'
gds_out = '/foss/designs/gds/tt_um_wecallemjazzyfact_bgr_ldo.gds'

os.makedirs('/foss/designs/gds', exist_ok=True)

lib = gdstk.read_gds(gds_in)
ldo_top = lib.top_level()[0]

top = lib.new_cell('tt_um_wecallemjazzyfact_bgr_ldo')
top.add(gdstk.Reference(ldo_top, origin=(1.800, 146.560)))

# Add prBoundary polygon covering (0, 0) to (145.360, 225.760) on layer 235, datatype 4
top.add(gdstk.rectangle((0.0, 0.0), (145.360, 225.760), layer=235, datatype=4))

# Add met4.drawing (layer 71, datatype 20) AND met4.pin (layer 71, datatype 16) rectangle for every pin
for pname, (lx, by, rx, ty) in pins.items():
    top.add(gdstk.rectangle((lx, by), (rx, ty), layer=71, datatype=20))
    top.add(gdstk.rectangle((lx, by), (rx, ty), layer=71, datatype=16))
    top.add(gdstk.Label(pname, ((lx+rx)/2, (by+ty)/2), layer=71, texttype=16))

lib.write_gds(gds_out)
print(f'Successfully assembled {gds_out} with met4.drawing and met4.pin rects!')
