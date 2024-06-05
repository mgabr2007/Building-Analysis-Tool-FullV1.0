# IFC and Excel File Analysis Tool

## Overview

This Streamlit application provides an interactive interface for analyzing IFC (Industry Foundation Classes) files and Excel spreadsheets. It allows users to visualize component counts in IFC files and perform data analysis and visualization on Excel files.

## Features

- **IFC File Analysis:** Upload and analyze IFC files to view project metadata, perform component count visualization, and conduct detailed analysis of building components.
- **Excel File Analysis:** Upload and analyze Excel spreadsheets to select and visualize data columns, and generate insights from the data.
- **IFC File Comparison:** Compare the components of two IFC files to identify differences and view detailed and overall comparison charts.
- **Detailed Object Data Extraction:** Extract and display detailed object data from IFC files, including property sets and quantity sets.

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/ifc-excel-analysis-tool.git
    cd ifc-excel-analysis-tool
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

To run the application, use the following command:
```sh
streamlit run app.py
