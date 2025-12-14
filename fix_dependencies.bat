@echo off
echo ====================================
echo Fixing pip and setuptools first
echo ====================================
echo.

echo Step 1: Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 2: Uninstalling old packages...
pip uninstall -y torch torchvision transformers sentence-transformers faiss-cpu

echo.
echo Step 3: Installing required packages...
pip install --upgrade groq==0.11.0
pip install scikit-learn==1.3.2
pip install numpy==1.24.3

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Now run: python test_rag.py
echo.
pause
