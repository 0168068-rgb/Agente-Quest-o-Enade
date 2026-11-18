!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"
!include "x64.nsh"

!define PRODUCT "SmartDuck"
!define VERSION "1.9.0"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\SmartDuck"

Unicode true
RequestExecutionLevel user
SetCompressor /SOLID lzma
ManifestDPIAware true
ManifestSupportedOS all
BrandingText "SmartDuck | Assistente de notas"
SetFont "Segoe UI" 9

!define MUI_ICON "resources\smartduck.ico"
!define MUI_UNICON "resources\smartduck.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP "resources\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\sidebar.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "resources\sidebar.bmp"
!define MUI_TEXTCOLOR "17345A"

VIProductVersion "1.9.0.0"
VIAddVersionKey /LANG=1046 "ProductName" "SmartDuck"
VIAddVersionKey /LANG=1046 "ProductVersion" "${VERSION}"
VIAddVersionKey /LANG=1046 "FileVersion" "${VERSION}"
VIAddVersionKey /LANG=1046 "LegalCopyright" "SmartDuck"
