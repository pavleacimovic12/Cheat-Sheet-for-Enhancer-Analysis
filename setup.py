from setuptools import setup, find_packages

setup(
    name="hall-of-fame-enhancers",
    version="1.0.0",
    description="Interactive genomic data visualization platform for analyzing enhancer accessibility profiles",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "streamlit>=1.24.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "pyarrow>=12.0.0"
    ],
    entry_points={
        "console_scripts": [
            "enhancer-analysis=app:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)