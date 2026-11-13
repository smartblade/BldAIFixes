@echo off
rem Compile sources of BldMystery with Visual C++ 6.0 and compare procedures
rem with the original BBLibc.dll and Blade.exe.
rem
rem Usage: build.bat <path to BldMystery>
rem
rem Run it in a command prompt with VC6 environment (VCVARS32.BAT).
rem Compiler options can be changed with CFLAGS environment variable,
rem options of compare_obj.py with COMPARE_FLAGS.

setlocal
if "%~1"=="" (
    echo Usage: build.bat ^<path to BldMystery^>
    exit /b 1
)
set BLD=%~1
set OUT=%~dp0out
if not exist "%OUT%" mkdir "%OUT%"

if "%CFLAGS%"=="" set CFLAGS=/Zp4 /MD /Od /Ob1 /Gd /W3
set INCLUDES=/I "%BLD%\src" /I "%BLD%\src\include" /I "%BLD%\src\Blade" /I "%BLD%\src\Python-1.5.2\Include"
rem Asserts are enabled: the original binaries call _assert
set DEFINES=/D WIN32 /D _WINDOWS /D BLD_NATIVE
set COMPARE=python "%~dp0compare_obj.py"

cl 2>&1 | findstr /C:"Version 12.00" >nul
if errorlevel 1 (
    echo cl.exe is not Visual C++ 6.0 compiler:
    cl 2>&1 | findstr /C:"Version"
    exit /b 1
)
rem Rich header of BBLibc.dll: cl.exe 12.00.8799 (Visual C++ 6.0 SP4)
cl 2>&1 | findstr /C:"Version 12.00.8799" >nul
if errorlevel 1 (
    echo Warning: the original binaries are compiled with cl.exe 12.00.8799,
    echo code of other builds can differ:
    cl 2>&1 | findstr /C:"Version"
)

echo === BBLibc.dll
for %%f in (IDataFile Name BBLibc) do (
    cl /nologo /c %CFLAGS% %INCLUDES% %DEFINES% /D _USRDLL /D BBLIBC_LIB_EXPORT= /Fo"%OUT%\%%f.obj" "%BLD%\src\BBLibc\%%f.cpp"
    if errorlevel 1 exit /b 1
)
%COMPARE% --raw "%BLD%\src\BBLibc\asm\raw.txt" %COMPARE_FLAGS% "%OUT%\IDataFile.obj" "%OUT%\Name.obj" "%OUT%\BBLibc.obj"

rem OctTree.cpp of BldMystery pull request 7 with constants declared as
rem 'static double' and its variants with 'static const double' and literals
if not exist "%BLD%\src\BWorld\OctTree.cpp" (
    echo %BLD%\src\BWorld\OctTree.cpp not found, skip Blade.exe
    exit /b 0
)
python "%~dp0make_octtree_variants.py" "%BLD%\src\BWorld\OctTree.cpp" "%OUT%"
if errorlevel 1 exit /b 1
cl /nologo /c %CFLAGS% %INCLUDES% %DEFINES% /Fo"%OUT%\OctTree.obj" "%BLD%\src\BWorld\OctTree.cpp"
if errorlevel 1 exit /b 1
for %%v in (const literal) do (
    cl /nologo /c %CFLAGS% %INCLUDES% %DEFINES% /Fo"%OUT%\OctTree_%%v.obj" "%OUT%\OctTree_%%v.cpp"
    if errorlevel 1 exit /b 1
)
for %%v in (OctTree OctTree_const OctTree_literal) do (
    echo === Blade.exe: %%v.cpp
    %COMPARE% --raw "%BLD%\src\Blade\asm\raw.txt" --relocs %COMPARE_FLAGS% "%OUT%\%%v.obj"
)
