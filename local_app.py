"""Local convenience entry point. Public deployment must use app.py."""
import runpy
from pathlib import Path
import streamlit as st
from growth.local_config import read_local_settings

if st.get_option('server.address') not in ('127.0.0.1','localhost','::1'):
    st.error('Saved keys require a loopback-only server. Start the local app with run.ps1.')
    st.stop()

root=Path(__file__).resolve().parent
runpy.run_path(str(root/'app.py'),init_globals={'_LOCAL_SETTINGS':read_local_settings(root)})
