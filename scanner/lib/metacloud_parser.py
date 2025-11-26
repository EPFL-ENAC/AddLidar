"""Parser for .metacloud files with attribute extraction and validation."""

import re
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Supported date formats (most specific to least specific)
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
]


@dataclass
class MetacloudParseError:
    """Represents a parsing error in the metacloud file."""

    line_number: int
    line_content: str
    error_type: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line_number}: {self.error_type} - {self.message}"


@dataclass
class MetacloudAttributes:
    """Parsed attributes from a .metacloud file."""

    name: Optional[str] = None
    date: Optional[str] = None  # ISO format YYYY-MM-DD
    extra_attributes: dict = field(default_factory=dict)
    errors: list[MetacloudParseError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "date": self.date,
            "extra_attributes": self.extra_attributes,
            "parse_errors": [str(e) for e in self.errors] if self.errors else None,
        }


def parse_date(
    value: str, line_number: int, line_content: str
) -> tuple[Optional[str], Optional[MetacloudParseError]]:
    """Parse a date string and return ISO format or error."""
    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(value.strip(), fmt)
            return parsed.strftime("%Y-%m-%d"), None
        except ValueError:
            continue

    return None, MetacloudParseError(
        line_number=line_number,
        line_content=line_content,
        error_type="INVALID_DATE_FORMAT",
        message=f"Could not parse date '{value}'. Expected formats: YYYY-MM-DD, DD/MM/YYYY, DD.MM.YYYY",
    )


def parse_quoted_value(
    value: str, line_number: int, line_content: str
) -> tuple[Optional[str], Optional[MetacloudParseError]]:
    """Parse a quoted string value."""
    value = value.strip()

    # Check for properly quoted string
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1], None

    # Check for single quotes (warn but accept)
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        logger.warning(
            f"Line {line_number}: Using single quotes, double quotes recommended"
        )
        return value[1:-1], None

    # Check for unclosed quotes
    if value.startswith('"') or value.startswith("'"):
        return None, MetacloudParseError(
            line_number=line_number,
            line_content=line_content,
            error_type="UNCLOSED_QUOTE",
            message="Value has opening quote but no closing quote",
        )

    # No quotes at all - this might be intentional for simple values
    return None, MetacloudParseError(
        line_number=line_number,
        line_content=line_content,
        error_type="MISSING_QUOTES",
        message=f"Value '{value}' should be enclosed in double quotes",
    )


def parse_attribute_line(
    line: str, line_number: int
) -> tuple[Optional[str], Optional[str], Optional[MetacloudParseError]]:
    """
    Parse a single attribute line in format: key "value" or key value
    Returns (key, value, error)
    """
    line = line.strip()
    if not line:
        return None, None, None

    # Match pattern: key followed by whitespace and then quoted or unquoted value
    # Pattern: word characters for key, then space(s), then the rest is value
    match = re.match(r"^(\w+)\s+(.+)$", line)
    if not match:
        return (
            None,
            None,
            MetacloudParseError(
                line_number=line_number,
                line_content=line,
                error_type="INVALID_FORMAT",
                message='Expected format: key "value"',
            ),
        )

    key = match.group(1).lower()
    raw_value = match.group(2).strip()

    # Try to parse quoted value
    parsed_value, error = parse_quoted_value(raw_value, line_number, line)

    if error and error.error_type == "MISSING_QUOTES":
        # For unquoted values, use the raw value but keep the error as warning
        return key, raw_value, error

    return key, parsed_value, error


def parse_metacloud_file(file_path: str) -> MetacloudAttributes:
    """
    Parse a .metacloud file and extract attributes.

    The file format is:
    ```
    POINTS_FILES
    ./path/to/file1.las
    ...

    METACLOUD_ATTRIBUTES
    name "Mission Name"
    date "2024-03-15"
    creator "Your Name"
    ...
    ```
    """
    result = MetacloudAttributes()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try latin-1 as fallback
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            result.errors.append(
                MetacloudParseError(
                    line_number=0,
                    line_content="",
                    error_type="FILE_READ_ERROR",
                    message=f"Could not read file: {e}",
                )
            )
            return result
    except Exception as e:
        result.errors.append(
            MetacloudParseError(
                line_number=0,
                line_content="",
                error_type="FILE_READ_ERROR",
                message=f"Could not read file: {e}",
            )
        )
        return result

    # Find METACLOUD_ATTRIBUTES section
    lines = content.split("\n")
    in_attributes_section = False
    attributes_start_line = 0

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Check for section markers
        if stripped == "METACLOUD_ATTRIBUTES":
            in_attributes_section = True
            attributes_start_line = i
            continue

        # Exit attributes section on new section or end of file
        if in_attributes_section and stripped.isupper() and stripped.isalpha():
            break

        if not in_attributes_section:
            continue

        # Skip empty lines in attributes section
        if not stripped:
            continue

        # Parse attribute line
        key, value, error = parse_attribute_line(stripped, i)

        if error:
            # For missing quotes, log as warning but still use the value
            if error.error_type == "MISSING_QUOTES":
                logger.warning(str(error))
            else:
                result.errors.append(error)
                continue

        if key is None:
            continue

        # Handle special attributes
        if key == "name":
            result.name = value
        elif key == "date":
            parsed_date, date_error = parse_date(value, i, stripped)
            if date_error:
                result.errors.append(date_error)
            else:
                result.date = parsed_date
        else:
            # Store in extra_attributes
            result.extra_attributes[key] = value

    if not in_attributes_section:
        logger.info(f"No METACLOUD_ATTRIBUTES section found in {file_path}")

    return result


def parse_metacloud_attributes_only(file_path: str) -> dict:
    """
    Convenience function that parses a metacloud file and returns a dict
    suitable for API calls.
    """
    attrs = parse_metacloud_file(file_path)
    return attrs.to_dict()
