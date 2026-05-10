#! /usr/bin/python3
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(os.path.abspath(os.getcwd()))
# os.chdir('/home/pi/Documents/MaskedFaceRecognitionSystem1')

from interfaces import database
from interfaces import connectionServer
import sys
import logging

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import requests

from interfaces.adminScreen import adminLoginWindow, adminWindow, adminSyncWindow, adminSettings
from interfaces.mainWindow import mainWindow
from interfaces.regWindow import regWindow
from interfaces.modWindow import modWindow



from interfaces import global_initialize as global_ini


class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("ui/start.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        
        # Initialize timer for real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every 1000 ms (1 second)
        
        # Initial update
        self.update_datetime()
        
        if not os.path.exists('datasets'):
            os.makedirs('datasets')
            
        if not os.listdir("datasets"): 
            self.breakInButton.setEnabled(False)
        else:
            self.breakInButton.setEnabled(True)
        self.breakInButton.clicked.connect(self.syncSlot)
        self.logButton.clicked.connect(self.runSlot2)
        
        self._new_window = None
        self._new_window2 = None
        self._new_window3 = None
    
    # 1: main window (Face Detection Attendance)
    def syncSlot(self):
        response = requests.get(global_ini.checksum_url)
        server_sum = int(response.text)

        client_sum = len(os.listdir('datasets'))

        if server_sum == client_sum:
            print('Equal')
            self.runSlot()
            
        else:
            print('Not Equal')
            msg = QMessageBox()
            msg.setWindowTitle("DATABASE NOT SYNC")
            msg.setText("System detects that local database is not sync with the database stored in Server")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ignore)
            msg.setDefaultButton(QMessageBox.Ignore)
            buttonY = msg.button(QMessageBox.Ignore)
            buttonY.setText('Launch anyway')
            msg.setInformativeText("If you launch the application now, you may not able to detect some newly registered user. Contact Admin to perform synchronization.")
            
            x = msg.exec()
            
            if x == QMessageBox.Ignore:
                print("Continue Launching")
                self.runSlot()
                     
            else:
                print("Abort launching")
    
    
    def runSlot(self):
        self.close() 
        self.outputWindow_()
        
    def outputWindow_(self):
        self._new_window = mainWindow()
        self._new_window.show()
        self._new_window.exitButton.clicked.connect(self.backMenu)
        
    def backMenu(self):
        self.close()
        self._new_window = Window()
        self._new_window.show()
        
    # 2: admin Login screen
    def runSlot2(self):
        self.close()
        self.outputWindow2_()
    
    def outputWindow2_(self):
        self._new_window = adminLoginWindow()
        self._new_window.show()
        self._new_window.passwordField.setEchoMode(QLineEdit.Password)
        self._new_window.signButton.clicked.connect(self.loginfunction)
        self._new_window.backButton.clicked.connect(self.backMenu)


    def loginfunction(self):
        username = self._new_window.usernameField.text()
        password = self._new_window.passwordField.text()
        
        if len(username) == 0 or len(password) == 0:
            self._new_window.error.setText("Please input all required fields")
            return
        
        try:
            # Use parameterized query to prevent SQL injection
            query = 'SELECT password FROM admin WHERE username = %s'
            global_ini.mycursor.execute(query, (username,))
            
            # Fetch the result safely
            result = global_ini.mycursor.fetchone()
            
            # Check if any result was found
            if result is None:
                self._new_window.error.setText("Invalid username")
                self._new_window.usernameField.clear()
                self._new_window.passwordField.clear()
                return
            
            # Safely access the password
            result_pass = result.get('password')
            
            if result_pass == password:
                self._new_window.error.setText("Login Successfully")
                self.runSlot3()
            else:
                self._new_window.error.setText("Invalid password")
                self._new_window.passwordField.clear()
        
        except Exception as e:
            logging.error(f"Login error: {e}")
            self._new_window.error.setText("Login error. Please try again.")
            self._new_window.usernameField.clear()
            self._new_window.passwordField.clear()

    # 3: admin screen  
    def runSlot3(self):
        self.close()
        self.outputWindow3_()
    
    def outputWindow3_(self):
        self._new_window = adminWindow()
        self._new_window.show()
        self._new_window.regButton.clicked.connect(self.runSlot4)
        self._new_window.modButton.clicked.connect(self.runSlot5)
        self._new_window.syncButton.clicked.connect(self.runSlot6)
        self._new_window.settingsButton.clicked.connect(self.runSlot7)
        self._new_window.logout.clicked.connect(self.backMenu)
    
    # 4: registration screen    
    def runSlot4(self):
        self.close()
        self.outputWindow4_()
    
    def outputWindow4_(self):
        self._new_window = regWindow()
        self._new_window.show()
        self._new_window.BackButton.clicked.connect(self.runSlot3)
    
    # 5: modifying screen
    def runSlot5(self):
        self.close()
        self.outputWindow5_()
    
    def outputWindow5_(self):
        self._new_window = modWindow()
        self._new_window.show()
        self._new_window.BackButton.clicked.connect(self.runSlot3)
        
    # 6: Sync Server Database
    def runSlot6(self):
        msg = QMessageBox()
        msg.setWindowTitle("Sync Server Database")
        msg.setText("Are you sure you want to sync Server Database?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        buttonY = msg.button(QMessageBox.Ignore)
        
        x = msg.exec()
            
        if x == QMessageBox.Yes:
            self.outputWindow6_()
            
    
    def outputWindow6_(self):
        self._new_window2 = adminSyncWindow()
        self._new_window2.show()        

    # 7: settings screen
    def runSlot7(self):
        self.outputWindow7_()
    
    def outputWindow7_(self):
        self._new_window3 = adminSettings()
        self._new_window3.show()
        self._new_window3.cancel_button.clicked.connect(self._new_window3.close)

    def update_datetime(self):
        # Get current date and time
        current_datetime = QDateTime.currentDateTime()
        
        # Format date with full details
        date_str = current_datetime.toString("dddd, dd MMMM yyyy")
        time_str = current_datetime.toString("hh:mm:ss")
        
        # Construct HTML with the date and time, including DS-DIGI font
        date_html = f'<html><head><style>@font-face {{ font-family: "DS-DIGI"; src: url("C:/xampp/htdocs/Development/FaceRecognitionAttendanceSystem/fonts/DS-DIGI.TTF") format("truetype"); }}</style></head><body><p align="center"><span style="font-family: \'DS-DIGI\', monospace; ">{date_str}</span></p></body></html>'
        time_html = f'<html><head><style>@font-face {{ font-family: "DS-DIGI"; src: url("C:/xampp/htdocs/Development/FaceRecognitionAttendanceSystem/fonts/DS-DIGI.TTF") format("truetype"); }}</style></head><body><p align="center"><span style="font-family: \'DS-DIGI\', monospace; ">{time_str}</span></p></body></html>'
        
        # Directly set the HTML text
        self.title.setText(date_html)
        self.title_2.setText(time_html)


def main():
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())

if __name__ == '__main__':
    main()