# pip show customtkinter | Select-String -Pattern 'Location: (\w*)' | Out-File test.txt

pyinstaller --noconfirm --onedir --windowed --add-data "C:\Users\craus\mambaenv\envs\pyrot\Lib\site-packages\customtkinter;customtkinter\" --add-data 'icons;icons\' --add-data 'specs;specs\'  .\pyrot.py
Start-Sleep -Seconds 2
New-Item -Path dist\pyrot\ -Name 'specs' -ItemType Directory -Force
Copy-Item -Path specs\*.yaml -Destination dist\pyrot\specs
New-Item -Path dist\pyrot\ -Name "icons" -ItemType Directory -Force
New-Item -Path dist\pyrot\icons -Name ".keep" -Force
Copy-Item -Path config.yaml -Destination .\dist\pyrot

$compress = @{
    Path             = ".\dist\pyrot\*"
    CompressionLevel = "Fastest"
    DestinationPath  = ".\dist\pyrot.zip"
}
Compress-Archive @compress