"""Integration tests for MCP resource handlers (Phase 1)."""

import inspect
import sys
from typing import Awaitable, Callable, cast
from dataclasses import dataclass
from pathlib import Path

import pytest

from mcp.server import Server as McpServer
from mcp.types import Resource

# Allow importing server.py even if the MCP SDK lacks uri_pattern support.
if "uri_pattern" not in inspect.signature(McpServer.read_resource).parameters:
    _original_read_resource = McpServer.read_resource

    def _read_resource_shim(self, *args, **kwargs):
        return _original_read_resource(self, *args)

    McpServer.read_resource = _read_resource_shim

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import server


@dataclass
class FakeCharter:
    name: str
    description: str
    content: str

    def load_content(self) -> str:
        return self.content


class FakeResourceManager:
    def __init__(self) -> None:
        self._charters = {
            "backend": FakeCharter("backend", "Backend charter", "# Backend Charter"),
            "ui": FakeCharter("ui", "UI charter", "# UI Charter"),
        }

    def list_charters(self):
        return list(self._charters.values())

    def get_charter(self, name: str):
        return self._charters.get(name)


class FakeResolver:
    def __init__(self) -> None:
        self._templates = {
            "lean_baseline_service_template": "# Lean Template",
            "standard_service_template": "# Standard Template",
        }

    def list_templates(self):
        return sorted(self._templates.keys())

    def get_template(self, template_id: str):
        return self._templates.get(template_id)


@pytest.mark.asyncio
async def test_list_resources_includes_templates_and_charters(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_resolver = FakeResolver()
    fake_manager = FakeResourceManager()

    monkeypatch.setattr(server, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server, "get_template_resolver", lambda: fake_resolver)
    monkeypatch.setattr(server, "get_resource_manager", lambda: fake_manager)

    list_resources_handler = cast(
        Callable[[], Awaitable[list[Resource]]],
        server.list_resources,
    )
    resources = await list_resources_handler()

    template_uris = {str(res.uri) for res in resources if str(res.uri).startswith("akr://template/")}
    charter_uris = {str(res.uri) for res in resources if str(res.uri).startswith("akr://charter/")}

    assert "akr://template/lean_baseline_service_template" in template_uris
    assert "akr://template/standard_service_template" in template_uris
    assert "akr://charter/backend" in charter_uris
    assert "akr://charter/ui" in charter_uris

    assert all(res.mimeType == "text/markdown" for res in resources)


@pytest.mark.asyncio
async def test_read_template_resource_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_resolver = FakeResolver()

    monkeypatch.setattr(server, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server, "get_template_resolver", lambda: fake_resolver)

    content = await server.read_template_resource("akr://template/lean_baseline_service_template")
    assert content == "# Lean Template"


@pytest.mark.asyncio
async def test_read_template_resource_not_found_lists_available(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_resolver = FakeResolver()

    monkeypatch.setattr(server, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server, "get_template_resolver", lambda: fake_resolver)

    content = await server.read_template_resource("akr://template/unknown")
    assert "Template not found" in content
    assert "akr://template/lean_baseline_service_template" in content


@pytest.mark.asyncio
async def test_read_charter_resource_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_manager = FakeResourceManager()

    monkeypatch.setattr(server, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server, "get_resource_manager", lambda: fake_manager)

    content = await server.read_charter_resource("akr://charter/backend")
    assert content == "# Backend Charter"


@pytest.mark.asyncio
async def test_read_charter_resource_not_found_lists_available(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_manager = FakeResourceManager()

    monkeypatch.setattr(server, "ensure_initialized", lambda: None)
    monkeypatch.setattr(server, "get_resource_manager", lambda: fake_manager)

    content = await server.read_charter_resource("akr://charter/unknown")
    assert "Charter not found" in content
    assert "akr://charter/backend" in content


@pytest.mark.asyncio
async def test_list_resource_templates_returns_patterns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "ensure_initialized", lambda: None)

    templates = await server.list_resource_templates()

    uri_templates = {tmpl.uriTemplate for tmpl in templates}
    assert "akr://template/{id}" in uri_templates
    assert "akr://charter/{domain}" in uri_templates
