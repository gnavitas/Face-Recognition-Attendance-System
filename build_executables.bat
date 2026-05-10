@echo off
echo Building executables...

echo Installing required packages...
pip install pyinstaller flask flask-mysqldb pillow opencv-python numpy pandas pyqt5 tensorflow deepface mediapipe

echo Building Face Recognition Attendance System...
cd FaceRecognitionAttendanceSystem
pyinstaller --clean --onefile --icon=faceid.ico --add-data "datasets;datasets" --add-data "ui;ui" --add-data "src;src" --add-data "trainer;trainer" --add-data "sound;sound" --add-data "interfaces;interfaces" --add-data "images;images" --add-data "fonts;fonts" --add-data "config.ini;." as.py

echo Copying required folders to dist directory...
xcopy /E /I /Y datasets dist\datasets
xcopy /E /I /Y ui dist\ui
xcopy /E /I /Y src dist\src
xcopy /E /I /Y trainer dist\trainer
xcopy /E /I /Y sound dist\sound
xcopy /E /I /Y interfaces dist\interfaces
xcopy /E /I /Y images dist\images
xcopy /E /I /Y fonts dist\fonts
copy config.ini dist\config.ini

cd ..

echo Building CSC Server...
cd CSC_Server
pyinstaller --clean --onefile server.spec
cd ..

echo Done! Executables are in the dist folders of each project.
echo Press any key to exit...
pause > nul 