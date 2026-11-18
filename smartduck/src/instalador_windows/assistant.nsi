!include "common.nsh"
!include "nsDialogs.nsh"
!include "WinMessages.nsh"

Name "SmartDuck"
Caption "SmartDuck - Ativar no Chrome"
OutFile "dist\SmartDuck.exe"
VIAddVersionKey /LANG=1046 "FileDescription" "SmartDuck - Assistente de ativação no Chrome"
VIAddVersionKey /LANG=1046 "OriginalFilename" "SmartDuck.exe"

Var ChromeExe
Var Dialog
Var PathField
Var StatusLabel
Var Button

!define MUI_DISABLE_INSERT_LANGUAGE_AFTER_PAGES_WARNING
Page custom AssistantPage
Page instfiles CloseAssistant
!insertmacro MUI_LANGUAGE "PortugueseBR"

Function CloseAssistant
  Quit
FunctionEnd

Function .onInit
  SetShellVarContext current
  StrCpy $INSTDIR "$EXEDIR"
  IfFileExists "$INSTDIR\extensao\manifest.json" ready
    MessageBox MB_OK|MB_ICONEXCLAMATION "Os arquivos do SmartDuck não foram encontrados nesta pasta.$\r$\n$\r$\nExecute SmartDuck_Instalar_1.9.0.exe para instalar ou reparar."
    Abort
  ready:
FunctionEnd

Function AssistantPage
  !insertmacro MUI_HEADER_TEXT "Ative o SmartDuck Simples 1.9.0" "Copie a pasta, abra as extensões e conclua a ativação."
  nsDialogs::Create 1018
  Pop $Dialog
  ${If} $Dialog == error
    Abort
  ${EndIf}

  ${NSD_CreateLabel} 0 0 100% 12u "1. Pasta da extensão"
  Pop $0
  ${NSD_CreateText} 0 14u 100% 14u "$INSTDIR\extensao"
  Pop $PathField
  SendMessage $PathField ${EM_SETREADONLY} 1 0

  ${NSD_CreateButton} 0 34u 100u 16u "Copiar pasta"
  Pop $Button
  ${NSD_OnClick} $Button CopyPath
  ${NSD_CreateButton} 106u 34u 100u 16u "Abrir pasta"
  Pop $Button
  ${NSD_OnClick} $Button OpenFolder

  ${NSD_CreateButton} 0 55u 100% 18u "2. Abrir extensões no Chrome"
  Pop $Button
  ${NSD_OnClick} $Button OpenExtensions
  ${NSD_CreateLabel} 0 79u 100% 27u "3. Ative Modo do desenvolvedor. Clique em Carregar sem compactação, cole a pasta copiada e clique em Selecionar pasta."
  Pop $0

  ${NSD_CreateButton} 0 109u 100% 17u "Guia de uso e atualização"
  Pop $Button
  ${NSD_OnClick} $Button OpenGuide
  ${NSD_CreateLabel} 0 130u 100% 10u "No painel deve aparecer SIMPLES 1.9.0 e Realizar."
  Pop $StatusLabel
  SetCtlColors $StatusLabel "205256" "FFFFFF"

  GetDlgItem $0 $HWNDPARENT 1
  SendMessage $0 ${WM_SETTEXT} 0 "STR:Fechar"
  GetDlgItem $0 $HWNDPARENT 2
  ShowWindow $0 ${SW_HIDE}
  GetDlgItem $0 $HWNDPARENT 3
  ShowWindow $0 ${SW_HIDE}
  nsDialogs::Show
FunctionEnd

Function CopyPath
  Pop $0
  SendMessage $PathField ${EM_SETSEL} 0 -1
  SendMessage $PathField ${WM_COPY} 0 0
  ${NSD_SetFocus} $PathField
  ${NSD_SetText} $StatusLabel "Pasta copiada. Cole com Ctrl+V na seleção de pasta."
FunctionEnd

Function OpenFolder
  Pop $0
  ClearErrors
  ExecShell "open" "$INSTDIR\extensao"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "Não foi possível abrir a pasta. Copie o caminho mostrado acima e abra-o no Explorador de Arquivos."
  ${EndIf}
FunctionEnd

Function FindChrome
  StrCpy $ChromeExe ""
  ReadRegStr $ChromeExe HKCU "Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" ""
  IfFileExists "$ChromeExe" found
  ${If} ${RunningX64}
    SetRegView 64
    ReadRegStr $ChromeExe HKLM "Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" ""
    SetRegView 32
    IfFileExists "$ChromeExe" found
  ${EndIf}
  ReadRegStr $ChromeExe HKLM "Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" ""
  IfFileExists "$ChromeExe" found
  StrCpy $ChromeExe "$LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
  IfFileExists "$ChromeExe" found
  StrCpy $ChromeExe "$PROGRAMFILES64\Google\Chrome\Application\chrome.exe"
  IfFileExists "$ChromeExe" found
  StrCpy $ChromeExe "$PROGRAMFILES32\Google\Chrome\Application\chrome.exe"
  IfFileExists "$ChromeExe" found
  SearchPath $ChromeExe "chrome.exe"
  IfFileExists "$ChromeExe" found
  StrCpy $ChromeExe ""
  found:
FunctionEnd

Function OpenExtensions
  Pop $0
  Call FindChrome
  ${If} $ChromeExe == ""
    MessageBox MB_OK|MB_ICONINFORMATION "Não encontrei o Google Chrome.$\r$\n$\r$\nSe ele já está instalado, abra-o e digite chrome://extensions na barra de endereços. Caso contrário, instale o Chrome e abra este assistente novamente."
    Return
  ${EndIf}
  ClearErrors
  Exec '"$ChromeExe" "chrome://extensions/"'
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "Não foi possível abrir o Chrome. Abra o navegador e digite chrome://extensions na barra de endereços."
  ${Else}
    ${NSD_SetText} $StatusLabel "Ative o modo de desenvolvedor e carregue a pasta."
  ${EndIf}
FunctionEnd

Function OpenGuide
  Pop $0
  ExecShell "open" "$INSTDIR\LEIA-ME-INSTALACAO.html"
FunctionEnd

Section
SectionEnd
