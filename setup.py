"""
Setup configuration for the Barotrauma Model package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="barotrauma-model",
    version="2.2.0",
    author="Dr. Diego L Malpica (Aerospace Medicine) ORCID: https://orcid.org/0000-0002-2257-4940",
    author_email="dlmalpica@yahoo.com",
    description="Physics-informed middle-ear barotrauma risk model for hypobaric-chamber training (FAC-anchored)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/strikerdlm/barotrauma_model",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
            "myst-parser>=0.15",
        ]
    },
    entry_points={
        "console_scripts": [
            "barotrauma-app=app.streamlit_app:main",
        ],
    },
    package_data={
        "barotrauma": ["data/*.json", "data/*.csv"],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="barotrauma aviation medicine physiology simulation risk-assessment",
    project_urls={
        "Documentation": "https://github.com/strikerdlm/barotrauma_model/docs",
        "Source": "https://github.com/strikerdlm/barotrauma_model",
        "Tracker": "https://github.com/strikerdlm/barotrauma_model/issues",
    },
)