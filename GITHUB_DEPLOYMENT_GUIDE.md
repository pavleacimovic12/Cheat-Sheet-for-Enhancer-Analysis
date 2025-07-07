# GitHub to Posit Cloud Deployment Guide

## Overview
This repository contains a complete Hall of Fame Enhancers Analysis application ready for deployment on Posit Cloud via GitHub integration.

## Repository Contents

### Essential Application Files
- `app.py` - Main Streamlit application with complete imaging and visualization
- `data_processor_chunked.py` - Data processing engine for chunked CSV files
- `visualization.py` - PyGenomeTracks-style visualization generator
- `requirements.txt` - Python dependencies for Posit Cloud

### Data Files
- `Enhancer_and_experiment_metadata_1751579195077.feather` - Complete metadata (249KB)
- `part1_*.csv` through `part4_*.csv` - Chunked peak accessibility data (20 files, ~300MB total)

### Configuration Files
- `.streamlit/config.toml` - Streamlit server configuration
- `runtime.txt` - Python version specification
- `Procfile` - Process file for deployment
- `setup.py` - Package setup configuration

### Documentation
- `README.md` - Application overview and usage instructions
- `POSIT_DEPLOYMENT.md` - Detailed deployment instructions
- `LICENSE` - MIT license

## GitHub Upload Instructions

1. **Create New GitHub Repository**
   ```bash
   # Initialize git repository
   git init
   git add .
   git commit -m "Initial commit: Hall of Fame Enhancers Analysis App"
   
   # Add remote and push
   git remote add origin https://github.com/YOUR_USERNAME/hof-enhancers-analysis.git
   git branch -M main
   git push -u origin main
   ```

2. **File Size Verification**
   - All CSV chunks are under 25MB GitHub limit
   - Total repository size: ~300MB
   - Metadata file: 249KB
   - All files optimized for GitHub upload

## Posit Cloud Deployment

### Method 1: Direct GitHub Integration
1. Log into Posit Cloud
2. Click "New Project" → "New Project from Git Repository"
3. Enter your GitHub repository URL
4. Posit Cloud will automatically detect and install dependencies

### Method 2: Manual Upload
1. Download repository as ZIP
2. Upload to Posit Cloud
3. Extract files in project directory

## Application Features

### Data Processing
- **2.8M+ peak accessibility records** across 49 Hall of Fame enhancers
- **34 cell types** with comprehensive metadata integration
- **Real-time filtering** by cargo, experiment, gene, and GC delivered
- **Efficient chunked data loading** with caching

### Visualization System
- **Side-by-side layout** (2:1 ratio) with imaging and accessibility charts
- **Tabbed imaging interface** with 700px embedded viewers
- **Experiment-specific prioritization**: EPI→contact sheets, Lightsheet→neuroglancer
- **PyGenomeTracks-style** accessibility visualizations at 2000px height

### Interactive Features
- **Dynamic filtering system** with smart option updates
- **Enhanced summary tables** with proper column configuration
- **Real-time metrics dashboard** showing data completeness
- **Professional genomic theme** with gradient headers

## Technical Specifications

- **Framework**: Streamlit 1.28+
- **Data Processing**: Pandas, PyArrow
- **Visualization**: Plotly
- **Data Size**: 300MB total, 2.8M+ records
- **Performance**: Cached loading, optimized for large datasets
- **Browser Compatibility**: All modern browsers

## Support

For deployment issues or questions:
1. Check `POSIT_DEPLOYMENT.md` for detailed instructions
2. Verify all dependencies in `requirements.txt`
3. Ensure Python 3.11 runtime environment
4. Contact support if data loading issues occur

## License
MIT License - see LICENSE file for details