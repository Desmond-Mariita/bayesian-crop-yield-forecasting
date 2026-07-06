"""
Setup configuration for Bayesian Crop Yield Forecasting package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="bayesian-crop-yield-forecasting",
    version="0.1.0",
    author="Desmond Momanyi Mariita",
    author_email="dmariita@keragita.com",
    description="Crop Yield Forecasting with Uncertainty Quantification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Desmond-Mariita/bayesian-crop-yield-forecasting",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
    ],
)
