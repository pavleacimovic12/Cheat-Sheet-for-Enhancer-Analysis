import streamlit as st
import pandas as pd
import numpy as np
import pyarrow.feather as feather
import streamlit.components.v1 as components
from data_processor_chunked import DataProcessor
from visualization import VisualizationGenerator
import os

# Configure page
st.set_page_config(
    page_title="Hall of Fame Enhancers Analysis",
    page_icon="🧬",
    layout="wide"
)

# Cache data loading for better performance
@st.cache_data
def load_data():
    """Load and process all data files - cached for performance"""
    processor = DataProcessor()
    result = processor.load_all_data()
    
    if result and len(result) == 3:
        peak_data, metadata, hof_enhancers = result
        
        # Clean any remaining NaN values in HOF enhancers
        if hof_enhancers is not None and not hof_enhancers.empty:
            hof_enhancers = hof_enhancers.fillna('')
            
            # Replace empty strings with more meaningful values where appropriate
            for col in ['cargo', 'experiment', 'proximal_gene', 'gc_delivered']:
                if col in hof_enhancers.columns:
                    hof_enhancers[col] = hof_enhancers[col].replace('', 'Not Available')
        
        return peak_data, metadata, hof_enhancers
    else:
        st.error("Failed to load data properly")
        return None, None, None

# Load data with progress indicator
with st.spinner('Loading Hall of Fame enhancers data...'):
    try:
        peak_data, enhancer_metadata, hof_enhancers = load_data()
        
        if hof_enhancers is not None and not hof_enhancers.empty:
            # Calculate some quick stats for display
            total_enhancers = len(hof_enhancers)
            total_experiments = len([x for x in hof_enhancers['experiment'].unique() if x != '' and x != 'Not Available'])
            total_cargos = len([x for x in hof_enhancers['cargo'].unique() if x != '' and x != 'Not Available'])
            
            st.success(f"✅ Successfully loaded {total_enhancers} Hall of Fame enhancers across {total_experiments} experiments with {total_cargos} cargo types!")
        else:
            st.error("❌ No HOF enhancers found. Please check data files.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

# Compact title
st.title("Cheat Sheet for Enhancer Analysis")

# Check if we have data to work with
if hof_enhancers is None or hof_enhancers.empty or peak_data is None or peak_data.empty:
    st.error("No Hall of Fame enhancers data available. Please check data files.")
    st.stop()

# Setup base data for smart filtering - using metadata instead of HOF enhancers for filtering
base_enhancers = hof_enhancers['enhancer_id'].unique() if hof_enhancers is not None and not hof_enhancers.empty else []
base_metadata = enhancer_metadata[enhancer_metadata['enhancer_id'].isin(base_enhancers)] if enhancer_metadata is not None and not enhancer_metadata.empty else pd.DataFrame()

# Sort cell types numerically by their leading numbers (1-34) - exactly like main app
import re
def extract_cell_type_number(cell_type):
    match = re.match(r'^(\d+)', str(cell_type))
    return int(match.group(1)) if match else 999

base_cell_types = sorted(peak_data['cell_type'].unique(), key=extract_cell_type_number) if peak_data is not None and not peak_data.empty else []

# Initialize session state for filters if not exists - exactly like main app
if 'filter_state' not in st.session_state:
    st.session_state.filter_state = {
        'enhancer': 'All',
        'cargo': 'All', 
        'experiment': 'All',
        'gene': 'All',
        'gc_delivered': 'All',
        'cell_type': 'All'
    }

# Smart filter function - updates available options based on current selections
def get_filtered_options(selected_filters, base_metadata):
    """Get available options for each filter based on current selections - cell type remains independent"""
    
    # For each filter, determine what should be available based on OTHER selected filters
    def get_options_for_filter(exclude_filter):
        current_metadata = base_metadata.copy()
        
        # Apply all filters EXCEPT the one we're calculating options for
        for filter_name, filter_value in selected_filters.items():
            if filter_name == exclude_filter or filter_name == 'cell_type':  # Skip cell type and target filter
                continue
            if filter_value != 'All':
                if filter_name == 'enhancer':
                    current_metadata = current_metadata[current_metadata['enhancer_id'] == filter_value]
                elif filter_name == 'cargo':
                    current_metadata = current_metadata[current_metadata['cargo'] == filter_value]
                elif filter_name == 'experiment':
                    current_metadata = current_metadata[current_metadata['experiment'] == filter_value]
                elif filter_name == 'gene':
                    current_metadata = current_metadata[current_metadata['proximal_gene'] == filter_value]
                elif filter_name == 'gc_delivered':
                    current_metadata = current_metadata[current_metadata['GC delivered'] == filter_value]
        
        return current_metadata
    
    # Get available options for each filter
    enhancer_metadata = get_options_for_filter('enhancer')
    available_enhancers = sorted(enhancer_metadata['enhancer_id'].unique()) if not enhancer_metadata.empty else []
    
    cargo_metadata = get_options_for_filter('cargo')
    available_cargos = sorted([x for x in cargo_metadata['cargo'].dropna().unique() if x != '']) if not cargo_metadata.empty else []
    
    experiment_metadata = get_options_for_filter('experiment')
    available_experiments = sorted([x for x in experiment_metadata['experiment'].dropna().unique() if x != '']) if not experiment_metadata.empty else []
    
    gene_metadata = get_options_for_filter('gene')
    available_genes = sorted([x for x in gene_metadata['proximal_gene'].dropna().unique() if x != '']) if not gene_metadata.empty else []
    
    gc_metadata = get_options_for_filter('gc_delivered')
    available_gc_delivered = sorted([x for x in gc_metadata['GC delivered'].dropna().unique() if x != '']) if not gc_metadata.empty else []
    
    # Cell type stays independent - always show all cell types
    available_cell_types = base_cell_types
    
    return {
        'enhancers': available_enhancers,
        'cargos': available_cargos,
        'experiments': available_experiments, 
        'genes': available_genes,
        'gc_delivered': available_gc_delivered,
        'cell_types': available_cell_types
    }

# Get current filter options
current_options = get_filtered_options(st.session_state.filter_state, base_metadata)

# Create sidebar filters
st.sidebar.markdown("### 🔍 Filter Options")

# Sidebar filter controls with smart filtering - exactly like main app
selected_enhancer = st.sidebar.selectbox(
    "Select Enhancer",
    options=["All"] + current_options['enhancers'],
    index=0 if st.session_state.filter_state['enhancer'] == 'All' or st.session_state.filter_state['enhancer'] not in current_options['enhancers'] else current_options['enhancers'].index(st.session_state.filter_state['enhancer']) + 1,
    help="Choose a specific enhancer to analyze"
)

selected_cargo = st.sidebar.selectbox(
    "Filter by Cargo",
    options=["All"] + current_options['cargos'],
    index=0 if st.session_state.filter_state['cargo'] == 'All' or st.session_state.filter_state['cargo'] not in current_options['cargos'] else current_options['cargos'].index(st.session_state.filter_state['cargo']) + 1,
    help="Filter by experimental cargo type"
)

selected_experiment = st.sidebar.selectbox(
    "Filter by Experiment", 
    options=["All"] + current_options['experiments'],
    index=0 if st.session_state.filter_state['experiment'] == 'All' or st.session_state.filter_state['experiment'] not in current_options['experiments'] else current_options['experiments'].index(st.session_state.filter_state['experiment']) + 1,
    help="Filter by experiment identifier"
)

selected_gene = st.sidebar.selectbox(
    "Filter by Proximal Gene",
    options=["All"] + current_options['genes'],
    index=0 if st.session_state.filter_state['gene'] == 'All' or st.session_state.filter_state['gene'] not in current_options['genes'] else current_options['genes'].index(st.session_state.filter_state['gene']) + 1,
    help="Filter by nearest gene"
)

selected_gc_delivered = st.sidebar.selectbox(
    "Filter by GC Delivered",
    options=["All"] + current_options['gc_delivered'],
    index=0 if st.session_state.filter_state['gc_delivered'] == 'All' or st.session_state.filter_state['gc_delivered'] not in current_options['gc_delivered'] else current_options['gc_delivered'].index(st.session_state.filter_state['gc_delivered']) + 1,
    help="Filter by genome copies delivered"
)

selected_cell_type = st.sidebar.selectbox(
    "Filter by Cell Type",
    options=["All"] + current_options['cell_types'],
    index=0 if st.session_state.filter_state['cell_type'] == 'All' or st.session_state.filter_state['cell_type'] not in current_options['cell_types'] else current_options['cell_types'].index(st.session_state.filter_state['cell_type']) + 1,
    help="Filter by cell type for accessibility tracks"
)

# Update session state
st.session_state.filter_state = {
    'enhancer': selected_enhancer,
    'cargo': selected_cargo,
    'experiment': selected_experiment,
    'gene': selected_gene,
    'gc_delivered': selected_gc_delivered,
    'cell_type': selected_cell_type
}

# Initialize filtered_enhancers and relevant_metadata
filtered_enhancers = pd.DataFrame()
relevant_metadata = pd.DataFrame()

# Apply metadata filters only if data is available - exactly like main app
if hof_enhancers is not None and not hof_enhancers.empty:
    enhancer_ids_to_include = set(hof_enhancers['enhancer_id'].unique())
    
    if enhancer_metadata is not None and not enhancer_metadata.empty:
        if any(filter_val != "All" for filter_val in [selected_cargo, selected_experiment, selected_gene, selected_gc_delivered]):
            filtered_metadata = enhancer_metadata.copy()
            
            if selected_cargo != "All":
                filtered_metadata = filtered_metadata[filtered_metadata['cargo'] == selected_cargo]
            
            if selected_experiment != "All":
                filtered_metadata = filtered_metadata[filtered_metadata['experiment'] == selected_experiment]
                
            if selected_gene != "All":
                filtered_metadata = filtered_metadata[filtered_metadata['proximal_gene'] == selected_gene]
                
            if selected_gc_delivered != "All":
                filtered_metadata = filtered_metadata[filtered_metadata['GC delivered'] == selected_gc_delivered]
            
            # Get the enhancer IDs that match the metadata filters
            matching_enhancer_ids = set(filtered_metadata['enhancer_id'].unique())
            enhancer_ids_to_include = enhancer_ids_to_include.intersection(matching_enhancer_ids)
    
    # Filter HOF enhancers to only include those that pass metadata filters - ONE record per enhancer
    filtered_enhancers = hof_enhancers[hof_enhancers['enhancer_id'].isin(list(enhancer_ids_to_include))].drop_duplicates(subset=['enhancer_id'], keep='first').copy()
    relevant_metadata = enhancer_metadata[enhancer_metadata['enhancer_id'].isin(list(enhancer_ids_to_include))] if enhancer_metadata is not None and not enhancer_metadata.empty else pd.DataFrame()

# Display results
if filtered_enhancers.empty:
    st.warning("⚠️ No enhancers match the selected filters. Please adjust your filter criteria.")
elif selected_enhancer == "All":
    st.info(f"📊 Select a specific enhancer from the dropdown above to view detailed analysis")
    st.markdown("### Available Enhancers")
    
    # Show summary table of all enhancers - exactly like main app
    enhancer_summary = []
    for idx, enhancer_row in filtered_enhancers.iterrows():
        enhancer_id = enhancer_row.get('enhancer_id', 'Unknown')
        enhancer_peaks = peak_data[peak_data['enhancer_id'] == enhancer_id]
        
        if not enhancer_peaks.empty:
            enhancer_summary.append({
                'Enhancer ID': enhancer_id,
                'Chromosome': enhancer_peaks.iloc[0]['chr'],
                'Start': f"{enhancer_peaks.iloc[0]['start']:,}",
                'End': f"{enhancer_peaks.iloc[0]['end']:,}",
                'Length (bp)': f"{enhancer_peaks.iloc[0]['end'] - enhancer_peaks.iloc[0]['start']:,}",
                'Cell Types': enhancer_peaks['cell_type'].nunique(),
                'Mean Accessibility': f"{enhancer_peaks['accessibility_score'].mean():.4f}",
                'Max Accessibility': f"{enhancer_peaks['accessibility_score'].max():.4f}"
            })
    
    if enhancer_summary:
        summary_df = pd.DataFrame(enhancer_summary)
        st.dataframe(summary_df, use_container_width=True)
    

    
else:
    # Process selected enhancer - exactly like main app
    for idx, enhancer_row in filtered_enhancers.iterrows():
        enhancer_id = enhancer_row.get('enhancer_id', 'Unknown')
        
        # Create expandable section for each enhancer
        with st.expander(f"🎯 **{enhancer_id}**", expanded=(len(filtered_enhancers) == 1)):
            
            # Compact metadata display
            enhancer_metadata = relevant_metadata[relevant_metadata['enhancer_id'] == enhancer_id] if not relevant_metadata.empty else pd.DataFrame()
            enhancer_peaks = peak_data[peak_data['enhancer_id'] == enhancer_id]
            
            # Single line compact info
            if not enhancer_metadata.empty and not enhancer_peaks.empty:
                meta_row = enhancer_metadata.iloc[0]
                cargo = meta_row.get('cargo', 'N/A')
                experiment = meta_row.get('experiment', 'N/A')
                gene = meta_row.get('proximal_gene', 'N/A')
                chr_info = enhancer_peaks.iloc[0]['chr']
                start_pos = enhancer_peaks.iloc[0]['start']
                end_pos = enhancer_peaks.iloc[0]['end']
                length = end_pos - start_pos
                
                st.markdown(f"**{cargo} • {experiment} • {gene} • {chr_info}:{start_pos:,}-{end_pos:,} ({length:,}bp)**")
            
            # Get all imaging data for this enhancer from the metadata dataframe
            if not relevant_metadata.empty:
                # Get the metadata row for this specific enhancer, experiment type, and GC delivered
                enhancer_meta_row = relevant_metadata[
                    (relevant_metadata['enhancer_id'] == enhancer_id) & 
                    (relevant_metadata['experiment'] == selected_experiment)
                ]
                
                # If GC delivered filter is set, apply it too
                if selected_gc_delivered != "All":
                    enhancer_meta_row = enhancer_meta_row[
                        enhancer_meta_row['GC delivered'] == selected_gc_delivered
                    ]
                
                # If no match for the specific experiment, try any record for this enhancer
                if enhancer_meta_row.empty:
                    enhancer_meta_row = relevant_metadata[relevant_metadata['enhancer_id'] == enhancer_id]
                
                if not enhancer_meta_row.empty:
                    # Extract multiple visualization URLs from the authentic metadata
                    meta_row = enhancer_meta_row.iloc[0]
                    image_link = meta_row.get('image_link', '') if pd.notna(meta_row.get('image_link')) else ''
                    neuroglancer_1 = meta_row.get('neuroglancer_1', '') if pd.notna(meta_row.get('neuroglancer_1')) else ''
                    neuroglancer_3 = meta_row.get('neuroglancer_3', '') if pd.notna(meta_row.get('neuroglancer_3')) else ''
                    viewer_link = meta_row.get('viewer_link', '') if pd.notna(meta_row.get('viewer_link')) else ''
                    coronal_mip = meta_row.get('coronal_mip', '') if pd.notna(meta_row.get('coronal_mip')) else ''
                    sagittal_mip = meta_row.get('sagittal_mip', '') if pd.notna(meta_row.get('sagittal_mip')) else ''
                else:
                    # No metadata found for this enhancer
                    image_link = neuroglancer_1 = neuroglancer_3 = viewer_link = coronal_mip = sagittal_mip = ''
            else:
                # No metadata available
                image_link = neuroglancer_1 = neuroglancer_3 = viewer_link = coronal_mip = sagittal_mip = ''
            
            # Collect all valid URLs with proper categorization - exactly like main app
            imaging_urls = []
            
            # Handle image_link based on experiment type and content
            if image_link and image_link.startswith('http'):
                # Some records have multiple URLs separated by commas in the same field
                url_parts = [url.strip() for url in image_link.split(',')]
                for url in url_parts:
                    if url.startswith('http'):
                        if 'contact_sheets' in url.lower():
                            imaging_urls.append(('Contact Sheet', url))
                        elif 'neuroglancer' in url.lower():
                            imaging_urls.append(('Neuroglancer (Primary)', url))
                        else:
                            imaging_urls.append(('Image Viewer', url))
            
            # Add dedicated neuroglancer viewers
            if neuroglancer_1 and neuroglancer_1.startswith('http'):
                imaging_urls.append(('Neuroglancer 1', neuroglancer_1))
            if neuroglancer_3 and neuroglancer_3.startswith('http'):
                imaging_urls.append(('Neuroglancer 3', neuroglancer_3))
            
            # Add viewer link
            if viewer_link and viewer_link.startswith('http'):
                imaging_urls.append(('Viewer Link', viewer_link))
            
            # Add MIP projections only if they're not "FALSE"
            if coronal_mip and coronal_mip.startswith('http') and coronal_mip.lower() != 'false':
                imaging_urls.append(('Coronal MIP', coronal_mip))
            if sagittal_mip and sagittal_mip.startswith('http') and sagittal_mip.lower() != 'false':
                imaging_urls.append(('Sagittal MIP', sagittal_mip))
            
            # Get experiment type for prioritization (EPI vs Lightsheet)
            experiment_type = meta_row.get('experiment', '') if not enhancer_metadata.empty else ''
            
            # Sort URLs by priority based on experiment type
            if 'EPI' in experiment_type.upper():
                # EPI experiments: prioritize contact sheets first, then neuroglancer
                priority_order = ['Contact Sheet', 'Neuroglancer (Primary)', 'Neuroglancer 1', 'Neuroglancer 3', 'Viewer Link', 'Coronal MIP', 'Sagittal MIP']
            else:
                # Lightsheet experiments: prioritize neuroglancer first, then contact sheets
                priority_order = ['Neuroglancer (Primary)', 'Neuroglancer 1', 'Neuroglancer 3', 'Contact Sheet', 'Viewer Link', 'Coronal MIP', 'Sagittal MIP']
            
            # Sort imaging URLs by priority
            imaging_urls.sort(key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else len(priority_order))
            
            # Display in side-by-side layout (2:1 ratio) - exactly like main app
            if imaging_urls:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### 🖼️ Imaging")
                    
                    # Create tabs for different imaging types
                    tab_names = [f"{name}" for name, _ in imaging_urls]
                    tabs = st.tabs(tab_names)
                    
                    for i, (name, url) in enumerate(imaging_urls):
                        with tabs[i]:
                            st.markdown(f"**{name}**")
                            
                            # Display with proper iframe embedding at 700px height
                            components.iframe(url, height=700, scrolling=True)
                
                with col2:
                    st.markdown("#### 📊 Accessibility Tracks")
                    
                    # Generate accessibility visualization
                    if not enhancer_peaks.empty:
                        cell_type_filter = selected_cell_type if selected_cell_type != "All" else None
                        
                        # Create visualization with proper filtering
                        if cell_type_filter:
                            filtered_peaks = enhancer_peaks[enhancer_peaks['cell_type'] == cell_type_filter]
                        else:
                            filtered_peaks = enhancer_peaks
                        
                        if not filtered_peaks.empty:
                            viz_gen = VisualizationGenerator()
                            fig = viz_gen.create_peak_visualization(filtered_peaks, enhancer_id)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No accessibility data available for the selected cell type.")
                    else:
                        st.warning("No accessibility data available for this enhancer.")
            else:
                # No imaging available, just show accessibility
                st.markdown("#### 📊 Accessibility Tracks")
                
                if not enhancer_peaks.empty:
                    cell_type_filter = selected_cell_type if selected_cell_type != "All" else None
                    
                    # Create visualization with proper filtering
                    if cell_type_filter:
                        filtered_peaks = enhancer_peaks[enhancer_peaks['cell_type'] == cell_type_filter]
                    else:
                        filtered_peaks = enhancer_peaks
                    
                    if not filtered_peaks.empty:
                        viz_gen = VisualizationGenerator()
                        fig = viz_gen.create_peak_visualization(filtered_peaks, enhancer_id)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No accessibility data available for the selected cell type.")
                else:
                    st.warning("No accessibility data available for this enhancer.")
                    
