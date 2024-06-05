import streamlit as st
import pandas as pd
import logging
import os
from utils import handle_file_upload, process_ifc_file, read_excel
from analysis import display_metadata, count_building_components, detailed_analysis, visualize_component_count, generate_insights, export_analysis_to_pdf, get_objects_data_by_class, get_attribute_value, visualize_data

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def welcome_page():
    st.title("IFC and Excel File Analysis Tool")
    st.write("""
    ### Welcome to the IFC and Excel File Analysis Tool

    This Streamlit application provides an interactive interface for analyzing IFC (Industry Foundation Classes) files and Excel spreadsheets. It allows users to visualize component counts in IFC files and perform data analysis and visualization on Excel files.

    #### Features:

    - **IFC File Analysis:** Upload and analyze IFC files to view project metadata, perform component count visualization, and conduct detailed analysis of building components.
    - **Excel File Analysis:** Upload and analyze Excel spreadsheets to select and visualize data columns, and generate insights from the data.
    - **IFC File Comparison:** Compare the components of two IFC files to identify differences and view detailed and overall comparison charts.
    - **Detailed Object Data Extraction:** Extract and display detailed object data from IFC files, including property sets and quantity sets.

    #### License:
    This project is licensed under the GNU General Public License v3.0. For more details, see the LICENSE file in the root directory of this source tree or visit [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

    #### Copyright:
    Copyright (C) [2024] [Mostafa Gabr]. All rights reserved.
    """)

def ifc_file_analysis():
    st.write("""
    ### Instructions for Analyzing IFC Files:

    1. **Upload an IFC File:** Click on the "Choose a IFC file" button to upload an IFC (Industry Foundation Classes) file.

    2. **View Project Metadata:** After the file is processed, metadata of the project, including name, description, and phase, will be displayed.

    3. **Component Count Visualization:** Choose a chart type (Bar Chart or Pie Chart) to visualize the count of building components.

    4. **Detailed Analysis:** Expand the "Show Detailed Component Analysis" section, select a product type, and view detailed analysis of the selected product type.

    5. **Export Analysis as PDF:** Click the "Export Analysis as PDF" button to download a PDF report of the analysis.
    """)

    file_path, file_name = handle_file_upload("IFC", ['ifc'])
    if file_path:
        with st.spinner('Processing IFC file...'):
            ifc_file = process_ifc_file(file_path)
            if ifc_file:
                display_metadata(ifc_file)
                component_count = count_building_components(ifc_file)
                chart_type = st.radio("Chart Type", options=['Bar Chart', 'Pie Chart'], key="chart")
                fig = visualize_component_count(component_count, chart_type)
                st.plotly_chart(fig)
                detailed_analysis_ui(ifc_file)

                ifc_metadata = {
                    "Name": ifc_file.by_type('IfcProject')[0].Name,
                    "Description": ifc_file.by_type('IfcProject')[0].Description,
                    "Phase": ifc_file.by_type('IfcProject')[0].Phase,
                    "CreationDate": datetime.fromtimestamp(ifc_file.by_type('IfcProject')[0].CreationDate) if hasattr(ifc_file.by_type('IfcProject')[0], 'CreationDate') else 'Not available'
                }

                figs = [fig]

                # Get user inputs for cover page
                author = st.text_input("Author", value="Mostafa Gabr")
                subject = st.text_input("Main Subject", value="IFC and Excel File Analysis Report")
                cover_text = st.text_area("Cover Page Text", value="This report contains the analysis of IFC and Excel files. The following sections include metadata, component counts, and visualizations of the data.")

                if st.button("Export Analysis as PDF"):
                    pdf_file_path = export_analysis_to_pdf(ifc_metadata, component_count, figs, author, subject, cover_text)
                    with open(pdf_file_path, 'rb') as f:
                        st.download_button('Download PDF Report', f, file_name.replace('.ifc', '.pdf'))
            os.remove(file_path)

def excel_file_analysis():
    st.write("""
    ### Instructions for Analyzing Excel Files:

    1. **Upload an Excel File:** Click on the "Choose an Excel file" button to upload an Excel spreadsheet.

    2. **Select Columns to Display:** Choose the columns you want to display from the uploaded Excel file.

    3. **Visualize Data:** Click on "Visualize Data" to generate charts for the selected columns.

    4. **Generate Insights:** Click on "Generate Insights" to view descriptive statistics and other insights from the data.
    """)

    file_path, _ = handle_file_upload("Excel", ['xlsx'])
    if file_path:
        df = read_excel(file_path)
        if not df.empty:
            selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist(), key="columns")
            if selected_columns:
                st.dataframe(df[selected_columns])
                figs = []
                if st.button("Visualize Data", key="visualize"):
                    figs = visualize_data(df, selected_columns)
                if st.button("Generate Insights", key="insights"):
                    generate_insights(df)
                if figs and st.button("Export Analysis as PDF"):
                    pdf_file_path = export_analysis_to_pdf({"Name": "Excel Data Analysis"}, {}, figs, "Author Name", "Excel Data Analysis Report", "This report contains the analysis of Excel data.")
                    with open(pdf_file_path, 'rb') as f:
                        st.download_button('Download PDF Report', f, 'excel_analysis.pdf')
            os.remove(file_path)

def compare_ifc_files_ui():
    st.title("Compare IFC Files")
    st.write("""
    ### Instructions for Comparing IFC Files:

    Please follow the steps below to compare the components of two IFC (Industry Foundation Classes) files:

    1. **Upload First IFC File:** Click on the "Choose File" button below labeled **"Choose the first IFC file"**. Navigate to the location of the first IFC file on your device and select it for upload.

    2. **Upload Second IFC File:** Similarly, use the second "Choose File" button labeled **"Choose the second IFC file"** to upload the second IFC file you wish to compare with the first one.

    After uploading both files, you will be prompted to:

    3. **Select a Component Type for Detailed Comparison:** From the dropdown menu, select one of the available component types (e.g., walls, doors, windows) to compare between the two IFC files. The application will display a bar chart showing the count of the selected component type in both files, along with their difference.

    4. **View Overall Comparison:** After selecting a specific component type, you can also choose to view an overall comparison of all components by clicking the **"Show Overall Comparison"** button. This will display a pie chart visualizing the proportion of differences across all component types, giving you a comprehensive overview of how the two IFC files differ.

    This step-by-step process will help you understand the detailed differences in building components between the two IFC files, as well as provide an overall summary of the differences.
    """)

    file_path1, file_name1 = handle_file_upload("first IFC", ['ifc'])
    file_path2, file_name2 = handle_file_upload("second IFC", ['ifc'])

    if file_path1 and file_path2:
        with st.spinner('Processing IFC files...'):
            ifc_file1 = process_ifc_file(file_path1)
            ifc_file2 = process_ifc_file(file_path2)
            if ifc_file1 and ifc_file2:
                comparison_result = compare_ifc_files(ifc_file1, ifc_file2)
                all_component_types = list(comparison_result.keys())
                selected_component = st.selectbox("Select a component type for detailed comparison:", all_component_types, key="component_type")

                figs = []
                if selected_component:
                    component_data = comparison_result[selected_component]
                    fig = go.Figure(data=[
                        go.Bar(name=f"{file_name1} - File 1", x=[selected_component], y=[component_data['File 1 Count']], marker_color='indianred'),
                        go.Bar(name=f"{file_name2} - File 2", x=[selected_component], y=[component_data['File 2 Count']], marker_color='lightseagreen'),
                        go.Bar(name='Difference', x=[selected_component], y=[component_data['Difference']], marker_color='lightslategray')
                    ])
                    fig.update_layout(barmode='group', title_text=f'Comparison of {selected_component} in {file_name1} and {file_name2}', xaxis_title="Component Type", yaxis_title="Count", paper_bgcolor='white', plot_bgcolor='white', font_color='black')
                    st.plotly_chart(fig)
                    figs.append
