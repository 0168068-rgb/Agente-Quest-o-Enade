; Script de Instalação Inno Setup para AVALIA AutoBatch v5.1
; ==========================================================

[Setup]
AppId={{D38F24C5-9E52-4751-A3D2-990B0F396D8A}
AppName=AVALIA AutoBatch
AppVersion=5.1
AppPublisher=Hamilcar Silva
DefaultDirName={userappdata}\Programs\AVALIA AutoBatch
DefaultGroupName=AVALIA AutoBatch
DisableProgramGroupPage=yes
OutputDir=dist_installer
OutputBaseFilename=AVALIA_AutoBatch_Setup_Instalador
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Uninstallable: no

[Files]
Source: "dist\AVALIA_AutoBatch\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AVALIA AutoBatch"; Filename: "{app}\AVALIA_AutoBatch.exe"
Name: "{group}\{cm:UninstallProgram,AVALIA AutoBatch}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AVALIA AutoBatch"; Filename: "{app}\AVALIA_AutoBatch.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AVALIA_AutoBatch.exe"; Description: "{cm:LaunchProgram,AVALIA AutoBatch}"; Flags: nowait postinstall skipifsilent
