from imagecleaner.core.dataset_loader import DatasetLoader
from imagecleaner.core.image_metadata import ImageMetadataExtractor
from imagecleaner.detectors.blur_detector import BlurDetector
from imagecleaner.detectors.brightness_detector import BrightnessDetector
from imagecleaner.detectors.resolution_detector import ResolutionDetector
from imagecleaner.reports.quality_score import QualityScorer


def main() -> None:
    loader = DatasetLoader("datasets")
    dataset = loader.discover()

    metadata_extractor = ImageMetadataExtractor()
    blur_detector = BlurDetector()
    brightness_detector = BrightnessDetector()
    resolution_detector = ResolutionDetector()
    quality_scorer = QualityScorer()

    print("\n========== QUALITY DIAGNOSTIC ==========")

    for image in dataset.images:
        metadata = metadata_extractor.extract(image)

        blur = blur_detector.detect(image)

        brightness = brightness_detector.detect(image)

        resolution = resolution_detector.detect(metadata)

        quality = quality_scorer.calculate(
            image=image,
            blur=blur,
            brightness=brightness,
            resolution=resolution,
            is_duplicate=False,
        )

        print(f"\nImage: {image.filename}")
        print(f"  Blur status       : {blur.is_blurry}")
        print(f"  Blur score        : {blur.score:.2f}")
        print(f"  Brightness score  : {brightness.score:.2f}")
        print(f"  Brightness status : {brightness.status}")
        print(
            f"  Resolution        : "
            f"{resolution.width}x{resolution.height}"
        )
        print(
            f"  Megapixels        : "
            f"{resolution.megapixels:.2f}"
        )
        print(
            f"  Low resolution   : "
            f"{resolution.is_low_resolution}"
        )
        print(
            f"  Final score       : "
            f"{quality.score:.2f}"
        )
        print(
            f"  Grade             : "
            f"{quality.grade}"
        )


if __name__ == "__main__":
    main()