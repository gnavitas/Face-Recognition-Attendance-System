# Face Recognition Attendance System

A modern attendance system that uses facial recognition technology to automate the process of taking attendance. This system provides an efficient and contactless way to track attendance in various settings such as schools, offices, or organizations.

## Features

- Real-time face detection and recognition
- User-friendly graphical interface
- Automated attendance tracking
- Database integration for storing attendance records
- Training interface for adding new faces
- Logging system for tracking operations
- Sound notifications
- Configurable settings

## System Requirements

- Windows 10 or later
- Python 3.8 or later
- XAMPP (for database)
- Webcam
- Minimum 4GB RAM
- 1GB free disk space

## Installation

1. **Clone or download the repository**
   ```bash
   git clone [repository-url]
   cd FaceRecognitionAttendanceSystem
   ```

2. **Set up Python Virtual Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Required Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Install XAMPP
   - Start Apache and MySQL services
   - Import the provided `iassist.sql` file into phpMyAdmin
   - Configure database connection in `config.ini`

5. **Configuration**
   - Open `config.ini`
   - Update the database credentials if needed
   - Adjust other settings as required

## Usage

1. **Start the System**
   - Run `server.py` from table CSC_Server to start server then run `as.py` from folder FaceRecognitionAttendanceSystem. 
   - Or use the executable if provided

2. **First-time Setup**
   - Add users through the training interface (from admin)
   - Take multiple photos per person for better recognition
   - Train the model with collected data

3. **Taking Attendance**
   - Position the camera to capture faces clearly
   - The system will automatically detect and recognize faces
   - Attendance is recorded in real-time
   - Sound notifications indicate successful recognition

4. **Viewing Records**
   - Access attendance records through the database.


## Project Structure

- `src/`: Core source code files
- `ui/`: User interface components
- `trainer/`: Face recognition training modules
- `datasets/`: Storage for face data
- `images/`: System images and icons
- `logs/`: System logs
- `sound/`: Notification sound files
- `interfaces/`: Interface definitions
- `config.ini`: System configuration file

## Troubleshooting

1. **Camera Issues**
   - Ensure webcam is properly connected
   - Check camera permissions
   - Verify no other application is using the camera

2. **Recognition Problems**
   - Ensure proper lighting
   - Retrain model with more face data
   - Check face detection logs

3. **Database Connection**
   - Verify XAMPP services are running
   - Check database credentials in config.ini
   - Ensure database schema is properly imported

## Logs

The system maintains several log files:
- `face_detection.log`: Face detection events
- `face_recognition.log`: Recognition events
- `model_initialization.log`: Model loading and initialization
- `database.log`: Database operations

## Support

For technical support or bug reports, please:
1. Check the log files
2. Review troubleshooting steps
3. Contact system administrator

## Security Notes

- Keep the database credentials secure
- Regularly backup the database
- Update dependencies as needed
- Monitor system logs for unusual activity

## License

[Specify License Information]

---

Last Updated: [Current Date] 



# For settings
If you want to change the ip address/port number of server OR database configuration, you can open the config.ini file with notepad/vscode/etc. to edit the settings. Make sure only modify the value but not key/name/format.

eg. Before modify...

[db]
host = localhost
port = 3306 
user = root
password =
database = iassist

[server]
ip = localhost
port = 5000

eg. After modify...

[db]
host = localhost
port = 3306 
user = root
password = 
database = iassist 

[server]
ip = localhost
port = 5200
