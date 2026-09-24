from pathlib import Path

from PIL import Image, ImageOps


class ImageStandardizer:
    """Convert images to configured standard requirements."""

    def standardize(
        self,
        image_path: str | Path,
        output_path: str | Path,
        *,
        required_format: str | None = None,
        required_color_mode: str | None = None,
        min_width: int | None = None,
        max_width: int | None = None,
        min_height: int | None = None,
        max_height: int | None = None,
        required_aspect_ratio: float | None = None,
    ) -> Path:
        """Standardize one image and save the result."""

        image_path = Path(image_path)
        output_path = Path(output_path)

        with Image.open(image_path) as image:
            result = ImageOps.exif_transpose(image).copy()

        if required_color_mode is not None:
            result = self._convert_color_mode(
                result,
                required_color_mode,
            )

        save_format = (
            required_format
            or image_path.suffix.lstrip(".").upper()
        )

        if save_format == "JPG":
            save_format = "JPEG"

        # JPEG does not support transparency.
        if save_format == "JPEG" and result.mode in {"RGBA", "LA"}:
            result = result.convert("RGB")

        result = self._resize_to_requirements(
            result,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            required_aspect_ratio=required_aspect_ratio,
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result.save(
            output_path,
            format=save_format,
        )

        result.close()

        return output_path

    @staticmethod
    def _convert_color_mode(
        image: Image.Image,
        mode: str,
    ) -> Image.Image:
        """Convert an image to the requested color mode."""

        return image.convert(mode.upper())

    @staticmethod
    def _resize_to_requirements(
        image: Image.Image,
        *,
        min_width: int | None,
        max_width: int | None,
        min_height: int | None,
        max_height: int | None,
        required_aspect_ratio: float | None,
    ) -> Image.Image:
        """Resize an image to configured dimension requirements."""

        width, height = image.size

        if required_aspect_ratio is not None:
            width, height = ImageStandardizer._fit_aspect_ratio(
                width,
                height,
                required_aspect_ratio,
            )

        target_width = width
        target_height = height

        if min_width is not None:
            target_width = max(target_width, min_width)

        if max_width is not None:
            target_width = min(target_width, max_width)

        if min_height is not None:
            target_height = max(target_height, min_height)

        if max_height is not None:
            target_height = min(target_height, max_height)

        if (
            target_width == image.width
            and target_height == image.height
        ):
            return image

        return image.resize(
            (target_width, target_height),
            Image.Resampling.LANCZOS,
        )

    @staticmethod
    def _fit_aspect_ratio(
        width: int,
        height: int,
        aspect_ratio: float,
    ) -> tuple[int, int]:
        """Fit dimensions to the requested aspect ratio."""

        if aspect_ratio <= 0:
            raise ValueError(
                "required_aspect_ratio must be greater than zero."
            )

        current_ratio = width / height

        if current_ratio > aspect_ratio:
            height = round(width / aspect_ratio)
        else:
            width = round(height * aspect_ratio)

        return width, height