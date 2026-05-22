@echo off
chcp 65001 > nul 2>&1
title Yerel AI Asistan - Kurulum

echo.
echo ================================================
echo    YEREL YAPAY ZEKA ASISTANI - KURULUM
echo ================================================
echo.

:: Python kontrolu
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python kurulu degil!
    echo Lutfen https://www.python.org/downloads/ adresinden Python 3.8+ indirin.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i bulundu.

:: Ollama kontrolu
ollama --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [UYARI] Ollama kurulu degil!
    echo Ollama olmadan program calismaz.
    echo.
    echo Kurmak icin: https://ollama.com/download/windows
    echo.
    set /p INDIR="Ollama indirme sayfasi acilsin mi? (e/h): "
    if /i "%INDIR%"=="e" (
        start https://ollama.com/download/windows
        echo Ollama kurduktan sonra bu scripti tekrar calistirin.
    )
    echo.
    pause
    exit /b 1
)

echo [OK] Ollama bulundu.

:: Ollama servisini baslat
echo.
echo [*] Ollama servisi baslatiliyor...
start /b ollama serve > nul 2>&1
timeout /t 3 /nobreak > nul

:: Model kontrolu
echo [*] Kurulu modeller kontrol ediliyor...
ollama list 2> nul | findstr /v "NAME" | findstr /v "^$" > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] Hic model kurulu degil.
    echo [*] llama3.1 indiriliyor... (yaklasik 5GB)
    echo [*] Internet hiziniza gore 5-20 dakika surebilir.
    echo.
    ollama pull llama3.1
    if %errorlevel% neq 0 (
        echo [HATA] Model indirilemedi! Internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
    echo [OK] llama3.1 basariyla indirildi!
) else (
    echo [OK] Kurulu modeller mevcut:
    ollama list
)

echo.
echo ================================================
echo    KURULUM TAMAMLANDI!
echo ================================================
echo.
echo Baslatmak icin: calistir.bat
echo      veya CMD: python ai_asistan.py
echo.
pause