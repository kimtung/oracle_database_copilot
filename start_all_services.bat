@echo off
title Oracle AI Copilot — Startup Manager
color 0A
chcp 65001 >nul

echo ============================================================
echo   ORACLE AI COPILOT — KHOI DONG TAT CA DICH VU
echo   %DATE% %TIME%
echo ============================================================
echo.

:: ─────────────────────────────────────────────────────────────
:: BUOC 1 — PostgreSQL Service
:: ─────────────────────────────────────────────────────────────
echo [1/5] Kiem tra PostgreSQL (postgresql-x64-18)...
sc query postgresql-x64-18 | findstr /i "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo       [OK] PostgreSQL dang chay.
) else (
    echo       [..] Dang khoi dong PostgreSQL...
    net start postgresql-x64-18 >nul 2>&1
    timeout /t 5 /nobreak >nul
    sc query postgresql-x64-18 | findstr /i "RUNNING" >nul
    if %ERRORLEVEL% EQU 0 (
        echo       [OK] PostgreSQL da khoi dong.
    ) else (
        echo       [!!] CANH BAO: Khong the khoi dong PostgreSQL!
    )
)
echo.

:: ─────────────────────────────────────────────────────────────
:: BUOC 2 — Oracle Database Service (ORCL Instance)
:: ─────────────────────────────────────────────────────────────
echo [2/5] Kiem tra Oracle Database (OracleServiceORCL)...
sc query OracleServiceORCL | findstr /i "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Oracle Database dang chay.
) else (
    echo       [..] Dang khoi dong Oracle Database...
    net start OracleServiceORCL >nul 2>&1
    timeout /t 15 /nobreak >nul
    sc query OracleServiceORCL | findstr /i "RUNNING" >nul
    if %ERRORLEVEL% EQU 0 (
        echo       [OK] Oracle Database da khoi dong.
    ) else (
        echo       [!!] CANH BAO: Khong the khoi dong Oracle Database!
    )
)
echo.

:: ─────────────────────────────────────────────────────────────
:: BUOC 3 — Oracle TNS Listeners
:: ─────────────────────────────────────────────────────────────
echo [3/5] Kiem tra Oracle TNS Listeners...

sc query OracleOraDB19Home1TNSListener | findstr /i "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Listener chinh dang chay.
) else (
    echo       [..] Dang khoi dong Listener chinh...
    net start OracleOraDB19Home1TNSListener >nul 2>&1
    timeout /t 5 /nobreak >nul
    sc query OracleOraDB19Home1TNSListener | findstr /i "RUNNING" >nul
    if %ERRORLEVEL% EQU 0 (
        echo       [OK] Listener chinh da khoi dong.
    ) else (
        echo       [!!] CANH BAO: Khong the khoi dong Listener chinh!
    )
)

sc query OracleOraDB19Home1TNSListenerKETNOITHUONG | findstr /i "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Listener KETNOI THUONG dang chay.
) else (
    echo       [..] Dang khoi dong Listener KETNOI THUONG...
    net start OracleOraDB19Home1TNSListenerKETNOITHUONG >nul 2>&1
    timeout /t 5 /nobreak >nul
    sc query OracleOraDB19Home1TNSListenerKETNOITHUONG | findstr /i "RUNNING" >nul
    if %ERRORLEVEL% EQU 0 (
        echo       [OK] Listener KETNOI THUONG da khoi dong.
    ) else (
        echo       [!!] CANH BAO: Khong the khoi dong Listener KETNOI THUONG!
    )
)
echo.

:: ─────────────────────────────────────────────────────────────
:: BUOC 4 — Backend FastAPI (db-copilot tren port 8000)
:: ─────────────────────────────────────────────────────────────
echo [4/5] Kiem tra Backend API (localhost:8000)...
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Backend dang chay tren port 8000.
) else (
    echo       [..] Dang khoi dong Backend FastAPI...
    start "DB-Copilot Backend" cmd /k "title DB-Copilot Backend [port 8000] && cd /d d:\2026\oracle_ai\db-copilot && "C:\Users\Hi Windows 11 23\.local\bin\uv.exe" run db-copilot"
    echo       [OK] Da mo cua so Backend (cho ~10 giay de khoi dong hoan tat).
)
echo.

:: ─────────────────────────────────────────────────────────────
:: BUOC 5 — Frontend Vite Dev Server (port 5173)
:: ─────────────────────────────────────────────────────────────
echo [5/5] Kiem tra Frontend Dev Server (localhost:5173)...
netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Frontend dang chay tren port 5173.
) else (
    echo       [..] Dang khoi dong Frontend Vite...
    start "Oracle AI Frontend" cmd /k "title Oracle AI Frontend [port 5173] && cd /d d:\2026\oracle_ai\frontend && npm run dev"
    echo       [OK] Da mo cua so Frontend.
)
echo.

:: ─────────────────────────────────────────────────────────────
:: HOAN THANH
:: ─────────────────────────────────────────────────────────────
echo ============================================================
echo   TAT CA DICH VU DA DUOC XU LY!
echo.
echo   - PostgreSQL  : localhost:5432
echo   - Oracle DB   : localhost:1521/ORCL
echo   - Backend API : http://localhost:8000/api/v1/health
echo   - Frontend    : http://localhost:5173
echo ============================================================
echo.

:: Tu dong mo browser sau 12 giay (cho Backend khoi dong xong)
echo   Mo trinh duyet sau 12 giay...
timeout /t 12 /nobreak >nul
start "" "http://localhost:5173"

echo   Xong! Nhan phim bat ky de dong cua so nay.
pause >nul
