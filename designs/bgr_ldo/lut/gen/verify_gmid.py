import os
import sys

# Ensure parent directory (lut/) is in python path
GEN_DIR = os.path.dirname(os.path.abspath(__file__))
LUT_DIR = os.path.dirname(GEN_DIR)
if LUT_DIR not in sys.path:
    sys.path.insert(0, LUT_DIR)

import lookup

print("=== Verifying NFET LUT Lookup Values ===")
try:
    # Perform lookups for Vth (VT) at L=4.0um, VDS=0.25V, VGS=1.0V, VSB=0.0V / 0.78V
    vth_vsb0 = lookup.lookup('nfet', 'VT', L=4e-6, VGS=1.0, VDS=0.25, VSB=0.0)
    vth_vsb078 = lookup.lookup('nfet', 'VT', L=4e-6, VGS=1.0, VDS=0.25, VSB=0.78)
    
    print("\n--- Vth (VT) Check ---")
    print(f"VT (VSB=0.0, L=4.0um)  = {vth_vsb0:.4f} V (Expected ~0.647V)")
    print(f"VT (VSB=0.78, L=4.0um) = {vth_vsb078:.4f} V (Expected ~1.068V)")
    
    # Calculate error
    err_vsb0 = abs(vth_vsb0 - 0.647)
    err_vsb078 = abs(vth_vsb078 - 1.068)
    print(f"VSB=0.0 absolute error: {err_vsb0:.4f} V")
    print(f"VSB=0.78 absolute error: {err_vsb078:.4f} V")
    
    # Check if they are within acceptable margins
    if err_vsb0 < 0.05 and err_vsb078 < 0.05:
        print(">> Vth verification: SUCCESS")
    else:
        print(">> Vth verification: WARNING - Discrepancy observed")
        
    # Perform additional queries
    id_val = lookup.lookup('nfet', 'ID', L=4e-6, VGS=1.0, VDS=0.25, VSB=0.0)
    gm_val = lookup.lookup('nfet', 'GM', L=4e-6, VGS=1.0, VDS=0.25, VSB=0.0)
    print(f"\n--- Additional operating point data at VGS=1.0V, VDS=0.25V ---")
    print(f"ID                     = {id_val*1e6:.4f} uA")
    print(f"GM                     = {gm_val*1e6:.4f} uS")
    print(f"gm/Id ratio            = {gm_val/id_val:.4f} V^-1")
    
except Exception as e:
    print("Error during lookups:", e)
    print("Please make sure you have executed the sweep script ('run_sweep.py') to generate the pkl data files first.")
