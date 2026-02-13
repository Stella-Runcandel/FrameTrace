[Setup]
AppName=Frame Trace
AppVersion=0.9B
DefaultDirName={localappdata}\Frame Trace
DefaultGroupName=Frame Trace
OutputDir=installer_output
OutputBaseFilename=FrameTrace_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Frame Trace\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Frame Trace"; Filename: "{app}\Frame Trace.exe"
Name: "{userdesktop}\Frame Trace"; Filename: "{app}\Frame Trace.exe"

[Run]
Filename: "{app}\Frame Trace.exe"; Description: "Launch Frame Trace"; Flags: nowait postinstall skipifsilent
