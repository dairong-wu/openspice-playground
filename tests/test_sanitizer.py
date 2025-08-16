"""Tests for netlist sanitizer"""

import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sanitizer import sanitize_netlist, check_netlist_safety

def test_remove_dangerous_commands():
    """Test removal of dangerous commands"""
    
    netlist = """* Test circuit
V1 in 0 1
R1 in out 1k
.shell rm -rf /
!ls -la
source /etc/passwd
cd ..
write /etc/shadow
.end
"""
    
    sanitized = sanitize_netlist(netlist)
    


    lines = sanitized.split('\n')
    

    dangerous_found = False
    for line in lines:
        if line.strip().startswith('*'):

            continue

        if '.shell' in line.lower() and not line.strip().startswith('*'):
            dangerous_found = True
        if '!' in line and not line.strip().startswith('*'):
            dangerous_found = True
        if '/etc/passwd' in line and not line.strip().startswith('*'):
            dangerous_found = True
        if '/etc/shadow' in line and not line.strip().startswith('*'):
            dangerous_found = True
    
    assert not dangerous_found, "Dangerous commands were not properly removed"
    

    assert 'V1 in 0 1' in sanitized
    assert 'R1 in out 1k' in sanitized

def test_add_control_block():
    """Test automatic addition of .control block"""
    
    netlist = """* Simple RC
V1 in 0 1
R1 in out 1k
C1 out 0 1u
.tran 1ms 10ms
.end
"""
    
    sanitized = sanitize_netlist(netlist)
    

    assert '.control' in sanitized
    assert 'set filetype=ascii' in sanitized
    assert 'run' in sanitized
    assert 'write output.raw' in sanitized
    assert 'quit' in sanitized
    assert '.endc' in sanitized

def test_modify_existing_control():
    """Test modification of existing .control block"""
    
    netlist = """* Test
V1 in 0 1
.control
run
.endc
.end
"""
    
    sanitized = sanitize_netlist(netlist)
    

    assert 'set filetype=ascii' in sanitized
    assert 'write output.raw' in sanitized
    assert 'quit' in sanitized

def test_check_safety():
    """Test safety checker"""
    
    safe_netlist = """* Safe circuit
V1 in 0 1
R1 in out 1k
.end
"""
    
    unsafe_netlist = """* Unsafe circuit
V1 in 0 1
.shell echo "dangerous"
.end
"""
    
    is_safe, warnings = check_netlist_safety(safe_netlist)
    assert is_safe
    assert len(warnings) == 0
    
    is_safe, warnings = check_netlist_safety(unsafe_netlist)
    assert not is_safe
    assert len(warnings) > 0

if __name__ == "__main__":
    test_remove_dangerous_commands()
    test_add_control_block()
    test_modify_existing_control()
    test_check_safety()
    print("All sanitizer tests passed!")