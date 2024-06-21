import os
import re
import unicodedata
from pathlib import Path


def secure_filename(filename):
    # Normalize unicode characters
    filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")

    # Remove any non-alphanumeric characters except for '-', '_', and '.'
    filename = re.sub(r"[^\w\-_\.]", "", filename)

    # Remove any leading or trailing dots or spaces
    filename = filename.strip(". ")

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Ensure the filename isn't empty after sanitization
    if not filename:
        filename = "unnamed_file"

    # Handle Windows reserved names
    if os.name == "nt":
        windows_reserved = (
            {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
        )
        name, ext = os.path.splitext(filename)
        if name.upper() in windows_reserved:
            filename = f"_{filename}"

    return filename


def get_safe_filename(filename):
    """
    Get a safe version of the filename.
    """
    return secure_filename(Path(filename).name)
