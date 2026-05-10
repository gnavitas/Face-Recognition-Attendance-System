import subprocess
import sys
import os
from tkinter import *
from tkinter import ttk

def run_server():
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CSC_Server", "server.py")
    subprocess.Popen([sys.executable, server_path])

def run_face_recognition():
    face_recognition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FaceRecognitionAttendanceSystem", "as.py")
    subprocess.Popen([sys.executable, face_recognition_path])

def main():
    root = Tk()
    root.title("System Launcher")
    root.geometry("300x150")
    
    # Create a style
    style = ttk.Style()
    style.configure('TButton', padding=5, font=('Arial', 10))
    
    # Create buttons
    server_button = ttk.Button(root, text="Launch Server", command=run_server)
    server_button.pack(pady=20)
    
    face_recognition_button = ttk.Button(root, text="Launch Face Recognition", command=run_face_recognition)
    face_recognition_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main() 