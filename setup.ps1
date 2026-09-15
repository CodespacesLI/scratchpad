# Prueft und installiert die Voraussetzungen fuer scratchpad unter Windows.
# Aufruf: .\setup.cmd [claude|codex|beide|pruefen]
#
# Installiert fehlende Basis-Werkzeuge ueber winget (Git, Node.js LTS, Python) und den
# gewaehlten Agenten ueber dessen offiziellen Weg. "pruefen" installiert nichts.
# Laeuft mit Windows PowerShell 5.1. Datei bewusst nur ASCII: 5.1 liest Skripte ohne
# BOM in der Landes-Codepage.
param([Parameter(Position = 0)][string]$Auswahl)

$MinNode = 22
$Auswahlen = @('claude', 'codex', 'beide', 'pruefen')

if ([string]::IsNullOrWhiteSpace($Auswahl)) {
  $Auswahl = Read-Host 'Agent installieren (claude, codex, beide) oder nur pruefen (pruefen)'
}
$Auswahl = "$Auswahl".Trim().ToLowerInvariant()
if ($Auswahl -notin $Auswahlen) {
  Write-Host "FEHLER: Unbekannte Auswahl: $Auswahl (erlaubt: $($Auswahlen -join ', '))" -ForegroundColor Red
  exit 1
}
$Agenten = switch ($Auswahl) { 'claude' { @('claude') } 'codex' { @('codex') } 'beide' { @('claude', 'codex') } default { @() } }

# Fuehrt ein Werkzeug aus und liefert die erste Ausgabezeile, oder $null wenn es fehlt
# oder scheitert. Scheitern zaehlt als fehlend: so faellt auch der Python-Platzhalter des
# Microsoft Store durch, der zwar im PATH liegt, aber nichts ausfuehrt.
function Get-Ausgabe([string]$Befehl, [string[]]$Argumente) {
  $ErrorActionPreference = 'Continue'
  $cmd = Get-Command $Befehl -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $cmd) { return $null }
  try {
    $out = & $cmd.Source @Argumente 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    return "$(@($out)[0])".Trim()
  } catch { return $null }
}

function Get-Stand {
  $node = Get-Ausgabe 'node' @('-p', 'process.versions.node')
  $nodeOk = $false
  if ($node) { $nodeOk = [int]($node.Split('.')[0]) -ge $MinNode }
  $python = $null
  foreach ($name in @('python', 'python3')) {
    $python = Get-Ausgabe $name @('-c', 'import sys; assert sys.version_info >= (3, 9); print(sys.version.split()[0])')
    if ($python) { break }
  }
  return [ordered]@{
    Git    = Get-Ausgabe 'git' @('--version')
    Node   = $(if ($nodeOk) { "v$node" } else { $null })
    Npm    = Get-Ausgabe 'npm' @('--version')
    Python = $python
    claude = Get-Ausgabe 'claude' @('--version')
    codex  = Get-Ausgabe 'codex' @('--version')
  }
}

# Uebernimmt PATH-Eintraege, die ein Installer gerade in die Registry geschrieben hat.
# Angehaengt statt ersetzt, damit Eintraege der laufenden Sitzung erhalten bleiben.
function Update-Pfad {
  $neu = @([Environment]::GetEnvironmentVariable('Path', 'Machine'), [Environment]::GetEnvironmentVariable('Path', 'User')) -join ';'
  $vorhanden = $env:Path -split ';'
  foreach ($eintrag in ($neu -split ';')) {
    if ($eintrag -and ($vorhanden -notcontains $eintrag)) { $env:Path = "$env:Path;$eintrag" }
  }
}

function Install-Winget([string]$Id, [string]$Override) {
  Write-Host "Installiere $Id ueber winget ..."
  $argumente = @('install', '--id', $Id, '-e', '--source', 'winget', '--silent', '--accept-package-agreements', '--accept-source-agreements')
  if ($Override) { $argumente += @('--override', $Override) }
  & winget @argumente
  if ($LASTEXITCODE -ne 0) { Write-Host "WARNUNG: winget meldete Exit $LASTEXITCODE fuer $Id." -ForegroundColor Yellow }
}

$Installiert = $false
if ($Auswahl -ne 'pruefen') {
  $stand = Get-Stand
  if (-not ($stand.Git -and $stand.Node -and $stand.Npm -and $stand.Python)) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
      Write-Host 'WARNUNG: winget fehlt. Git, Node.js 22+ und Python 3 von Hand installieren oder den Dev Container nutzen (README).' -ForegroundColor Yellow
    } else {
      if (-not $stand.Git) { Install-Winget 'Git.Git' }
      if (-not ($stand.Node -and $stand.Npm)) { Install-Winget 'OpenJS.NodeJS.LTS' }
      # PrependPath=1: python.exe landet vor dem Store-Platzhalter im PATH.
      if (-not $stand.Python) { Install-Winget 'Python.Python.3.13' '/quiet InstallAllUsers=0 PrependPath=1' }
      $Installiert = $true
      Update-Pfad
    }
  }

  if (($Agenten -contains 'claude') -and -not $stand.claude) {
    Write-Host 'Installiere Claude Code (offizieller Installer) ...'
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; irm https://claude.ai/install.ps1 | iex"
    $bin = Join-Path $env:USERPROFILE '.local\bin'
    $userPfad = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ((Test-Path $bin) -and (($userPfad -split ';') -notcontains $bin)) {
      [Environment]::SetEnvironmentVariable('Path', (@($userPfad, $bin) | Where-Object { $_ }) -join ';', 'User')
    }
    $Installiert = $true
    Update-Pfad
  }

  if (($Agenten -contains 'codex') -and -not $stand.codex) {
    if (Get-Ausgabe 'npm' @('--version')) {
      Write-Host 'Installiere Codex CLI ueber npm ...'
      & (Get-Command npm -CommandType Application | Select-Object -First 1).Source install -g '@openai/codex'
      $Installiert = $true
      Update-Pfad
    } else {
      Write-Host 'WARNUNG: npm fehlt, Codex CLI nicht installiert.' -ForegroundColor Yellow
    }
  }
}

$stand = Get-Stand
$fehlt = $false
Write-Host ''
Write-Host 'Stand:'
function Write-Zeile([string]$Name, $Wert, [bool]$Pflicht) {
  if ($Wert) { Write-Host ("  [ok]    {0,-12} {1}" -f $Name, $Wert) -ForegroundColor Green }
  elseif ($Pflicht) { Write-Host ("  [fehlt] {0}" -f $Name) -ForegroundColor Red }
  else { Write-Host ("  [-]     {0,-12} nicht installiert" -f $Name) }
}
Write-Zeile 'Git' $stand.Git $true
Write-Zeile "Node.js $MinNode+" $stand.Node $true
Write-Zeile 'npm' $stand.Npm $true
Write-Zeile 'Python 3.9+' $stand.Python $true
foreach ($basis in @($stand.Git, $stand.Node, $stand.Npm, $stand.Python)) { if (-not $basis) { $fehlt = $true } }
foreach ($agent in @('claude', 'codex')) {
  $pflicht = $Agenten -contains $agent
  Write-Zeile $agent $stand[$agent] $pflicht
  if ($pflicht -and -not $stand[$agent]) { $fehlt = $true }
}
if (($Auswahl -eq 'pruefen') -and -not ($stand.claude -or $stand.codex)) {
  Write-Host '  Kein Agent gefunden: .\setup.cmd claude oder .\setup.cmd codex' -ForegroundColor Red
  $fehlt = $true
}

Write-Host ''
if ($fehlt) {
  Write-Host 'Es fehlt noch etwas (siehe oben). Ohne lokale Installation geht es mit dem Dev Container (README).' -ForegroundColor Red
  exit 1
}
Write-Host 'Alles bereit. Weiter: python start.py claude   (oder: python start.py codex)' -ForegroundColor Green
if ($Installiert) { Write-Host 'Wichtig: Ein NEUES Terminal oeffnen, damit die neuen Programme gefunden werden.' -ForegroundColor Yellow }
exit 0
