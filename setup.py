#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="uni-diff",
    version="0.1.0",
    author="uni-diff contributors",
    description="Universal file diff tool - compare any files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/uni-diff",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (none required for basic text diff)
    ],
    extras_require={
        "pdf": ["pymupdf>=1.20.0"],
        "docx": ["python-docx>=0.8.0"],
        "xlsx": ["openpyxl>=3.0.0"],
        "pptx": ["python-pptx>=0.6.0"],
        "image": ["Pillow>=9.0.0", "pytesseract>=0.3.0"],
        "png": ["Pillow>=9.0.0"],
        "all": [
            "pymupdf>=1.20.0",
            "python-docx>=0.8.0",
            "openpyxl>=3.0.0",
            "python-pptx>=0.6.0",
            "Pillow>=9.0.0",
            "pytesseract>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "uni-diff=cli:main",
        ],
    },
)
