import streamlit as st
import ifcopenshell
import ifcopenshell.util.element as Element
import pandas as pd
import pprint
import tempfile

pp = pprint.PrettyPrinter()

# Function to get objects data by class
def get_objects_data_by_class(file, class_type):
    def add_pset_attributes(psets):
        # Add property set attributes to a set
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(f'{pset_name}.{property_name}')
    
    pset_attributes = set()
    objects_data = []
    objects = file.by_type(class_type)  # Get objects of the specified class type
      
    for obj in objects:
        psets = Element.get_psets(obj, psets_only=True)
        add_pset_attributes(psets)
        qtos = Element.get_psets(obj, qtos_only=True)
        add_pset_attributes(qtos)
        objects_data.append({
            "ExpressId": obj.id(),
            "GlobalId": getattr(obj, 'GlobalId', None),  # Safely get GlobalId
            "Class": obj.is_a(),
            "PredefinedType": Element.get_predefined_type(obj),
            "Name": getattr(obj, 'Name', None),  # Safely get Name
            "Level": Element.get_container(obj).Name if Element.get_container(obj) else "",  # Safely get Level
            "Type": Element.get_type(obj).Name if Element.get_type(obj) else "",  # Safely get Type
            "QuantitySets": qtos,
            "PropertySets": psets,
        })
    return objects_data, list(pset_attributes)

# Function to get attribute value
def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data.get(attribute, None)  # Safely get the attribute value
    elif "." in attribute:
        pset_name = attribute.split(".", 1)[0]
        prop_name = attribute.split(".", -1)[1]
        if pset_name in object_data["PropertySets"]:
            return object_data["PropertySets"][pset_name].get(prop_name, None)  # Safely get property set attribute
        if pset_name in object_data["QuantitySets"]:
            return object_data["QuantitySets"][pset_name].get(prop_name, None)  # Safely get quantity set attribute
    return None

# Streamlit UI setup
st.title('IFC File Processor')

# Instructions for the user
st.markdown("""
## Instructions for Using the IFC File Processor

1. **Upload an IFC File**:
   - Use the "Choose an IFC file" button to upload your IFC file. This file should be in the `.ifc` format.

2. **Select Class Type**:
   - After uploading the IFC file, select the class type of objects you want to analyze from the dropdown menu. The dropdown will be populated with all unique class types present in the uploaded IFC file.

3. **View Object Data**:
   - The app will display a table containing detailed information about the objects of the selected class type. This table includes attributes like `ExpressId`, `GlobalId`, `Class`, `PredefinedType`, `Name`, `Level`, and `Type`, along with any property sets and quantity sets associated with the objects.

   **Explanation**:
   - **ExpressId**: The internal identifier of the object in the IFC file.
   - **GlobalId**: The globally unique identifier of the object.
   - **Class**: The type of the object (e.g., IfcBeam, IfcWall).
   - **PredefinedType**: A subtype or specific classification of the object.
   - **Name**: The name of the object.
   - **Level**: The floor or level where the object is located.
   - **Type**: The specific type of the object.
   - **PropertySets** and **QuantitySets**: These columns contain various properties and quantities associated with the objects, respectively.

4. **View Floor and Type Summary**:
   - Below the detailed table, you will see another table that shows the total count of each type of object per floor. This table is grouped by `Level` and `Type`.

   **Explanation**:
   - This summary helps you understand how many objects of each type are present on each floor. For example, it will show you how many beams, walls, or windows are on each level of the building.

5. **Download Data**:
   - You can download the detailed object data as a CSV file by clicking the "Download data as CSV" button. This allows you to further analyze the data offline or integrate it with other tools.
""")

# File uploader widget
uploaded_file = st.file_uploader("Choose an IFC file", type="ifc")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    file = ifcopenshell.open(temp_file_path)
    
    # Get all unique classes in the IFC file
    all_classes = set(entity.is_a() for entity in file)
    class_type = st.selectbox('Select Class Type', sorted(all_classes))  # Dropdown for class types

    # Get objects data and property set attributes
    data, pset_attributes = get_objects_data_by_class(file, class_type)
    attributes = ["ExpressId", "GlobalId", "Class", "PredefinedType", "Name", "Level", "Type"] + pset_attributes

    # Prepare data for DataFrame
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))

    dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)

    # Display detailed object data
    st.subheader("Detailed Object Data")
    st.write(dataframe)

    # Group by floor and type, and count the total number for each type per floor
    st.subheader("Summary by Floor and Type")
    if 'Level' in dataframe.columns and 'Type' in dataframe.columns:
        floor_type_counts = dataframe.groupby(['Level', 'Type']).size().reset_index(name='Count')
        st.write(floor_type_counts)  # Display the grouped data
    else:
        st.write("Columns 'Level' and 'Type' not found in the data.")

    # Download button for CSV export
    st.download_button(
        label="Download data as CSV",
        data=dataframe.to_csv(index=False).encode('utf-8'),
        file_name='ifc_data.csv',
        mime='text/csv',
    )
