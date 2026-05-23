<#
.SYNOPSIS
    absorb-osp — Installer for Windows (PowerShell)

.DESCRIPTION
    Installs the absorb-osp workflow for Claude Code and optionally Hermes Agent.
    Creates backups of existing files before overwriting.

.PARAMETER Prefix
    Installation directory (default: ~\.claude)

.PARAMETER Hermes
    Also install Hermes Agent configuration

.EXAMPLE
    .\install.ps1
    .\install.ps1 -Prefix "$env:USERPROFILE\.claude"
    .\install.ps1 -Hermes
#>

param(
    [string]$Prefix = "$env:USERPROFILE\.claude",
    [switch]$Hermes
)

$REPO_URL = "https://github.com/justmicos/micos"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"

function Write-Info  { Write-Host "[INFO]" -ForegroundColor Blue -NoNewline; Write-Host " $args" }
function Write-Ok    { Write-Host "[OK]"   -ForegroundColor Green -NoNewline; Write-Host "   $args" }
function Write-Warn  { Write-Host "[WARN]" -ForegroundColor Yellow -NoNewline; Write-Host " $args" }
function Write-Error { Write-Host "[ERROR]" -ForegroundColor Red -NoNewline; Write-Host " $args" }

# ── Backup Function ────────────────────────────────────────────────

function Backup-File {
    param([string]$Path)
    if (Test-Path $Path) {
        $backup = "$Path.$TIMESTAMP.bak"
        Copy-Item $Path $backup
        Write-Warn "Backed up existing: $Path → $backup"
    }
}

# ── Install for Claude Code ────────────────────────────────────────

function Install-Claude {
    $src = Join-Path $SCRIPT_DIR "claude"
    $dst = $Prefix

    Write-Info "Installing absorb-osp for Claude Code..."
    Write-Info "  Source: $src"
    Write-Info "  Target: $dst"
    Write-Info ""

    # Validate source
    if (-not (Test-Path $src)) {
        Write-Error "Cannot find 'claude/' directory in $src"
        Write-Error "Run this script from within the cloned repository."
        Write-Host ""
        Write-Info "Correct usage:"
        Write-Info "  git clone $REPO_URL"
        Write-Info "  cd micos/absorb-osp && .\install.ps1"
        exit 1
    }

    # Create directories
    New-Item -ItemType Directory -Force -Path "$dst\skills\absorb-osp" | Out-Null
    New-Item -ItemType Directory -Force -Path "$dst\rules" | Out-Null
    New-Item -ItemType Directory -Force -Path "$dst\absorbed" | Out-Null

    $filesCopied = 0
    $filesSkipped = 0

    # Skill definition
    $skillSrc = Join-Path $src "SKILL.md"
    if (Test-Path $skillSrc) {
        $skillDst = "$dst\skills\absorb-osp\SKILL.md"
        Backup-File $skillDst
        Copy-Item $skillSrc $skillDst
        Write-Ok "Installed → $skillDst"
        $filesCopied++
    }

    # Workflow spec
    $specSrc = Join-Path $src "WORKFLOW_SPEC.md"
    if (Test-Path $specSrc) {
        $specDst = "$dst\skills\absorb-osp\WORKFLOW_SPEC.md"
        Backup-File $specDst
        Copy-Item $specSrc $specDst
        Write-Ok "Installed → $specDst"
        $filesCopied++
    }

    # Enforcement rules
    $rulesSrc = Join-Path $src "rules\absorb-workflow.md"
    if (Test-Path $rulesSrc) {
        $rulesDst = "$dst\rules\absorb-workflow.md"
        Backup-File $rulesDst
        Copy-Item $rulesSrc $rulesDst
        Write-Ok "Installed → $rulesDst"
        $filesCopied++
    }

    # Templates (don't overwrite existing)
    $tmplSrc = Join-Path $SCRIPT_DIR "templates"
    if (Test-Path $tmplSrc) {
        Get-ChildItem "$tmplSrc\*.md" | ForEach-Object {
            $destName = "TEMPLATE_$($_.Name)"
            $destPath = "$dst\absorbed\$destName"
            if (-not (Test-Path $destPath)) {
                Copy-Item $_.FullName $destPath
                Write-Ok "Installed template → $destPath"
                $filesCopied++
            } else {
                $filesSkipped++
            }
        }
    }

    # Shared indexes (don't overwrite existing)
    $sharedSrc = Join-Path $SCRIPT_DIR "shared"
    if (Test-Path $sharedSrc) {
        Get-ChildItem "$sharedSrc\*.md" | ForEach-Object {
            $destPath = "$dst\absorbed\$($_.Name)"
            if (-not (Test-Path $destPath)) {
                Copy-Item $_.FullName $destPath
                Write-Ok "Created index → $destPath"
                $filesCopied++
            } else {
                $filesSkipped++
            }
        }
    }

    Write-Host ""
    Write-Info "Claude Code install summary: $filesCopied new/updated, $filesSkipped skipped (already exist)"
}

# ── Install for Hermes Agent ───────────────────────────────────────

function Install-Hermes {
    $src = Join-Path $SCRIPT_DIR "hermes"
    $hermesConfig = "$env:USERPROFILE\.hermes\config"

    if (-not (Test-Path $hermesConfig)) {
        Write-Warn "Hermes config directory not found at $hermesConfig"
        New-Item -ItemType Directory -Force -Path $hermesConfig | Out-Null
        Write-Info "Created Hermes config directory"
    }

    $filesCopied = 0

    $yamlSrc = Join-Path $src "absorb-osp.yaml"
    if (Test-Path $yamlSrc) {
        $yamlDst = "$hermesConfig\absorb-osp.yaml"
        Backup-File $yamlDst
        Copy-Item $yamlSrc $yamlDst
        Write-Ok "Installed → $yamlDst"
        $filesCopied++
    }

    Write-Host ""
    Write-Info "Hermes install summary: $filesCopied file(s) installed"
}

# ── Main ───────────────────────────────────────────────────────────

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     absorb-osp  Installation             ║" -ForegroundColor Cyan
Write-Host "║     v2.0.0                               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Install-Claude

if ($Hermes) {
    Install-Hermes
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Installation Complete!                   ║" -ForegroundColor Cyan
Write-Host "║                                           ║" -ForegroundColor Cyan
Write-Host "║  Next steps:                              ║" -ForegroundColor Cyan
Write-Host "║  1. Restart your agent session            ║" -ForegroundColor Cyan
Write-Host "║  2. Send a GitHub URL to test:            ║" -ForegroundColor Cyan
Write-Host '║     "Absorb https://github.com/..."       ║' -ForegroundColor Cyan
Write-Host "║                                           ║" -ForegroundColor Cyan
Write-Host "║  Docs: $REPO_URL           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
