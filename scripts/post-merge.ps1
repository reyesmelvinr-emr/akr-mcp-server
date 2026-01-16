<#
.SYNOPSIS
    AKR Template Synchronization Hook (PowerShell version)

.DESCRIPTION
    Git post-merge hook for application repositories
    
    This hook:
    1. Detects changes to .akr-config.json
    2. Checks for updates in core-akr-templates repository
    3. Notifies VS Code of configuration changes
    
.NOTES
    Installation:
    Copy to .git/hooks/post-merge.ps1
    Configure Git to use PowerShell hooks:
    git config core.hooksPath .git/hooks
#>

# Configuration
$TemplatesDir = Join-Path $env:USERPROFILE ".akr\templates"
$ConfigFile = ".akr-config.json"

Write-Host "`n🔄 AKR Template Sync Hook" -ForegroundColor Blue

# Function to check if file changed in merge
function Test-FileChanged {
    param([string]$FilePath)
    
    $changedFiles = git diff-tree -r --name-only --no-commit-id HEAD@{1} HEAD 2>$null
    return $changedFiles -contains $FilePath
}

# Function to update template repository
function Update-Templates {
    if (-not (Test-Path $TemplatesDir)) {
        Write-Host "  ⚠  Template directory not found: $TemplatesDir" -ForegroundColor Yellow
        Write-Host "  →  Run setup script to clone core-akr-templates" -ForegroundColor Blue
        return $false
    }
    
    Write-Host "  →  Checking template repository for updates..." -ForegroundColor Blue
    
    Push-Location $TemplatesDir
    
    try {
        # Check if it's a git repository
        $gitStatus = git status 2>&1
        if ($gitStatus -match "not a git repository") {
            Write-Host "  ✗  Template directory is not a git repository" -ForegroundColor Red
            return $false
        }
        
        # Fetch updates
        git fetch origin main --quiet 2>$null
        
        # Check if updates are available
        $local = git rev-parse HEAD
        $remote = git rev-parse origin/main
        
        if ($local -eq $remote) {
            Write-Host "  ✓  Templates are up to date" -ForegroundColor Green
            return $true
        }
        
        # Pull updates
        Write-Host "  ↓  Pulling template updates..." -ForegroundColor Yellow
        git pull origin main --quiet 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓  Templates updated successfully" -ForegroundColor Green
            
            # Show what changed
            $commits = git log --oneline --no-merges "$local..HEAD" | Select-Object -First 5
            foreach ($commit in $commits) {
                Write-Host "    →  $commit" -ForegroundColor Blue
            }
            
            return $true
        } else {
            Write-Host "  ✗  Failed to update templates" -ForegroundColor Red
            return $false
        }
    }
    finally {
        Pop-Location
    }
}

# Function to notify VS Code
function New-VSCodeNotification {
    param([string]$Message)
    
    $notificationFile = ".akr-notification.json"
    $timestamp = Get-Date -Format "o"
    
    $notification = @{
        timestamp = $timestamp
        type = "template-sync"
        message = $Message
        action = "reload-mcp-config"
    } | ConvertTo-Json
    
    $notification | Out-File -FilePath $notificationFile -Encoding UTF8
    
    Write-Host "  ✓  VS Code notification created" -ForegroundColor Green
}

# Main logic

# Check if .akr-config.json changed
if (Test-FileChanged $ConfigFile) {
    Write-Host "  !  Configuration file changed: $ConfigFile" -ForegroundColor Yellow
    
    # Validate JSON syntax
    if (Test-Path $ConfigFile) {
        try {
            Get-Content $ConfigFile -Raw | ConvertFrom-Json | Out-Null
            Write-Host "  ✓  Configuration is valid JSON" -ForegroundColor Green
        }
        catch {
            Write-Host "  ✗  Configuration has JSON syntax errors" -ForegroundColor Red
            Write-Host "  →  Please fix $ConfigFile before proceeding" -ForegroundColor Yellow
        }
    }
    
    # Update templates
    Update-Templates
    
    New-VSCodeNotification "Configuration and templates updated. Please reload MCP server."
    
    Write-Host "`n  ⚠  Action Required:" -ForegroundColor Yellow
    Write-Host "     Reload the MCP server in VS Code:"
    Write-Host "     1. Open Command Palette (Ctrl+Shift+P)"
    Write-Host "     2. Run: 'Developer: Reload Window'`n"
}
else {
    # Check templates even if config didn't change
    if (Test-Path $TemplatesDir) {
        Update-Templates
    }
}

Write-Host "  ✓  Post-merge hook completed`n" -ForegroundColor Green

exit 0
