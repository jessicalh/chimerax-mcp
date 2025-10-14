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

; Privileges - allow user to choose
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline dialog

; Windows version
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Configuration file
Source: "chimerax_mcp_config.json"; DestDir: "{app}"; Flags: ignoreversion confirmoverwrite

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
  InstallForAllUsers: Boolean;

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

  // Default to all users if running as admin, current user otherwise
  InstallForAllUsers := IsAdmin;

  Result := True; // Continue installation even if Python not found
end;

procedure InitializeWizard();
var
  Page: TInputOptionWizardPage;
begin
  // Create custom page for installation mode selection
  Page := CreateInputOptionPage(wpLicense,
    'Installation Mode', 'Choose installation scope',
    'Select whether to install for all users or just for you.',
    False, False);

  // Add options
  Page.Add('Install for all users (requires administrator privileges)');
  Page.Add('Install for current user only (no admin required)');

  // Set default based on admin status
  if IsAdmin then
    Page.Values[0] := True
  else
    Page.Values[1] := True;

  // Store for later use
  Page.Tag := 1; // Mark page as created
end;

function GetDefaultInstallDir(Param: String): String;
begin
  if InstallForAllUsers then
    Result := ExpandConstant('{autopf}\ChimeraX-MCP')
  else
    Result := ExpandConstant('{localappdata}\ChimeraX-MCP');
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo,
  MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  S: String;
begin
  S := '';

  if InstallForAllUsers then
    S := S + 'Installation Mode:' + NewLine + Space + 'All Users (requires admin)' + NewLine + NewLine
  else
    S := S + 'Installation Mode:' + NewLine + Space + 'Current User Only' + NewLine + NewLine;

  S := S + MemoDirInfo + NewLine + NewLine;

  Result := S;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Page: TWizardPage;
  InputPage: TInputOptionWizardPage;
begin
  Result := True;

  // Check if this is our custom page
  if CurPageID = wpLicense + 1 then
  begin
    Page := PageFromID(CurPageID);
    if (Page <> nil) and (Page.Tag = 1) then
    begin
      InputPage := TInputOptionWizardPage(Page);
      InstallForAllUsers := InputPage.Values[0];

      // Update installation directory based on selection
      if InstallForAllUsers then
      begin
        WizardForm.DirEdit.Text := ExpandConstant('{autopf}\ChimeraX-MCP');
        if not IsAdmin then
        begin
          MsgBox('Installing for all users requires administrator privileges. ' +
                 'Please run the installer as administrator or choose "Current user only".',
                 mbError, MB_OK);
          Result := False;
        end;
      end
      else
      begin
        WizardForm.DirEdit.Text := ExpandConstant('{localappdata}\ChimeraX-MCP');
      end;
    end;
  end;
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
