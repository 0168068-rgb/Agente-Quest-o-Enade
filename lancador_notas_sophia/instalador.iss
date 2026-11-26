#define AppName "Lançador de Notas SophiA"
#define AppVersion "1.0.0"
#define AppExe "LancadorNotasSophia.exe"

[Setup]
AppId={{855C6C99-89C1-4FC4-89D6-1D6E7C9C1B4A}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\LancadorNotasSophia
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
OutputDir=dist\instalador
OutputBaseFilename=LancadorNotasSophia-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExe}
CloseApplications=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Files]
Source: "dist\LancadorNotasSophia\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent

; Não há UninstallDelete: relatórios ficam na pasta escolhida pelo usuário.
