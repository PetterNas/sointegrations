@ECHO OFF
TITLE Uninstall Web Tools
ECHO ===============================================================================
ECHO.                                                                              
ECHO This will uninstall SuperOffice Mail Link and SuperOffice Web Extensions.                          
ECHO It will also clear HKCU for SuperOffice keys.                                                                              
ECHO It will delete these two "SuperOffice" folders:                          
ECHO.                                                                              
ECHO %localappdata%\SuperOffice                                                    
ECHO %appdata%\SuperOffice                                                         
ECHO.                                                                              
ECHO.                                                                              
ECHO Admin rights are required to run the tool.                                    
ECHO.                                                                              
ECHO ===============================================================================
:PROMPT
SET /P STARTTASK=Do you want to continue? ([yes]/[no])?                   
IF /I "%STARTTASK%" EQU "yes" GOTO :YES
IF /I "%STARTTASK%" EQU "no" GOTO :NO
ECHO.
ECHO ===============================================================================
:YES
ECHO.
ECHO Uninstalling Mail Link....
WMIC Product Where Name='SuperOffice MailLink' Call Uninstall /nointeractive >nul
ECHO.
ECHO Mail Link uninstalled.
ECHO.
ECHO ===============================================================================


ECHO. 
ECHO. 
ECHO Uninstalling Web Extensions..
WMIC Product Where Name='SuperOffice Web Extensions' Call Uninstall /nointeractive >nul
ECHO Web Extensions uninstalled.
@RD /S /Q "%localappdata%\SuperOffice"
@RD /S /Q "%appdata%\SuperOffice"

ECHO.
ECHO.
ECHO Appdata and localappdata folders deleted.
ECHO.
ECHO.
for /f "delims=" %%a in ('reg query HKCU /f "SuperOffice" /s /k') do (reg.exe delete  "%%a" /f)>nul 2> nul 
ECHO.
ECHO Deleted SuperOffice entries in HKCU.
ECHO.
:NO
ECHO Have a nice day!
ECHO.
:END
PAUSE

