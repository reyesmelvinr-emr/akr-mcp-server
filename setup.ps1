<#
.SYNOPSIS
    Automated setup script for AKR MCP Documentation Server

.DESCRIPTION
    This script automates the setup of the AKR MCP server:
    - Verifies Python 3.10+ installation
    - Creates Python virtual environment
    - Installs required dependencies
    - Clones core-akr-templates repository
    - Configures VS Code settings
    - Verifies installation

.PARAMETER SkipVSCode
    Skip VS Code configuration steps

.PARAMETER TemplatesRepo
    URL of the core-akr-templates repository
    Default: https://github.com/reyesmelvinr-emr/core-akr-templates

.EXAMPLE
    .\setup.ps1
    
.EXAMPLE
    .\setup.ps1 -SkipVSCode
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipVSCode,
    
    [Parameter(Mandatory=$false)]
    [string]$TemplatesRepo = "https://github.com/reyesmelvinr-emr/core-akr-templates",
    
    [Parameter(Mandatory=$false)]
    [switch]$ConfigureRepo
)

# Color output functions
function Write-Step {
    param([string]$Message)
    Write-Host "`n✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  → $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "`n🎉 $Message" -ForegroundColor Green
}

# Application repository configuration mode
if ($ConfigureRepo) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  AKR MCP - Application Repository Setup" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    $RepoPath = Get-Location
    Write-Info "Configuring application repository: $RepoPath"
    
    # Check for .akr-config.json
    $configPath = Join-Path $RepoPath ".akr-config.json"
    if (-not (Test-Path $configPath)) {
        Write-Error "No .akr-config.json found in $RepoPath"
        Write-Info "Please create a configuration file using examples from core-akr-templates"
        Write-Info "Example: https://github.com/reyesmelvinr-emr/core-akr-templates/tree/main/.akr/examples"
        exit 1
    }
    
    Write-Step "Configuration file found: .akr-config.json"
    
    # Detect repository type
    $config = Get-Content $configPath | ConvertFrom-Json
    $repoType = $config.repository.type
    if (-not $repoType) {
        # Auto-detect
        if (Test-Path (Join-Path $RepoPath "packages")) {
            $repoType = "monorepo"
            Write-Info "Auto-detected: Monorepo (packages/ directory found)"
        } elseif (Test-Path (Join-Path $RepoPath "apps")) {
            $repoType = "monorepo"
            Write-Info "Auto-detected: Monorepo (apps/ directory found)"
        } else {
            $repoType = "standard"
            Write-Info "Auto-detected: Standard repository"
        }
    } else {
        Write-Info "Repository type: $repoType"
    }
    
    # Detect platform
    $remoteUrl = git config --get remote.origin.url 2>$null
    $platform = "unknown"
    if ($remoteUrl -match "dev\.azure\.com|visualstudio\.com") {
        $platform = "Azure DevOps"
    } elseif ($remoteUrl -match "github\.com") {
        $platform = "GitHub"
    }
    Write-Info "Platform: $platform"
    
    # Create .vscode directory if needed
    $vscodeDir = Join-Path $RepoPath ".vscode"
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir | Out-Null
        Write-Step "Created .vscode directory"
    }
    
    # Check if AKR_MCP_SERVER_PATH is set
    if (-not $env:AKR_MCP_SERVER_PATH) {
        Write-Warning "AKR_MCP_SERVER_PATH environment variable not set"
        Write-Info "Please run the main setup first: .\setup.ps1"
        exit 1
    }
    
    # Copy MCP configuration template
    $templatePath = Join-Path $env:AKR_MCP_SERVER_PATH "templates\mcp.json.template"
    $mcpConfigPath = Join-Path $vscodeDir "mcp.json"
    
    if (Test-Path $templatePath) {
        Copy-Item $templatePath $mcpConfigPath -Force
        Write-Step "VS Code MCP configuration installed"
        Write-Info "Location: $mcpConfigPath"
    } else {
        # Create inline if template doesn't exist
        $mcpConfig = @{
            mcpServers = @{
                "akr-documentation-server" = @{
                    command = "python"
                    args = @("$env:AKR_MCP_SERVER_PATH/src/server.py")
                    env = @{
                        PYTHONPATH = "$env:AKR_MCP_SERVER_PATH/src"
                        VSCODE_WORKSPACE_FOLDER = "`${workspaceFolder}"
                        AKR_TEMPLATES_DIR = "$HOME/.akr/templates"
                    }
                }
            }
        }
        $mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath
        Write-Step "VS Code MCP configuration created"
    }
    
    # Display summary
    Write-Success "Application repository configured successfully!"
    Write-Host "`nConfiguration Summary:" -ForegroundColor Cyan
    Write-Host "  Repository: $($config.repository.name)" -ForegroundColor White
    Write-Host "  Type: $repoType" -ForegroundColor White
    Write-Host "  Platform: $platform" -ForegroundColor White
    Write-Host "  VS Code Config: $mcpConfigPath" -ForegroundColor White
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "  1. Open this repository in VS Code" -ForegroundColor White
    Write-Host "  2. Reload VS Code window (Ctrl+Shift+P → 'Reload Window')" -ForegroundColor White
    Write-Host "  3. Test MCP connection: @workspace /docs.health-check" -ForegroundColor White
    
    exit 0
}

# Script start
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AKR MCP Server Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Step 1: Verify Python installation
Write-Step "Step 1: Verifying Python installation"

try {
    $pythonVersion = python --version 2>&1
    Write-Info "Found: $pythonVersion"
    
    # Extract version number
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Error "Python 3.10+ required. Found: $pythonVersion"
            Write-Info "Please install Python 3.10 or higher from https://www.python.org"
            exit 1
        }
    }
} catch {
    Write-Error "Python not found in PATH"
    Write-Info "Please install Python 3.10+ from https://www.python.org"
    exit 1
}

# Step 2: Create virtual environment
Write-Step "Step 2: Creating virtual environment"

if (Test-Path "venv") {
    Write-Warning "Virtual environment already exists. Skipping creation."
    Write-Info "To recreate, delete the 'venv' folder and run setup again."
} else {
    Write-Info "Creating venv..."
    python -m venv venv
    
    if (-not (Test-Path "venv")) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    Write-Info "Virtual environment created successfully"
}

# Step 3: Activate virtual environment and install dependencies
Write-Step "Step 3: Installing dependencies"

Write-Info "Activating virtual environment..."
$venvActivate = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"

# Check execution policy
$executionPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($executionPolicy -eq "Restricted") {
    Write-Warning "Execution policy is Restricted"
    Write-Info "Setting execution policy to RemoteSigned for current user..."
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

# Activate and install
& $venvActivate

Write-Info "Installing Python packages..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    exit 1
}

Write-Info "Dependencies installed successfully"

# Step 4: Clone core-akr-templates repository
Write-Step "Step 4: Setting up template repository"

$templatesDir = Join-Path $env:USERPROFILE ".akr\templates"

if (Test-Path $templatesDir) {
    Write-Warning "Template directory already exists: $templatesDir"
    Write-Info "Checking for updates..."
    
    Push-Location $templatesDir
    try {
        $gitStatus = git status 2>&1
        if ($gitStatus -match "Not a git repository") {
            Write-Warning "Directory exists but is not a git repository"
            Write-Info "Please manually remove $templatesDir and run setup again"
        } else {
            git pull origin main --quiet
            Write-Info "Templates updated successfully"
        }
    } catch {
        Write-Warning "Could not update templates: $_"
    }
    Pop-Location
} else {
    Write-Info "Cloning core-akr-templates..."
    New-Item -ItemType Directory -Path (Split-Path $templatesDir) -Force | Out-Null
    
    git clone $TemplatesRepo $templatesDir --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone template repository"
        Write-Info "Repository: $TemplatesRepo"
        exit 1
    }
    
    Write-Info "Templates cloned to: $templatesDir"
}

# Step 5: Configure VS Code
if (-not $SkipVSCode) {
    Write-Step "Step 5: Configuring VS Code"
    
    $vscodeDir = Join-Path $ScriptDir ".vscode"
    
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir | Out-Null
    }
    
    # Check if GitHub Copilot is installed
    $copilotInstalled = code --list-extensions 2>&1 | Select-String "github.copilot"
    
    if (-not $copilotInstalled) {
        Write-Warning "GitHub Copilot extension not detected"
        Write-Info "Please install GitHub Copilot from VS Code marketplace"
        Write-Info "Extensions → Search 'GitHub Copilot'"
    } else {
        Write-Info "GitHub Copilot extension found"
    }
    
    # Verify MCP configuration exists
    $mcpConfigPath = Join-Path $vscodeDir "mcp.json"
    if (Test-Path $mcpConfigPath) {
        Write-Info "MCP configuration found: .vscode/mcp.json"
    } else {
        Write-Warning "MCP configuration not found"
        Write-Info "Expected: .vscode/mcp.json"
    }
} else {
    Write-Info "Skipping VS Code configuration (--SkipVSCode specified)"
}

# Step 6: Create logs directory
Write-Step "Step 6: Setting up logging"

$logsDir = Join-Path $ScriptDir "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Info "Created logs directory"
} else {
    Write-Info "Logs directory already exists"
}

# Step 7: Verify installation
Write-Step "Step 7: Verifying installation"

Write-Info "Checking MCP SDK installation..."
$mcpVersion = pip show mcp 2>&1

if ($mcpVersion -match "Version: (.+)") {
    Write-Info "MCP SDK version: $($matches[1])"
} else {
    Write-Error "MCP SDK not installed correctly"
    exit 1
}

Write-Info "Verifying server.py..."
if (Test-Path "src\server.py") {
    Write-Info "Server file found"
} else {
    Write-Error "Server file not found: src\server.py"
    exit 1
}

# Final success message
Write-Success "Setup completed successfully!"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "1. Activate the virtual environment:" -ForegroundColor Yellow
Write-Host "   .\venv\Scripts\Activate.ps1`n"

Write-Host "2. For application repositories, create .akr-config.json:" -ForegroundColor Yellow
Write-Host "   See examples in: $templatesDir\.akr\examples\`n"

Write-Host "3. Open VS Code and enable MCP server:" -ForegroundColor Yellow
Write-Host "   GitHub Copilot Chat → Settings → MCP Servers`n"

Write-Host "4. Test with GitHub Copilot Chat:" -ForegroundColor Yellow
Write-Host "   Try: @workspace /docs.list-templates`n"

Write-Host "========================================`n" -ForegroundColor Cyan

# Optional: Install git hooks
Write-Host "Would you like to install git hooks for template synchronization? (Y/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Info "Installing git hooks..."
    
    $hooksDir = Join-Path $ScriptDir ".git\hooks"
    if (Test-Path $hooksDir) {
        # Copy post-merge hook (will be created in next task)
        $hookSource = Join-Path $ScriptDir "scripts\post-merge"
        $hookDest = Join-Path $hooksDir "post-merge"
        
        if (Test-Path $hookSource) {
            Copy-Item $hookSource $hookDest -Force
            Write-Info "Git hooks installed"
        } else {
            Write-Warning "Hook script not found: scripts\post-merge"
            Write-Info "Will be available after completing all setup tasks"
        }
    } else {
        Write-Warning "Not a git repository. Skipping hook installation."
    }
}

Write-Host "`nSetup complete! 🚀`n" -ForegroundColor Green
