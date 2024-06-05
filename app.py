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
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(f'{pset_name}.{property_name}')
    
    pset_attributes = set()
    objects_data = []
    objects = file.by_type(class_type)
      
    for object in objects:
        psets = Element.get_psets(object, psets_only=True)
        add_pset_attributes(psets)
        qtos = Element.get_psets(object, qtos_only=True)
        add_pset_attributes(qtos)
        objects_data.append({
            "ExpressId": object.id(),
            "GlobalId": object.GlobalId,
            "Class": object.is_a(),
            "PredefinedType": Element.get_predefined_type(object),
            "Name": object.Name,
            "Level": Element.get_container(object).Name
            if Element.get_container(object)
            else "",
            "Type": Element.get_type(object).Name
            if Element.get_type(object)
            else "",
            "QuantitySets": qtos,
            "PropertySets": psets,
        })
    return objects_data, list(pset_attributes)

# Function to get attribute value
def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".",1)[0]
        prop_name = attribute.split(".",-1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        if pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
    else:
        return None

# Streamlit UI
st.title('IFC File Processor')

uploaded_file = st.file_uploader("Choose an IFC file", type="ifc")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    file = ifcopenshell.open(temp_file_path)
    class_type = st.selectbox('Select Class Type', ['IfcBuildingElement', 'IfcBeam', 'IfcWall', 'IfcWindow'])

    data, pset_attributes = get_objects_data_by_class(file, class_type)
    attributes = ["ExpressId", "GlobalId", "Class", "PredefinedType", "Name", "Level", "Type"] + pset_attributes

    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))

    dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)
    st.write(dataframe)

    if class_type == 'IfcBeam':
        beams = dataframe[(dataframe["Class"] == "IfcBeam")]
        if "Qto_BeamBaseQuantities.NetVolume" in beams.columns:
            values = beams.groupby(["Level", "Type", "PredefinedType"])["Qto_BeamBaseQuantities.NetVolume"].sum()
            st.write(values)
        else:
            st.write("Column 'Qto_BeamBaseQuantities.NetVolume' not found in the data.")
    
    # Group by floor and type, and count the total number for each type per floor
    if 'Level' in dataframe.columns and 'Type' in dataframe.columns:
        floor_type_counts = dataframe.groupby(['Level', 'Type']).size().reset_index(name='Count')
        st.write(floor_type_counts)
    else:
        st.write("Columns 'Level' and 'Type' not found in the data.")

    st.download_button(
        label="Download data as CSV",
        data=dataframe.to_csv(index=False).encode('utf-8'),
        file_name='ifc_data.csv',
        mime='text/csv',
    )
