from setuptools import setup, find_packages

setup(
    name="middle_ear_model",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "pytest>=6.2.0",
        "sqlite3",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Middle ear barotrauma simulation model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 