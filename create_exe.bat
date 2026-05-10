@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Creating executable...
pyinstaller --onefile --name "FaceRecognitionSystem" --add-data "CSC_Server;CSC_Server" --add-data "FaceRecognitionAttendanceSystem;FaceRecognitionAttendanceSystem" start_system.py

echo.
echo Executable created successfully!
echo You can find it in the 'dist' folder.

echo Copying required directories...
xcopy /E /I /Y CSC_Server dist\CSC_Server
xcopy /E /I /Y FaceRecognitionAttendanceSystem dist\FaceRecognitionAttendanceSystem

echo.
echo All files copied successfully!
pause 