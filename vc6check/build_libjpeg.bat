@echo off
rem Compile IJG libjpeg 6b with Visual C++ 6.0 and search its procedures in
rem the original BBLibc.dll.
rem
rem Usage: build_libjpeg.bat <path to BldMystery> [<path to jpeg-6b>]
rem
rem Without the path to jpeg-6b sources jpegsrc.v6b.tar.gz is downloaded
rem from www.ijg.org (curl and tar of Windows 10 are used).
rem Run it in a command prompt with VC6 environment (VCVARS32.BAT).
rem Compiler options can be changed with CFLAGS environment variable.

setlocal
if "%~1"=="" (
    echo Usage: build_libjpeg.bat ^<path to BldMystery^> [^<path to jpeg-6b^>]
    exit /b 1
)
set BLD=%~1
set OUT=%~dp0out
set JPEG=%~2
if not exist "%OUT%" mkdir "%OUT%"

if "%JPEG%"=="" (
    set JPEG=%OUT%\jpeg-6b
    if not exist "%OUT%\jpeg-6b\jpeglib.h" (
        curl -L -o "%OUT%\jpegsrc.v6b.tar.gz" https://www.ijg.org/files/jpegsrc.v6b.tar.gz
        if errorlevel 1 exit /b 1
        tar -xzf "%OUT%\jpegsrc.v6b.tar.gz" -C "%OUT%"
        if errorlevel 1 exit /b 1
    )
)
if not exist "%JPEG%\jpeglib.h" (
    echo %JPEG%\jpeglib.h not found
    exit /b 1
)

if "%CFLAGS%"=="" set CFLAGS=/Zp4 /MD /Od /Ob1 /Gd /W3

cl 2>&1 | findstr /C:"Version 12.00" >nul
if errorlevel 1 (
    echo cl.exe is not Visual C++ 6.0 compiler:
    cl 2>&1 | findstr /C:"Version"
    exit /b 1
)
cl 2>&1 | findstr /C:"Version 12.00.8799" >nul
if errorlevel 1 (
    echo Warning: the original binaries are compiled with cl.exe 12.00.8799,
    echo code of other builds can differ:
    cl 2>&1 | findstr /C:"Version"
)

rem jconfig.h for Visual C++ from jconfig.vc of libjpeg
if not exist "%OUT%\jpeg_config" mkdir "%OUT%\jpeg_config"
copy /y "%JPEG%\jconfig.vc" "%OUT%\jpeg_config\jconfig.h" >nul
if errorlevel 1 exit /b 1

rem LIBOBJECTS of makefile.vc of libjpeg 6b with jmemnobs memory manager
set LIBOBJECTS=jcapimin jcapistd jctrans jcparam jdatadst jcinit jcmaster jcmarker jcmainct jcprepct jccoefct jccolor jcsample jchuff jcphuff jcdctmgr jfdctfst jfdctflt jfdctint jdapimin jdapistd jdtrans jdatasrc jdmaster jdinput jdmarker jdhuff jdphuff jdmainct jdcoefct jdpostct jddctmgr jidctfst jidctflt jidctint jidctred jdsample jdcolor jquant1 jquant2 jdmerge jcomapi jutils jerror jmemmgr jmemnobs

if not exist "%OUT%\jpeg" mkdir "%OUT%\jpeg"
for %%f in (%LIBOBJECTS%) do (
    cl /nologo /c %CFLAGS% /I "%OUT%\jpeg_config" /Fo"%OUT%\jpeg\%%f.obj" "%JPEG%\%%f.c"
    if errorlevel 1 exit /b 1
)

echo === libjpeg 6b in BBLibc.dll
python "%~dp0compare_obj.py" --raw "%BLD%\src\BBLibc\asm\raw.txt" --search "%OUT%\jpeg"
