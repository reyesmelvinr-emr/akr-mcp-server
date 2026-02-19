<#
scripts/validate_write_bypasses.ps1

Purpose:
  Detect unauthorized direct writes outside write_operations.py
  - .write_text( ... )
  - open( ..., 'w' ) or open( ..., "w" )

Exit codes:
  0 = PASS (no bypasses)
  1 = FAIL (bypass found)
#>

$ErrorActionPreference = "Stop"

# Paths to scan (match plan's intent: src/ + tests/) 
$roots = @("src", "tests")

# Files we allow to contain these patterns (canonical write gateway)
# NOTE: Adjust if your canonical file lives elsewhere or is named differently. 
$allowedFileRegex = "write_operations\.py$"

# Optional: explicit exclusions (e.g., if you truly want cross_repository.py excluded)
# Only use this if you're intentionally allowing a non-doc pipeline to write. 
$excludedFiles = @(
    # "cross_repository.py"
)

function Get-PyFiles($roots) {
    $files = @()
    foreach ($r in $roots) {
        if (Test-Path $r) {
            $files += Get-ChildItem -Path $r -Recurse -File -Filter *.py
        }
    }
    return $files
}

function ShouldSkipFile($fileFullName) {
    foreach ($ex in $excludedFiles) {
        if ($fileFullName -like "*$ex") { return $true }
    }
    return $false
}

# Regex patterns equivalent to the Bash scan (and slightly stricter)
$patternWriteText = "\.write_text\s*\("
$patternOpenWrite = "open\s*\([^)]*['""]w['""]"
$patternDocsPath = "docs[\\/]"

$pyFiles = Get-PyFiles $roots

$violations = @()

foreach ($f in $pyFiles) {
    if (ShouldSkipFile $f.FullName) { continue }

    # Skip allowed file (write_operations.py)
    if ($f.FullName -match $allowedFileRegex) { continue }

    # Search for .write_text(
    $m1 = Select-String -Path $f.FullName -Pattern $patternWriteText -AllMatches -ErrorAction SilentlyContinue
    if ($m1) {
        foreach ($hit in $m1) {
            if ($hit.Line -match $patternDocsPath) {
                $violations += [PSCustomObject]@{
                    File    = $hit.Path
                    Line    = $hit.LineNumber
                    Pattern = ".write_text("
                    Text    = $hit.Line.Trim()
                }
            }
        }
    }

    # Search for open(..., 'w') or open(..., "w")
    $m2 = Select-String -Path $f.FullName -Pattern $patternOpenWrite -AllMatches -ErrorAction SilentlyContinue
    if ($m2) {
        foreach ($hit in $m2) {
            if ($hit.Line -match $patternDocsPath) {
                $violations += [PSCustomObject]@{
                    File    = $hit.Path
                    Line    = $hit.LineNumber
                    Pattern = "open(...,'w')"
                    Text    = $hit.Line.Trim()
                }
            }
        }
    }
}

if ($violations.Count -gt 0) {
    Write-Host "❌ FAIL: Found direct write bypass patterns outside write_operations.py" -ForegroundColor Red
    foreach ($v in $violations) {
        Write-Host (" - {0}:{1} [{2}] {3}" -f $v.File, $v.Line, $v.Pattern, $v.Text) -ForegroundColor Yellow
    }
    exit 1
}

Write-Host "✅ PASS: No direct write bypasses detected." -ForegroundColor Green
exit 0
