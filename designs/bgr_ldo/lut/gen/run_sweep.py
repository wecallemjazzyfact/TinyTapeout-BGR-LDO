import numpy as np
import subprocess
import os
import pickle
import sys

# Define sweep ranges
L_list = [0.5, 1.0, 2.0, 4.0, 8.0, 20.0]  # in um
VSB_list = [0.0, 0.4, 0.8, 1.2]
VDS_list = [0.1, 0.3, 0.6, 1.0, 1.65, 2.5, 3.3]
VGS_list = np.arange(0.0, 3.301, 0.025)

L_meters = np.array(L_list) * 1e-6
VGS_arr = np.array(VGS_list)
VDS_arr = np.array(VDS_list)
VSB_arr = np.array(VSB_list)

num_L = len(L_list)
num_VGS = len(VGS_list)
num_VDS = len(VDS_list)
num_VSB = len(VSB_list)

# Output directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def run_nfet_sweep():
    print("=== Characterizing NFET (sky130_fd_pr__nfet_g5v0d10v5) ===")
    nch = {
        'INFO': 'sky130_fd_pr__nfet_g5v0d10v5 characterization',
        'CORNER': 'tt',
        'TEMP': np.array([300.15]),
        'NFING': 1,
        'L': L_meters,
        'W': 10.0e-6,
        'VGS': VGS_arr,
        'VDS': VDS_arr,
        'VSB': VSB_arr,
        'METHOD': 'pchip'
    }
    
    # Initialize 4D output arrays
    outvars = ['ID', 'VT', 'GM', 'GDS', 'CGG', 'CGS', 'CGD', 'CGB', 'VDSAT']
    for var in outvars:
        nch[var] = np.zeros((num_L, num_VGS, num_VDS, num_VSB))
        
    temp_spice = 'nfet_sweep_temp.sp'
    temp_out = 'nfet_sweep_temp.txt'
    
    total_steps = num_L * num_VSB * num_VDS
    step_count = 0
    
    for i, L in enumerate(L_list):
        for j, VSB in enumerate(VSB_list):
            for k, VDS in enumerate(VDS_list):
                step_count += 1
                if step_count % 20 == 0 or step_count == total_steps:
                    print(f"  Progress: {step_count}/{total_steps} sweeps...")
                
                # Write SPICE netlist for this iteration
                netlist = f"""* NFET Sweep Temp
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.param L_val={L}u VDS_val={VDS} VSB_val={VSB}

Vds d s {{VDS_val}}
Vgs g s 0.0
Vsb s 0 {{VSB_val}}

XMN d g s 0 sky130_fd_pr__nfet_g5v0d10v5 L={{L_val}} W=10u nf=1 ad=0 as=0 pd=0 ps=0 nrd=0 nrs=0 sa=0 sb=0 sd=0 mult=1

.save i(Vds)
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gm]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gds]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgg]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgs]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgd]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgb]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vth]
.save @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vdsat]

.control
  set wr_singlescale
  dc Vgs 0.0 3.3 0.025
  wrdata {temp_out} i(Vds) @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gm] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gds] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgg] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgs] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgd] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgb] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vth] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vdsat]
.endc
.end
"""
                with open(temp_spice, 'w') as f:
                    f.write(netlist)
                    
                # Run ngspice
                res = subprocess.run(['ngspice', '-b', temp_spice], capture_output=True, text=True)
                if not os.path.exists(temp_out):
                    print(f"Error: SPICE simulation failed for L={L} VSB={VSB} VDS={VDS}!")
                    print(res.stderr)
                    sys.exit(1)
                    
                # Parse data
                raw_data = []
                with open(temp_out, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        try:
                            raw_data.append([float(x) for x in parts])
                        except ValueError:
                            continue
                raw_data = np.array(raw_data)
                
                # Check data length
                if len(raw_data) != num_VGS:
                    print(f"Error: Expected {num_VGS} points, got {len(raw_data)}!")
                    sys.exit(1)
                
                # Extract and store parameters (voltages/currents are positive)
                nch['ID'][i, :, k, j] = raw_data[:, 1]
                nch['GM'][i, :, k, j] = raw_data[:, 2]
                nch['GDS'][i, :, k, j] = raw_data[:, 3]
                nch['CGG'][i, :, k, j] = raw_data[:, 4]
                nch['CGS'][i, :, k, j] = -raw_data[:, 5]
                nch['CGD'][i, :, k, j] = -raw_data[:, 6]
                nch['CGB'][i, :, k, j] = -raw_data[:, 7]
                nch['VT'][i, :, k, j] = raw_data[:, 8]
                nch['VDSAT'][i, :, k, j] = raw_data[:, 9]
                
    # Clean up temp files
    if os.path.exists(temp_spice):
        os.remove(temp_spice)
    if os.path.exists(temp_out):
        os.remove(temp_out)
        
    # Save to pickle in lut/data/
    outfile = os.path.join(DATA_DIR, 'nfet_g5v0d10v5.pkl')
    with open(outfile, 'wb') as f:
        pickle.dump(nch, f)
    print(f"NFET Characterization Complete. Saved to '{outfile}'\n")

def run_pfet_sweep():
    print("=== Characterizing PFET (sky130_fd_pr__pfet_g5v0d10v5) ===")
    pch = {
        'INFO': 'sky130_fd_pr__pfet_g5v0d10v5 characterization',
        'CORNER': 'tt',
        'TEMP': np.array([300.15]),
        'NFING': 1,
        'L': L_meters,
        'W': 10.0e-6,
        'VGS': VGS_arr,
        'VDS': VDS_arr,
        'VSB': VSB_arr,
        'METHOD': 'pchip'
    }
    
    outvars = ['ID', 'VT', 'GM', 'GDS', 'CGG', 'CGS', 'CGD', 'CGB', 'VDSAT']
    for var in outvars:
        pch[var] = np.zeros((num_L, num_VGS, num_VDS, num_VSB))
        
    temp_spice = 'pfet_sweep_temp.sp'
    temp_out = 'pfet_sweep_temp.txt'
    
    total_steps = num_L * num_VSB * num_VDS
    step_count = 0
    
    for i, L in enumerate(L_list):
        for j, VSB in enumerate(VSB_list):
            for k, VDS in enumerate(VDS_list):
                step_count += 1
                if step_count % 20 == 0 or step_count == total_steps:
                    print(f"  Progress: {step_count}/{total_steps} sweeps...")
                
                # Write SPICE netlist for this iteration
                netlist = f"""* PFET Sweep Temp
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.param L_val={L}u VDS_val={VDS} VSB_val={VSB}

Vds d s {{-VDS_val}}
Vgs g s 0.0
Vsb b s {{VSB_val}}
Vs s 0 3.3

XMP d g s b sky130_fd_pr__pfet_g5v0d10v5 L={{L_val}} W=10u nf=1 ad=0 as=0 pd=0 ps=0 nrd=0 nrs=0 sa=0 sb=0 sd=0 mult=1

.save i(Vds)
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gm]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gds]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgg]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgs]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgd]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgb]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vth]
.save @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vdsat]

.control
  set wr_singlescale
  dc Vgs 0.0 -3.3 -0.025
  wrdata {temp_out} i(Vds) @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gm] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gds] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgg] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgs] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgd] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgb] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vth] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vdsat]
.endc
.end
"""
                with open(temp_spice, 'w') as f:
                    f.write(netlist)
                    
                # Run ngspice
                res = subprocess.run(['ngspice', '-b', temp_spice], capture_output=True, text=True)
                if not os.path.exists(temp_out):
                    print(f"Error: SPICE simulation failed for L={L} VSB={VSB} VDS={VDS}!")
                    print(res.stderr)
                    sys.exit(1)
                    
                # Parse data
                raw_data = []
                with open(temp_out, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        try:
                            raw_data.append([float(x) for x in parts])
                        except ValueError:
                            continue
                raw_data = np.array(raw_data)
                
                # Check data length
                if len(raw_data) != num_VGS:
                    print(f"Error: Expected {num_VGS} points, got {len(raw_data)}!")
                    sys.exit(1)
                
                # Extract and store parameters (absolute values/magnitudes are stored)
                pch['ID'][i, :, k, j] = np.abs(raw_data[:, 1])
                pch['GM'][i, :, k, j] = np.abs(raw_data[:, 2])
                pch['GDS'][i, :, k, j] = np.abs(raw_data[:, 3])
                pch['CGG'][i, :, k, j] = np.abs(raw_data[:, 4])
                pch['CGS'][i, :, k, j] = -raw_data[:, 5]
                pch['CGD'][i, :, k, j] = -raw_data[:, 6]
                pch['CGB'][i, :, k, j] = -raw_data[:, 7]
                pch['VT'][i, :, k, j] = np.abs(raw_data[:, 8])
                pch['VDSAT'][i, :, k, j] = np.abs(raw_data[:, 9])
                
    # Clean up temp files
    if os.path.exists(temp_spice):
        os.remove(temp_spice)
    if os.path.exists(temp_out):
        os.remove(temp_out)
        
    # Save to pickle in lut/data/
    outfile = os.path.join(DATA_DIR, 'pfet_g5v0d10v5.pkl')
    with open(outfile, 'wb') as f:
        pickle.dump(pch, f)
    print(f"PFET Characterization Complete. Saved to '{outfile}'\n")

if __name__ == '__main__':
    run_nfet_sweep()
    run_pfet_sweep()
    print("All characterizations completed successfully!")
