$ErrorActionPreference = "Stop"
Set-Location "C:\Users\10448\Desktop\GPT-Image2-Studio1"
& "C:\Users\10448\AppData\Local\Programs\Python\Python314\Scripts\pyinstaller.exe" --noconfirm --clean "AI_Image_Generator.spec"
Write-Host "Build complete! The new Aero version is at dist/AI_Image_Generator.exe"
Copy-Item "dist\AI_Image_Generator.exe" "C:\Users\10448\Desktop\AI_Studio_Aero.exe" -Force
