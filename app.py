"""
OpenSPICE Playground - Web UI for ngspice simulation
Main Streamlit application
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import io
import base64

from core.netlist_examples import EXAMPLES, get_example_netlist, generate_parametric_netlist
from core.sanitizer import sanitize_netlist
from core.runner import run_ngspice
from core.raw_parser import parse_ascii_raw
from core.utils import dataframe_to_csv, format_unit


st.set_page_config(
    page_title="OpenSPICE Playground",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


if 'netlist' not in st.session_state:
    st.session_state.netlist = ""
if 'results' not in st.session_state:
    st.session_state.results = None
if 'log' not in st.session_state:
    st.session_state.log = ""

def main():
    st.title("OpenSPICE Playground")
    st.markdown("Web-based SPICE circuit simulator using ngspice")
    

    with st.sidebar:
        st.header("Examples & Tools")
        

        st.subheader("Load Example")
        example_names = list(EXAMPLES.keys())
        selected_example = st.selectbox(
            "Select an example circuit:",
            [""] + example_names,
            help="Choose a pre-built circuit example"
        )
        
        if selected_example and st.button("Load Example", type="primary"):
            st.session_state.netlist = get_example_netlist(selected_example)
            st.rerun()
        

        st.subheader("🔧 Parametric Circuit Generator")
        circuit_type = st.selectbox(
            "Circuit Type:",
            ["RC Low-Pass Filter", "RC High-Pass Filter", "RLC Filter"]
        )
        
        if circuit_type == "RC Low-Pass Filter":
            col1, col2 = st.columns(2)
            with col1:
                R = st.number_input("R (Ω)", value=1000, min_value=1, max_value=1000000)
                C = st.number_input("C (µF)", value=1.0, min_value=0.001, max_value=1000.0)
            with col2:
                Vin = st.number_input("Vin (V)", value=1.0, min_value=0.1, max_value=100.0)
                freq = st.number_input("Freq (Hz)", value=1000, min_value=1, max_value=1000000)
            
            if st.button("Generate Circuit"):
                st.session_state.netlist = generate_parametric_netlist(
                    "rc_lowpass", R=R, C=C*1e-6, Vin=Vin, freq=freq
                )
                st.rerun()
    

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Netlist Editor")
        

        netlist_input = st.text_area(
            "Enter your ngspice netlist:",
            value=st.session_state.netlist,
            height=400,
            help="Enter a valid ngspice netlist. The .control block will be automatically added/modified.",
            placeholder="""* Example: RC Circuit
Vin in 0 AC 1
R1 in out 1k
C1 out 0 1u
.ac dec 50 10 1e6
.end"""
        )
        

        col1_1, col1_2, col1_3 = st.columns(3)
        
        with col1_1:
            run_button = st.button("▶️ Run Simulation", type="primary", use_container_width=True)
        with col1_2:
            clear_button = st.button("🗑️ Clear", type="secondary", use_container_width=True)
        with col1_3:
            download_netlist = st.download_button(
                "💾 Download Netlist",
                data=netlist_input,
                file_name="circuit.cir",
                mime="text/plain",
                use_container_width=True
            )
    
    with col2:
        st.header("Results")
        
        if clear_button:
            st.session_state.results = None
            st.session_state.log = ""
            st.rerun()
        
        if run_button and netlist_input.strip():
            with st.spinner("Running ngspice simulation..."):
                try:

                    sanitized_netlist = sanitize_netlist(netlist_input)
                    

                    success, log, raw_path = run_ngspice(sanitized_netlist)
                    
                    st.session_state.log = log
                    
                    if success and raw_path and os.path.exists(raw_path):

                        df, metadata = parse_ascii_raw(raw_path)
                        st.session_state.results = {
                            'dataframe': df,
                            'metadata': metadata,
                            'raw_path': raw_path
                        }
                        st.success("✅ Simulation completed successfully!")
                    else:
                        st.error(f"❌ Simulation failed. Check the log below.")
                        st.session_state.results = None
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.results = None
        

        if st.session_state.results:
            results = st.session_state.results
            df = results['dataframe']
            metadata = results['metadata']
            

            st.subheader("Select traces to plot:")
            

            x_var = None
            y_vars = []
            for var_info in metadata['variables']:
                if var_info['name'].lower() in ['time', 'frequency']:
                    x_var = var_info['name']
                else:
                    y_vars.append(var_info['name'])
            
            if x_var and y_vars:
                selected_traces = st.multiselect(
                    "Choose variables to plot:",
                    options=y_vars,
                    default=y_vars[:min(3, len(y_vars))]
                )
                
                if selected_traces:

                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    for trace in selected_traces:
                        if trace in df.columns:
                            ax.plot(df.index, df[trace], label=trace, linewidth=2)
                    
                    ax.set_xlabel(format_unit(x_var, metadata))
                    ax.set_ylabel("Value")
                    ax.set_title("Simulation Results")
                    ax.grid(True, alpha=0.3)
                    ax.legend()
                    

                    if x_var.lower() == 'frequency':
                        ax.set_xscale('log')
                    
                    st.pyplot(fig)
                    plt.close()
    

    if st.session_state.results:
        st.header("📋 Data Table & Downloads")
        
        col3, col4 = st.columns([2, 1])
        
        with col3:

            df_display = st.session_state.results['dataframe']
            st.dataframe(df_display, use_container_width=True, height=300)
        
        with col4:
            st.subheader("📥 Downloads")
            

            csv_data = dataframe_to_csv(df_display)
            st.download_button(
                "📊 Download CSV",
                data=csv_data,
                file_name="simulation_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            

            if 'raw_path' in st.session_state.results:
                raw_path = st.session_state.results['raw_path']
                if os.path.exists(raw_path):
                    with open(raw_path, 'rb') as f:
                        raw_data = f.read()
                    st.download_button(
                        "📁 Download RAW file",
                        data=raw_data,
                        file_name="output.raw",
                        mime="application/octet-stream",
                        use_container_width=True
                    )
    

    if st.session_state.log:
        with st.expander("📜 Simulation Log", expanded=False):
            st.text(st.session_state.log)
    

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>OpenSPICE Playground v1.0.0 | Built with using Streamlit & ngspice</p>
            <p>Security: Dangerous commands are filtered. Execution timeout: 10 seconds.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()