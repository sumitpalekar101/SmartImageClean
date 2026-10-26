
from pathlib import Path

from PIL import Image, ImageOps


class ImageStandardizer:
    """Convert images to configured standard requirements."""

    FORMAT_EXTENSIONS = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
        "BMP": ".bmp",
        "TIFF": ".tiff",
        "GIF": ".gif",
    }

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

        # Validate dimension requirements.
        if min_width is not None and min_width < 1:
            raise ValueError("min_width must be greater than zero.")

        if max_width is not None and max_width < 1:
            raise ValueError("max_width must be greater than zero.")

        if min_height is not None and min_height < 1:
            raise ValueError("min_height must be greater than zero.")

        if max_height is not None and max_height < 1:
            raise ValueError("max_height must be greater than zero.")

        if (
            min_width is not None
            and max_width is not None
            and min_width > max_width
        ):
            raise ValueError("min_width cannot exceed max_width.")

        if (
            min_height is not None
            and max_height is not None
            and min_height > max_height
        ):
            raise ValueError("min_height cannot exceed max_height.")

        if (
            required_aspect_ratio is not None
            and required_aspect_ratio <= 0
        ):
            raise ValueError(
                "required_aspect_ratio must be greater than zero."
            )

        # Open the image and correct its EXIF orientation.
        with Image.open(image_path) as image:
            result = ImageOps.exif_transpose(image).copy()

        try:
            # Convert color mode when requested.
            if required_color_mode is not None:
                result = self._convert_color_mode(
                    result,
                    required_color_mode,
                )

            # Determine the required output format.
            save_format = (
                required_format
                or image_path.suffix.lstrip(".")
            ).upper()

            if save_format == "JPG":
                save_format = "JPEG"

            if save_format not in self.FORMAT_EXTENSIONS:
                raise ValueError(
                    f"Unsupported output format: {save_format}"
                )

            # JPEG does not support transparency.
            if (
                save_format == "JPEG"
                and result.mode in {"RGBA", "LA", "P"}
            ):
                result = result.convert("RGB")

            # Resize according to the requested requirements.
            result = self._resize_to_requirements(
                result,
                min_width=min_width,
                max_width=max_width,
                min_height=min_height,
                max_height=max_height,
                required_aspect_ratio=required_aspect_ratio,
            )

            # Match the filename extension to the actual format.
            output_path = output_path.with_suffix(
                self.FORMAT_EXTENSIONS[save_format]
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            result.save(
                output_path,
                format=save_format,
            )

            return output_path

        finally:
            result.close()

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
        """Resize an image while preserving its proportions where possible."""

        original_width, original_height = image.size

        if original_width <= 0 or original_height <= 0:
            raise ValueError("Image dimensions must be positive.")

        ratio = (
            required_aspect_ratio
            if required_aspect_ratio is not None
            else original_width / original_height
        )

        # Determine the permitted scale range.
        lower_scale = 0.0
        upper_scale = float("inf")

        if min_width is not None:
            lower_scale = max(lower_scale, min_width / original_width)

        if max_width is not None:
            upper_scale = min(upper_scale, max_width / original_width)

        if min_height is not None:
            lower_scale = max(lower_scale, min_height / original_height)

        if max_height is not None:
            upper_scale = min(upper_scale, max_height / original_height)

        if lower_scale > upper_scale:
            raise ValueError(
        f"Dimension limits conflict for image size "
        f"{original_width}x{original_height}. "
        f"Required limits: width={min_width}..{max_width}, "
        f"height={min_height}..{max_height}, "
        f"aspect_ratio={required_aspect_ratio}."
    )

        # Keep the original size if possible; otherwise resize to fit.
        scale = min(1.0, upper_scale)

        if scale < lower_scale:
            scale = lower_scale

        target_width = max(1, round(original_width * scale))
        target_height = max(1, round(original_height * scale))

        # Apply an explicitly requested aspect ratio, if provided.
        if required_aspect_ratio is not None:
            target_width = max(1, round(target_height * ratio))
            target_height = max(1, round(target_width / ratio))

        # Verify the final dimensions after rounding.
        if (
            (min_width is not None and target_width < min_width)
            or (max_width is not None and target_width > max_width)
            or (min_height is not None and target_height < min_height)
            or (max_height is not None and target_height > max_height)
        ):
            raise ValueError(
                f"Cannot satisfy dimension limits without changing proportions: "
                f"calculated {target_width}x{target_height}."
            )

        if (target_width, target_height) == image.size:
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
            width = max(1, round(height * aspect_ratio))
        else:
            height = max(1, round(width / aspect_ratio))

        return width, height
