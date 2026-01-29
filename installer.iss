; Inno Setup Script for Dict-to-Anki
; Creates a professional Windows installer

[Setup]
AppName=Dict-to-Anki
AppVersion=1.0.0
AppPublisher=Dict-to-Anki
AppPublisherURL=https://github.com/yourusername/dict-to-anki
DefaultDirName={autopf}\DictToAnki
DefaultGroupName=Dict-to-Anki
OutputDir=Output
OutputBaseFilename=DictToAnki-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\DictToAnki.exe
; SetupIconFile=assets\icon.ico  ; Commented out - no icon file yet
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\DictToAnki.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Dict-to-Anki"; Filename: "{app}\DictToAnki.exe"
Name: "{group}\Uninstall Dict-to-Anki"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Dict-to-Anki"; Filename: "{app}\DictToAnki.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DictToAnki.exe"; Description: "Launch Dict-to-Anki"; Flags: nowait postinstall skipifsilent

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Registry]
; Auto-start on Windows login (optional, controlled by app settings)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "DictToAnki"; ValueData: """{app}\DictToAnki.exe"""; Flags: uninsdeletevalue

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Show message about AnkiConnect
    MsgBox('Important: Dict-to-Anki requires Anki with the AnkiConnect add-on installed.' + #13#10 + #13#10 +
           'AnkiConnect code: 2055492159' + #13#10 + #13#10 +
           'Install it from Anki: Tools → Add-ons → Get Add-ons', mbInformation, MB_OK);
  end;
end;
