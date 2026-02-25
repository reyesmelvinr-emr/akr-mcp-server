# Security

## Overview

AKR MCP server prioritizes safe-by-default behavior for documentation writes. Read-only tools are always available; write tools are gated and disabled unless explicitly enabled.

## MCP Trust Model

### Transport Security

The Model Context Protocol (MCP) supports two primary transport mechanisms:

1. **stdio (Default & Recommended)**
   - Communication via standard input/output streams
   - Inherently secure for local development environments
   - Process runs with same permissions as the invoking client
   - No network exposure or remote attack surface
   - **This is the default and recommended mode for AKR-MCP-Server**

2. **HTTP/SSE (Future Enhancement)**
   - Requires explicit authentication (API keys, OAuth, or JWT)
   - Must use TLS for transport encryption
   - Subject to network security considerations
   - Not implemented in v0.2.0; planned for future releases with proper auth

### Trust Assumptions

- **stdio mode**: The server trusts the local client (VS Code, Claude Desktop, etc.) that spawned it
- The server does **not** infer user identity from the MCP protocol itself
- Write operations require explicit dual-confirmation (env flag + per-call parameter)
- No automatic team/role-based authorization in v0.2.0

## Write Operations (v0.2.0)

Write operations are disabled by default and require two explicit signals:

1. Environment flag: `AKR_ENABLE_WRITE_OPS=true`
2. Per-call confirmation: `allowWrites=true`

If either signal is missing, the server returns a permission error and no files are written.

## MCP Inspector Guidance

**Required Version: ≥ 0.14.1**

MCP Inspector versions prior to 0.14.1 contain a critical remote code execution (RCE) vulnerability (CVE-2025-49596) that allows malicious MCP servers to execute arbitrary code on the client machine.

### Vulnerability Details

- **CVE ID**: CVE-2025-49596
- **Severity**: Critical (Remote Code Execution)
- **Affected Versions**: MCP Inspector < 0.14.1
- **Fixed In**: MCP Inspector 0.14.1 and later
- **Impact**: Untrusted MCP servers could execute arbitrary commands on the client

### Recommendations

1. **Always use MCP Inspector version 0.14.1 or later**
2. Only connect to trusted MCP servers
3. Review server source code before connecting to third-party servers
4. Use stdio transport (default) rather than HTTP when possible
5. Keep your MCP SDK and Inspector tooling up to date

### Verification

Check your MCP Inspector version:

```bash
mcp --version
# Expected: 0.14.1 or higher
```

If you have an older version, update immediately:

```bash
npm install -g @modelcontextprotocol/inspector@latest
# or
pip install --upgrade mcp[cli]
```

### References

- [MCP Security Advisory](https://modelcontextprotocol.io/)
- [CVE-2025-49596 Details](https://threatprotect.qualys.com/2025/07/03/anthropic-model-context-protocol-mcp-inspector-remote-code-execution-vulnerability-cve-2025-49596/)

## Roadmap (v0.3.0)

Future options for team-based write gating:

- Git author allow-list (`git config user.email`)
- Signed JWT passed in tool input
- VS Code workspace setting enforcement (requires extension integration)

### Future Remote Transport (Not Implemented in v0.2.0)

When remote hosting is added in future versions:

- **Prefer streamable-HTTP** over SSE (SSE being phased out in MCP examples)
- **Require TLS 1.2+** for all remote connections
- **Enforce authentication**: OAuth 2.0, API keys, or signed JWTs
- **Rate limiting** per client/token
- **Audit logging** of all tool invocations

### Write Tool Path Safety

Write operations include additional safety measures:

- **Directory allow-list**: Only write to approved paths (e.g., `docs/`, `akr_content/`)
- **Symlink rejection**: Refuse to follow symlinks to prevent escaping allowed directories
- **Path normalization**: Resolve `..` and `.` components, reject absolute paths outside workspace
- **Validation**: Check for directory traversal attempts (`../../../etc/passwd`)

These are server-side safety belts consistent with the least-privilege security posture.
