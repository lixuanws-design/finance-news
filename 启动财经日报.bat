@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════
echo   财经热点日报 - Financial News Digest
echo   多源聚合 + AI分析 + A股关联
echo ═══════════════════════════════════════
echo.
echo  启动服务...
echo  浏览器将自动打开 http://localhost:8899
echo.
echo  关闭此窗口停止服务
echo ═══════════════════════════════════════
start "" "http://localhost:8899"
python "%~dp0app.py"
pause
