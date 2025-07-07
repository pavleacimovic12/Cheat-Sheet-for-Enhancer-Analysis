# Posit Cloud Deployment Guide

## Step 1: Prepare Files for GitHub
1. Run the preparation script to move data files to main directory:
   ```bash
   python prepare_for_github.py
   ```
   This moves all CSV chunks and metadata from `data_chunks/` to the main directory.

## Step 2: Upload to GitHub
1. Create a new GitHub repository
2. Upload all files from this `fin_enhancer` folder to the repository
3. Ensure all 20 CSV chunks and the metadata feather file are included in the main directory

## Step 3: Deploy to Posit Cloud
1. Go to [Posit Cloud](https://posit.cloud/)
2. Click "New Project"
3. Select "New Project from Git Repository"
4. Enter your GitHub repository URL
5. Click "Deploy Project"

## Step 4: Configuration
Posit Cloud will automatically:
- Install Python dependencies from `requirements.txt`
- Use Python 3.11 as specified in `runtime.txt`
- Configure Streamlit with the `.streamlit/config.toml` settings

## Step 5: Launch
Once deployed, your app will be available at:
`https://your-username.posit.cloud/content/your-project-id/`

## Required Files Included:
✅ `app.py` - Main Streamlit application
✅ `data_processor_chunked.py` - Handles automatic CSV chunk assembly
✅ `visualization.py` - Creates genomic visualizations
✅ `requirements.txt` - Python dependencies
✅ `runtime.txt` - Python version specification
✅ `.streamlit/config.toml` - Streamlit configuration
✅ All 20 CSV chunks + metadata in main directory

## Data Processing:
The app automatically combines all CSV chunks when it starts, providing the complete 294MB dataset with all 55 Hall of Fame enhancers and full functionality.

## Latest Fix (Required):
The current app.py file has been updated to fix a NameError and properly handle data loading from chunked CSV files. Make sure to upload the latest version of app.py to your GitHub repository.

## Troubleshooting:
- If deployment fails, check that all files are under 25MB
- Verify Python version is 3.11
- Ensure all dependencies are properly listed in requirements.txt