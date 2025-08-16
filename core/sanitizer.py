"""
Netlist sanitizer for security and safety
Removes dangerous commands and ensures proper .control block
"""

import re
from typing import List, Tuple


DANGEROUS_PATTERNS = [
    (r'\.shell\s+.*', 'shell command'),
    (r'\!.*', 'shell escape'),
    (r'source\s+["\']?/.*', 'absolute path source'),
    (r'source\s+.*\.\./', 'path traversal'),
    (r'cd\s+.*', 'change directory'),
    (r'write\s+["\']?/.*', 'write to absolute path'),
    (r'write\s+.*\.\./', 'write with path traversal'),
    (r'rusage.*', 'resource usage'),
]

def sanitize_netlist(netlist: str) -> str:
    """
    Sanitize netlist for safe execution
    - Remove dangerous commands
    - Ensure proper .control block with ASCII output
    """
    lines = netlist.split('\n')
    sanitized_lines = []
    in_control = False
    control_start_idx = -1
    control_end_idx = -1
    has_control = False
    

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        

        if line_lower.startswith('.control'):
            in_control = True
            has_control = True
            control_start_idx = len(sanitized_lines)
            sanitized_lines.append(line)
            continue
        elif line_lower.startswith('.endc'):
            in_control = False
            control_end_idx = len(sanitized_lines)
            sanitized_lines.append(line)
            continue
        

        is_dangerous = False
        for pattern, description in DANGEROUS_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                is_dangerous = True

                sanitized_lines.append(f"* REMOVED (security - {description}): {line}")
                break
        
        if not is_dangerous:
            sanitized_lines.append(line)
    

    if has_control and control_start_idx >= 0:

        control_lines = []
        has_filetype = False
        has_run = False
        has_write = False
        has_quit = False
        

        for i in range(control_start_idx + 1, control_end_idx):
            if i < len(sanitized_lines):
                line_lower = sanitized_lines[i].lower().strip()
                if 'set filetype' in line_lower:
                    has_filetype = True
                if line_lower == 'run':
                    has_run = True
                if 'write' in line_lower and 'output.raw' in line_lower:
                    has_write = True
                if line_lower == 'quit':
                    has_quit = True
                

                is_safe = True
                for pattern, _ in DANGEROUS_PATTERNS:
                    if re.search(pattern, sanitized_lines[i], re.IGNORECASE):
                        is_safe = False
                        break
                if is_safe:
                    control_lines.append(sanitized_lines[i])
        

        new_control = ['.control']
        if not has_filetype:
            new_control.append('set filetype=ascii')
        if not has_run:
            new_control.append('run')
        

        for line in control_lines:
            if not any(x in line.lower() for x in ['set filetype', 'run', 'write', 'quit']):
                new_control.append(line)
        
        if not has_write:
            new_control.append('write output.raw')
        if not has_quit:
            new_control.append('quit')
        new_control.append('.endc')
        

        sanitized_lines = (
            sanitized_lines[:control_start_idx] +
            new_control +
            sanitized_lines[control_end_idx + 1:]
        )
    else:

        end_idx = -1
        for i in range(len(sanitized_lines) - 1, -1, -1):
            if sanitized_lines[i].lower().strip().startswith('.end'):
                end_idx = i
                break
        
        if end_idx >= 0:
            control_block = [
                '.control',
                'set filetype=ascii',
                'run',
                'write output.raw',
                'quit',
                '.endc'
            ]
            sanitized_lines = (
                sanitized_lines[:end_idx] +
                control_block +
                sanitized_lines[end_idx:]
            )
        else:

            sanitized_lines.extend([
                '.control',
                'set filetype=ascii',
                'run',
                'write output.raw',
                'quit',
                '.endc',
                '.end'
            ])
    
    return '\n'.join(sanitized_lines)

def check_netlist_safety(netlist: str) -> Tuple[bool, List[str]]:
    """
    Check if netlist contains dangerous commands
    Returns (is_safe, list_of_warnings)
    """
    warnings = []
    
    for pattern, description in DANGEROUS_PATTERNS:
        matches = re.findall(pattern, netlist, re.IGNORECASE | re.MULTILINE)
        if matches:
            warnings.append(f"Found dangerous pattern ({description}): {pattern}")
    
    return len(warnings) == 0, warnings