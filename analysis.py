import pandas as pd
import ifcopenshell.util.element as Element
import plotly.express as px
import plotly.graph_objects as go
import logging
from collections import defaultdict
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
import tempfile

def display_metadata(ifc_file):
    project = ifc_file.by_type('IfcProject')
    if project:
        project = project[0]
        st.write("### Project Metadata")
        st.write(f"Name: {project.Name}")
        st.write(f"Description: {project.Description}")
        st.write(f"Phase: {project.Phase}")
        if hasattr(project, 'CreationDate'):
            st.write(f"Time Stamp: {datetime.fromtimestamp(project.CreationDate)}")
        else:
            st.write("Time Stamp: Not available")

def count_building_components(ifc_file):
    component_count = defaultdict(int)
    try:
        for ifc_entity in ifc_file.by_type('IfcProduct'):
            component_count[ifc_entity.is_a()] += 1
    except Exception as e:
        error_message = f"Error processing IFC file: {e}"
        logging.error(error_message)
        st.error(error_message)
    return component_count

def detailed_analysis(ifc_file, product_type, sort_by=None):
    product_count = defaultdict(int)
    try:
        for product in ifc_file.by_type(product_type):
            product_name = product.Name if product.Name else "Unnamed"
            type_name = product_name.split(':')[0] if product_name else "Unnamed"
            product_count[type_name] += 1
    except Exception as e:
        error_message = f"Error during detailed analysis: {e}"
        logging.error(error_message)
        st.error(error_message)
        return

    labels, values = zip(*product_count.items()) if product_count else ((), ())
    if values:
        fig = px.pie(values=values, names=labels, title=f"Distribution of {product_type} Products by Type")
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', font_color='black')
        st.plotly_chart(fig)

        if sort_by:
            df = pd.DataFrame({'Type': labels, 'Count': values}).sort_values(by=sort_by, ascending=False)
            st.table(df)
    else:
        st.write(f"No products found for {product_type}.")

def visualize_component_count(component_count, chart_type='Bar Chart'):
    labels, values = zip(*sorted(component_count.items(), key=lambda item: item[1], reverse=True)) if component_count else ((), ())
    if chart_type == 'Bar Chart':
        fig = px.bar(x=labels, y=values)
    elif chart_type == 'Pie Chart':
        fig = px.pie(values=values, names=labels)
    fig.update_layout(transition_duration=500, paper_bgcolor='white', plot_bgcolor='white', font_color='black')
    return fig

def generate_insights(df):
    if not df.empty:
        st.write("Descriptive Statistics:", df.describe())

def export_analysis_to_pdf(ifc_metadata, component_count, figs, author, subject, cover_text):
    buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(buffer.name, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    # Cover Page
    flowables.append(Spacer(1, 1 * inch))
    flowables.append(Paragraph(subject, styles['Title']))
    flowables.append(Spacer(1, 0.5 * inch))
    flowables.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    flowables.append(Paragraph(f"Author: {author}", styles['Normal']))
    flowables.append(Spacer(1, 1 * inch))
    flowables.append(Paragraph(cover_text, styles['Normal']))
    flowables.append(Spacer(1, 2 * inch))

    # IFC Metadata
    flowables.append(Paragraph("IFC File Metadata", styles['Heading2']))
    metadata_table_data = [
        ["Name", ifc_metadata.get('Name', 'Not available')],
        ["Description", ifc_metadata.get('Description', 'Not available')],
        ["Phase", ifc_metadata.get('Phase', 'Not available')],
        ["Creation Date", ifc_metadata.get('CreationDate', 'Not available')]
    ]
    metadata_table = Table(metadata_table_data)
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    flowables.append(metadata_table)
    flowables.append(Spacer(1, 0.5 * inch))

    # Component Count
    flowables.append(Paragraph("Component Count", styles['Heading2']))
    component_table_data = [["Component", "Count"]] + [[component, str(count)] for component, count in component_count.items()]
    component_table = Table(component_table_data)
    component_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    flowables.append(component_table)
    flowables.append(Spacer(1, 0.5 * inch))

    # Adding Images
    for idx, fig in enumerate(figs):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            try:
                fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', font_color='black')
                fig.write_image(tmp_file.name, format='png', engine='kaleido')
                flowables.append(Spacer(1, 0.5 * inch))
                flowables.append(Paragraph(f"Chart {idx + 1}", styles['Heading2']))
                flowables.append(Image(tmp_file.name))
            except Exception as e:
                logging.error(f"Error exporting chart to image: {e}")
                st.error(f"Error exporting chart to image: {e}")

    doc.build(flowables)
    return buffer.name
