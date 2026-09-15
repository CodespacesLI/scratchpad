# Prueft und installiert die Voraussetzungen fuer scratchpad unter Windows.
# Aufruf: .\setup.cmd [claude|codex|beide|pruefen]
#
# Braucht KEINE Admin-Rechte: alles landet im Benutzerordner und im Benutzer-PATH.
# Git und Python kommen per winget als Benutzer-Installation, Node.js als offizielles
# ZIP von nodejs.org (der MSI-Installer wuerde Admin-Rechte verlangen), die Agenten ueber
# ihren offiziellen Weg. "pruefen" installiert nichts.
# Laeuft mit Windows PowerShell 5.1. Datei bewusst nur ASCII: 5.1 liest Skripte ohne
# BOM in der Landes-Codepage.
param([Parameter(Position = 0)][string]$Auswahl)

$MinNode = 22
$Auswahlen = @('claude', 'codex', 'beide', 'pruefen')
$NodeZiel = Join-Path $env:LOCALAPPDATA 'Programs\nodejs'
# Fortschrittsbalken machen Downloads in PowerShell 5.1 um ein Vielfaches langsamer.
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

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
    NodeAlt = $(if ($node -and -not $nodeOk) { "v$node" } else { $null })
    Npm    = Get-Ausgabe 'npm' @('--version')
    Python = $python
    claude = Get-Ausgabe 'claude' @('--version')
    codex  = Get-Ausgabe 'codex' @('--version')
  }
}

# Uebernimmt PATH-Eintraege, die ein Installer gerade in die Registry geschrieben hat.
# VORNE eingefuegt: sonst gewinnt in dieser Sitzung weiter der Store-Platzhalter aus
# WindowsApps gegen das frisch installierte Python.
function Update-Pfad {
  $registry = @([Environment]::GetEnvironmentVariable('Path', 'Machine'), [Environment]::GetEnvironmentVariable('Path', 'User')) -join ';'
  $vorhanden = $env:Path -split ';'
  $neu = @($registry -split ';' | Where-Object { $_ -and ($vorhanden -notcontains $_) })
  if ($neu.Count -gt 0) { $env:Path = (@($neu) + $env:Path) -join ';' }
}

function Add-BenutzerPfad([string]$Ordner) {
  $userPfad = [Environment]::GetEnvironmentVariable('Path', 'User')
  $eintraege = @($userPfad -split ';' | Where-Object { $_ })
  if ($eintraege -notcontains $Ordner) {
    [Environment]::SetEnvironmentVariable('Path', (@($eintraege) + $Ordner) -join ';', 'User')
  }
}

function Install-Winget([string]$Id, [string]$Override) {
  Write-Host "Installiere $Id ueber winget (Benutzer-Installation) ..."
  $argumente = @('install', '--id', $Id, '-e', '--source', 'winget', '--scope', 'user', '--accept-package-agreements', '--accept-source-agreements', '--override', $Override)
  & winget @argumente
  if ($LASTEXITCODE -ne 0) { Write-Host "WARNUNG: winget meldete Exit $LASTEXITCODE fuer $Id." -ForegroundColor Yellow }
}

# Node.js ohne Admin: das offizielle ZIP der neuesten LTS nach %LOCALAPPDATA%\Programs\nodejs,
# Pruefsumme gegen SHASUMS256.txt, dann in den Benutzer-PATH.
function Install-NodeZip {
  $arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'x64' }
  Write-Host 'Installiere Node.js (LTS) als ZIP von nodejs.org ...'
  try {
    # Erst in eine Variable: PowerShell 5.1 reicht ein JSON-Array aus Invoke-RestMethod
    # sonst als EIN Objekt durch die Pipeline, und der Filter waehlt das ganze Array.
    $index = Invoke-RestMethod 'https://nodejs.org/dist/index.json'
    $release = $index | Where-Object { $_.lts -and ($_.files -contains "win-$arch-zip") } | Select-Object -First 1
    if (-not $release) { throw 'Keine passende LTS-Version in nodejs.org/dist/index.json gefunden.' }
    $name = "node-$($release.version)-win-$arch"
    $basis = "https://nodejs.org/dist/$($release.version)"
    $zip = Join-Path $env:TEMP "$name.zip"
    Invoke-WebRequest "$basis/$name.zip" -OutFile $zip -UseBasicParsing
    $summen = (Invoke-WebRequest "$basis/SHASUMS256.txt" -UseBasicParsing).Content
    $erwartet = ($summen -split "`n" | Where-Object { $_ -match "\s$([regex]::Escape($name)).zip$" } | Select-Object -First 1) -replace '\s.*$', ''
    if (-not $erwartet -or ((Get-FileHash $zip -Algorithm SHA256).Hash -ne $erwartet.ToUpperInvariant())) {
      throw 'Pruefsumme stimmt nicht.'
    }
    $programme = Split-Path -Parent $NodeZiel
    New-Item -ItemType Directory -Path $programme -Force | Out-Null
    if (Test-Path $NodeZiel) { Remove-Item $NodeZiel -Recurse -Force }
    $entpackt = Join-Path $programme $name
    if (Test-Path $entpackt) { Remove-Item $entpackt -Recurse -Force }
    # tar (seit Windows 10 dabei) entpackt die ~10.000 Dateien in Sekunden, Expand-Archive in Minuten.
    $tar = Join-Path $env:SystemRoot 'System32\tar.exe'
    if (Test-Path $tar) { & $tar -xf $zip -C $programme } else { Expand-Archive $zip -DestinationPath $programme -Force }
    Rename-Item $entpackt $NodeZiel
    Remove-Item $zip -Force
    Add-BenutzerPfad $NodeZiel
    Write-Host "  Node.js $($release.version) liegt in $NodeZiel"
  } catch {
    Write-Host "WARNUNG: Node.js-Installation gescheitert: $($_.Exception.Message)" -ForegroundColor Yellow
  }
}

# Das Terminal kann aelter sein als eine fruehere Installation: erst den PATH aus der
# Registry holen, sonst gilt ein laengst installiertes Programm als fehlend.
Update-Pfad

$Installiert = $false
if ($Auswahl -ne 'pruefen') {
  $stand = Get-Stand

  if (-not ($stand.Node -and $stand.Npm)) {
    if ($stand.NodeAlt) {
      Write-Host "WARNUNG: Node.js $($stand.NodeAlt) ist zu alt. Liegt es im System-PATH, verdeckt es das neue Node.js; dann deinstallieren." -ForegroundColor Yellow
    }
    Install-NodeZip
    $Installiert = $true
    Update-Pfad
  }

  if (-not ($stand.Git -and $stand.Python)) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
      Write-Host 'WARNUNG: winget fehlt. Git und Python von Hand installieren oder Codespaces nutzen (README).' -ForegroundColor Yellow
    } else {
      # /CURRENTUSER und InstallAllUsers=0: Installation ins Benutzerprofil, kein Admin-Dialog.
      if (-not $stand.Git) { Install-Winget 'Git.Git' '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES /SP- /CURRENTUSER' }
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
    if (Test-Path $bin) { Add-BenutzerPfad $bin }
    $Installiert = $true
    Update-Pfad
  }

  if (($Agenten -contains 'codex') -and -not $stand.codex) {
    $npm = Get-Command npm -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($npm -and (Get-Ausgabe 'npm' @('--version'))) {
      Write-Host 'Installiere Codex CLI ueber npm ...'
      & $npm.Source install -g '@openai/codex'
      # Globale npm-Pakete liegen je nach Node-Installation neben node.exe oder in %APPDATA%\npm.
      $prefix = Get-Ausgabe 'npm' @('prefix', '-g')
      if ($prefix -and (Test-Path $prefix)) { Add-BenutzerPfad $prefix }
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
  Write-Host 'Es fehlt noch etwas (siehe oben). Ohne lokale Installation geht es mit Codespaces (README).' -ForegroundColor Red
  exit 1
}
Write-Host 'Alles bereit. Weiter: python start.py claude   (oder: python start.py codex)' -ForegroundColor Green
if ($Installiert) { Write-Host 'Wichtig: Ein NEUES Terminal oeffnen, damit die neuen Programme gefunden werden.' -ForegroundColor Yellow }
exit 0
