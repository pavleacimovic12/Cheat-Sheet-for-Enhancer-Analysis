"""
Data Processor for GitHub Deployment with Chunked CSV Files
Handles loading and combining chunked CSV files automatically
"""

import pandas as pd
import os
import glob
from pathlib import Path

class DataProcessor:
    """Process and load genomic data from chunked CSV files and metadata"""
    
    def __init__(self):
        # Get absolute path to current directory for Posit Cloud compatibility
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = self.base_path  # Use absolute path for all operations
        print(f"DataProcessor initialized with base_path: {self.base_path}")
        print(f"Available files: {[f for f in os.listdir(self.base_path) if f.endswith(('.csv', '.feather'))][:5]}...")
        
    def load_all_data(self):
        """Load and process all data files including chunked CSV files"""
        # Load peak data from chunked files
        peak_data = self.load_peak_data()
        
        if peak_data is None or peak_data.empty:
            return None, None, None
        
        # Load enhancer metadata
        enhancer_metadata = self.load_metadata()
        
        # Extract Hall of Fame enhancers
        hof_enhancers = self.extract_hof_enhancers(enhancer_metadata, peak_data)
        
        print(f"=== FINAL VALIDATION ===")
        print(f"Peak data: {len(peak_data) if peak_data is not None else 'None'}")
        print(f"Metadata: {len(enhancer_metadata) if enhancer_metadata is not None else 'None'}")
        print(f"HOF enhancers: {len(hof_enhancers) if hof_enhancers is not None else 'None'}")
        
        # Validate data integrity
        self.validate_data_integrity(peak_data, enhancer_metadata)
        
        # CRITICAL: Ensure HOF enhancers is properly formatted
        if hof_enhancers is not None and len(hof_enhancers) > 0:
            print(f"✅ Successfully returning {len(hof_enhancers)} HOF enhancers")
            print(f"✅ Sample enhancer: {hof_enhancers.iloc[0]['enhancer_id']}")
        else:
            print("❌ CRITICAL ERROR: HOF enhancers is empty or None!")
            
        return peak_data, enhancer_metadata, hof_enhancers
    
    def load_peak_data(self):
        """Load and combine chunked CSV files"""
        print(f"Loading peak data from directory: {self.data_dir}")
        try:
            # Pattern to match all chunk files in current directory
            chunk_patterns = [
                "part1*chunk*.csv",
                "part2*chunk*.csv", 
                "part3*chunk*.csv",
                "part4*chunk*.csv"
            ]
            
            all_chunks = []
            for pattern in chunk_patterns:
                search_pattern = os.path.join(self.data_dir, pattern)
                chunk_files = glob.glob(search_pattern)
                chunk_files.sort()  # Ensure proper order
                print(f"Pattern {pattern}: found {len(chunk_files)} files")
                
                if chunk_files:
                    print(f"Loading {len(chunk_files)} chunks for pattern {pattern}")
                    
                    for chunk_file in chunk_files:
                        df = pd.read_csv(chunk_file)
                        all_chunks.append(df)
                        print(f"  Loaded {os.path.basename(chunk_file)}: {len(df):,} rows")
            
            if not all_chunks:
                print("No chunk files found in current directory")
                print("Expected files: part1*chunk*.csv, part2*chunk*.csv, part3*chunk*.csv, part4*chunk*.csv")
                print("Current directory contents:")
                for file in os.listdir("."):
                    if file.endswith(".csv"):
                        print(f"  {file}")
                return None
            
            # Combine all chunks
            combined_df = pd.concat(all_chunks, ignore_index=True)
            print(f"Combined all chunks: {len(combined_df):,} total rows")
            
            # CRITICAL FIX: Rename columns to match expected names
            if 'enhancer_start' in combined_df.columns:
                combined_df = combined_df.rename(columns={
                    'enhancer_start': 'start',
                    'enhancer_end': 'end',
                    'signal_value': 'accessibility_score',
                    'genomic_position': 'position_index'
                })
                print("Renamed columns: enhancer_start->start, enhancer_end->end, signal_value->accessibility_score")
            
            # Remove any duplicate rows
            original_length = len(combined_df)
            combined_df = combined_df.drop_duplicates()
            if len(combined_df) < original_length:
                print(f"Removed {original_length - len(combined_df):,} duplicate rows")
            
            return combined_df
            
        except Exception as e:
            print(f"Error loading peak data: {str(e)}")
            return None
    
    def load_metadata(self):
        """Load enhancer metadata from feather file"""
        try:
            # Use absolute path for Posit Cloud compatibility
            metadata_path = os.path.join(self.base_path, "Enhancer_and_experiment_metadata_1751579195077.feather")
            print(f"Looking for metadata at: {metadata_path}")
            print(f"File exists: {os.path.exists(metadata_path)}")
            if os.path.exists(metadata_path):
                metadata = pd.read_feather(metadata_path)
                print(f"Loaded metadata: {len(metadata)} records")
                
                # Fix column names to match expected format
                column_mapping = {
                    'Enhancer_ID': 'enhancer_id',
                    'Cargo': 'cargo',
                    'Experiment_Type': 'experiment',
                    'Proximal_Gene': 'proximal_gene',
                    'Image_link': 'image_link',
                    'Neuroglancer 1': 'neuroglancer_1',
                    'Neuroglancer 3': 'neuroglancer_3',
                    'Viewer Link': 'viewer_link',
                    'Coronal_MIP': 'coronal_mip',
                    'Sagittal_MIP': 'sagittal_mip'
                }
                
                # Rename columns that exist
                existing_columns = {old_col: new_col for old_col, new_col in column_mapping.items() if old_col in metadata.columns}
                metadata = metadata.rename(columns=existing_columns)
                
                print(f"Renamed columns: {existing_columns}")
                print(f"Enhanced metadata columns: {list(metadata.columns)}")
                
                return metadata
            else:
                print(f"Metadata file not found at {metadata_path}")
                print("Expected file: Enhancer_and_experiment_metadata_1751579195077.feather")
                print("Current directory contents:")
                for file in os.listdir("."):
                    if file.endswith(".feather"):
                        print(f"  {file}")
                return None
        except Exception as e:
            print(f"Error loading metadata: {str(e)}")
            return None
    
    def extract_hof_enhancers(self, metadata_df, peak_data):
        """Extract the Hall of Fame enhancers and merge with metadata"""
        print("=== EXTRACTING HOF ENHANCERS ===")
        print(f"Input metadata: {len(metadata_df) if metadata_df is not None else 'None'}")
        print(f"Input peak data: {len(peak_data) if peak_data is not None else 'None'}")
        
        if peak_data is None or peak_data.empty:
            return pd.DataFrame()
        
        # CRITICAL FIX: Get unique enhancer IDs from peak data (these are our Hall of Fame enhancers)
        hof_enhancer_ids = peak_data['enhancer_id'].unique()
        print(f"Found {len(hof_enhancer_ids)} unique Hall of Fame enhancers from peak data: {hof_enhancer_ids[:5]}...")
        
        # If we have metadata, merge it
        if metadata_df is not None and not metadata_df.empty and 'enhancer_id' in metadata_df.columns:
            # Filter metadata for HOF enhancers
            hof_metadata = metadata_df[metadata_df['enhancer_id'].isin(hof_enhancer_ids)].copy()
            
            # Ensure all HOF enhancers are represented
            missing_enhancers = set(hof_enhancer_ids) - set(hof_metadata['enhancer_id'])
            
            if missing_enhancers:
                # Create placeholder entries for missing enhancers
                missing_data = []
                for enhancer_id in missing_enhancers:
                    # Get basic info from peak data
                    enhancer_peaks = peak_data[peak_data['enhancer_id'] == enhancer_id]
                    cell_types = enhancer_peaks['cell_type'].unique()
                    
                    missing_data.append({
                        'enhancer_id': enhancer_id,
                        'chr': enhancer_peaks['chr'].iloc[0] if not enhancer_peaks.empty else '',
                        'start': enhancer_peaks['start'].iloc[0] if 'start' in enhancer_peaks.columns and not enhancer_peaks.empty else 0,
                        'end': enhancer_peaks['end'].iloc[0] if 'end' in enhancer_peaks.columns and not enhancer_peaks.empty else 0,
                        'cargo': 'Unknown',
                        'experiment': 'Unknown',
                        'proximal_gene': 'Unknown',
                        'gc_delivered': 'Unknown',
                        'image_link': '',
                        'neuroglancer_1': '',
                        'neuroglancer_3': '',
                        'viewer_link': '',
                        'coronal_mip': '',
                        'sagittal_mip': ''
                    })
                
                if missing_data:
                    missing_df = pd.DataFrame(missing_data)
                    hof_metadata = pd.concat([hof_metadata, missing_df], ignore_index=True)
                    print(f"Added {len(missing_data)} placeholder entries for missing enhancers")
            
            # Add basic statistics for each enhancer
            enhanced_enhancers = []
            for _, base_enhancer in hof_metadata.iterrows():
                enhancer_id = base_enhancer['enhancer_id']
                
                # Get all metadata records for this enhancer from HOF metadata
                enhancer_metadata_records = hof_metadata[hof_metadata['enhancer_id'] == enhancer_id]
                
                if len(enhancer_metadata_records) > 0:
                    # Use the first record for primary metadata
                    primary_record = enhancer_metadata_records.iloc[0]
                    
                    # Create comprehensive enhancer record
                    enhanced_record = {
                        'enhancer_id': enhancer_id,
                        'chr': base_enhancer.get('chr', ''),
                        'start': base_enhancer.get('start', 0),
                        'end': base_enhancer.get('end', 0),
                        'is_hof': True,
                        
                        # Core metadata fields from feather file
                        'cargo': primary_record.get('cargo', 'Unknown'),
                        'experiment': primary_record.get('experiment', 'Unknown'), 
                        'proximal_gene': primary_record.get('proximal_gene', 'Unknown'),
                        'gc_delivered': primary_record.get('GC delivered', 'Unknown'),
                        
                        # Imaging metadata
                        'image_link': primary_record.get('image_link', ''),
                        'neuroglancer_1': primary_record.get('neuroglancer_1', ''),
                        'neuroglancer_3': primary_record.get('neuroglancer_3', ''),
                        'viewer_link': primary_record.get('viewer_link', ''),
                        'coronal_mip': primary_record.get('coronal_mip', ''),
                        'sagittal_mip': primary_record.get('sagittal_mip', ''),
                        
                        # Additional fields
                        'genotype': primary_record.get('Genotype', ''),
                        'target_cell_population': primary_record.get('Target_Cell_Population', ''),
                        'plasmid_id': primary_record.get('Plasmid_ID', '')
                    }
                    enhanced_enhancers.append(enhanced_record)
                else:
                    print(f"WARNING: No metadata found for enhancer {enhancer_id}")
                    
            enhanced_hof = pd.DataFrame(enhanced_enhancers)
            print(f"Successfully created {len(enhanced_hof)} enhanced HOF enhancers")
        else:
            # Create basic enhancer info from peak data only
            print("Creating basic enhancer info from peak data (no metadata)")
            enhancer_info = []
            for enhancer_id in hof_enhancer_ids:
                enhancer_peaks = peak_data[peak_data['enhancer_id'] == enhancer_id]
                if not enhancer_peaks.empty:
                    enhancer_info.append({
                        'enhancer_id': enhancer_id,
                        'chr': enhancer_peaks['chr'].iloc[0],
                        'start': enhancer_peaks['start'].iloc[0] if 'start' in enhancer_peaks.columns else 0,
                        'end': enhancer_peaks['end'].iloc[0] if 'end' in enhancer_peaks.columns else 0,
                        'is_hof': True,
                        'cargo': 'Unknown',
                        'experiment': 'Unknown',
                        'proximal_gene': 'Unknown',
                        'gc_delivered': 'Unknown',
                        'image_link': '',
                        'neuroglancer_1': '',
                        'neuroglancer_3': '',
                        'viewer_link': '',
                        'coronal_mip': '',
                        'sagittal_mip': '',
                        'genotype': '',
                        'target_cell_population': '',
                        'plasmid_id': ''
                    })
            
            enhanced_hof = pd.DataFrame(enhancer_info)
            print(f"Created {len(enhanced_hof)} basic enhancer records")
        
        return enhanced_hof.sort_values('enhancer_id')
    
    def get_enhancer_summary(self, peak_data):
        """Generate comprehensive summary statistics for enhancers"""
        if peak_data is None or peak_data.empty:
            return {}
        
        summary = {
            'total_enhancers': peak_data['enhancer_id'].nunique(),
            'total_measurements': len(peak_data),
            'cell_types': peak_data['cell_type'].nunique() if 'cell_type' in peak_data.columns else 0,
            'chromosomes': peak_data['chr'].nunique() if 'chr' in peak_data.columns else 0,
            'max_accessibility': peak_data['accessibility'].max() if 'accessibility' in peak_data.columns else 0,
            'mean_accessibility': peak_data['accessibility'].mean() if 'accessibility' in peak_data.columns else 0
        }
        
        return summary
    
    def validate_data_integrity(self, peak_data, metadata):
        """Validate data integrity and consistency"""
        print("\n=== Data Validation ===")
        
        if peak_data is not None and not peak_data.empty:
            print(f"✓ Peak data loaded: {len(peak_data):,} rows")
            print(f"✓ Unique enhancers: {peak_data['enhancer_id'].nunique()}")
            if 'cell_type' in peak_data.columns:
                print(f"✓ Cell types: {peak_data['cell_type'].nunique()}")
        else:
            print("✗ Peak data missing or empty")
        
        if metadata is not None and not metadata.empty:
            print(f"✓ Metadata loaded: {len(metadata):,} records")
            print(f"✓ Unique enhancers in metadata: {metadata['enhancer_id'].nunique()}")
        else:
            print("✗ Metadata missing or empty")
        
        # Check for common enhancers
        if peak_data is not None and metadata is not None:
            peak_enhancers = set(peak_data['enhancer_id'].unique())
            meta_enhancers = set(metadata['enhancer_id'].unique())
            common_enhancers = peak_enhancers.intersection(meta_enhancers)
            print(f"✓ Common enhancers between datasets: {len(common_enhancers)}")
        
        print("======================\n")