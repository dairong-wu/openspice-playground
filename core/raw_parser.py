"""
ASCII RAW file parser for ngspice output
Parses the ASCII RAW format into pandas DataFrame
"""

import re
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Any
from pathlib import Path

def parse_ascii_raw(raw_file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parse ngspice ASCII RAW file
    
    Args:
        raw_file_path: Path to the RAW file
    
    Returns:
        (DataFrame with results, metadata dictionary)
    """
    
    with open(raw_file_path, 'r') as f:
        lines = f.readlines()
    
    metadata = {
        'title': '',
        'date': '',
        'plotname': '',
        'flags': '',
        'no_variables': 0,
        'no_points': 0,
        'variables': []
    }
    

    i = 0
    values_start = -1
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('Title:'):
            metadata['title'] = line[6:].strip()
        elif line.startswith('Date:'):
            metadata['date'] = line[5:].strip()
        elif line.startswith('Plotname:'):
            metadata['plotname'] = line[9:].strip()
        elif line.startswith('Flags:'):
            metadata['flags'] = line[6:].strip()
        elif line.startswith('No. Variables:'):
            metadata['no_variables'] = int(line.split(':')[1].strip())
        elif line.startswith('No. Points:'):
            metadata['no_points'] = int(line.split(':')[1].strip())
        elif line.startswith('Variables:'):

            i += 1
            var_idx = 0
            while var_idx < metadata['no_variables'] and i < len(lines):
                var_line = lines[i].strip()
                if var_line and not var_line.startswith('Values:'):


                    parts = re.split(r'\s+', var_line)
                    if len(parts) >= 3:
                        var_info = {
                            'index': int(parts[0]),
                            'name': parts[1],
                            'type': parts[2]
                        }
                        if len(parts) > 3:
                            var_info['unit'] = ' '.join(parts[3:])
                        else:
                            var_info['unit'] = ''
                        metadata['variables'].append(var_info)
                        var_idx += 1
                    i += 1
                elif var_line.startswith('Values:'):

                    values_start = i + 1
                    break
                else:
                    i += 1
            break
        i += 1
    

    if values_start == -1:
        for j in range(i, len(lines)):
            if lines[j].strip().startswith('Values:'):
                values_start = j + 1
                break
    
    if values_start == -1:

        return pd.DataFrame(), metadata
    

    data_lines = []
    for j in range(values_start, len(lines)):
        line = lines[j].strip()
        if line and not line.startswith('Binary:'):
            data_lines.append(line)
    

    n_vars = metadata['no_variables']
    n_points = metadata['no_points']
    

    is_tab_format = False
    if data_lines and len(data_lines) > 0:

        for line in data_lines[:min(3, len(data_lines))]:
            if '\t' in line:
                is_tab_format = True
                break
    
    data = []
    line_idx = 0
    
    if is_tab_format:

        for point_idx in range(n_points):
            if line_idx >= len(data_lines):
                break
                
            point_data = []
            

            first_line = data_lines[line_idx].strip()
            

            if '\t' in first_line:
                parts = first_line.split('\t', 1)
                if len(parts) >= 2:

                    value_str = parts[1].strip()
                    point_data.append(parse_value(value_str))
                line_idx += 1
            else:

                line_idx += 1
                if line_idx < len(data_lines):

                    value_line = data_lines[line_idx].strip()

                    if value_line.startswith('\t'):
                        value_line = value_line[1:]
                    point_data.append(parse_value(value_line))
                    line_idx += 1
            

            for var_idx in range(1, n_vars):
                if line_idx >= len(data_lines):
                    break
                    
                value_line = data_lines[line_idx].strip()
                

                if value_line.startswith('\t'):
                    value_line = value_line[1:]
                elif '\t' in value_line:

                    parts = value_line.split('\t', 1)
                    if len(parts) >= 2:
                        value_line = parts[1]
                
                point_data.append(parse_value(value_line))
                line_idx += 1
            
            if len(point_data) == n_vars:
                data.append(point_data)
    else:

        for point_idx in range(n_points):
            if line_idx >= len(data_lines):
                break
                
            point_data = []
            

            first_line = data_lines[line_idx].strip()
            try:

                int(first_line)

                line_idx += 1
            except ValueError:

                pass
            

            for var_idx in range(n_vars):
                if line_idx >= len(data_lines):
                    break
                    
                value_line = data_lines[line_idx].strip()
                point_data.append(parse_value(value_line))
                line_idx += 1
            
            if len(point_data) == n_vars:
                data.append(point_data)
    

    if data:

        columns = [var['name'] for var in metadata['variables']]
        

        df = pd.DataFrame(data, columns=columns)
        

        x_var = None
        for var in metadata['variables']:
            if var['name'].lower() in ['time', 'frequency']:
                x_var = var['name']
                break
        

        if x_var and x_var in df.columns:
            df = df.set_index(x_var)
    else:
        df = pd.DataFrame()
    
    return df, metadata

def parse_value(value_str: str) -> float:
    """
    Parse a single value from RAW file
    Handles real numbers, complex numbers, and scientific notation
    """
    value_str = value_str.strip()
    

    if ',' in value_str:
        real_imag = value_str.split(',')
        try:
            real_part = float(real_imag[0].strip())
            imag_part = float(real_imag[1].strip()) if len(real_imag) > 1 else 0.0
            if imag_part != 0:
                return complex(real_part, imag_part)
            else:
                return real_part
        except ValueError:
            return 0.0
    else:

        try:
            return float(value_str.strip())
        except ValueError:
            return 0.0