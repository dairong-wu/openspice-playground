# ⚡ OpenSPICE Playground

A web-based circuit simulator powered by ngspice and Streamlit. Design, simulate, and analyze electronic circuits directly in your browser with an intuitive interface and real-time visualization.

![OpenSPICE Playground](assets/screenshot.png)

## ✨ Features

- 📝 **Interactive Netlist Editor** - Write and edit SPICE netlists with syntax highlighting
- 🎯 **Pre-built Examples** - Load ready-to-use circuit examples with one click
- 🔧 **Parametric Circuit Generator** - Generate circuits with customizable parameters
- 📊 **Interactive Waveform Viewer** - Visualize simulation results with matplotlib
- 📁 **Export Capabilities** - Download results as CSV or RAW format
- 🔒 **Security First** - Sandboxed execution with command filtering
- ⏱️ **Resource Protection** - Automatic timeout and temporary file management

## 🚀 Quick Start

### Local Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/openspice-playground.git
cd openspice-playground
```

2. **Install ngspice:**
```bash
# Ubuntu/Debian
sudo apt-get install ngspice

# macOS
brew install ngspice

# Windows
# Download from http://ngspice.sourceforge.net/
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
streamlit run app.py
```

5. **Open your browser to** `http://localhost:8501`

### 🐳 Docker

```bash
# Build the image
docker build -t openspice-playground .

# Run the container
docker run -p 7860:7860 openspice-playground
```

Access the application at `http://localhost:7860`

## 📖 Usage Guide

### Basic Workflow

1. **Write or load a netlist** - Use the editor or select an example
2. **Run simulation** - Click the "Run Simulation" button
3. **View results** - Select traces to plot and explore the data
4. **Export data** - Download CSV or RAW files for further analysis

### Netlist Syntax (ngspice standard)

```spice
* Circuit Title (first line is always a comment)
* Component definitions
Vname n+ n- [DC value] [AC mag phase] [transient_spec]
Rname n1 n2 value
Cname n1 n2 value
Lname n1 n2 value

* Analysis commands
.tran tstep tstop [tstart [tmax]]
.ac dec|lin|oct points fstart fstop
.dc source start stop step

* End statement (required)
.end
```

### Example Circuits

#### RC Low-Pass Filter
```spice
* RC Low-Pass Filter
Vin in 0 AC 1 SIN(0 1 1k)
R1 in out 1k
C1 out 0 1u
.ac dec 50 10 1e6
.tran 10us 10ms
.end
```

#### CMOS Inverter
```spice
* CMOS Inverter (Level 1)
Vdd vdd 0 1.8
Vin in 0 PULSE(0 1.8 0 1n 1n 50n 100n)
M1 out in 0 0 NMOS L=1u W=10u
M2 out in vdd vdd PMOS L=1u W=10u
.model NMOS NMOS (LEVEL=1 VTO=0.5 KP=100e-6 LAMBDA=0.02)
.model PMOS PMOS (LEVEL=1 VTO=-0.5 KP=50e-6 LAMBDA=0.02)
.tran 0.1n 200n
.end
```

#### BJT CE Amplifier
```spice
* BJT CE Amplifier AC
Vin in 0 AC 1
Rb in base 100k
Rc vcc out 4.7k
Re emit 0 1k
Cc out load 1u
Vcc vcc 0 12
Q1 out base emit QNPN
.model QNPN NPN (BF=100 IS=1e-15)
.ac dec 100 10 10Meg
.end
```

## 🔒 Security Features

- **Command Filtering**: Dangerous commands like `.shell`, `!`, and file system access are blocked
- **Sandboxed Execution**: All simulations run in temporary directories
- **Timeout Protection**: Default 10-second timeout (configurable via `NGSPICE_TIMEOUT`)
- **Path Sanitization**: Prevents directory traversal and absolute path access

## 🚀 Deployment

### Hugging Face Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Select "Docker" as the SDK
3. Upload this repository
4. The app will automatically deploy

### Streamlit Cloud

1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with default settings
4. Add `ngspice` to system packages in Advanced Settings

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=core

# Skip heavy tests
CI_SKIP_HEAVY=true pytest tests/
```

## 📦 Project Structure

```
openspice-playground/
├─ app.py                 # Main Streamlit application
├─ core/                  # Core modules
│  ├─ netlist_examples.py # Circuit examples
│  ├─ sanitizer.py        # Security filtering
│  ├─ runner.py           # ngspice execution
│  ├─ raw_parser.py       # Output parsing
│  └─ utils.py            # Utilities
├─ tests/                 # Test suite
├─ requirements.txt       # Python dependencies
├─ Dockerfile            # Container definition
└─ README.md             # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
