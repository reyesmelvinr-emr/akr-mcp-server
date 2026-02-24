from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional, Tuple


def validate_enforcement_config(config: dict) -> Tuple[bool, list[str]]:
    """Validate enforcement config at startup."""
    errors: list[str] = []
    documentation = config.get("documentation")
    if documentation is None:
        errors.append("Missing documentation config section")
        return False, errors

    enforcement = documentation.get("enforcement")
    if enforcement is None:
        errors.append("Missing documentation.enforcement config section")
        return False, errors

    required_keys = [
        "enabled",
        "validationStrictness",
        "requireYamlFrontmatter",
        "enforceSectionOrder",
        "autoFixEnabled",
        "writeMode"
    ]

    for key in required_keys:
        if key not in enforcement:
            errors.append(f"Missing enforcement config key: {key}")

    return len(errors) == 0, errors


def resolve_template_path(template_name: str, config: Optional[dict] = None) -> Path:
    """Resolve template name to full path in akr_content/templates/."""
    base_path: Optional[Path] = None
    if config:
        templates_path = config.get("paths", {}).get("templates")
        if templates_path:
            base_path = Path(templates_path)
            if not base_path.is_absolute():
                repo_root = Path(__file__).resolve().parent.parent.parent
                base_path = repo_root / base_path

    if base_path is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        base_path = repo_root / "akr_content" / "templates"

    return base_path / template_name


class ErrorType(str, Enum):
    ENFORCEMENT_FAILED = "ENFORCEMENT_FAILED"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    CONFIG_DISABLED = "CONFIG_DISABLED"
    WRITE_FAILED = "WRITE_FAILED"
    COMMIT_FAILED = "COMMIT_FAILED"
    WORKFLOW_VIOLATION = "WORKFLOW_VIOLATION"
    PERMISSION_DENIED = "PERMISSION_DENIED"


def error_response(error_type: ErrorType, message: str, **extras: object) -> dict:
    """Build a standard error response payload."""
    return {"success": False, "error": message, "error_type": error_type.value, **extras}
