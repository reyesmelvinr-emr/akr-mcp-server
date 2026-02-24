# Security

## Overview

AKR MCP server prioritizes safe-by-default behavior for documentation writes. Read-only tools are always available; write tools are gated and disabled unless explicitly enabled.

## Trust Model

- MCP over stdio is considered local and trusted.
- MCP over HTTP requires explicit authentication and transport security.
- The server does not currently infer user identity from the MCP protocol.

## Write Operations (v0.2.0)

Write operations are disabled by default and require two explicit signals:

1. Environment flag: `AKR_ENABLE_WRITE_OPS=true`
2. Per-call confirmation: `allowWrites=true`

If either signal is missing, the server returns a permission error and no files are written.

## MCP Inspector Guidance

Use MCP Inspector version 0.14.1 or later to avoid known security issues in earlier versions.

## Roadmap (v0.3.0)

Future options for team-based write gating:

- Git author allow-list (`git config user.email`)
- Signed JWT passed in tool input
- VS Code workspace setting enforcement (requires extension integration)
