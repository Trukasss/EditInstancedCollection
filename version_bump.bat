echo off
set python="C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe"
set current_dir=%~dp0
set script="%current_dir%version_bump.py"

%python% %script% "patch"