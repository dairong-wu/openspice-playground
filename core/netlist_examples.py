"""
Pre-defined netlist examples and parametric circuit generators
"""

from typing import Dict, Any

EXAMPLES = {
    "RC Low-Pass Filter (AC/TRAN)": """* RC Low-Pass Filter
Vin in 0 AC 1 SIN(0 1 1k)
R1 in out 1k
C1 out 0 1u
.ac dec 50 10 1e6
.tran 10us 10ms
.end""",
    
    "CMOS Inverter (Level 1)": """* CMOS Inverter (Level 1)
Vdd vdd 0 1.8
Vin in 0 PULSE(0 1.8 0 1n 1n 50n 100n)
M1 out in 0 0 NMOS L=1u W=10u
M2 out in vdd vdd PMOS L=1u W=10u
.model NMOS NMOS (LEVEL=1 VTO=0.5 KP=100e-6 LAMBDA=0.02)
.model PMOS PMOS (LEVEL=1 VTO=-0.5 KP=50e-6 LAMBDA=0.02)
.tran 0.1n 200n
.end""",
    
    "BJT CE Amplifier (AC)": """* BJT CE Amplifier AC
Vin in 0 AC 1
Rb in base 100k
Rc vcc out 4.7k
Re emit 0 1k
Cc out load 1u
Vcc vcc 0 12
Q1 out base emit QNPN
.model QNPN NPN (BF=100 IS=1e-15)
.ac dec 100 10 10Meg
.end""",
    
    "RLC Resonant Circuit": """* RLC Series Resonant Circuit
Vin in 0 AC 1
R1 in n1 50
L1 n1 n2 10m
C1 n2 0 100n
.ac dec 100 100 100k
.end""",
    
    "Diode Rectifier": """* Half-Wave Rectifier
Vin in 0 SIN(0 10 50)
D1 in out DIODE
R1 out 0 1k
C1 out 0 100u
.model DIODE D (IS=1e-14 RS=0.1)
.tran 0.1ms 100ms
.end""",
    
    "Op-Amp Inverting Amplifier": """* Ideal Op-Amp Inverting Amplifier
Vin in 0 SIN(0 0.1 1k)
Rin in n_inv 10k
Rf n_inv out 100k
* Ideal op-amp (VCVS with high gain)
Eop out 0 0 n_inv 1e6
.tran 10us 5ms
.end"""
}

def get_example_netlist(name: str) -> str:
    """Get example netlist by name"""
    return EXAMPLES.get(name, "")

def generate_parametric_netlist(circuit_type: str, **params: Any) -> str:
    """Generate parametric netlist based on circuit type and parameters"""
    
    if circuit_type == "rc_lowpass":
        R = params.get('R', 1000)
        C = params.get('C', 1e-6)
        Vin = params.get('Vin', 1)
        freq = params.get('freq', 1000)
        
        return f"""* Parametric RC Low-Pass Filter
* R = {R} ohms, C = {C*1e6} uF
* Vin = {Vin} V, freq = {freq} Hz
Vin in 0 AC {Vin} SIN(0 {Vin} {freq})
R1 in out {R}
C1 out 0 {C}
.ac dec 50 1 1e7
.tran {1/(freq*100)} {10/freq}
.end"""
    
    elif circuit_type == "rc_highpass":
        R = params.get('R', 1000)
        C = params.get('C', 1e-6)
        Vin = params.get('Vin', 1)
        
        return f"""* Parametric RC High-Pass Filter
* R = {R} ohms, C = {C*1e6} uF
Vin in 0 AC {Vin}
C1 in n1 {C}
R1 n1 0 {R}
.ac dec 50 1 1e7
.end"""
    
    elif circuit_type == "rlc_filter":
        R = params.get('R', 50)
        L = params.get('L', 1e-3)
        C = params.get('C', 1e-6)
        
        return f"""* Parametric RLC Filter
* R = {R} ohms, L = {L*1e3} mH, C = {C*1e6} uF
Vin in 0 AC 1
R1 in n1 {R}
L1 n1 n2 {L}
C1 n2 0 {C}
.ac dec 100 10 1e6
.end"""
    
    return "* Unknown circuit type"