@echo off
echo Starting Face Recognition System...
echo.

cd CSC_Server
start /B python server.py
echo Server started successfully.

cd ../FaceRecognitionAttendanceSystem
start python as.py
echo Attendance System started successfully.

echo.
echo Both systems are now running.
echo Press any key to exit this window...
pause > nul 