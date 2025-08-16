"""Test running example circuits"""

import sys
import os
import pytest


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.netlist_examples import EXAMPLES
from core.sanitizer import sanitize_netlist
from core.runner import run_ngspice, check_ngspice_installed
from core.raw_parser import parse_ascii_raw


SKIP_HEAVY = os.environ.get('CI_SKIP_HEAVY', 'false').lower() == 'true'

@pytest.mark.skipif(not check_ngspice_installed(), reason="ngspice not installed")
def test_rc_filter():
    """Test RC filter simulation"""
    netlist = EXAMPLES["RC Low-Pass Filter (AC/TRAN)"]
    sanitized = sanitize_netlist(netlist)
    
    success, log, raw_path = run_ngspice(sanitized, timeout=5)
    
    assert success, f"Simulation failed: {log}"
    assert raw_path and os.path.exists(raw_path)
    

    df, metadata = parse_ascii_raw(raw_path)
    assert len(df) > 0
    assert 'v(out)' in df.columns or 'V(out)' in df.columns
    

    if raw_path:
        os.unlink(raw_path)

@pytest.mark.skipif(not check_ngspice_installed(), reason="ngspice not installed")
def test_bjt_amplifier():
    """Test BJT amplifier simulation"""
    netlist = EXAMPLES["BJT CE Amplifier (AC)"]
    sanitized = sanitize_netlist(netlist)
    
    success, log, raw_path = run_ngspice(sanitized, timeout=5)
    
    assert success, f"Simulation failed: {log}"
    assert raw_path and os.path.exists(raw_path)
    

    df, metadata = parse_ascii_raw(raw_path)
    assert len(df) > 0
    

    if raw_path:
        os.unlink(raw_path)

@pytest.mark.skipif(SKIP_HEAVY or not check_ngspice_installed(), reason="Skipping heavy test or ngspice not installed")
def test_cmos_inverter():
    """Test CMOS inverter simulation (heavy test)"""
    netlist = EXAMPLES["CMOS Inverter (Level 1)"]
    sanitized = sanitize_netlist(netlist)
    
    success, log, raw_path = run_ngspice(sanitized, timeout=10)
    
    assert success, f"Simulation failed: {log}"
    assert raw_path and os.path.exists(raw_path)
    

    df, metadata = parse_ascii_raw(raw_path)
    assert len(df) > 0
    assert 'time' in [v['name'].lower() for v in metadata['variables']]
    

    if raw_path:
        os.unlink(raw_path)

if __name__ == "__main__":
    if check_ngspice_installed():
        test_rc_filter()
        test_bjt_amplifier()
        if not SKIP_HEAVY:
            test_cmos_inverter()
        print("All example tests passed!")
    else:
        print("ngspice not installed, skipping tests")