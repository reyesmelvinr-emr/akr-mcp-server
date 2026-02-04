import subprocess
from pathlib import Path

import pytest

from tools.write_operations import write_documentation


def _init_git_repo(repo_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    _init_git_repo(tmp_path)
    return tmp_path


def _enforcement_config() -> dict:
    return {
        "documentation": {
            "enforcement": {
                "enabled": True,
                "validationStrictness": "baseline",
                "requireYamlFrontmatter": True,
                "enforceSectionOrder": True,
                "autoFixEnabled": True,
                "allowRetry": True,
                "maxRetries": 3,
                "writeMode": "git"
            }
        }
    }


def test_write_documentation_enforces_before_write(git_repo: Path):
    result = write_documentation(
        repo_path=str(git_repo),
        doc_path="docs/test.md",
        content="Hello world",
        source_file="src/service.cs",
        component_type="service",
        template="minimal_service_template.md",
        overwrite=False,
        config=_enforcement_config()
    )

    assert result.get("success") is False
    assert not (git_repo / "docs" / "test.md").exists()


def test_write_documentation_with_valid_content(git_repo: Path):
    valid_markdown = """---
feature: TEST
domain: Testing
layer: API
component: TestService
status: deployed
version: 1.0
componentType: Service
priority: P2
lastUpdated: 2026-02-04
---

# Service: TestService

## Purpose
Test purpose.

## Key Methods
- GetById

## Dependencies
None.

## API Endpoints
None.

## Business Rules
None.

## Notes
None.

## Questions & Gaps
None.

## Documentation Standards
Minimal.
"""

    result = write_documentation(
        repo_path=str(git_repo),
        doc_path="docs/test.md",
        content=valid_markdown,
        source_file="src/service.cs",
        component_type="service",
        template="minimal_service_template.md",
        overwrite=True,
        config=_enforcement_config()
    )

    assert result.get("success") is True
    file_path = git_repo / "docs" / "test.md"
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")
    yaml_lines = [i for i, line in enumerate(content.splitlines()) if line.strip() == "---"]
    assert len(yaml_lines) >= 2
    yaml_end = yaml_lines[1]
    header_pos = next((i for i, line in enumerate(content.splitlines()) if line.startswith("<!--")), -1)
    assert header_pos > yaml_end
