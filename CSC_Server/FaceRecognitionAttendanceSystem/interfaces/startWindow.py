from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from interfaces import global_initialize as global_ini
from interfaces.mainWindow import mainWindow

class startWindow(QDialog):
    def __init__(self):
        super(startWindow, self).__init__()
        
        # Set window flags to make it borderless
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Variables to track mouse movement
        self.dragging = False
        self.offset = None

        loadUi("ui/start.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        
        # Initialize main window
        self.main_window = None
        
        # Connect buttons to set attendance type and show main window
        self.loginButton.clicked.connect(lambda: self.set_attendance_type("Log-in"))
        self.breakInButton.clicked.connect(lambda: self.set_attendance_type("Break-in"))
        self.breakOutButton.clicked.connect(lambda: self.set_attendance_type("Break-out"))
        self.signOutButton.clicked.connect(lambda: self.set_attendance_type("Log-out"))

    def set_attendance_type(self, attendance_type):
        # Set the global attendance type
        global_ini.ATTENDANCE_TYPE = attendance_type
        
        # Create main window if it doesn't exist
        if not self.main_window:
            self.main_window = mainWindow()
        
        # Update the attendance type label with the specific text
        self.main_window.AttendanceTypeLabel.setText(attendance_type)
        self.main_window.Typelabel.setText(attendance_type)
        
        # Show the main window and hide this window
        self.main_window.show()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None