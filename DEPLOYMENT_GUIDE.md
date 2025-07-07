# Deployment Guide for Posit Cloud

## Overview
This guide will help you deploy the Hall of Fame Enhancers Analysis application to Posit Cloud for sharing and publication.

## Prerequisites
- Posit Cloud account (free or paid)
- All data files included in the `attached_assets/` folder

## Step-by-Step Deployment

### 1. Prepare Your Files
Before uploading, ensure you have these files ready:

**Core Application Files:**
- `app.py` - Main Streamlit application
- `data_processor.py` - Data processing module
- `visualization.py` - Visualization engine
- `posit_requirements.txt` - Python dependencies
- `manifest.json` - Posit Cloud configuration

**Data Files (from attached_assets/):**
- `Enhancer_and_experiment_metadata_1751579195077.feather` - Metadata
- `part1 (1)_1751576434359.csv` - Peak data part 1
- `part2 (1)_1751576437893.csv` - Peak data part 2
- `part3_1751576441401.csv` - Peak data part 3
- `part4_1751576447956.csv` - Peak data part 4

### 2. Upload to Posit Cloud

#### Option A: Direct Upload
1. Go to [posit.cloud](https://posit.cloud)
2. Sign in to your account
3. Click "New Project" → "New Project from Git Repository" or "Upload"
4. Upload all files maintaining the directory structure:
   ```
   project-root/
   ├── app.py
   ├── data_processor.py
   ├── visualization.py
   ├── posit_requirements.txt
   ├── manifest.json
   └── attached_assets/
       ├── Enhancer_and_experiment_metadata_1751579195077.feather
       ├── part1 (1)_1751576434359.csv
       ├── part2 (1)_1751576437893.csv
       ├── part3_1751576441401.csv
       └── part4_1751576447956.csv
   ```

#### Option B: GitHub Upload (Recommended)
1. Create a new GitHub repository
2. Upload all files to the repository
3. In Posit Cloud, choose "New Project from Git Repository"
4. Enter your GitHub repository URL

### 3. Configure the Environment

1. **Install Dependencies:**
   - Open the terminal in Posit Cloud
   - Run: `pip install -r posit_requirements.txt`

2. **Set Python Environment:**
   - Ensure Python 3.8+ is selected
   - Verify all packages are installed correctly

### 4. Run the Application

1. **Start the Streamlit App:**
   - In the terminal, run: `streamlit run app.py --server.port 8080`
   - Or use the "Run App" button if available

2. **Access Your App:**
   - The app will be available at the provided Posit Cloud URL
   - Share this URL with colleagues or make it public

### 5. Publishing Options

#### Make Public:
1. Go to your project settings in Posit Cloud
2. Change visibility to "Public"
3. Share the public URL

#### Share with Specific Users:
1. Go to project settings
2. Add collaborators by email
3. Set appropriate permissions (viewer/editor)

## Important Notes

### Data File Handling
- Keep all data files in the `attached_assets/` folder
- File paths are relative to the project root
- Large files may take time to upload

### Memory Requirements
- The app processes ~55 enhancers across 34 cell types
- Ensure your Posit Cloud plan has sufficient memory (recommended: 2GB+)

### URL Sharing
- Public URLs are persistent and can be bookmarked
- Private projects require Posit Cloud login to access

### Performance Tips
1. **Caching:** The app uses Streamlit's caching for performance
2. **Data Loading:** Initial load may take 30-60 seconds
3. **Concurrent Users:** Free plans have limited concurrent users

## Troubleshooting

### Common Issues:

**Dependencies Not Installing:**
```bash
pip install --upgrade pip
pip install -r posit_requirements.txt
```

**Data Files Not Found:**
- Verify the `attached_assets/` folder is uploaded
- Check file names match exactly (case-sensitive)

**Memory Issues:**
- Upgrade to a paid Posit Cloud plan
- Optimize data loading in the code

**App Not Loading:**
- Check the terminal for error messages
- Verify all Python packages are installed
- Ensure port 8080 is available

### Getting Help:
- Check Posit Cloud documentation
- Contact Posit Cloud support for platform issues
- Review app logs in the terminal for debugging

## Success Indicators
✓ All files uploaded successfully
✓ Dependencies installed without errors
✓ App starts without Python errors
✓ Data loads correctly (55 enhancers visible)
✓ Filters work properly
✓ Visualizations render correctly
✓ Imaging links are accessible

Your Hall of Fame Enhancers Analysis app is now ready for sharing and collaboration on Posit Cloud!