<#
.SYNOPSIS
    Automated verification script for AKR-MCP-Server v0.2.0 implementation.

.DESCRIPTION
    Validates all acceptance criteria from the v0.2.0 implementation plan.
    Generates a detailed report of what passes/fails.

.PARAMETER SkipTests
    Skip running pytest (useful for quick checks).

.PARAMETER DetailedOutput
    Show detailed output for each check.

.EXAMPLE
    .\scripts\verify_v0.2.0.ps1
    .\scripts\verify_v0.2.0.ps1 -SkipTests
    .\scripts\verify_v0.2.0.ps1 -DetailedOutput
#>

param(
    [switch]$SkipTests,
    [switch]$DetailedOutput
)

# Color definitions
$ColorPass = "Green"
$ColorFail = "Red"
$ColorWarn = "Yellow"
$ColorInfo = "Cyan"
$ColorHeader = "Magenta"

# Results tracking
$script:TotalChecks = 0
$script:PassedChecks = 0
$script:FailedChecks = 0
$script:Warnings = 0
$script:FailedItems = @()

function Write-Header {
    param([string]$Text)
    Write-Host "`n============================================" -ForegroundColor $ColorHeader
    Write-Host " $Text" -ForegroundColor $ColorHeader
    Write-Host "============================================" -ForegroundColor $ColorHeader
}

function Write-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details = "",
        [bool]$IsWarning = $false
    )
    
    $script:TotalChecks++
    
    if ($Passed) {
        $script:PassedChecks++
        Write-Host "✓ " -NoNewline -ForegroundColor $ColorPass
        Write-Host $Name -ForegroundColor $ColorPass
        if ($DetailedOutput -and $Details) {
            Write-Host "  $Details" -ForegroundColor DarkGray
        }
    }
    elseif ($IsWarning) {
        $script:Warnings++
        Write-Host "⚠ " -NoNewline -ForegroundColor $ColorWarn
        Write-Host $Name -ForegroundColor $ColorWarn
        if ($Details) {
            Write-Host "  $Details" -ForegroundColor DarkGray
        }
    }
    else {
        $script:FailedChecks++
        $script:FailedItems += $Name
        Write-Host "✗ " -NoNewline -ForegroundColor $ColorFail
        Write-Host $Name -ForegroundColor $ColorFail
        if ($Details) {
            Write-Host "  $Details" -ForegroundColor DarkGray
        }
    }
}

function Test-FileExists {
    param([string]$Path, [string]$Description)
    $exists = Test-Path $Path
    Write-Check -Name $Description -Passed $exists -Details "Path: $Path"
    return $exists
}

function Test-StringInFile {
    param(
        [string]$Path,
        [string]$Pattern,
        [string]$Description,
        [switch]$IsRegex
    )
    
    if (-not (Test-Path $Path)) {
        Write-Check -Name $Description -Passed $false -Details "File not found: $Path"
        return $false
    }
    
    $content = Get-Content $Path -Raw -ErrorAction SilentlyContinue
    if ($IsRegex) {
        $found = $content -match $Pattern
    }
    else {
        $found = $content -like "*$Pattern*"
    }
    
    Write-Check -Name $Description -Passed $found -Details "Pattern: $Pattern"
    return $found
}

# Change to repository root
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor $ColorInfo
Write-Host "     AKR-MCP-Server v0.2.0 Verification Script             " -ForegroundColor $ColorInfo
Write-Host "     Automated Acceptance Criteria Validation              " -ForegroundColor $ColorInfo
Write-Host "============================================================" -ForegroundColor $ColorInfo
Write-Host "Repository: $repoRoot" -ForegroundColor DarkGray
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray

# ============================================
# Phase 1: Template Externalization and MCP Resources
# ============================================
Write-Header "Phase 1: Template Externalization and MCP Resources"

# Check submodule exists
$submoduleStatus = git submodule status 2>&1
$submoduleConfigured = $submoduleStatus -match "templates/core"
Write-Check -Name "Git submodule configured for templates/core" -Passed $submoduleConfigured -Details $submoduleStatus

# Check submodule has commits
if ($submoduleConfigured) {
    $submoduleCommit = ($submoduleStatus -split '\s+')[0]
    $hasCommit = $submoduleCommit -match '^[a-f0-9]{7,40}$'
    Write-Check -Name "Submodule pinned to specific commit" -Passed $hasCommit -Details "Commit: $submoduleCommit"
}

# Check if submodule directory exists
Test-FileExists -Path "templates/core" -Description "Submodule directory templates/core exists"

# Check TemplateResolver exists
Test-FileExists -Path "src/resources/template_resolver.py" -Description "TemplateResolver implementation exists"

# Check TemplateSchemaBuilder exists
Test-FileExists -Path "src/tools/template_schema_builder.py" -Description "TemplateSchemaBuilder implementation exists"

# Check MCP resource handlers in server.py
Test-StringInFile -Path "src/server.py" -Pattern "list_resources" -Description "MCP list_resources handler implemented"
Test-StringInFile -Path "src/server.py" -Pattern "read_resource" -Description "MCP read_resource handler implemented"
Test-StringInFile -Path "src/server.py" -Pattern "list_resource_templates" -Description "MCP resource templates handler implemented"

# Check VERSION_MANAGEMENT.md
Test-FileExists -Path "docs/VERSION_MANAGEMENT.md" -Description "VERSION_MANAGEMENT.md documentation exists"

# ============================================
# Phase 2: Write Operations Gating
# ============================================
Write-Header "Phase 2: Write Operations Gating"

# Check environment variable usage
Test-StringInFile -Path "src/server.py" -Pattern "AKR_ENABLE_WRITE_OPS" -Description "AKR_ENABLE_WRITE_OPS environment flag implemented"

# Check write operations gating logic
Test-StringInFile -Path "src/tools/write_operations.py" -Pattern "allowWrites" -Description "allowWrites parameter in write operations"

# Check SECURITY.md
$securityExists = Test-FileExists -Path "docs/SECURITY.md" -Description "SECURITY.md documentation exists"
if ($securityExists) {
    Test-StringInFile -Path "docs/SECURITY.md" -Pattern "MCP trust" -Description "SECURITY.md documents MCP trust model"
    Test-StringInFile -Path "docs/SECURITY.md" -Pattern "write.* default" -IsRegex -Description "SECURITY.md documents write ops default behavior"
}

# Check README mentions write ops
Test-StringInFile -Path "README.md" -Pattern "write.*operation" -IsRegex -Description "README.md documents write operations"

# ============================================
# Phase 3: Dual-Faceted Validation
# ============================================
Write-Header "Phase 3: Dual-Faceted Validation"

# Check ValidationEngine implementation
$validationLibExists = Test-FileExists -Path "src/tools/validation_library.py" -Description "ValidationEngine implementation exists"
if ($validationLibExists) {
    Test-StringInFile -Path "src/tools/validation_library.py" -Pattern "class ValidationEngine" -Description "ValidationEngine class defined"
    Test-StringInFile -Path "src/tools/validation_library.py" -Pattern "TemplateSchemaBuilder" -Description "ValidationEngine uses TemplateSchemaBuilder"
}

# Check CLI tool
Test-FileExists -Path "scripts/akr_validate.py" -Description "CLI validation tool (akr_validate.py) exists"

# Check jsonschema dependency
Test-StringInFile -Path "requirements.txt" -Pattern "jsonschema" -Description "jsonschema dependency in requirements.txt"

# Check VALIDATION_GUIDE.md
$validationGuideExists = Test-FileExists -Path "docs/VALIDATION_GUIDE.md" -Description "VALIDATION_GUIDE.md documentation exists"
if ($validationGuideExists) {
    Test-StringInFile -Path "docs/VALIDATION_GUIDE.md" -Pattern "TIER_1" -Description "VALIDATION_GUIDE.md documents tier levels"
}

# ============================================
# Phase 4: Extractor Deprecation and Cleanup
# ============================================
Write-Header "Phase 4: Extractor Deprecation and Cleanup"

# Check CodeAnalyzer
Test-FileExists -Path "src/tools/code_analytics.py" -Description "CodeAnalyzer implementation exists"

# Check extract_code_context tool registration
Test-StringInFile -Path "src/server.py" -Pattern "extract_code_context" -Description "extract_code_context tool registered"

# Check deprecated extractors have warning headers
$deprecatedExtractors = @(
    "src/tools/extractors/typescript_extractor.py",
    "src/tools/extractors/business_rule_extractor.py",
    "src/tools/extractors/failure_mode_extractor.py",
    "src/tools/extractors/method_flow_analyzer.py",
    "src/tools/extractors/example_extractor.py"
)

foreach ($extractor in $deprecatedExtractors) {
    if (Test-Path $extractor) {
        $extractorName = Split-Path $extractor -Leaf
        Test-StringInFile -Path $extractor -Pattern "DEPRECATED" -Description "Deprecation header in $extractorName"
    }
}

# Check CHANGELOG.md
$changelogExists = Test-FileExists -Path "docs/CHANGELOG.md" -Description "CHANGELOG.md exists"
if ($changelogExists) {
    Test-StringInFile -Path "docs/CHANGELOG.md" -Pattern "v0.2.0" -Description "CHANGELOG.md has v0.2.0 section"
}

# ============================================
# Phase 5: Testing and Documentation
# ============================================
Write-Header "Phase 5: Testing and Documentation"

# Check test files exist
$testFiles = @(
    "tests/test_template_resolver.py",
    "tests/test_mcp_resources.py",
    "tests/test_validation_library.py",
    "tests/test_integration_e2e.py"
)

foreach ($testFile in $testFiles) {
    $testName = Split-Path $testFile -Leaf
    Test-FileExists -Path $testFile -Description "Test file $testName exists"
}

# Check documentation files
$requiredDocs = @(
    "docs/ARCHITECTURE.md",
    "docs/COPILOT_CHAT_WORKFLOW.md",
    "docs/VALIDATION_GUIDE.md",
    "docs/VERSION_MANAGEMENT.md",
    "docs/SECURITY.md",
    "docs/INSTALLATION_AND_SETUP.md"
)

foreach ($doc in $requiredDocs) {
    $docName = Split-Path $doc -Leaf
    Test-FileExists -Path $doc -Description "Documentation file $docName exists"
}

# ============================================
# General Checks
# ============================================
Write-Header "General Quality Checks"

# Check for Windows-specific paths in documentation
Write-Host "Checking for Windows-specific paths in documentation..." -ForegroundColor $ColorInfo
$windowsPaths = Get-ChildItem docs/*.md -Recurse -ErrorAction SilentlyContinue | 
Select-String "C:\\\\" -SimpleMatch -ErrorAction SilentlyContinue

if ($windowsPaths) {
    $pathCount = ($windowsPaths | Measure-Object).Count
    Write-Check -Name "No Windows-specific paths in documentation" -Passed $false -Details "Found $pathCount occurrences" -IsWarning $true
    if ($DetailedOutput) {
        $windowsPaths | Select-Object -First 5 | ForEach-Object {
            Write-Host "    $($_.Filename):$($_.LineNumber) - $($_.Line.Trim())" -ForegroundColor DarkGray
        }
    }
}
else {
    Write-Check -Name "No Windows-specific paths in documentation" -Passed $true
}

# Check for consistent MCP resource URIs
$uriPatterns = @("akr://template/", "akr://charter/")
$uriConsistent = $true
foreach ($pattern in $uriPatterns) {
    $found = Select-String -Path "src/server.py" -Pattern $pattern -SimpleMatch -ErrorAction SilentlyContinue
    if (-not $found) {
        $uriConsistent = $false
    }
}
Write-Check -Name "MCP resource URIs are consistent (akr:// scheme)" -Passed $uriConsistent

# Check .gitmodules file
Test-FileExists -Path ".gitmodules" -Description ".gitmodules file exists for submodule configuration"

# ============================================
# Run Tests (Optional)
# ============================================
if (-not $SkipTests) {
    Write-Header "Running Test Suite"
    
    Write-Host "Running pytest with coverage..." -ForegroundColor $ColorInfo
    
    try {
        $testOutput = pytest --cov=src --cov-report=term-missing --tb=short -q 2>&1
        $testsPassed = $LASTEXITCODE -eq 0
        
        # Extract coverage percentage
        $coverageLine = $testOutput | Select-String "TOTAL.*\d+%" | Select-Object -Last 1
        if ($coverageLine) {
            $coverageMatch = $coverageLine -match "(\d+)%"
            if ($coverageMatch) {
                $coverage = [int]$Matches[1]
                $coverageMet = $coverage -ge 80
                Write-Check -Name "Test coverage ≥80% (Current: $coverage%)" -Passed $coverageMet
            }
        }
        
        # Extract test count
        $testSummary = $testOutput | Select-String "passed|failed" | Select-Object -Last 1
        if ($testSummary) {
            Write-Host "  Test Summary: $testSummary" -ForegroundColor DarkGray
        }
        
        Write-Check -Name "All tests pass" -Passed $testsPassed
        
        if ($DetailedOutput -and -not $testsPassed) {
            Write-Host "`nTest Output (last 20 lines):" -ForegroundColor $ColorWarn
            $testOutput | Select-Object -Last 20 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
        }
    }
    catch {
        Write-Check -Name "Run pytest successfully" -Passed $false -Details $_.Exception.Message
    }
}
else {
    Write-Host "Skipping test execution (use without -SkipTests to run)" -ForegroundColor $ColorWarn
}

# ============================================
# Additional Validation
# ============================================
Write-Header "Additional Validation"

# Check if coverage.json exists and has data
if (Test-Path "coverage.json") {
    $coverageContent = Get-Content "coverage.json" -Raw
    $hasData = $coverageContent.Length -gt 10
    Write-Check -Name "coverage.json has data" -Passed $hasData -IsWarning (-not $hasData)
}

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    $hasPython = $LASTEXITCODE -eq 0
    Write-Check -Name "Python is available" -Passed $hasPython -Details $pythonVersion
}
catch {
    Write-Check -Name "Python is available" -Passed $false
}

# Check if pytest is installed
try {
    $pytestVersion = pytest --version 2>&1
    $hasPytest = $LASTEXITCODE -eq 0
    Write-Check -Name "pytest is installed" -Passed $hasPytest -Details $pytestVersion
}
catch {
    Write-Check -Name "pytest is installed" -Passed $false
}

# Check Git status
$gitStatus = git status --short 2>&1
$isClean = [string]::IsNullOrWhiteSpace($gitStatus)
Write-Check -Name "Git working tree is clean" -Passed $isClean -Details $(if ($isClean) { "No uncommitted changes" } else { "Uncommitted changes found" }) -IsWarning (-not $isClean)

# ============================================
# Generate Summary Report
# ============================================
Write-Header "Verification Summary"

$passRate = if ($script:TotalChecks -gt 0) { 
    [math]::Round(($script:PassedChecks / $script:TotalChecks) * 100, 2) 
}
else { 
    0 
}

Write-Host ""
Write-Host "Total Checks:  " -NoNewline
Write-Host $script:TotalChecks -ForegroundColor $ColorInfo

Write-Host "Passed:        " -NoNewline
Write-Host $script:PassedChecks -ForegroundColor $ColorPass

Write-Host "Failed:        " -NoNewline
Write-Host $script:FailedChecks -ForegroundColor $(if ($script:FailedChecks -eq 0) { $ColorPass } else { $ColorFail })

Write-Host "Warnings:      " -NoNewline
Write-Host $script:Warnings -ForegroundColor $(if ($script:Warnings -eq 0) { $ColorPass } else { $ColorWarn })

Write-Host "Pass Rate:     " -NoNewline
Write-Host "$passRate%" -ForegroundColor $(if ($passRate -ge 90) { $ColorPass } elseif ($passRate -ge 75) { $ColorWarn } else { $ColorFail })

if ($script:FailedChecks -gt 0) {
    Write-Host "`nFailed Checks:" -ForegroundColor $ColorFail
    $script:FailedItems | ForEach-Object { Write-Host "  • $_" -ForegroundColor $ColorFail }
}

Write-Host ""
if ($script:FailedChecks -eq 0) {
    Write-Host "============================================================" -ForegroundColor $ColorPass
    Write-Host "  ALL CHECKS PASSED - v0.2.0 READY FOR RELEASE!           " -ForegroundColor $ColorPass
    Write-Host "============================================================" -ForegroundColor $ColorPass
    
    Write-Host "`nNext Steps:" -ForegroundColor $ColorInfo
    Write-Host "  1. Review VERIFICATION_CHECKLIST.md" -ForegroundColor DarkGray
    Write-Host "  2. Update IMPLEMENTATION_PLAN_V0.2.0.md checkboxes" -ForegroundColor DarkGray
    Write-Host "  3. Create GitHub release tag:" -ForegroundColor DarkGray
    Write-Host "     git tag v0.2.0 -a -m 'Release v0.2.0'" -ForegroundColor Yellow
    Write-Host "     git push origin v0.2.0" -ForegroundColor Yellow
    
    exit 0
}
elseif ($passRate -ge 75) {
    Write-Host "============================================================" -ForegroundColor $ColorWarn
    Write-Host "  MOSTLY READY - Address failed checks before release      " -ForegroundColor $ColorWarn
    Write-Host "============================================================" -ForegroundColor $ColorWarn
    exit 1
}
else {
    Write-Host "============================================================" -ForegroundColor $ColorFail
    Write-Host "  SIGNIFICANT ISSUES - Review implementation plan          " -ForegroundColor $ColorFail
    Write-Host "============================================================" -ForegroundColor $ColorFail
    exit 2
}
