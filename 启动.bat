@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════
echo   📰 财经热点日报 - Financial News Digest
echo ═══════════════════════════════════════
echo.
echo  启动服务中...
echo  浏览器将自动打开: http://localhost:8899
echo.
python "%~dp0app.py"
pause
