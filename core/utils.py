"""
Utility functions for file I/O, CSV export, and formatting
"""

import pandas as pd
from typing import Dict, Any, Optional
import io

def dataframe_to_csv(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV string"""
    output = io.StringIO()
    df.to_csv(output)
    return output.getvalue()

def format_unit(variable_name: str, metadata: Dict[str, Any]) -> str:
    """Format variable name with unit"""
    for var_info in metadata.get('variables', []):
        if var_info['name'] == variable_name:
            unit = var_info.get('unit', '')
            if unit:
                return f"{variable_name} ({unit})"
            elif variable_name.lower() == 'time':
                return "Time (s)"
            elif variable_name.lower() == 'frequency':
                return "Frequency (Hz)"
    return variable_name

def format_value(value: float, precision: int = 4) -> str:
    """Format numeric value with appropriate precision"""
    if abs(value) < 1e-3 or abs(value) > 1e6:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}"

def parse_spice_value(value_str: str) -> float:
    """Parse SPICE-format value (with suffixes like k, m, u, n, p)"""
    value_str = value_str.strip().upper()
    

    suffixes = {
        'T': 1e12,
        'G': 1e9,
        'MEG': 1e6,
        'K': 1e3,
        'M': 1e-3,
        'U': 1e-6,
        'N': 1e-9,
        'P': 1e-12,
        'F': 1e-15
    }
    
    for suffix, multiplier in suffixes.items():
        if value_str.endswith(suffix):
            num_part = value_str[:-len(suffix)]
            try:
                return float(num_part) * multiplier
            except ValueError:
                pass
    

    try:
        return float(value_str)
    except ValueError:
        raise ValueError(f"Cannot parse SPICE value: {value_str}")
from typing import Dict, Any, Optional
import io

def dataframe_to_csv(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV string"""
    output = io.StringIO()
    df.to_csv(output)
    return output.getvalue()

def format_unit(variable_name: str, metadata: Dict[str, Any]) -> str:
    """Format variable name with unit"""
    for var_info in metadata.get('variables', []):
        if var_info['name'] == variable_name:
            unit = var_info.get('unit', '')
            if unit:
                return f"{variable_name} ({unit})"
            elif variable_name.lower() == 'time':
                return "Time (s)"
            elif variable_name.lower() == 'frequency':
                return "Frequency (Hz)"
    return variable_name

def format_value(value: float, precision: int = 4) -> str:
    """Format numeric value with appropriate precision"""
    if abs(value) < 1e-3 or abs(value) > 1e6:
        return f"{value:.{precision}e}"
    else:
        return f"{value:.{precision}f}"

def parse_spice_value(value_str: str) -> float:
    """Parse SPICE-format value (with suffixes like k, m, u, n, p)"""
    value_str = value_str.strip().upper()
    

    suffixes = {
        'T': 1e12,
        'G': 1e9,
        'MEG': 1e6,
        'K': 1e3,
        'M': 1e-3,
        'U': 1e-6,
        'N': 1e-9,
        'P': 1e-12,
        'F': 1e-15
    }
    
    for suffix, multiplier in suffixes.items():
        if value_str.endswith(suffix):
            num_part = value_str[:-len(suffix)]
            try:
                return float(num_part) * multiplier
            except ValueError:
                pass
    

    try:
        return float(value_str)
    except ValueError:
        raise ValueError(f"Cannot parse SPICE value: {value_str}")