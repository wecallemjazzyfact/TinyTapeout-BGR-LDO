import os
import sys

# Ensure local pygmid package inside lut/ is in the python path
LUT_DIR = os.path.dirname(os.path.abspath(__file__))
if LUT_DIR not in sys.path:
    sys.path.insert(0, LUT_DIR)

from pygmid import Lookup as lk

# Load tables
nfet_pkl = os.path.join(LUT_DIR, 'data', 'nfet_g5v0d10v5.pkl')
pfet_pkl = os.path.join(LUT_DIR, 'data', 'pfet_g5v0d10v5.pkl')

nfet = None
pfet = None

if os.path.exists(nfet_pkl):
    try:
        nfet = lk(nfet_pkl)
    except Exception as e:
        print(f"Warning: Failed to load NFET LUT from {nfet_pkl}: {e}")
if os.path.exists(pfet_pkl):
    try:
        pfet = lk(pfet_pkl)
    except Exception as e:
        print(f"Warning: Failed to load PFET LUT from {pfet_pkl}: {e}")

def lookup(device, outvar, **kwargs):
    """
    Perform transistor lookup.
    
    Args:
        device (str): 'nfet' or 'pfet' (case-insensitive)
        outvar (str): Parameter to look up (e.g. 'VT', 'GM', 'ID', 'GDS', 'CGG', etc.
                      or ratio like 'GM_ID', 'GM_CGG', etc.)
        **kwargs: Sizing parameters: L, VGS, VDS, VSB, etc.
    """
    dev = device.lower()
    if dev == 'nfet':
        if nfet is None:
            raise RuntimeError("NFET lookup table not loaded! Please run the sweep script first.")
        return nfet.look_up(outvar, **kwargs)
    elif dev == 'pfet':
        if pfet is None:
            raise RuntimeError("PFET lookup table not loaded! Please run the sweep script first.")
        return pfet.look_up(outvar, **kwargs)
    else:
        raise ValueError(f"Unknown device type: {device}. Must be 'nfet' or 'pfet'.")

def lookupVGS(device, **kwargs):
    """
    Look up VGS for a given current density (ID_W) or inversion level (GM_ID).
    
    Args:
        device (str): 'nfet' or 'pfet'
        **kwargs: Sizing parameters: GM_ID or ID_W, L, VDS, VSB, etc.
    """
    dev = device.lower()
    if dev == 'nfet':
        if nfet is None:
            raise RuntimeError("NFET lookup table not loaded! Please run the sweep script first.")
        return nfet.look_upVGS(**kwargs)
    elif dev == 'pfet':
        if pfet is None:
            raise RuntimeError("PFET lookup table not loaded! Please run the sweep script first.")
        return pfet.look_upVGS(**kwargs)
    else:
        raise ValueError(f"Unknown device type: {device}. Must be 'nfet' or 'pfet'.")
