import streamlit as st
from pages import welcome_page, ifc_file_analysis, excel_file_analysis, compare_ifc_files_ui, display_detailed_object_data

def main():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.session_state.analysis_choice = "Welcome"
    if st.sidebar.button("Analyze IFC File"):
        st.session_state.analysis_choice = "Analyze IFC File"
    if st.sidebar.button("Analyze Excel File"):
        st.session_state.analysis_choice = "Analyze Excel File"
    if st.sidebar.button("Compare IFC Files"):
        st.session_state.analysis_choice = "Compare IFC Files"
    if st.sidebar.button("Detailed Object Data"):
        st.session_state.analysis_choice = "Detailed Object Data"

    if 'analysis_choice' not in st.session_state:
        st.session_state.analysis_choice = "Welcome"

    if st.session_state.analysis_choice == "Welcome":
        welcome_page()
    elif st.session_state.analysis_choice == "Analyze IFC File":
        ifc_file_analysis()
    elif st.session_state.analysis_choice == "Analyze Excel File":
        excel_file_analysis()
    elif st.session_state.analysis_choice == "Compare IFC Files":
        compare_ifc_files_ui()
    elif st.session_state.analysis_choice == "Detailed Object Data":
        display_detailed_object_data()

if __name__ == "__main__":
    main()

st.sidebar.markdown("""
----------------
#### Copyright Notice
Copyright (C) [2024] [Mostafa Gabr]. All rights reserved.

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
""")
