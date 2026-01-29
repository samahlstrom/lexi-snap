; Inno Setup Script for Lexi Snap
; Creates a professional Windows installer

[Setup]
AppName=Lexi Snap
AppVersion=1.0.0
AppPublisher=Lexi Snap
AppPublisherURL=https://github.com/yourusername/lexi-snap
DefaultDirName={autopf}\LexiSnap
DefaultGroupName=Lexi Snap
OutputDir=Output
OutputBaseFilename=LexiSnap-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\LexiSnap.exe
SetupIconFile=assets\icon.ico
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\LexiSnap.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Lexi Snap"; Filename: "{app}\LexiSnap.exe"
Name: "{group}\Uninstall Lexi Snap"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Lexi Snap"; Filename: "{app}\LexiSnap.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LexiSnap.exe"; Description: "Launch Lexi Snap"; Flags: nowait postinstall skipifsilent

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Registry]
; Auto-start on Windows login (optional, controlled by app settings)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "LexiSnap"; ValueData: """{app}\LexiSnap.exe"""; Flags: uninsdeletevalue

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Show message about AnkiConnect
    MsgBox('Important: Lexi Snap requires Anki with the AnkiConnect add-on installed.' + #13#10 + #13#10 +
           'AnkiConnect code: 2055492159' + #13#10 + #13#10 +
           'Install it from Anki: Tools → Add-ons → Get Add-ons', mbInformation, MB_OK);
  end;
end;
