@echo off
setlocal

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

python model_training.py --epochs 80 --initial-epochs 20 --batch-size 32

endlocal
