from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


class ImageRestorer:
    """Improve image quality using configurable enhancement operations."""

    def restore(
        self,
        image_path: str | Path,
        output_path: str | Path,
        *,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        denoise: bool = False,
        upscale: float = 1.0,
    ) -> Path:
        """
        Restore and enhance an image while preserving the original.

        Args:
            image_path: Path to the source image.
            output_path: Path for the restored image.
            brightness: Brightness factor. 1.0 keeps the original.
            contrast: Contrast factor. 1.0 keeps the original.
            sharpness: Sharpness factor. 1.0 keeps the original.
            denoise: Apply noise reduction when True.
            upscale: Resize factor. 1.0 keeps the original size.
        """
        image_path = Path(image_path)
        output_path = Path(output_path)

        if brightness <= 0:
            raise ValueError("brightness must be greater than zero.")

        if contrast <= 0:
            raise ValueError("contrast must be greater than zero.")

        if sharpness <= 0:
            raise ValueError("sharpness must be greater than zero.")

        if upscale <= 0:
            raise ValueError("upscale must be greater than zero.")

        with Image.open(image_path) as image:
            result = image.copy()

        if denoise:
            result = result.filter(ImageFilter.MedianFilter(size=3))

        if brightness != 1.0:
            result = ImageEnhance.Brightness(result).enhance(brightness)

        if contrast != 1.0:
            result = ImageEnhance.Contrast(result).enhance(contrast)

        if sharpness != 1.0:
            result = ImageEnhance.Sharpness(result).enhance(sharpness)

        if upscale != 1.0:
            width = round(result.width * upscale)
            height = round(result.height * upscale)

            result = result.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        result.save(output_path)
        result.close()

        return output_path