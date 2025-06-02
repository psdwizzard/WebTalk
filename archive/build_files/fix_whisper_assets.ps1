# Fix WebTalk Whisper Assets
# This script copies the missing Whisper assets to the installed WebTalk server

Write-Host "Fixing WebTalk Whisper Assets..." -ForegroundColor Green

# Create the whisper directory structure
$whisperDir = "C:\Program Files\WebTalk\_internal\whisper"
$assetsDir = "$whisperDir\assets"
$normalizersDir = "$whisperDir\normalizers"

Write-Host "Creating whisper directories..." -ForegroundColor Yellow
New-Item -Path $whisperDir -ItemType Directory -Force | Out-Null
New-Item -Path $assetsDir -ItemType Directory -Force | Out-Null
New-Item -Path $normalizersDir -ItemType Directory -Force | Out-Null

# Copy assets
Write-Host "Copying Whisper assets..." -ForegroundColor Yellow
Copy-Item "C:\temp\whisper_backup\assets\*" $assetsDir -Force
Copy-Item "C:\temp\whisper_backup\normalizers\*" $normalizersDir -Recurse -Force

# Verify the copy
if (Test-Path "$assetsDir\mel_filters.npz") {
    Write-Host "✅ Successfully copied Whisper assets!" -ForegroundColor Green
    Write-Host "✅ mel_filters.npz is now available" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to copy mel_filters.npz" -ForegroundColor Red
}

Write-Host "Done! You can now test WebTalk." -ForegroundColor Green
Read-Host "Press Enter to exit" 