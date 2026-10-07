# SmartImageClean

A configurable Python library for automated image quality analysis, validation, standardization, restoration, and dataset cleaning.

[![PyPI Version](https://img.shields.io/pypi/v/smartimageclean.svg)](https://pypi.org/project/smartimageclean/)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)]()

## Overview

SmartImageClean is a reusable and configurable Python library designed to analyze, validate, standardize, restore, and clean image datasets.

The library checks images for common quality and consistency problems such as low resolution, unsuitable brightness, blur, incorrect format, color mode mismatch, aspect-ratio mismatch, file-size limits, and duplicate images.

Instead of applying the same operation to every image, SmartImageClean first analyzes each image against configurable requirements and then makes a decision based on the analysis.

## Problem Statement

Image datasets collected from different sources often contain images with different resolutions, formats, color modes, brightness levels, blur levels, aspect ratios, and file sizes.

Manually checking and preparing these images is time-consuming and inconsistent.

SmartImageClean provides an automated and configurable approach for analyzing image quality, identifying problems, standardizing images, and validating the processed results.

## Key Features

- Recursive image dataset discovery
- Image validation
- Image metadata extraction
- Blur and sharpness detection
- Brightness analysis
- Resolution and dimension checking
- Duplicate detection
- Similar-image detection
- Image quality scoring
- Configuration-based quality analysis
- Rule-based decision engine
- Image standardization
- Image restoration
- Automatic re-analysis after processing
- Quarantine-based cleaning
- Review reports
- Command-line interface
- Automated testing
- Reusable Python API

## Workflow

```text
Image Dataset
      ↓
Dataset Loading
      ↓
Validation
      ↓
Image Analysis
      ↓
Quality Checks
      ↓
Configuration Check
      ↓
Decision Engine
      ↓
   Acceptable?
    ↙       ↘
  YES        NO
   ↓          ↓
 KEEP     STANDARDIZE
              ↓
         RE-ANALYZE
              ↓
        Final Result
              ↓
            Report

            
---

### Section 6 — Architecture

```markdown
## Architecture

SmartImageClean follows a modular, configuration-driven architecture.

```text
                  IMAGE DATASET
                       ↓
                Dataset Loader
                       ↓
                   Validator
                       ↓
                Image Analysis
                       ↓
              Configuration Check
                       ↓
                Decision Engine
                       ↓
             ┌─────────┴─────────┐
             ↓                   ↓
            KEEP              REVIEW
                                 ↓
                           Standardization
                                 ↓
                            Re-analysis
                                 ↓
                            Final Result
                                 ↓
                               Report

                               
---

### Section 7 — Project Structure

```markdown
## Project Structure

```text
SmartImageClean/
│
├── imagecleaner/
│   ├── cleaner.py
│   ├── cli.py
│   ├── __init__.py
│   ├── __main__.py
│   │
│   ├── config/
│   ├── core/
│   ├── detectors/
│   ├── exceptions/
│   ├── reports/
│   ├── restoration/
│   ├── standardization/
│   ├── utils/
│   └── validators/
│
├── tests/
│   ├── test_metadata.py
│   ├── test_pipeline.py
│   ├── test_validator.py
│   ├── test_config.py
│   ├── test_standardizer.py
│   └── test_restorer.py
│
├── test_quality_diagnostic.py
├── README.md
├── pyproject.toml
└── requirements.txt


---

### Section 8 — Installation

```markdown
## Installation

Install SmartImageClean directly from PyPI:

```bash
pip install smartimageclean

After installation, the package can be imported using:

import imagecleaner


---

### Section 9 — Requirements

```markdown
## Requirements

- Python 3.13+
- Pillow
- NumPy
- OpenCV
- ImageHash
- Pandas

Development and testing use:

- pytest
- Black
- Ruff

## Basic Python Usage

```python
from imagecleaner import ImageCleaner

cleaner = ImageCleaner("datasets")

result = cleaner.run()


---

### Section 11 — Configuration

```markdown
## Configuration

SmartImageClean allows users to configure image requirements according to their application.

Example:

```python
cleaner.configure(
    min_width=224,
    min_height=224,
    required_format="JPEG",
    required_color_mode="RGB"
)


---

### Section 12 — Analysis

```markdown
## Image Analysis

Analysis evaluates each image based on the active configuration requirements.

The system can examine:

- Image dimensions
- Brightness
- Blur/sharpness
- Image format
- Color mode
- Aspect ratio
- File size
- Duplicate status
- Quality score

The analysis produces structured information that is passed to the decision engine.

## Decision Engine

The decision engine uses the analysis results to classify images.

Typical decisions include:

- **KEEP** — image satisfies the required conditions.
- **REVIEW** — image has one or more issues that require further processing or manual inspection.
- **REMOVE** — image is considered a removal candidate according to the cleaning rules.

SmartImageClean is designed to avoid unsafe automatic deletion by preserving original files and using quarantine-based cleaning.

## Decision Engine

The decision engine uses the analysis results to classify images.

Typical decisions include:

- **KEEP** — image satisfies the required conditions.
- **REVIEW** — image has one or more issues that require further processing or manual inspection.
- **REMOVE** — image is considered a removal candidate according to the cleaning rules.

SmartImageClean is designed to avoid unsafe automatic deletion by preserving original files and using quarantine-based cleaning.

## Image Standardization

Standardization converts images into a common predefined format and set of requirements so that they are consistent and suitable for a particular application.

It can handle requirements such as:

- Image format
- Color mode
- Width
- Height
- Aspect ratio
- Orientation

After standardization, the processed images can be analyzed again to verify whether they now satisfy the configured requirements.


## Re-analysis

SmartImageClean can automatically re-analyze standardized images.

The workflow is:

    Initial Analysis
           ↓
    Identify Unacceptable Images
           ↓
    Standardization
           ↓
    Re-analysis
           ↓
    Final Result

This prevents the system from assuming that every transformed image has automatically become acceptable.

If an image still fails a quality requirement after standardization, it can remain under review.


## Image Restoration

SmartImageClean also provides image restoration utilities for improving image quality.

Supported operations include:

- Brightness adjustment
- Contrast enhancement
- Sharpness enhancement
- Denoising
- Image upscaling

Example:

    from imagecleaner.restoration.restorer import ImageRestorer

    restorer = ImageRestorer()

    restorer.restore(
        "input.jpg",
        "output.jpg",
        brightness=1.2,
        contrast=1.1,
        sharpness=1.3
    )

The original image is preserved while the restored image is written to a separate output path.


## Command Line Interface

SmartImageClean provides a command-line interface.

Show help:

    python -m imagecleaner --help

Run normal analysis:

    python -m imagecleaner "datasets"

Run automatic processing:

    python -m imagecleaner "datasets" --process

The CLI supports options for processing, standardization, quarantine, and cleaning.


## Reports

SmartImageClean can generate reports containing information about image analysis and cleaning decisions.

Reports can help users identify:

- Total images processed
- Acceptable images
- Images requiring review
- Removal candidates
- Duplicate information
- Quality-related problems
- Processing results

A review report can be generated in the project's `reports/` directory.


## Safety Approach

SmartImageClean follows a conservative cleaning approach.

The system does not immediately delete original images during automatic processing.

Instead, problematic images can be:

1. Identified during analysis.
2. Standardized when possible.
3. Re-analyzed.
4. Kept for review if problems remain.
5. Moved to quarantine when cleaning is explicitly requested.

This helps reduce accidental data loss.


## Technology Stack

| Technology |          Purpose                   |
|------------|------------------------------------|                          
| Python     | Core programming language          |
| Pillow     | Image processing                   |
| OpenCV     | Image analysis                     |
| NumPy      | Numerical operations               |
| ImageHash  | Duplicate and similarity detection |
| Pandas     | Data handling                      |
| pathlib    | File and directory handling        |
| hashlib    | File hashing                       |
| argparse   | Command-line interface             |
| dataclasses| Structured results                 |
| pytest     | Automated testing                  |


## Testing

The project includes automated tests for major components.

Tested areas include:

- Configuration
- Image validation
- Metadata extraction
- Pipeline processing
- Standardization
- Restoration

Current test result:

    26 tests passed

Run the tests using:

    python -m pytest -q


## Package Information

**Package name:** `smartimageclean`

**Current version:** `0.1.2`

**PyPI installation:**

    pip install smartimageclean

**Python import:**

    import imagecleaner

**Main class:**

    from imagecleaner import ImageCleaner

SmartImageClean is distributed as a reusable Python package for image dataset quality analysis and preprocessing.


## Development Status

SmartImageClean is currently in the **Alpha** stage.

The current release focuses on:

- Image quality analysis
- Configuration-based validation
- Standardization
- Restoration utilities
- Dataset cleaning
- Reporting
- Automated testing
- Command-line usage

The library is designed to be extended with additional image-processing and AI-based capabilities in future versions.


## Future Scope

Future versions may include:

- AI-based image classification
- Advanced image-quality assessment
- Deep-learning-based restoration
- More advanced duplicate detection
- Dataset-specific profiles
- Web-based user interface
- Batch processing improvements
- Cloud-based dataset processing
- Additional image formats
- Advanced visualization and analytics


## Use Cases

SmartImageClean can be used in:

- Machine learning dataset preparation
- Computer vision projects
- Research image datasets
- E-commerce product image processing
- Photography platforms
- Internal company image collections
- Academic projects
- Image preprocessing pipelines

The library is designed to work with different image datasets rather than being limited to one specific application.


## Design Principles

SmartImageClean follows these design principles:

- **Reusable** — designed as a Python library.
- **Configurable** — image requirements can be customized.
- **Modular** — different responsibilities are separated into modules.
- **Safe** — original images are preserved during processing.
- **Verifiable** — processed images can be re-analyzed.
- **Extensible** — new detectors and processing methods can be added later.


## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.


## Author

**Sumit Palekar**

Creator and Maintainer of SmartImageClean

- Email: sumitpalekar101@gmail.com
- 💼 [LinkedIn](https://www.linkedin.com/in/sumit-palekar-450686252/)