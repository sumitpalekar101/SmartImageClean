# SmartImageClean

**Clean, validate, standardize, and prepare image datasets with a simple Python API.**

[![PyPI Version](https://img.shields.io/pypi/v/smartimageclean.svg)](https://pypi.org/project/smartimageclean/)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

SmartImageClean is a configurable Python library for image quality analysis, validation, standardization, restoration, and dataset cleaning. It helps developers and ML practitioners find common image issues and prepare datasets through a reusable Python pipeline.

## Why SmartImageClean?

Image datasets can contain images with inconsistent dimensions, formats, brightness, sharpness, aspect ratios, color modes, and file sizes. Checking these issues manually takes time.

SmartImageClean provides a workflow for analyzing images against configurable requirements, identifying images that need attention, standardizing them when possible, and reviewing the resulting analysis.

## Install

```bash
python -m pip install smartimageclean
```

Upgrade to the latest published version:

```bash
python -m pip install --upgrade smartimageclean
```

- **PyPI package name:** `smartimageclean`
- **Python import name:** `imagecleaner`

## Quick Start

1. Put your images in a folder, for example `datasets/`.
2. Install SmartImageClean.
3. Create a Python file and run the pipeline:

```python
from imagecleaner import ImageCleanerPipeline

pipeline = ImageCleanerPipeline("datasets")
result = pipeline.process()
```

That's the basic integration: import the pipeline, point it to your dataset, and call `process()`.

`process()` returns a structured result. The pipeline workflow is designed to analyze the dataset, standardize images that fail configured requirements, and re-analyze the standardized output. Exact behavior depends on the installed release and configuration.

## Workflow

```text
Image Dataset
     |
     v
Load and Validate Images
     |
     v
Analyze Quality and Metadata
     |
     v
Check Configured Requirements
     |
     v
Decision
  /       \
Keep     Needs work
             |
             v
       Standardize image
             |
             v
         Re-analyze
             |
             v
        Final results
```

Typical checks include:

- Image dimensions and resolution
- Brightness
- Blur and sharpness
- Image format and color mode
- Aspect ratio and file size
- Duplicate detection
- Image quality score

Which checks run depends on the available settings and configuration.

## Configure the Pipeline

Use `configure()` to change supported validation requirements:

```python
from imagecleaner import ImageCleanerPipeline

pipeline = ImageCleanerPipeline("datasets")

pipeline.configure(
    min_width=224,
    min_height=224,
    required_format="JPEG",
    required_color_mode="RGB",
)

result = pipeline.process()
```

Configuration options supported by the pipeline implementation include:

- `min_width`, `max_width`
- `min_height`, `max_height`
- `min_brightness`, `max_brightness`
- `blur_threshold`
- `min_quality_score`
- `required_format`
- `required_color_mode`
- `required_aspect_ratio`
- `max_file_size`
- `check_duplicates`
- `check_blur`
- `check_resolution`
- `check_brightness`

Use values that fit your project and check the package configuration for accepted types, units, and valid ranges.

## Main API

| API | What it does |
|---|---|
| `ImageCleanerPipeline(...)` | Creates a pipeline for an image dataset |
| `run()` | Runs dataset analysis and returns a result |
| `process()` | Runs the processing workflow, including standardization and re-analysis where applicable |
| `configure(**overrides)` | Updates supported validation settings |
| `standardize(image_path, output_path)` | Standardizes an individual image |
| `restore(image_path, output_path, ...)` | Applies supported image enhancement operations |
| `settings` | Provides access to current pipeline settings |
| `clean` | Provides the current cleaning setting |

### Analyze without the processing workflow

```python
from imagecleaner import ImageCleanerPipeline

pipeline = ImageCleanerPipeline("datasets")
result = pipeline.run()
```

### Standardize an individual image

```python
pipeline.standardize(
    image_path="datasets/photo.png",
    output_path="standardized/photo.jpg",
)
```

### Restore an image

```python
pipeline.restore(
    image_path="datasets/photo.jpg",
    output_path="restored/photo.jpg",
    brightness=1.1,
    contrast=1.1,
    sharpness=1.2,
    denoise=False,
    upscale=1.0,
)
```

Restoration options and output behavior depend on the installed implementation. Use a separate output path to help preserve the original image.

## Understanding the Result

`run()` and `process()` return a `PipelineResult`. Useful result properties include:

| Property | Meaning |
|---|---|
| `total_images` | Number of images represented in the result |
| `kept_count` | Images marked to be kept |
| `review_count` | Images that need review |
| `removal_count` | Removal candidates |
| `duplicate_count` | Images identified as duplicates |
| `acceptable_count` | Images satisfying the active configuration |
| `unacceptable_count` | Images failing the active configuration |

The result may also include a `processing` summary, with information such as initial counts and the number of standardized images. The final image count may differ from the original count because the final result can represent the re-analyzed standardized dataset.

Supporting result classes in the pipeline include `PipelineImageResult`, `ImageAnalysis`, `ConfigurationAnalysis`, and `ProcessingSummary`.

## Reports and Console Summary

The project includes a review-report component. Report formats, output directory, filenames, and whether reports and summaries are generated automatically can vary by release and settings.

Check the behavior of the version you install before relying on automatic TXT, CSV, or JSON report generation.

## Command-Line Interface

If the CLI is included in your installed version, view its available commands with:

```bash
python -m imagecleaner --help
```

The source project has documented commands for dataset analysis and processing. Confirm supported flags with the help output for your installed release.

## Safety Notes

- Test the pipeline on a copy of your dataset before using cleaning or quarantine features.
- Review cleaning settings before running operations that move files.
- Standardization cannot guarantee that every image will pass every quality check.
- Keep backups of important source images.

## Technology

The project uses Python and image/data-processing tools such as Pillow, OpenCV, NumPy, ImageHash, and Pandas. The published package metadata defines the actual runtime requirements for each release.


## Project Structure

The repository is organized into modules for the pipeline, configuration, detectors, reports, restoration, standardization, utilities, and validators. The exact file layout can change between releases.

```text
SmartClean-AI/
├── imagecleaner/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cleaner.py
│   ├── cli.py
│   ├── config/
│   ├── core/
│   ├── detectors/
│   ├── exceptions/
│   ├── reports/
│   ├── restoration/
│   ├── standardization/
│   ├── utils/
│   └── validators/
├── tests/
├── README.md
├── pyproject.toml
├── requirements.txt
└── LICENSE
```

## Future Scope

Potential future improvements include AI-based image classification, advanced image-quality assessment, deep-learning-based restoration, dataset-specific profiles, a web interface, improved batch processing, cloud processing, additional image formats, and advanced visualization.

## License

SmartImageClean is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

**Sumit Palekar**
Creator and Maintainer of SmartImageClean

- Email: sumitpalekar101@gmail.com
- LinkedIn: https://www.linkedin.com/in/sumit-palekar-450686252/

## Links

- [SmartImageClean on PyPI](https://pypi.org/project/smartimageclean/)
- [GitHub repository](https://github.com/sumitpalekar101/SmartImageClean)