# Installs everything /showhow needs on Windows, then runs a short voice and
# transcription test so first-use downloads happen now instead of mid-video.
# Run: powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 [-Docker]
# -Docker also installs Docker Desktop (asks for admin) for reproducible `render --docker` renders.
param([switch]$Docker)
$ErrorActionPreference = 'Stop'

# Pinned versions: update them together, after a test video renders cleanly.
$Hyperframes = 'hyperframes@0.9.85'   # keep in step with HYPERFRAMES in render.py
$PythonPackages = 'kokoro-onnx==0.6.1', 'soundfile==0.14.0', 'numpy==2.5.3'
$WhisperTag = 'b5130'
$WhisperSha256 = 'F9EC6C52A2E949B62AB51FA21D0D497958F9E41C3010C157C4E42932D5316F3C'
$EarshotCommit = '972132643583fc0b9a60c6c50983ed7dc1aa55bf'  # tag v0.2.0

function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}

# Put a folder on the user PATH for good (new terminals and agent sessions see it).
# Reads and writes the raw registry value, so entries like %USERPROFILE%\bin stay unexpanded.
function Add-UserPath($dir) {
  if (-not $dir -or -not (Test-Path $dir)) { return }
  $known = ([Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')) -split ';' | ForEach-Object { $_.TrimEnd('\') }
  if ($known -contains $dir.TrimEnd('\')) { return }
  $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true)
  if (-not $key) { throw 'Could not open HKCU\Environment to update PATH.' }
  try {
    $raw = "$($key.GetValue('Path', '', 'DoNotExpandEnvironmentNames'))"
    $key.SetValue('Path', ($raw.TrimEnd(';') + ';' + $dir).TrimStart(';'), [Microsoft.Win32.RegistryValueKind]::ExpandString)
  } finally { $key.Close() }
  Write-Host "path $dir"
}

# Where winget, the Python installer, uv and npm put things when they don't add PATH themselves.
function Add-KnownPaths {
  Add-UserPath "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
  Add-UserPath "$env:ProgramFiles\nodejs"
  Add-UserPath "$env:APPDATA\npm"
  Add-UserPath "$env:LOCALAPPDATA\Programs\Python\Python312"
  Add-UserPath "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts"
  Add-UserPath "$HOME\.local\bin"
  Add-UserPath "$env:ProgramFiles\Docker\Docker\resources\bin"
  Get-ChildItem -Recurse -Path "$HOME\.local\whisper-cpp" -Filter 'whisper-cli.exe' -ErrorAction SilentlyContinue |
    Select-Object -First 1 | ForEach-Object { Add-UserPath $_.DirectoryName }
  Refresh-Path
}

function Step($name) { Write-Host "`n== $name" -ForegroundColor Cyan }

function Has($command) {
  $found = Get-Command $command -ErrorAction SilentlyContinue
  $found -and $found.Source -notlike '*\WindowsApps\*'
}

function Need($command, $wingetId) {
  if (Has $command) { Write-Host "ok   $command"; return }
  Write-Host "get  $command ($wingetId)"
  winget install --id $wingetId -e --silent --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { throw "winget could not install $wingetId (exit $LASTEXITCODE). Install it manually, then rerun." }
  Add-KnownPaths
  if (-not (Has $command)) { throw "$command is still not on PATH. Open a new terminal and rerun." }
}

function Run($file, [string[]]$arguments) {
  & $file @arguments
  if ($LASTEXITCODE -ne 0) { throw "$file $($arguments -join ' ') failed (exit $LASTEXITCODE)" }
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  throw 'winget is missing. Install "App Installer" from the Microsoft Store, then rerun.'
}

Step 'Tools'
Add-KnownPaths  # pick up tools installed since this shell started, and keep them on PATH
Need node   'OpenJS.NodeJS.LTS'   # hyperframes, npx
Need ffmpeg 'Gyan.FFmpeg'         # audio mixing, posters
Need python 'Python.Python.3.12'  # Kokoro voice-over
Need uv     'astral-sh.uv'        # beat analysis, ring baking, frame sheets
if ($Docker) { Need docker 'Docker.DockerDesktop' }  # render --docker (reproducible renders); asks for admin

Step 'Kokoro voice (Python venv)'
$venv = "$HOME\.cache\hyperframes\kokoro-venv"
$venvPython = "$venv\Scripts\python.exe"
# Always x64: kokoro and onnxruntime wheels exist for it everywhere, and Windows on ARM runs it emulated.
$x64Python = 'cpython-3.12-windows-x86_64-none'
if ((Test-Path $venvPython) -and ((& $venvPython -c 'import platform; print(platform.machine())') -ne 'AMD64')) {
  Write-Host 'redo venv is not x64'
  Remove-Item -Recurse -Force $venv
}
if (-not (Test-Path $venvPython)) { Run 'uv' @('venv', '--python', $x64Python, $venv) }
Run 'uv' (@('pip', 'install', '--python', $venvPython) + $PythonPackages)
[Environment]::SetEnvironmentVariable('HYPERFRAMES_PYTHON', $venvPython, 'User')
$env:HYPERFRAMES_PYTHON = $venvPython
Write-Host "ok   HYPERFRAMES_PYTHON=$venvPython"

Step 'whisper-cpp (transcription)'
if (Has 'whisper-cli') {
  Write-Host 'ok   whisper-cli'
} else {
  # Official ggml-org Windows build; the latest tagged releases may ship without binaries.
  $whisperDir = "$HOME\.local\whisper-cpp"
  $zip = Join-Path ([IO.Path]::GetTempPath()) 'whisper-bin-x64.zip'
  Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/ggml-org/whisper.cpp/releases/download/$WhisperTag/whisper-bin-x64.zip" -OutFile $zip
  $hash = (Get-FileHash $zip -Algorithm SHA256).Hash
  if ($hash -ne $WhisperSha256) { Remove-Item -Force $zip; throw "whisper-bin-x64.zip has SHA256 $hash, expected $WhisperSha256; not installing it." }
  Expand-Archive -Force -Path $zip -DestinationPath $whisperDir
  Remove-Item -Force $zip
  $bin = Split-Path (Get-ChildItem -Recurse -Path $whisperDir -Filter 'whisper-cli.exe' | Select-Object -First 1).FullName
  Add-UserPath $bin
  Refresh-Path
  if (-not (Has 'whisper-cli')) { throw 'whisper-cli is still not on PATH. Open a new terminal and rerun.' }
  Write-Host "ok   whisper-cli ($bin)"
}

Step 'earshot (optional audio QA, CPU torch, ~1.4 GB of models)'
# Optional: a failure here warns instead of stopping the install; /showhow skips audio QA without it.
# unsafe-best-match lets uv take torch from the official PyTorch CPU index and everything else from PyPI;
# shortcut: both indexes are trusted, so name confusion between them is the accepted risk until earshot pins its own index.
& uv tool install "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot@$EarshotCommit" --python 3.12 `
  --index https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match
if ($LASTEXITCODE -eq 0) { Add-KnownPaths; & earshot doctor --load }
if ($LASTEXITCODE -eq 0) { Write-Host 'ok   earshot' } else {
  Write-Host 'note earshot did not install; /showhow works without it and skips audio QA.' -ForegroundColor Yellow
}

Step 'Hyperframes skills'
# frame-presets only exists in the current single-skill layout, so an old install gets refreshed.
if ((Test-Path "$HOME\.claude\skills\hyperframes\assets\frame-presets") -or (Test-Path "$HOME\.agents\skills\hyperframes\assets\frame-presets")) {
  Write-Host 'ok   already installed'
} else {
  Run 'npx.cmd' @('-y', 'skills', 'add', 'heygen-com/hyperframes', '-g', '-a', 'claude-code', '-s', '*', '-y')
}

Step 'Script dependencies (uv)'
# --all-groups downloads the music-analysis packages into uv's cache too, so they work offline later;
# a plain `uv run` keeps only the base (Pillow) in the scripts' environment.
Run 'uv' @('sync', '--project', $PSScriptRoot, '--all-groups')

Step 'Render browser'
Run 'npx.cmd' @('-y', $Hyperframes, 'browser', 'ensure')

Step 'Voice and transcription test (downloads models on first run)'
$test = Join-Path ([IO.Path]::GetTempPath()) 'showhow-install-test'
New-Item -ItemType Directory -Force -Path $test | Out-Null
Push-Location $test
try {
  Run 'npx.cmd' @('-y', $Hyperframes, 'tts', 'Show how setup works.', '-o', 'test.wav')
  Run 'npx.cmd' @('-y', $Hyperframes, 'transcribe', 'test.wav')
} finally {
  Pop-Location
  Remove-Item -Recurse -Force $test -ErrorAction SilentlyContinue
}

Step 'Check'
foreach ($command in 'node', 'npx', 'ffmpeg', 'ffprobe', 'python', 'uv', 'whisper-cli') {
  if (-not (Has $command)) { throw "$command is not on PATH after install." }
  Write-Host ("ok   {0,-12} {1}" -f $command, (Get-Command $command).Source)
}
# Writing PATH through the registry sends no change notice; this call does, so apps started
# from the Start menu after this see the new PATH without signing out.
[Environment]::SetEnvironmentVariable('HYPERFRAMES_PYTHON', $venvPython, 'User')
Write-Host "ok   HYPERFRAMES_PYTHON=$([Environment]::GetEnvironmentVariable('HYPERFRAMES_PYTHON', 'User'))"
$dockerRunning = $false
if (Has 'docker') {
  cmd /c 'docker info >nul 2>&1'  # via cmd: PowerShell 5.1 with Stop turns native stderr into a fatal error
  $dockerRunning = $LASTEXITCODE -eq 0
}
if (-not (Has 'docker')) {
  Write-Host 'note Docker is not installed; renders run locally. Rerun with -Docker for reproducible render --docker.' -ForegroundColor Yellow
} elseif (-not $dockerRunning) {
  $desktop = "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
  if (Test-Path $desktop) { Start-Process $desktop }
  Write-Host 'note Docker is installed but not running. Open Docker Desktop once (accept its terms); render --docker works after that.' -ForegroundColor Yellow
}
npx.cmd -y $Hyperframes doctor
Write-Host "`nDone. Restart Claude (or open a new terminal) so it sees the new PATH, then run /showhow <task>." -ForegroundColor Green
