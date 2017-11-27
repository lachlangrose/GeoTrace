'---------------------------------------
'Elevate this script before invoking it.
'25.2.2011 FNL
'---------------------------------------
bElevate = False
if WScript.Arguments.Count > 0 Then If WScript.Arguments(WScript.Arguments.Count-1) <> "|" then bElevate = True
if bElevate Or WScript.Arguments.Count = 0 Then ElevateUAC
'******************
'Your script goes here
'******************
dim shell
set shell=createobject("wscript.shell")
shell.run "C:\Users\lgrose\Documents\GeoTraceInstall\deps.bat"
set shell=nothing
'-----------------------------------------
'Run this script under elevated privileges
'-----------------------------------------
Sub ElevateUAC
    sParms = " |"
    If WScript.Arguments.Count > 0 Then
            For i = WScript.Arguments.Count-1 To 0 Step -1
            sParms = " " & WScript.Arguments(i) & sParms
        Next
    End If
    Set oShell = CreateObject("Shell.Application")
    oShell.ShellExecute "wscript.exe", WScript.ScriptFullName & sParms, , "runas", 1
    WScript.Quit
End Sub