# pip show customtkinter | Select-String -Pattern 'Location: (\w*)' | Out-File test.txt

pyinstaller --noconfirm --onedir --windowed --add-data "C:\Users\craus\mambaenv\envs\pyrot\Lib\site-packages\customtkinter;customtkinter\"  .\pyrot.py
Start-Sleep -Seconds 2
New-Item -Path dist\pyrot\ -Name 'specs' -ItemType Directory -Force
Copy-Item -Path specs\*.yaml -Destination dist\pyrot\specs
New-Item -Path dist\pyrot\ -Name "icons" -ItemType Directory -Force
New-Item -Path dist\pyrot\icons -Name ".keep" -Force
Copy-Item -Path default_config.yaml -Destination .\dist\pyrot\config.yaml

$compress = @{
    Path             = ".\dist\pyrot\*"
    CompressionLevel = "Fastest"
    DestinationPath  = ".\dist\pyrot.zip"
}
Compress-Archive @compress -Update