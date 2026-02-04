#!/bin/bash
# Scan for dangerous write patterns outside write_operations.py

set -euo pipefail

echo "🔍 Scanning for doc write bypasses..."

# Find .write_text() calls outside write_operations.py
if grep -r --include="*.py" "\.write_text(" src/ tests/ | grep -v "write_operations.py"; then
  echo "❌ FAIL: Found .write_text() outside write_operations.py"
  exit 1
fi

# Find open(..., 'w') or open(..., "w") outside write_operations.py
if grep -r --include="*.py" "open([^)]*['\"]w['\"]" src/ tests/ | grep -v "write_operations.py"; then
  echo "❌ FAIL: Found open(..., 'w') outside write_operations.py"
  exit 1
fi

echo "✅ PASS: No direct write bypasses detected."
