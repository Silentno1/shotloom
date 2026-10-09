param(
    [ValidateSet("agents", "codex", "claude")]
    [string]$Agent = "agents",
    [string]$Target = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Source = Join-Path $Root "skill\shotloom"

function Move-InstallEntry([string]$FromPath, [string]$ToPath) {
    # Rename only: a failed/cross-volume move must not leave a partial copy.
    if ((Get-Item -LiteralPath $FromPath -Force).PSIsContainer) {
        [System.IO.Directory]::Move($FromPath, $ToPath)
    } else {
        [System.IO.File]::Move($FromPath, $ToPath)
    }
}

if ([string]::IsNullOrWhiteSpace($Target)) {
    switch ($Agent) {
        "agents" { $Target = Join-Path $HOME ".agents\skills" }
        "codex" {
            $CodexBase = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
            $Target = Join-Path $CodexBase "skills"
        }
        "claude" { $Target = Join-Path $HOME ".claude\skills" }
    }
}

$Destination = Join-Path $Target "shotloom"
if (-not (Test-Path -LiteralPath (Join-Path $Source "SKILL.md") -PathType Leaf)) {
    throw "Skill source is missing."
}
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Target = (Resolve-Path -LiteralPath $Target).Path
if ($Target.TrimEnd([char[]]"\/") -eq ([System.IO.Path]::GetPathRoot($Target)).TrimEnd([char[]]"\/")) {
    throw "Use a dedicated skills directory, not a filesystem root."
}
$Target = $Target.TrimEnd([char[]]"\/")
$Destination = Join-Path $Target "shotloom"
$TargetParent = Split-Path -Parent $Target
if ((Test-Path -LiteralPath $Destination) -and ((Resolve-Path -LiteralPath $Destination).Path -eq (Resolve-Path -LiteralPath $Source).Path)) {
    throw "Refusing to replace the source folder itself."
}

if (Test-Path -LiteralPath $Destination) {
    if (-not $Force) {
        throw "Refusing to replace existing installation: $Destination. Use -Force to back it up and install."
    }
}

# Sibling storage, never a hidden subfolder of the agent's discovery root.
$StateRoot = Join-Path $TargetParent ("." + (Split-Path -Leaf $Target) + ".shotloom-installer")
$StateItem = Get-Item -LiteralPath $StateRoot -Force -ErrorAction SilentlyContinue
if ($StateItem -and ($StateItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
    throw "Refusing linked installer storage: $StateRoot"
}
New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
$Stage = Join-Path $StateRoot ("stage-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Stage | Out-Null
$StagedSkill = Join-Path $Stage "shotloom"
try {
    Copy-Item -Recurse -LiteralPath $Source -Destination $StagedSkill
} catch {
    throw "Copy failed; existing install unchanged. Staging retained at ${Stage}: $($_.Exception.Message)"
}
$Backup = $null
if (Test-Path -LiteralPath $Destination) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $BackupParent = Join-Path $StateRoot ("backup-$Stamp-$([guid]::NewGuid().ToString('N'))")
    New-Item -ItemType Directory -Path $BackupParent | Out-Null
    $Backup = Join-Path $BackupParent "shotloom"
    try {
        Move-InstallEntry $Destination $Backup
    } catch {
        throw "Backup move failed; existing install unchanged. Staging retained at ${Stage}: $($_.Exception.Message)"
    }
    Write-Host "Backed up existing installation to $Backup"
}
try {
    Move-InstallEntry $StagedSkill $Destination
} catch {
    $InstallError = $_
    if ($Backup -and -not (Test-Path -LiteralPath $Destination)) {
        try {
            Move-InstallEntry $Backup $Destination
            Remove-Item -LiteralPath $BackupParent
            Write-Warning "Previous installation restored."
        } catch {
            Write-Warning "Restore failed; previous installation retained at $Backup"
        }
    }
    throw "Install failed; staging retained at ${Stage}: $($InstallError.Exception.Message)"
}
Remove-Item -LiteralPath $Stage
Write-Host "Installed Shotloom to $Destination"
