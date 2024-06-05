import streamlit as st
import pandas as pd
import ifcopenshell
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_file_upload(upload_type, file_types):
    uploaded_file = st.file_uploader(f"Choose a {upload_type} file", type=file_types, key=upload_type)
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_types[0]}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        return tmp_file_path, uploaded_file.name
    return None, None

def process_ifc_file(file_path):
    try:
        return ifcopenshell.open(file_path)
    except Exception as e:
        error_message = f"Error opening IFC file: {e}"
        logging.error(error_message)
        st.error(error_message)
        return None

def read_excel(file):
    try:
        return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        error_message = f"Failed to read Excel file: {e}"
        logging.error(error_message)
        st.error(error_message)
        return pd.DataFrame()
