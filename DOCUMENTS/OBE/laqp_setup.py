"""
Setup script for Louisiana QSO Party Processor
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="laqp-processor",
    version="0.1.0",
    description="Louisiana QSO Party Contest Log Processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    author="Jefferson Amateur Radio Club",
    author_email="questions@laqp.org",
    url="https://laqp.louisianacontestclub.org",
    
    packages=find_packages(exclude=["tests", "tests.*"]),
    
    python_requires=">=3.8",
    
    install_requires=[
        "sqlalchemy>=2.0.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "pandas>=2.0.0",
        "python-dateutil>=2.8.0",
        "wtforms>=3.0.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ],
        "prod": [
            "gunicorn>=21.0.0",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "laqp-process=scripts.process_all_logs:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Ham Radio",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    keywords="ham radio amateur radio contest qso party louisiana",
)
