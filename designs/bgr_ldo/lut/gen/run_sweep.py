import numpy as np
import subprocess
import os
import pickle
import sys
import time

# Define sweep ranges
L_list = [0.5, 1.0, 2.0, 4.0, 8.0, 20.0]  # in um
VSB_list = [0.0, 0.4, 0.78, 0.8, 1.2]
VDS_list = [round(x, 1) for x in np.arange(0.0, 3.301, 0.1)] # 34 points, 0.1V steps

# VGS grid with anchor points inserted
VGS_uniform_list = [round(x, 3) for x in np.arange(0.0, 3.301, 0.025)]
VGS_list = sorted(list(set(VGS_uniform_list + [0.920, 1.176])))

L_meters = np.array(L_list) * 1e-6
VGS_arr = np.array(VGS_list)
VDS_arr = np.array(VDS_list)
VSB_arr = np.array(VSB_list)

num_L = len(L_list)
num_VGS = len(VGS_list) # 135
num_VDS = len(VDS_list) # 34
num_VSB = len(VSB_list) # 5

# Output directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def parse_wrdata(filepath, expected_len):
    raw_data = []
    with open(filepath, 'r') as f:
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
    if len(raw_data) != expected_len:
        print(f"Error: Expected {expected_len} points in {filepath}, got {len(raw_data)}!")
        sys.exit(1)
    return raw_data

def run_nfet_sweep():
    print("=== Characterizing NFET (sky130_fd_pr__nfet_g5v0d10v5) ===", flush=True)
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
    temp_out_anc1 = 'nfet_sweep_anc1.txt'
    temp_out_anc2 = 'nfet_sweep_anc2.txt'
    
    total_steps = num_L * num_VSB
    step_count = 0
    start_time = time.time()
    
    for i, L in enumerate(L_list):
        for j, VSB in enumerate(VSB_list):
            step_count += 1
            if step_count == 1 or step_count % 2 == 0 or step_count == total_steps:
                elapsed = time.time() - start_time
                avg_time = elapsed / step_count
                eta = (total_steps - step_count) * avg_time
                percent = (step_count / total_steps) * 100
                bar = '█' * int(percent // 5) + '░' * (20 - int(percent // 5))
                sys.stdout.write(
                    f"\r  Progress: [{bar}] {percent:5.1f}% ({step_count}/{total_steps}) | "
                    f"L={L:.2f} VSB={VSB:.2f} | "
                    f"Elapsed: {int(elapsed//60):02d}m{int(elapsed%60):02d}s | "
                    f"ETA: {int(eta//60):02d}m{int(eta%60):02d}s"
                )
                sys.stdout.flush()
            
            # Write SPICE netlist for this iteration
            # XMN is defined only with L and W to match the anchor spice files exactly
            netlist = f"""* NFET Sweep Temp
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.param L_val={L} VSB_val={VSB}

Vds d 0 0.0
Vgs g 0 0.0
Vbs b 0 {{-VSB_val}}

XMN d g 0 b sky130_fd_pr__nfet_g5v0d10v5 L={{L_val}} W=10

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
  
  * 1. Uniform Sweep (133 VGS points)
  dc Vgs 0.0 3.3 0.025 Vds 0.0 3.3 0.1
  wrdata {temp_out} i(Vds) @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gm] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gds] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgg] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgs] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgd] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgb] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vth] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vdsat]
  
  * 2. Anchor 1 (VGS = 0.920)
  alter Vgs = 0.92
  dc Vds 0.0 3.3 0.1
  wrdata {temp_out_anc1} i(Vds) @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gm] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gds] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgg] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgs] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgd] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgb] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vth] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vdsat]
  
  * 3. Anchor 2 (VGS = 1.176)
  alter Vgs = 1.176
  dc Vds 0.0 3.3 0.1
  wrdata {temp_out_anc2} i(Vds) @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gm] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[gds] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgg] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgs] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgd] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[cgb] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vth] @m.xmn.msky130_fd_pr__nfet_g5v0d10v5[vdsat]
.endc
.end
"""
            # Clean up old output files
            for fpath in [temp_out, temp_out_anc1, temp_out_anc2]:
                if os.path.exists(fpath):
                    os.remove(fpath)
                    
            with open(temp_spice, 'w') as f:
                f.write(netlist)
                
            # Run ngspice
            res = subprocess.run(['ngspice', '-b', temp_spice], capture_output=True, text=True)
            if not os.path.exists(temp_out) or not os.path.exists(temp_out_anc1) or not os.path.exists(temp_out_anc2):
                print(f"Error: SPICE simulation failed for L={L} VSB={VSB}!")
                print(res.stderr)
                sys.exit(1)
                
            # Parse data
            raw_data = parse_wrdata(temp_out, 133 * 34)
            raw_data_anc1 = parse_wrdata(temp_out_anc1, 34)
            raw_data_anc2 = parse_wrdata(temp_out_anc2, 34)
            
            # Helper to assign slices into the 135-point VGS grid
            def assign_parameter(target_array, raw_unif, col_idx, sign_factor=1.0):
                for k in range(num_VDS):
                    unif_slice = raw_unif[k * 133 : (k + 1) * 133, col_idx] * sign_factor
                    # Target VGS slices: 0:37 -> unif 0:37; 38:49 -> unif 37:48; 50:135 -> unif 48:133
                    target_array[i, 0:37, k, j] = unif_slice[0:37]
                    target_array[i, 38:49, k, j] = unif_slice[37:48]
                    target_array[i, 50:135, k, j] = unif_slice[48:133]
                    
                    # Insert anchor values
                    target_array[i, 37, k, j] = raw_data_anc1[k, col_idx] * sign_factor
                    target_array[i, 49, k, j] = raw_data_anc2[k, col_idx] * sign_factor
            
            # Extract and store parameters (voltages/currents are positive)
            assign_parameter(nch['ID'], raw_data, 1, sign_factor=-1.0)
            assign_parameter(nch['GM'], raw_data, 2, sign_factor=1.0)
            assign_parameter(nch['GDS'], raw_data, 3, sign_factor=1.0)
            assign_parameter(nch['CGG'], raw_data, 4, sign_factor=1.0)
            assign_parameter(nch['CGS'], raw_data, 5, sign_factor=-1.0)
            assign_parameter(nch['CGD'], raw_data, 6, sign_factor=-1.0)
            assign_parameter(nch['CGB'], raw_data, 7, sign_factor=-1.0)
            assign_parameter(nch['VT'], raw_data, 8, sign_factor=1.0)
            assign_parameter(nch['VDSAT'], raw_data, 9, sign_factor=1.0)
                
    # Clean up temp files
    for fpath in [temp_spice, temp_out, temp_out_anc1, temp_out_anc2]:
        if os.path.exists(fpath):
            os.remove(fpath)
        
    # Save to pickle in lut/data/
    outfile = os.path.join(DATA_DIR, 'nfet_g5v0d10v5.pkl')
    with open(outfile, 'wb') as f:
        pickle.dump(nch, f)
    print(f"\nNFET Characterization Complete. Saved to '{outfile}'\n", flush=True)

def run_pfet_sweep():
    print("=== Characterizing PFET (sky130_fd_pr__pfet_g5v0d10v5) ===", flush=True)
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
    temp_out_anc1 = 'pfet_sweep_anc1.txt'
    temp_out_anc2 = 'pfet_sweep_anc2.txt'
    
    total_steps = num_L * num_VSB
    step_count = 0
    start_time = time.time()
    
    for i, L in enumerate(L_list):
        for j, VSB in enumerate(VSB_list):
            step_count += 1
            if step_count == 1 or step_count % 2 == 0 or step_count == total_steps:
                elapsed = time.time() - start_time
                avg_time = elapsed / step_count
                eta = (total_steps - step_count) * avg_time
                percent = (step_count / total_steps) * 100
                bar = '█' * int(percent // 5) + '░' * (20 - int(percent // 5))
                sys.stdout.write(
                    f"\r  Progress: [{bar}] {percent:5.1f}% ({step_count}/{total_steps}) | "
                    f"L={L:.2f} VSB={VSB:.2f} | "
                    f"Elapsed: {int(elapsed//60):02d}m{int(elapsed%60):02d}s | "
                    f"ETA: {int(eta//60):02d}m{int(eta%60):02d}s"
                )
                sys.stdout.flush()
            
            # Write SPICE netlist for this iteration
            netlist = f"""* PFET Sweep Temp
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.param L_val={L} VSB_val={VSB}

Vds d s 0.0
Vgs g s 0.0
Vsb b s {{VSB_val}}
Vs s 0 3.3

XMP d g s b sky130_fd_pr__pfet_g5v0d10v5 L={{L_val}} W=10

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
  
  * 1. Uniform Sweep (133 VGS points)
  dc Vgs 0.0 -3.3 -0.025 Vds 0.0 -3.3 -0.1
  wrdata {temp_out} i(Vds) @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gm] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gds] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgg] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgs] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgd] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgb] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vth] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vdsat]
  
  * 2. Anchor 1 (VGS = -0.920)
  alter Vgs = -0.92
  dc Vds 0.0 -3.3 -0.1
  wrdata {temp_out_anc1} i(Vds) @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gm] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gds] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgg] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgs] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgd] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgb] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vth] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vdsat]
  
  * 3. Anchor 2 (VGS = -1.176)
  alter Vgs = -1.176
  dc Vds 0.0 -3.3 -0.1
  wrdata {temp_out_anc2} i(Vds) @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gm] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gds] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgg] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgs] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgd] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgb] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vth] @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vdsat]
.endc
.end
"""
            # Clean up old output files
            for fpath in [temp_out, temp_out_anc1, temp_out_anc2]:
                if os.path.exists(fpath):
                    os.remove(fpath)
                    
            with open(temp_spice, 'w') as f:
                f.write(netlist)
                
            # Run ngspice
            res = subprocess.run(['ngspice', '-b', temp_spice], capture_output=True, text=True)
            if not os.path.exists(temp_out) or not os.path.exists(temp_out_anc1) or not os.path.exists(temp_out_anc2):
                print(f"Error: SPICE simulation failed for L={L} VSB={VSB}!")
                print(res.stderr)
                sys.exit(1)
                
            # Parse data
            raw_data = parse_wrdata(temp_out, 133 * 34)
            raw_data_anc1 = parse_wrdata(temp_out_anc1, 34)
            raw_data_anc2 = parse_wrdata(temp_out_anc2, 34)
            
            # Helper to assign slices into the 135-point VGS grid
            def assign_parameter(target_array, raw_unif, col_idx, sign_factor=1.0):
                for k in range(num_VDS):
                    unif_slice = raw_unif[k * 133 : (k + 1) * 133, col_idx] * sign_factor
                    # Target VGS slices: 0:37 -> unif 0:37; 38:49 -> unif 37:48; 50:135 -> unif 48:133
                    target_array[i, 0:37, k, j] = unif_slice[0:37]
                    target_array[i, 38:49, k, j] = unif_slice[37:48]
                    target_array[i, 50:135, k, j] = unif_slice[48:133]
                    
                    # Insert anchor values
                    target_array[i, 37, k, j] = raw_data_anc1[k, col_idx] * sign_factor
                    target_array[i, 49, k, j] = raw_data_anc2[k, col_idx] * sign_factor
            
            # Extract and store parameters (voltages/currents are positive)
            assign_parameter(pch['ID'], raw_data, 1, sign_factor=1.0)
            assign_parameter(pch['GM'], raw_data, 2, sign_factor=1.0)
            assign_parameter(pch['GDS'], raw_data, 3, sign_factor=1.0)
            assign_parameter(pch['CGG'], raw_data, 4, sign_factor=1.0)
            assign_parameter(pch['CGS'], raw_data, 5, sign_factor=-1.0)
            assign_parameter(pch['CGD'], raw_data, 6, sign_factor=-1.0)
            assign_parameter(pch['CGB'], raw_data, 7, sign_factor=-1.0)
            assign_parameter(pch['VT'], raw_data, 8, sign_factor=1.0)
            assign_parameter(pch['VDSAT'], raw_data, 9, sign_factor=1.0)
                
    # Clean up temp files
    for fpath in [temp_spice, temp_out, temp_out_anc1, temp_out_anc2]:
        if os.path.exists(fpath):
            os.remove(fpath)
        
    # Save to pickle in lut/data/
    outfile = os.path.join(DATA_DIR, 'pfet_g5v0d10v5.pkl')
    with open(outfile, 'wb') as f:
        pickle.dump(pch, f)
    print(f"\nPFET Characterization Complete. Saved to '{outfile}'\n", flush=True)

if __name__ == '__main__':
    run_nfet_sweep()
    run_pfet_sweep()
    print("All characterizations completed successfully!", flush=True)
