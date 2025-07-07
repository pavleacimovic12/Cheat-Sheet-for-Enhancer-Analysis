# 🧬 Hall of Fame Enhancers Analysis

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/yourusername/enhancer-analysis)
[![Posit Cloud](https://img.shields.io/badge/Posit%20Cloud-Deploy-orange)](https://posit.cloud)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io)

**Interactive genomic data visualization platform for analyzing 55 Hall of Fame enhancers with complete metadata, imaging integration, and pyGenomeTracks-style accessibility visualizations.**

## 🚀 Quick Deploy to Posit Cloud

### Option 1: Direct GitHub → Posit Cloud
1. Fork this repository
2. Go to [Posit Cloud](https://posit.cloud)
3. Create "New Project from Git Repository"
4. Enter your forked repository URL
5. Install dependencies: `pip install -r requirements.txt`
6. Run the app: `streamlit run app.py --server.port 8080`

### Option 2: Local Development
```bash
git clone https://github.com/yourusername/enhancer-analysis.git
cd enhancer-analysis
pip install -r requirements.txt
streamlit run app.py
```

## 📊 Features

### 🔬 Complete Genomic Analysis
- **55 Hall of Fame Enhancers**: Authentic genomic data from research
- **34 Cell Types**: Numerically ordered (1-34) for systematic analysis
- **2000px Height Visualizations**: Tall genomic browser-style plots
- **pyGenomeTracks Style**: Professional genomic visualization

### 🎛️ Advanced Filtering System
- **Enhancer Selection**: All 55 Hall of Fame enhancers
- **Cargo Filter**: Delivered genetic cargo types
- **Experiment Filter**: EPI, STPT, lightsheet experiments
- **Gene Filter**: Proximal gene associations
- **GC Delivered Filter**: 20 unique values (1.5×10⁹ to 5×10¹² genome copies)
- **Cell Type Filter**: Focus on specific cell types

### 📸 Imaging Integration
- **Neuroglancer Viewers**: Embedded 3D brain visualization
- **Contact Sheets**: High-resolution imaging contact sheets
- **MIP Projections**: Coronal and sagittal maximum intensity projections
- **Experiment-Specific Logic**: Lightsheet vs EPI prioritization
- **Dynamic Matching**: Filters precisely match imaging data

### 📈 Data Export & Analysis
- **CSV Export**: Download filtered accessibility data
- **Summary Statistics**: Comprehensive data metrics
- **Interactive Plots**: Plotly-based visualizations
- **Real-time Filtering**: Dynamic filter dependencies

## 🗂️ Project Structure

```
enhancer-analysis/
├── app.py                     # Main Streamlit application
├── data_processor.py          # Data processing module
├── visualization.py           # Genomic visualization engine
├── requirements.txt           # Python dependencies
├── runtime.txt               # Python version specification
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── data/                     # Data files directory
│   ├── Enhancer_and_experiment_metadata_1751579195077.feather
│   ├── part1 (1)_1751576434359.csv
│   ├── part2 (1)_1751576437893.csv
│   ├── part3_1751576441401.csv
│   └── part4_1751576447956.csv
├── docs/                     # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   └── API_REFERENCE.md
└── README.md                 # This file
```

## 🛠️ Technical Specifications

### Dependencies
- **Python**: 3.11+
- **Streamlit**: 1.28.0+
- **Pandas**: 2.0.0+
- **NumPy**: 1.24.0+
- **Plotly**: 5.15.0+
- **PyArrow**: 12.0.0+

### Data Files
- **Metadata**: 411 records with complete imaging links
- **Peak Data**: 310MB+ of accessibility measurements
- **File Format**: Feather and CSV for optimal performance

### Performance
- **Memory Requirements**: 2GB+ recommended
- **Load Time**: 30-60 seconds for initial data load
- **Concurrent Users**: Scalable on Posit Cloud

## 📋 Data Overview

### Enhancer Dataset
- **Total Enhancers**: 55 Hall of Fame enhancers
- **Genomic Coverage**: Multiple chromosomes and positions
- **Cell Types**: 34 systematically ordered cell types
- **Experiments**: EPI, STPT, lightsheet imaging

### Accessibility Data
- **Measurements**: Peak accessibility scores
- **Resolution**: High-resolution genomic positions
- **Normalization**: Consistent scaling across cell types
- **Format**: Ready for genomic browser visualization

### Imaging Integration
- **Neuroglancer**: 3D brain visualization links
- **Contact Sheets**: Allen Institute imaging
- **MIP Projections**: Maximum intensity projections
- **Experiment Types**: Lightsheet and EPI prioritization

## 🎯 Use Cases

### Research Applications
- **Comparative Analysis**: Compare enhancer activity across cell types
- **Experiment Planning**: Filter by cargo and experiment type
- **Data Export**: Download filtered datasets for analysis
- **Visualization**: Create publication-ready genomic plots

### Educational Use
- **Genomic Browser**: Learn pyGenomeTracks-style visualization
- **Data Filtering**: Understand dynamic filtering systems
- **Bioinformatics**: Explore real genomic datasets
- **Streamlit Development**: Reference for genomic applications

## 🔧 Configuration

### Streamlit Configuration
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8080
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### Environment Variables
No additional environment variables required - all data is file-based.

## 📖 Documentation

### Quick Start Guides
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [API Reference](docs/API_REFERENCE.md) - Code documentation
- [Data Dictionary](docs/DATA_DICTIONARY.md) - Data format specifications

### Examples
- [Basic Usage](examples/basic_usage.py) - Simple filtering examples
- [Advanced Filtering](examples/advanced_filtering.py) - Complex filter combinations
- [Data Export](examples/data_export.py) - Export functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Source**: Allen Institute for Brain Science
- **Visualization**: Inspired by pyGenomeTracks
- **Platform**: Built with Streamlit
- **Deployment**: Optimized for Posit Cloud

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/enhancer-analysis/issues)
- **Documentation**: [Project Wiki](https://github.com/yourusername/enhancer-analysis/wiki)
- **Community**: [Discussions](https://github.com/yourusername/enhancer-analysis/discussions)

## 🏷️ Version History

- **v1.0.0**: Initial release with complete functionality
- **v1.1.0**: Added GC delivered filter and enhanced imaging
- **v1.2.0**: Posit Cloud deployment optimization

---

**Ready for GitHub → Posit Cloud deployment!**

[![Deploy to Posit Cloud](https://img.shields.io/badge/Deploy%20to-Posit%20Cloud-orange?style=for-the-badge)](https://posit.cloud)