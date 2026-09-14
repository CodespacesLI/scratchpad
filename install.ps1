# Installiert scratchpad in ein Zielprojekt.
# Aufruf: pwsh -File install.ps1 <pfad-zum-zielprojekt> [neutral|codex|claude]
param([Parameter(Position = 0)][string]$Zielprojekt, [Parameter(Position = 1)][string]$Modus)
$ErrorActionPreference = 'Stop'
$Quelle = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Zielprojekt)) { throw 'FEHLER: Pfad des Zielprojekts fehlt.' }
if ([string]::IsNullOrWhiteSpace($Modus)) { $Modus = Read-Host 'Zielmodus (neutral, codex, claude)' }
$Modus = $Modus.ToLowerInvariant()
if ($Modus -notin @('neutral', 'codex', 'claude')) { throw "FEHLER: Unbekannter Zielmodus: $Modus (erlaubt: neutral, codex, claude)" }
if (-not (Test-Path $Zielprojekt)) { New-Item -ItemType Directory -Path $Zielprojekt -Force | Out-Null }
$Ziel = (Resolve-Path $Zielprojekt).Path
function Copy-Ordner([string]$Unterordner, [string]$ZielOrdner) { New-Item -ItemType Directory -Path $ZielOrdner -Force | Out-Null; Copy-Item -Path (Join-Path $Quelle "$Unterordner/*") -Destination $ZielOrdner -Recurse -Force; Write-Host "  kopiert: $Unterordner -> $($ZielOrdner.Substring($Ziel.Length + 1))" }
function Copy-Datei([string]$QuellDatei, [string]$ZielDatei) { New-Item -ItemType Directory -Path (Split-Path -Parent $ZielDatei) -Force | Out-Null; Copy-Item -Path (Join-Path $Quelle $QuellDatei) -Destination $ZielDatei -Force; Write-Host "  kopiert: $QuellDatei -> $($ZielDatei.Substring($Ziel.Length + 1))" }
function Ersetze-Platzhalter([string]$Basis, [string]$Agentenordner) { Get-ChildItem -Path $Basis -Recurse -File -Include '*.md', '*.json', '*.py' | ForEach-Object { $text = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($_.FullName)).Replace('<AGENTENORDNER>', $Agentenordner); [System.IO.File]::WriteAllBytes($_.FullName, [System.Text.Encoding]::UTF8.GetBytes($text)) } }
function Installiere-Kern([string]$Basis, [string]$Agentenordner) { Copy-Ordner kern (Join-Path $Basis 'vorgehen'); Copy-Datei vorlagen/tasks-README.md (Join-Path $Basis 'tasks/README.md'); Copy-Datei agent/AGENTS-block.md (Join-Path $Basis 'INSTRUCTIONS.md'); Ersetze-Platzhalter $Basis $Agentenordner }
function Get-PythonPfad { foreach ($name in @('python3', 'python')) { $cmd = Get-Command $name -ErrorAction SilentlyContinue; if ($cmd) { return $cmd.Source } }; return $null }
Write-Host "Installiere Scratchpad ($Modus) nach: $Ziel"
switch ($Modus) {
  'neutral' { Installiere-Kern (Join-Path $Ziel '.agents') .agents }
  'codex' {
    $Basis = Join-Path $Ziel '.agents'; Installiere-Kern $Basis .agents; Copy-Ordner agent/skills (Join-Path $Basis 'skills')
    $Agents = Join-Path $Ziel 'AGENTS.md'; $Start = '<!-- scratchpad:start -->'; $Ende = '<!-- scratchpad:end -->'
    if (-not (Test-Path $Agents) -or -not ((Get-Content -Raw $Agents) -match [regex]::Escape($Start))) { $prefix = if (Test-Path $Agents) { [Environment]::NewLine } else { '' }; Add-Content -LiteralPath $Agents -Value ($prefix + $Start + [Environment]::NewLine + (Get-Content -Raw (Join-Path $Basis 'INSTRUCTIONS.md')) + [Environment]::NewLine + $Ende); Write-Host '  ergaenzt: AGENTS.md (Scratchpad-Block)' } else { Write-Host '  unveraendert: AGENTS.md (Scratchpad-Block bereits vorhanden)' }
  }
  'claude' {
    $Basis = Join-Path $Ziel '.claude'; Copy-Ordner kern (Join-Path $Basis 'vorgehen'); Copy-Ordner agent/commands (Join-Path $Basis 'commands'); Copy-Ordner agent/skills (Join-Path $Basis 'skills')
    $HookZiel = Join-Path $Basis hooks; New-Item -ItemType Directory -Path $HookZiel -Force | Out-Null; Get-ChildItem (Join-Path $Quelle hooks) -Filter '*.py' -File | Where-Object Name -NotLike 'test_*.py' | Copy-Item -Destination $HookZiel -Force
    Copy-Datei vorlagen/tasks-README.md (Join-Path $Basis 'tasks/README.md'); Copy-Datei kern/antwortform.md (Join-Path $Basis 'output-styles/scratchpad-projektleiter.md')
    $Python = Get-PythonPfad; if (-not $Python) { throw 'FEHLER: python3/python nicht gefunden.' }; $Settings = Join-Path $Basis settings.json; if (-not (Test-Path $Settings)) { [System.IO.File]::WriteAllText($Settings, "{}`n", (New-Object System.Text.UTF8Encoding($false))) }; & $Python (Join-Path $Quelle install_settings.py) $Settings scratchpad-projektleiter (Join-Path $Quelle 'agent/settings-hooks.json') .claude; if ($LASTEXITCODE -ne 0) { throw 'FEHLER: install_settings.py scheiterte.' }; Ersetze-Platzhalter $Basis .claude
  }
}
Write-Host "Fertig. Scratchpad installiert ($Modus)."
