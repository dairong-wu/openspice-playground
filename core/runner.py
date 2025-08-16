"""
NgSpice runner with subprocess management and safety controls
"""

import subprocess
import tempfile
import os
import shutil
from pathlib import Path
from typing import Tuple, Optional
import time

# Default timeout in seconds (can be overridden by environment variable)
DEFAULT_TIMEOUT = int(os.environ.get('NGSPICE_TIMEOUT', '10'))

def run_ngspice(netlist: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[bool, str, Optional[str]]:
    """
    Run ngspice in batch mode with the given netlist
    
    Args:
        netlist: Sanitized netlist content
        timeout: Maximum execution time in seconds
    
    Returns:
        (success, log_content, raw_file_path)
    """
    
    # Create temporary directory for safe execution
    with tempfile.TemporaryDirectory(prefix='ngspice_') as tmpdir:
        try:
            # Write netlist to temporary file
            netlist_path = Path(tmpdir) / 'input.cir'
            netlist_path.write_text(netlist)
            
            # Output paths
            log_path = Path(tmpdir) / 'stdout.log'
            raw_path = Path(tmpdir) / 'output.raw'
            
            # Construct ngspice command
            cmd = [
                'ngspice',
                '-b',              # Batch mode
                '-o', str(log_path),  # Output log
                '-r', str(raw_path),  # Raw output file
                str(netlist_path)     # Input netlist
            ]
            
            # Run ngspice with timeout
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return False, f"Simulation timeout after {timeout} seconds", None
            
            # Read log file
            log_content = ""
            if log_path.exists():
                log_content = log_path.read_text()
            else:
                log_content = stdout if stdout else ""
            
            if stderr:
                log_content += f"\n\nSTDERR:\n{stderr}"
            
            log_content += f"\n\nExecution time: {execution_time:.2f} seconds"
            
            # Check if simulation was successful
            success = process.returncode == 0 and raw_path.exists()
            
            if success:
                # Copy raw file to a persistent location
                persistent_raw = tempfile.NamedTemporaryFile(
                    mode='wb',
                    suffix='.raw',
                    delete=False
                )
                shutil.copy2(raw_path, persistent_raw.name)
                persistent_raw.close()
                return True, log_content, persistent_raw.name
            else:
                return False, log_content, None
                
        except FileNotFoundError:
            return False, "ngspice not found. Please install ngspice.", None
        except Exception as e:
            return False, f"Error running ngspice: {str(e)}", None

def check_ngspice_installed() -> bool:
    """Check if ngspice is installed and accessible"""
    try:
        result = subprocess.run(
            ['ngspice', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
