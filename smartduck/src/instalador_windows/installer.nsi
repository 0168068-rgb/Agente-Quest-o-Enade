!include "common.nsh"

Name "SmartDuck ${VERSION}"
Caption "Instalar SmartDuck ${VERSION}"
OutFile "..\SmartDuck_Instalar_1.9.0.exe"
InstallDir "$LOCALAPPDATA\SmartDuck"
VIAddVersionKey /LANG=1046 "FileDescription" "Instalador do SmartDuck para Windows"
VIAddVersionKey /LANG=1046 "OriginalFilename" "SmartDuck_Instalar_1.9.0.exe"
ShowInstDetails show
ShowUninstDetails show

!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "SmartDuck no seu Chrome"
!define MUI_WELCOMEPAGE_TEXT "Este assistente prepara o SmartDuck e cria um atalho com o pato na sua área de trabalho.$\r$\n$\r$\nDepois da cópia, você ativa a extensão no Chrome em Modo do desenvolvedor > Carregar sem compactação.$\r$\n$\r$\nA instalação é apenas para o seu usuário e não exige administrador."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_TITLE "Arquivos do SmartDuck preparados"
!define MUI_FINISHPAGE_TEXT "Falta concluir a ativação no Chrome.$\r$\n$\r$\nO assistente mostrará a pasta e abrirá a página de extensões.$\r$\n$\r$\nSe você já usava outra pasta, consulte Guia e atualização para evitar duas cópias da extensão."
!define MUI_FINISHPAGE_RUN "$INSTDIR\SmartDuck.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Abrir assistente de ativação no Chrome"
!insertmacro MUI_PAGE_FINISH

!define MUI_UNCONFIRMPAGE_TEXT_TOP "Antes de continuar, remova o SmartDuck em chrome://extensions.$\r$\n$\r$\nEsta etapa remove os arquivos e atalhos desta instalação. A remoção da extensão no Chrome é feita por você."
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"

Function .onInit
  SetShellVarContext current
  ; A stable per-user folder preserves the unpacked extension ID on later updates.
  ; Ignore /D: the uninstaller must only handle this app's known directory.
  StrCpy $INSTDIR "$LOCALAPPDATA\SmartDuck"
FunctionEnd

Section "SmartDuck" SEC_MAIN
  SetShellVarContext current
  SetOverwrite on
  ClearErrors
  SetOutPath "$INSTDIR\extensao"
  Delete "$INSTDIR\extensao\lote.html"
  Delete "$INSTDIR\extensao\lote.mjs"
  Delete "$INSTDIR\extensao\transfer.mjs"
  Delete "$INSTDIR\extensao\tests\transfer.test.mjs"
  ClearErrors
  File /r "..\smartduck\*.*"
  SetOutPath "$INSTDIR"
  File "dist\SmartDuck.exe"
  File "resources\smartduck.ico"
  File "..\LEIA-ME-INSTALACAO.html"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONSTOP "Não foi possível copiar todos os arquivos.$\r$\n$\r$\nA instalação não foi concluída. Verifique o espaço disponível e a permissão da pasta, feche o assistente SmartDuck e execute este instalador novamente."
    SetErrorLevel 1
    Abort
  ${EndIf}

  WriteUninstaller "$INSTDIR\Desinstalar.exe"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONSTOP "Não foi possível criar o desinstalador. Feche o SmartDuck e execute o instalador novamente."
    SetErrorLevel 1
    Abort
  ${EndIf}

  ClearErrors
  CreateDirectory "$SMPROGRAMS\SmartDuck"
  CreateShortCut "$DESKTOP\SmartDuck.lnk" "$INSTDIR\SmartDuck.exe" "" "$INSTDIR\smartduck.ico"
  CreateShortCut "$SMPROGRAMS\SmartDuck\SmartDuck.lnk" "$INSTDIR\SmartDuck.exe" "" "$INSTDIR\smartduck.ico"
  CreateShortCut "$SMPROGRAMS\SmartDuck\Guia de instalação.lnk" "$INSTDIR\LEIA-ME-INSTALACAO.html" "" "$INSTDIR\smartduck.ico"
  CreateShortCut "$SMPROGRAMS\SmartDuck\Desinstalar SmartDuck.lnk" "$INSTDIR\Desinstalar.exe"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "Os arquivos foram copiados, mas algum atalho não pôde ser criado.$\r$\n$\r$\nVocê pode abrir SmartDuck.exe na pasta:$\r$\n$INSTDIR"
  ${EndIf}

  ClearErrors
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "SmartDuck (arquivos da extensão)"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\smartduck.ico"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\Desinstalar.exe"'
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoRepair" 1
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "EstimatedSize" $0
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "Os arquivos estão disponíveis, mas o registro na lista de aplicativos do Windows não pôde ser concluído.$\r$\n$\r$\nPara remover os arquivos, use Desinstalar.exe na pasta SmartDuck."
  ${EndIf}
SectionEnd

Function un.onInit
  SetShellVarContext current
  StrCpy $INSTDIR "$LOCALAPPDATA\SmartDuck"
FunctionEnd

Section "Uninstall"
  SetShellVarContext current
  SetOutPath "$TEMP"
  ClearErrors
  ; Explicit filenames only: never recursively remove a user's directory.
  !include "remove_extension.nsh"
  Delete "$INSTDIR\SmartDuck.exe"
  Delete "$INSTDIR\smartduck.ico"
  Delete "$INSTDIR\LEIA-ME-INSTALACAO.html"
  Delete "$DESKTOP\SmartDuck.lnk"
  Delete "$SMPROGRAMS\SmartDuck\SmartDuck.lnk"
  Delete "$SMPROGRAMS\SmartDuck\Guia de instalação.lnk"
  Delete "$SMPROGRAMS\SmartDuck\Desinstalar SmartDuck.lnk"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "Algum arquivo não pôde ser removido. Feche o assistente SmartDuck e execute a desinstalação novamente.$\r$\n$\r$\nPasta:$\r$\n$INSTDIR"
    SetErrorLevel 1
    Abort
  ${EndIf}
  !include "remove_directories.nsh"
  RMDir "$SMPROGRAMS\SmartDuck"
  DeleteRegKey HKCU "${UNINSTALL_KEY}"
  Delete "$INSTDIR\Desinstalar.exe"
  RMDir "$INSTDIR"
SectionEnd
