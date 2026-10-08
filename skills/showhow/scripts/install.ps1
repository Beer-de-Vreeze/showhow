# Installs everything /showhow needs on Windows, then runs a short voice and
# transcription test so first-use downloads happen now instead of mid-video.
# Run: powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = 'Stop'

function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}

# Put a folder on the user PATH for good (new terminals and agent sessions see it).
function Add-UserPath($dir) {
  if (-not $dir -or -not (Test-Path $dir)) { return }
  $user = "$([Environment]::GetEnvironmentVariable('Path', 'User'))"
  $known = ($user + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')) -split ';' | ForEach-Object { $_.TrimEnd('\') }
  if ($known -contains $dir.TrimEnd('\')) { return }
  [Environment]::SetEnvironmentVariable('Path', ($user.TrimEnd(';') + ';' + $dir).TrimStart(';'), 'User')
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
Need docker 'Docker.DockerDesktop' # render --docker (reproducible renders); asks for admin

Step 'Kokoro voice and MusicGen music (Python venv)'
$venv = "$HOME\.cache\hyperframes\kokoro-venv"
$venvPython = "$venv\Scripts\python.exe"
# Always x64: torch/kokoro wheels exist for it everywhere, and Windows on ARM runs it emulated.
$x64Python = 'cpython-3.12-windows-x86_64-none'
if ((Test-Path $venvPython) -and ((& $venvPython -c 'import platform; print(platform.machine())') -ne 'AMD64')) {
  Write-Host 'redo venv is not x64'
  Remove-Item -Recurse -Force $venv
}
if (-not (Test-Path $venvPython)) { Run 'uv' @('venv', '--python', $x64Python, $venv) }
Run 'uv' @('pip', 'install', '--python', $venvPython, 'kokoro-onnx', 'soundfile', 'transformers', 'torch', 'numpy')
[Environment]::SetEnvironmentVariable('HYPERFRAMES_PYTHON', $venvPython, 'User')
$env:HYPERFRAMES_PYTHON = $venvPython
Write-Host "ok   HYPERFRAMES_PYTHON=$venvPython"

Step 'whisper-cpp (transcription)'
if (Has 'whisper-cli') {
  Write-Host 'ok   whisper-cli'
} else {
  # Official ggml-org Windows build; the latest tagged releases may ship without binaries.
  $whisperTag = 'b5130'
  $whisperDir = "$HOME\.local\whisper-cpp"
  $zip = Join-Path ([IO.Path]::GetTempPath()) 'whisper-bin-x64.zip'
  Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/ggml-org/whisper.cpp/releases/download/$whisperTag/whisper-bin-x64.zip" -OutFile $zip
  Expand-Archive -Force -Path $zip -DestinationPath $whisperDir
  Remove-Item -Force $zip
  $bin = Split-Path (Get-ChildItem -Recurse -Path $whisperDir -Filter 'whisper-cli.exe' | Select-Object -First 1).FullName
  Add-UserPath $bin
  Refresh-Path
  if (-not (Has 'whisper-cli')) { throw 'whisper-cli is still not on PATH. Open a new terminal and rerun.' }
  Write-Host "ok   whisper-cli ($bin)"
}

Step 'Hyperframes skills'
if ((Test-Path "$HOME\.claude\skills\hyperframes-core") -or (Test-Path "$HOME\.agents\skills\hyperframes-core")) {
  Write-Host 'ok   already installed'
} else {
  Run 'npx.cmd' @('-y', 'skills', 'add', 'heygen-com/hyperframes', '-g', '-a', 'claude-code', '-s', '*', '-y')
}

Step 'Render browser'
Run 'npx.cmd' @('-y', 'hyperframes', 'browser', 'ensure')

Step 'Voice and transcription test (downloads models on first run)'
$test = Join-Path ([IO.Path]::GetTempPath()) 'showhow-install-test'
New-Item -ItemType Directory -Force -Path $test | Out-Null
Push-Location $test
try {
  Run 'npx.cmd' @('-y', 'hyperframes', 'tts', 'Show how setup works.', '-o', 'test.wav')
  Run 'npx.cmd' @('-y', 'hyperframes', 'transcribe', 'test.wav')
  Run $venvPython @('-c', "from transformers import AutoProcessor, MusicgenForConditionalGeneration as M; AutoProcessor.from_pretrained('facebook/musicgen-small'); M.from_pretrained('facebook/musicgen-small'); print('musicgen ok')")
} finally {
  Pop-Location
  Remove-Item -Recurse -Force $test -ErrorAction SilentlyContinue
}

Step 'Check'
foreach ($command in 'node', 'npx', 'ffmpeg', 'ffprobe', 'python', 'uv', 'whisper-cli', 'docker') {
  if (-not (Has $command)) { throw "$command is not on PATH after install." }
  Write-Host ("ok   {0,-12} {1}" -f $command, (Get-Command $command).Source)
}
Write-Host "ok   HYPERFRAMES_PYTHON=$([Environment]::GetEnvironmentVariable('HYPERFRAMES_PYTHON', 'User'))"
cmd /c 'docker info >nul 2>&1'  # via cmd: PowerShell 5.1 with Stop turns native stderr into a fatal error
if ($LASTEXITCODE -ne 0) {
  $desktop = "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
  if (Test-Path $desktop) { Start-Process $desktop }
  Write-Host 'note Docker is installed but not running. Open Docker Desktop once (accept its terms); render --docker works after that.' -ForegroundColor Yellow
}
npx.cmd -y hyperframes doctor
Write-Host "`nDone. Restart Claude (or open a new terminal) so it sees the new PATH, then run /showhow <task>." -ForegroundColor Green
