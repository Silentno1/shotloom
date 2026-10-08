param(
    [ValidateSet("agents", "codex", "claude")]
    [string]$Agent = "agents",
    [string]$Target = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Source = Join-Path $Root "skill\shotloom"

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
$Destination = Join-Path $Target "shotloom"
if ((Test-Path -LiteralPath $Destination) -and ((Resolve-Path -LiteralPath $Destination).Path -eq (Resolve-Path -LiteralPath $Source).Path)) {
    throw "Refusing to replace the source folder itself."
}

if (Test-Path $Destination) {
    if (-not $Force) {
        throw "Refusing to replace existing installation: $Destination. Use -Force to back it up and install."
    }
}

$Stage = Join-Path $Target (".shotloom-stage-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Stage | Out-Null
$StagedSkill = Join-Path $Stage "shotloom"
Copy-Item -Recurse -LiteralPath $Source -Destination $StagedSkill
$Backup = $null
if (Test-Path -LiteralPath $Destination) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Backup = "$Destination.backup-$Stamp-$([guid]::NewGuid().ToString('N'))"
    Move-Item -LiteralPath $Destination -Destination $Backup
    Write-Host "Backed up existing installation to $Backup"
}
try {
    Move-Item -LiteralPath $StagedSkill -Destination $Destination
} catch {
    if ($Backup -and -not (Test-Path -LiteralPath $Destination)) {
        Move-Item -LiteralPath $Backup -Destination $Destination
    }
    throw
}
Remove-Item -LiteralPath $Stage
Write-Host "Installed Shotloom to $Destination"
