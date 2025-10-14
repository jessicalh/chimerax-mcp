; ChimeraX MCP Server - Inno Setup Installer Script
; Creates a Windows installer that:
; - Installs the executable
; - Updates Claude Desktop configuration
; - Creates Start Menu shortcuts
; - Handles upgrades cleanly

#define MyAppName "ChimeraX MCP Server"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "ChimeraX MCP Contributors"
#define MyAppURL "https://github.com/jessicalh/chimerax-mcp"
#define MyAppExeName "chimerax-mcp-server.exe"

[Setup]
; Basic app information
AppId={{8F9D6C4E-5A3B-4C8D-9E2F-1A7B8C9D0E1F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation settings
DefaultDirName={autopf}\ChimeraX-MCP
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=chimerax-mcp-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Windows version
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Configuration updater script
Source: "update_claude_config.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Run]
; Update Claude Desktop configuration after installation
Filename: "python"; Parameters: """{app}\update_claude_config.py"" ""{app}\{#MyAppExeName}"""; \
    Description: "Configure Claude Desktop"; \
    Flags: postinstall skipifsilent runhidden; \
    StatusMsg: "Updating Claude Desktop configuration..."

; Optionally open README
Filename: "{app}\README.md"; Description: "View README"; \
    Flags: postinstall shellexec skipifsilent

[Code]
var
  PythonFound: Boolean;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // Check if Python is installed
  PythonFound := False;

  if Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    PythonFound := True;
  end;

  Result := True; // Continue installation even if Python not found
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  PythonPath: String;
  ConfigScript: String;
  ExePath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Only try to update config if Python is available
    if PythonFound then
    begin
      ConfigScript := ExpandConstant('{app}\update_claude_config.py');
      ExePath := ExpandConstant('{app}\{#MyAppExeName}');

      // Try to run the config updater
      // This is a backup method if the [Run] section fails
      if FileExists(ConfigScript) then
      begin
        Exec('python', '"' + ConfigScript + '" "' + ExePath + '"', '',
             SW_HIDE, ewWaitUntilTerminated, ResultCode);
      end;
    end;
  end;
end;

[CustomMessages]
english.InstallingChimeraXMCP=Installing ChimeraX MCP Server...
english.ConfiguringClaude=Configuring Claude Desktop...

[InstallDelete]
; Clean up old versions
Type: files; Name: "{app}\chimerax_mcp_server.py"
Type: files; Name: "{app}\*.pyc"

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\__pycache__"

[Registry]
; Add to PATH (optional, for command-line usage)
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; \
    Check: NeedsAddPath('{app}')

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKLM,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Response: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    Response := MsgBox('Do you want to remove the ChimeraX MCP entry from Claude Desktop configuration?',
                      mbConfirmation, MB_YESNO);
    if Response = IDYES then
    begin
      // Note: We don't automatically remove it to prevent data loss
      MsgBox('Please manually edit your Claude Desktop configuration file at:' + #13#10 +
             '%APPDATA%\Claude\claude_desktop_config.json' + #13#10 + #13#10 +
             'Remove the "chimerax" entry from the "mcpServers" section.',
             mbInformation, MB_OK);
    end;
  end;
end;
