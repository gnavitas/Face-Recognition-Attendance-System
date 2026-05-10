import os
import subprocess
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def main():
    base_dir = get_base_dir()
    
    # Start server
    server_dir = os.path.join(base_dir, "CSC_Server")
    if not os.path.exists(server_dir):
        print(f"Error: Could not find CSC_Server directory at {server_dir}")
        return
    
    subprocess.Popen([sys.executable, "server.py"], 
                    cwd=server_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("Server started successfully.")
    
    # Start attendance system
    attendance_dir = os.path.join(base_dir, "FaceRecognitionAttendanceSystem")
    if not os.path.exists(attendance_dir):
        print(f"Error: Could not find FaceRecognitionAttendanceSystem directory at {attendance_dir}")
        return
    
    subprocess.Popen([sys.executable, "as.py"],
                    cwd=attendance_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("Attendance System started successfully.")
    print("\nBoth systems are now running in separate windows.")
    print("You can close this window.")

if __name__ == "__main__":
    main() 