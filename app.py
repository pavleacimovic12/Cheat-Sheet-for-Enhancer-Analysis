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

# Setup base data for smart filtering - using HOF enhancers for filtering
base_enhancers = hof_enhancers['enhancer_id'].unique() if hof_enhancers is not None and not hof_enhancers.empty else []
base_metadata = hof_enhancers.copy() if hof_enhancers is not None and not hof_enhancers.empty else pd.DataFrame()
# Debug output removed per user request

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
            if filter_name != exclude_filter and filter_value != "All":
                if filter_name == 'enhancer':
                    current_metadata = current_metadata[current_metadata['enhancer_id'] == filter_value]
                elif filter_name == 'cargo':
                    current_metadata = current_metadata[current_metadata['cargo'] == filter_value]
                elif filter_name == 'experiment':
                    current_metadata = current_metadata[current_metadata['experiment'] == filter_value]
                elif filter_name == 'gene':
                    current_metadata = current_metadata[current_metadata['proximal_gene'] == filter_value]
                elif filter_name == 'gc_delivered':
                    current_metadata = current_metadata[current_metadata['gc_delivered'] == filter_value]
        
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
    available_gc_delivered = sorted([x for x in gc_metadata['gc_delivered'].dropna().unique() if x != '']) if not gc_metadata.empty else []
    
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

# Sidebar filter controls exactly like main app
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
    help="Focus on specific cell type for visualization"
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

# Apply filters to get final filtered data
filtered_metadata = base_metadata.copy()
if selected_enhancer != "All":
    filtered_metadata = filtered_metadata[filtered_metadata['enhancer_id'] == selected_enhancer]
if selected_cargo != "All":
    filtered_metadata = filtered_metadata[filtered_metadata['cargo'] == selected_cargo]
if selected_experiment != "All":
    filtered_metadata = filtered_metadata[filtered_metadata['experiment'] == selected_experiment]
if selected_gene != "All":
    filtered_metadata = filtered_metadata[filtered_metadata['proximal_gene'] == selected_gene]
if selected_gc_delivered != "All":
    filtered_metadata = filtered_metadata[filtered_metadata['gc_delivered'] == selected_gc_delivered]

# Get the filtered enhancer list
filtered_enhancer_ids = filtered_metadata['enhancer_id'].unique() if not filtered_metadata.empty else []
filtered_hof_enhancers = hof_enhancers[hof_enhancers['enhancer_id'].isin(filtered_enhancer_ids)]

# Filter peak data
filtered_peak_data = peak_data[peak_data['enhancer_id'].isin(filtered_enhancer_ids)]
if selected_cell_type != "All":
    filtered_peak_data = filtered_peak_data[filtered_peak_data['cell_type'] == selected_cell_type]

# Remove debug output per user request

# Individual enhancer analysis
if len(filtered_enhancer_ids) > 0:
    st.markdown('### 🧬 Individual Enhancer Analysis')
    
    # Select specific enhancer for detailed analysis
    if len(filtered_enhancer_ids) == 1:
        enhancer_id = filtered_enhancer_ids[0]
        st.info(f'Analyzing enhancer: **{enhancer_id}**')
    else:
        enhancer_id = st.selectbox(
            'Select enhancer for detailed analysis:',
            options=filtered_enhancer_ids,
            key='enhancer_selector'
        )
    
    if enhancer_id:
        # Get enhancer data
        enhancer_data = filtered_hof_enhancers[filtered_hof_enhancers['enhancer_id'] == enhancer_id].iloc[0]
        
        # Extract imaging information
        image_link = enhancer_data.get('image_link', '')
        neuroglancer_1 = enhancer_data.get('neuroglancer_1', '')
        neuroglancer_3 = enhancer_data.get('neuroglancer_3', '')
        viewer_link = enhancer_data.get('viewer_link', '')
        coronal_mip = enhancer_data.get('coronal_mip', '')
        sagittal_mip = enhancer_data.get('sagittal_mip', '')
        
        # Create imaging URLs list
        imaging_urls = []
        
        # Handle image_link based on experiment type and content
        if image_link and image_link.startswith('http'):
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
            imaging_urls.append(('Viewer', viewer_link))
        
        # Add MIP projections (exclude 'FALSE' values)
        if coronal_mip and coronal_mip.startswith('http') and coronal_mip.upper() != 'FALSE':
            imaging_urls.append(('Coronal MIP', coronal_mip))
        if sagittal_mip and sagittal_mip.startswith('http') and sagittal_mip.upper() != 'FALSE':
            imaging_urls.append(('Sagittal MIP', sagittal_mip))
        
        # Create main layout with imaging on left and chart on right
        col_left, col_right = st.columns([2, 1])  # 2:1 ratio for imaging:chart
        
        with col_left:
            # Imaging section with tabs
            st.markdown('**🖼️ Imaging Visualization**')
            
            if imaging_urls:
                # Separate different viewer types
                contact_sheets = [(title, url) for title, url in imaging_urls if 'contact' in title.lower() and 'sheet' in title.lower()]
                neuroglancer_viewers = [(title, url) for title, url in imaging_urls if 'neuroglancer' in title.lower()]
                mip_viewers = [(title, url) for title, url in imaging_urls if 'mip' in title.lower()]
                other_viewers = [(title, url) for title, url in imaging_urls if title not in [t for t, _ in contact_sheets + neuroglancer_viewers + mip_viewers]]
                
                # Prioritize based on experiment type
                current_experiment = str(enhancer_data['experiment']).lower()
                if 'lightsheet' in current_experiment:
                    primary_viewers = neuroglancer_viewers + mip_viewers
                    secondary_viewers = contact_sheets + other_viewers
                elif 'epi' in current_experiment:
                    primary_viewers = contact_sheets + neuroglancer_viewers
                    secondary_viewers = mip_viewers + other_viewers
                else:
                    # Default for STPT, SSv4, etc.
                    primary_viewers = neuroglancer_viewers + contact_sheets
                    secondary_viewers = mip_viewers + other_viewers
                
                all_viewers = primary_viewers + secondary_viewers
                
                if len(all_viewers) > 1:
                    # Use tabs for multiple viewers
                    tab_names = [title for title, _ in all_viewers]
                    tabs = st.tabs(tab_names)
                    
                    for tab, (title, url) in zip(tabs, all_viewers):
                        with tab:
                            # Use iframe display like main app
                            st.markdown(
                                f'<iframe src="{url}" width="100%" height="700" frameborder="0" '
                                f'style="border: 1px solid #ccc; border-radius: 4px;"></iframe>', 
                                unsafe_allow_html=True
                            )
                else:
                    # Single viewer - display directly
                    title, url = all_viewers[0]
                    st.markdown(
                        f'<iframe src="{url}" width="100%" height="700" frameborder="0" '
                        f'style="border: 1px solid #ccc; border-radius: 4px;"></iframe>', 
                        unsafe_allow_html=True
                    )
            else:
                st.info('No imaging visualizations available for this enhancer')
        
        with col_right:
            # Accessibility chart
            st.markdown('**📈 Peak Accessibility**')
            
            # Filter peak data for this enhancer
            enhancer_peak_data = filtered_peak_data[filtered_peak_data['enhancer_id'] == enhancer_id].copy()
            
            if selected_cell_type != 'All':
                enhancer_peak_data = enhancer_peak_data[enhancer_peak_data['cell_type'] == selected_cell_type]
                st.info(f'Showing data filtered for cell type: **{selected_cell_type}**')
            
            if not enhancer_peak_data.empty:
                try:
                    # Generate pyGenomeTracks-style visualization
                    viz_generator = VisualizationGenerator()
                    fig = viz_generator.create_peak_visualization(enhancer_peak_data, enhancer_id)
                    # Make visualization taller for enhanced track visibility
                    fig.update_layout(height=2000)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Compact statistics
                    cell_types_count = enhancer_peak_data['cell_type'].nunique()
                    max_accessibility = enhancer_peak_data['accessibility_score'].max()
                    mean_accessibility = enhancer_peak_data['accessibility_score'].mean()
                    std_accessibility = enhancer_peak_data['accessibility_score'].std()
                    
                    st.markdown(f'**📊 {cell_types_count} cells • Max: {max_accessibility:.4f} • Mean: {mean_accessibility:.4f} • Std: {std_accessibility:.4f}**')
                    
                    # Top cell types
                    if cell_types_count > 1:
                        top_cell_types = (enhancer_peak_data.groupby('cell_type')['accessibility_score']
                                        .mean()
                                        .sort_values(ascending=False)
                                        .head(5))
                        
                        top_list = ' • '.join([f'{ct}: {score:.4f}' for ct, score in top_cell_types.items()])
                        st.markdown(f'**Top:** {top_list}')
                    
                except Exception as e:
                    st.error(f'Error generating visualization: {str(e)}')
                    
                    # Fallback: Show data table
                    st.markdown('**Raw Peak Data Preview:**')
                    display_cols = ['cell_type', 'position_index', 'accessibility_score']
                    available_cols = [col for col in display_cols if col in enhancer_peak_data.columns]
                    st.dataframe(
                        enhancer_peak_data[available_cols].head(20),
                        use_container_width=True
                    )
            else:
                st.warning('⚠️ No peak accessibility data available for this enhancer with current filters')
else:
    st.warning('Selected enhancer not found in filtered results')

# Footer
st.markdown('---')
st.markdown('''
<div style='text-align: center; color: #666; padding: 20px;'>
    <strong>Hall of Fame Enhancers Analysis Tool</strong><br>
    Genomic Data Visualization Platform for Enhancer Accessibility Analysis
</div>
''', unsafe_allow_html=True)

