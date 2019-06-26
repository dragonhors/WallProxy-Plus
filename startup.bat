@echo off
::建议将proxy.exe发送到桌面快捷方式并在路径后加参数 --hide --single
::双击可切换窗口显示与隐藏
cd %~dp0
proxy.exe --hide --single
