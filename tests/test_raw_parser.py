"""Tests for RAW file parser"""

import pytest
import tempfile
from pathlib import Path
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.raw_parser import parse_ascii_raw

def create_test_raw_file():
    """Create a test RAW file (old format without tabs)"""
    content = """Title: Test Circuit
Date: Mon Jan 01 00:00:00 2024
Plotname: Transient Analysis
Flags: real
No. Variables: 3
No. Points: 5
Variables:
 0 time time
 1 v(in) voltage
 2 v(out) voltage
Values:
0
 0.000000e+00
 0.000000e+00
 0.000000e+00
1
 1.000000e-03
 1.000000e+00
 6.321206e-01
2
 2.000000e-03
 1.000000e+00
 8.646647e-01
3
 3.000000e-03
 1.000000e+00
 9.502129e-01
4
 4.000000e-03
 1.000000e+00
 9.816844e-01
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.raw', delete=False) as f:
        f.write(content)
        return f.name

def create_test_raw_file_with_tabs():
    """Create a test RAW file with tab-separated format (ngspice actual output)"""
    content = """Title: Test Circuit
Date: Mon Jan 01 00:00:00 2024
Plotname: Transient Analysis
Flags: real
No. Variables: 3
No. Points: 5
Variables:
 0	time	time
 1	v(in)	voltage
 2	v(out)	voltage
Values:
0	0.000000e+00
	0.000000e+00
	0.000000e+00
1	1.000000e-03
	1.000000e+00
	6.321206e-01
2	2.000000e-03
	1.000000e+00
	8.646647e-01
3	3.000000e-03
	1.000000e+00
	9.502129e-01
4	4.000000e-03
	1.000000e+00
	9.816844e-01
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.raw', delete=False) as f:
        f.write(content)
        return f.name

def test_parse_ascii_raw():
    """Test parsing of ASCII RAW file (old format)"""
    raw_file = create_test_raw_file()
    
    try:
        df, metadata = parse_ascii_raw(raw_file)
        

        assert metadata['title'] == 'Test Circuit'
        assert metadata['no_variables'] == 3
        assert metadata['no_points'] == 5
        assert len(metadata['variables']) == 3
        

        assert len(df) == 5
        assert 'v(in)' in df.columns
        assert 'v(out)' in df.columns
        assert df.index.name == 'time'
        

        assert df.index[0] == 0.0

        assert df['v(in)'].iloc[0] == 0.0
        assert df['v(in)'].iloc[1] == 1.0
        assert abs(df['v(out)'].iloc[1] - 0.6321206) < 1e-6
        
    finally:
        Path(raw_file).unlink()

def test_parse_ascii_raw_with_tabs():
    """Test parsing of ASCII RAW file with tab-separated values"""
    raw_file = create_test_raw_file_with_tabs()
    
    try:
        df, metadata = parse_ascii_raw(raw_file)
        

        assert metadata['title'] == 'Test Circuit'
        assert metadata['no_variables'] == 3
        assert metadata['no_points'] == 5
        

        assert len(df) == 5
        assert 'v(in)' in df.columns
        assert 'v(out)' in df.columns
        

        assert df.index[0] == 0.0
        assert df.index[1] == 0.001
        assert df['v(in)'].iloc[0] == 0.0
        assert df['v(in)'].iloc[1] == 1.0
        
    finally:
        Path(raw_file).unlink()

def test_parse_complex_raw():
    """Test parsing RAW file with complex numbers (AC analysis)"""
    content = """Title: AC Analysis
Date: Mon Jan 01 00:00:00 2024
Plotname: AC Analysis
Flags: complex
No. Variables: 2
No. Points: 3
Variables:
 0	frequency	frequency
 1	v(out)	voltage
Values:
0	1.000000e+01
	1.000000e+00,0.000000e+00
1	1.000000e+02
	7.071068e-01,-7.071068e-01
2	1.000000e+03
	1.000000e-01,-9.949874e-01
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.raw', delete=False) as f:
        f.write(content)
        raw_file = f.name
    
    try:
        df, metadata = parse_ascii_raw(raw_file)
        
        assert metadata['flags'] == 'complex'
        assert len(df) == 3
        assert df.index.name == 'frequency'
        

        val = df['v(out)'].iloc[1]
        if isinstance(val, complex):
            assert abs(val.real - 0.7071068) < 1e-6
            assert abs(val.imag + 0.7071068) < 1e-6
        
    finally:
        Path(raw_file).unlink()

def test_parse_mixed_format():
    """Test parsing RAW file with mixed tab formats (real ngspice output)"""

    content = """Title: BJT Circuit
Date: Mon Jan 01 00:00:00 2024
Plotname: AC Analysis
Flags: complex
No. Variables: 2
No. Points: 3
Variables:
 0	frequency	frequency
 1	v(out)	voltage
Values:
0	1.000000e+01
	1.000000e+00,0.000000e+00
1	1.000000e+02
0	7.071068e-01,-7.071068e-01
2	1.000000e+03
0	1.000000e-01,-9.949874e-01
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.raw', delete=False) as f:
        f.write(content)
        raw_file = f.name
    
    try:
        df, metadata = parse_ascii_raw(raw_file)
        

        assert len(df) > 0
        assert 'v(out)' in df.columns
        
    finally:
        Path(raw_file).unlink()

if __name__ == "__main__":
    test_parse_ascii_raw()
    test_parse_ascii_raw_with_tabs()
    test_parse_complex_raw()
    test_parse_mixed_format()
    print("All RAW parser tests passed!")