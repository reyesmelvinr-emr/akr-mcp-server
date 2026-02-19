#!/bin/bash
# Bypass Write Scan for AKR MCP Server
# Ensures no documentation writes occur outside the enforcement-gated write_operations module
# This prevents regressions where I/O code (Path.write_text or open(...,'w')) 
# appears outside the single, enforced write path.

set -e

echo "🔍 Scanning for doc write bypasses (unauthorized I/O patterns)..."
echo ""

FOUND_BYPASSES=0
DOCS_FILTER='docs[\\/]'

# Check 1: .write_text() calls outside write_operations.py
echo "[1/2] Checking for .write_text() outside write_operations.py..."
if grep -r --include="*.py" "\.write_text(" src/ tests/ 2>/dev/null | grep -v "write_operations.py" | grep -E "$DOCS_FILTER"; then
  echo "❌ FAIL: Found .write_text() outside write_operations.py"
  FOUND_BYPASSES=1
else
  echo "✅ PASS: No .write_text() found outside write_operations.py"
fi

echo ""

# Check 2: open(..., 'w') or open(..., "w") calls outside write_operations.py  
echo "[2/2] Checking for open(..., 'w') outside write_operations.py..."
if grep -r --include="*.py" "open([^)]*['\"]w['\"]" src/ tests/ 2>/dev/null | grep -v "write_operations.py" | grep -E "$DOCS_FILTER"; then
  echo "❌ FAIL: Found open(..., 'w') outside write_operations.py"
  FOUND_BYPASSES=1
else
  echo "✅ PASS: No open(..., 'w') found outside write_operations.py"
fi

echo ""
echo "================================================"

if [ $FOUND_BYPASSES -eq 0 ]; then
  echo "✅ PASS: No direct write bypasses detected."
  echo "All documentation writes are enforced via the hard gate in write_operations.py"
  exit 0
else
  echo "❌ FAIL: Write bypasses detected. All I/O must go through write_operations.py"
  exit 1
fi
