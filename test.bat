cd %~dp0

call venv\Scripts\activate.bat

python -m unittest discover -s ./tests

echo "All complate!!! plass any key..."
pause

deactivate
