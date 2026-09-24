# ImageCleaner

> A Unified Python Library for Automated Image Dataset Cleaning and Validation for Machine Learning Applications.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.1.0-orange)

---

## Overview

ImageCleaner is an open-source Python library designed to automate image dataset cleaning and validation before machine learning and computer vision training.

The library helps researchers, students, and developers improve dataset quality by detecting common image issues such as duplicate images, corrupted files, blur, low resolution, improper brightness, and unsupported formats.

---

## Features

- Duplicate Image Detection
- Corrupted Image Detection
- Blur Detection
- Resolution Validation
- Brightness Analysis
- Image Format Validation
- Dataset Quality Score
- CSV Report Generation
- JSON Report Generation
- Modular Python API
- Machine Learning Ready Output

---

## Project Structure

```
SmartClean-AI/
│
├── imagecleaner/
├── datasets/
├── docs/
├── examples/
├── logs/
├── reports/
├── tests/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/SmartClean-AI.git
```

Move into the project

```bash
cd SmartClean-AI
```

Create virtual environment

```bash
py -3.13 -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Basic Usage

```python
from imagecleaner import ImageCleaner

cleaner = ImageCleaner("datasets")

cleaner.clean()
```

---

## Current Modules

- Dataset Loader
- Image Validator
- Duplicate Detector
- Blur Detector
- Resolution Detector
- Brightness Detector
- Report Generator
- Quality Score

---

## Development Roadmap

### Foundation Edition (v1.0)

- Core Library
- Image Validation
- Duplicate Detection
- Blur Detection
- Reporting

### Enhanced Edition (v2.0)

- Better Architecture
- Configurable Rules
- Improved Reports
- Dataset Quality Metrics

### Professional Edition (v3.0)

- CLI
- Unit Testing
- GitHub Actions
- API Documentation
- PyPI Release

---

## Technology Stack

- Python 3.13
- OpenCV
- Pillow
- NumPy
- pandas
- imagehash
- pytest
- Ruff
- Black

---

## License

MIT License

---

## Author

**Sumit Palekar**

MCA Research Project

SmartClean AI