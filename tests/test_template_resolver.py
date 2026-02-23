"""Integration tests for TemplateResolver (Phase 1)."""

import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resources.template_resolver import TemplateResolver


def _create_repo_structure(base_path: Path) -> None:
    (base_path / "templates" / "core").mkdir(parents=True, exist_ok=True)
    (base_path / "akr_content" / "templates").mkdir(parents=True, exist_ok=True)


def test_list_templates_reads_submodule(tmp_path: Path) -> None:
    _create_repo_structure(tmp_path)
    core_path = tmp_path / "templates" / "core"

    (core_path / "alpha.md").write_text("## Alpha", encoding="utf-8")
    (core_path / ".hidden.md").write_text("hidden", encoding="utf-8")

    resolver = TemplateResolver(tmp_path, config={})
    assert resolver.list_templates() == ["alpha"]


def test_get_template_prefers_local_override(tmp_path: Path) -> None:
    _create_repo_structure(tmp_path)
    local_path = tmp_path / "akr_content" / "templates"
    core_path = tmp_path / "templates" / "core"

    (local_path / "sample.md").write_text("local content", encoding="utf-8")
    (core_path / "sample.md").write_text("submodule content", encoding="utf-8")

    resolver = TemplateResolver(tmp_path, config={})
    assert resolver.get_template("sample") == "local content"


def test_get_template_falls_back_to_submodule(tmp_path: Path) -> None:
    _create_repo_structure(tmp_path)
    core_path = tmp_path / "templates" / "core"

    (core_path / "fallback.md").write_text("submodule content", encoding="utf-8")

    resolver = TemplateResolver(tmp_path, config={})
    assert resolver.get_template("fallback") == "submodule content"


def test_remote_fetch_uses_cache_and_refreshes_on_expiry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _create_repo_structure(tmp_path)

    calls = {"count": 0}

    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, timeout: int):
        calls["count"] += 1
        return DummyResponse("remote content")

    fake_requests = SimpleNamespace(
        get=fake_get,
        exceptions=SimpleNamespace(RequestException=Exception),
    )

    import resources.template_resolver as template_resolver_module

    monkeypatch.setattr(template_resolver_module, "requests", fake_requests)

    config = {
        "http_fetch_enabled": True,
        "http_fetch_config": {
            "repo_url": "https://github.com/example/core-akr-templates",
            "cache_ttl_seconds": 60,
            "verify_checksums": False,
            "timeout_seconds": 1,
            "max_retries": 0,
            "pinned_version": "v1.0.0",
        },
    }

    resolver = TemplateResolver(tmp_path, config=config)

    first = resolver.get_template("remote_only")
    second = resolver.get_template("remote_only")

    assert first == "remote content"
    assert second == "remote content"
    assert calls["count"] == 1

    cache_key = "remote_only@v1.0.0"
    entry = resolver._cache[cache_key]
    entry.fetch_timestamp = time.time() - entry.ttl_seconds - 1

    third = resolver.get_template("remote_only")
    assert third == "remote content"
    assert calls["count"] == 2
