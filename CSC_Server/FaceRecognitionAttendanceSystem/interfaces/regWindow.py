from interfaces import global_initialize as global_ini
import mysql.connector
import cv2
import os
import pandas as pd
import qimage2ndarray
import time
import requests
import base64
import json
from tqdm import tqdm
import re
import shutil
import numpy as np
from src.commons import functions
from src.detectors import FaceDetector

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi


# ----------------------------------Registration Windows-----------------------------------
class regWindow(QDialog):
    def __init__(self):
        super(regWindow, self).__init__()
        loadUi("ui/reg.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        timer = QTimer(self)
        timer.timeout.connect(self.displayPre)
        timer.start(1)
        # Set consistent x-coordinate for messlabel
        self.messlabel.setGeometry(-325, 480, 1161, 71)
        self.messlabel.setAlignment(Qt.AlignCenter)
        self.messlabel.setText("Check.")
        self.RegButton.clicked.connect(self.datasets)
        self.CaptureButton.clicked.connect(self.capture)
        self.TrainButton.clicked.connect(self.training)
        self.progressBar.setVisible(False)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        
        # Make userIC uneditable and add event listener
        self.userIC.setReadOnly(True)
        self.userID.textChanged.connect(self.fetch_user_details)
        
        # Initialize validation state
        self.validation_state = {
            'no_mask': False,
            'smile': False,
            'eyes_closed': False,
            'no_glasses': False
        }
        
        # Define validation instructions - reordered to make mask first
        self.validation_instructions = [
            "Please remove your mask",
            "Please smile for the camera",
            "Please close your eyes",
            "Please remove your eyeglasses"
        ]
        
        # Load face cascade for eye detection
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def fetch_user_details(self):
        user_id = self.userID.text()
        if not user_id:
            return

        # Define sql and val outside the try block
        sql = "SELECT FirstName, LastName FROM emppersonal WHERE EmpNo = %s"
        val = (user_id,)

        try:
            # Verify database connection
            if not hasattr(global_ini, 'mycursor') or not global_ini.mycursor:
                print("Database cursor is not initialized")
                return

            # Verify and reset database connection
            try:
                # Consume any unread results
                while global_ini.mycursor.nextset():
                    pass
                
                # Reset cursor
                global_ini.mycursor.reset()
                
                # Test connection with a simple query
                global_ini.mycursor.execute("SELECT 1")
                global_ini.mycursor.fetchone()  # Consume the result
            except Exception as conn_err:
                print(f"Database connection error: {conn_err}")
                return
            
            # Execute query and check results
            global_ini.mycursor.execute(sql, val)
            result = global_ini.mycursor.fetchone()
            
            # Debug print to understand query results
            print(f"Query result for EmpNo {user_id}: {result}")
            
            if result:
                # Separate FirstName and LastName
                # Assuming result is a tuple or dictionary from buffered cursor
                first_name = result[0] if isinstance(result, tuple) else result.get('FirstName', '')
                last_name = result[1] if isinstance(result, tuple) else result.get('LastName', '')
                
                # Populate userName with FirstName
                self.userName.setText(first_name)
                
                # Populate userIC with LastName
                self.userIC.setText(last_name)
            else:
                # Clear fields if no match found
                self.userName.clear()
                self.userIC.clear()
                print(f"No user found with EmpNo: {user_id}")
        
        except mysql.connector.Error as mysql_err:
            # MySQL-specific error handling
            print(f"MySQL Error: {mysql_err}")
            print(f"Error Code: {mysql_err.errno}")
            print(f"SQL State: {mysql_err.sqlstate}")
            print(f"Error Message: {mysql_err.msg}")
            print(f"SQL Query: {sql}")
            print(f"Query Parameters: {val}")
            
            # Clear fields on error
            self.userName.clear()
            self.userIC.clear()
        
        except Exception as e:
            # General error handling
            print(f"Unexpected error fetching user details: {e}")
            print(f"SQL Query: {sql}")
            print(f"Query Parameters: {val}")
            
            # Clear fields on error
            self.userName.clear()
            self.userIC.clear()

    # Left-hand side video frame

    
    def displayPre(self):

        ret, img = global_ini.cap.read()
        img = cv2.flip(img,1)

        try:
            #faces store list of detected_face and region pair
            faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, img, align = True)
        except: #to avoid exception if no face detected
            faces = []

        for face, (x, y, w, h) in faces:
            if w > 130: #discard small detected faces

                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2) #draw rectangle to main image

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(img)
        self.videolabel.setPixmap(QPixmap.fromImage(image))
        
    
    def datasets(self):
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(int(global_ini.photo_num))
        self.progressBar.setValue(0)
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 480, 1161, 71)

        user_id = self.userID.text()
        user_name = self.userName.text()
        user_ic = self.userIC.text()

        # Consistency to keep all name upper case
        user_name = user_name.upper()
        
        directory = str(user_id)
        expath = os.path.join(global_ini.parent_dir, directory)
        
        # Remove webhook code
        try:
            os.makedirs(expath)
        except OSError as error:
            QMessageBox.critical(None, "Error", str(error))
            return

        if len(str(user_name)) == 0 or len(str(user_id)) == 0  or len(str(user_ic)) == 0:
            self.messlabel.setText("Please fill all the information")
        # -------------------------------- Maybe Need Modify ----------------------------    
        elif os.path.isdir(expath) and os.listdir(expath):  # Check if directory exists and is not empty
            self.messlabel.setText(f"User ID {user_id} already existed.")
        # --------------------------------------------------------------------------------
        elif not len(str(user_id)) == 8:
            self.messlabel.setText("User ID must be exactly 8 characters long")
        else:
            # Modify SQL to use userIC (which now contains full name) for LastName
            sql = "INSERT INTO emppersonal (EmpNo, FirstName, LastName) VALUES (%s, %s, %s)"
            val = (user_id, user_name, user_ic)

            try:
                global_ini.mycursor.execute(sql, val)
            except mysql.connector.IntegrityError as e:
                if e.errno == 1062:  
                    # Do nothing if the user already exists in the database
                    pass
            except Exception as e:
                QMessageBox.critical(None, "Error", str(repr(e)+"<br><br> Contact admin to resolve the issue"))
                return

            global_ini.mydb.commit()

            self.messlabel.setText("Please process to capture image...")
            self.RegButton.setEnabled(False)
            self.CaptureButton.setEnabled(True)
            self.BackButton.setEnabled(False)

    def check_smile(self, face_img):
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        smiles = self.smile_cascade.detectMultiScale(gray, 1.8, 20)
        return len(smiles) > 0

    def check_glasses(self, face_img):
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # If no eyes are detected, it's likely due to glasses
        if len(eyes) == 0:
            return True  # Glasses detected
            
        # Check if eyes are partially visible (common with glasses)
        for (ex, ey, ew, eh) in eyes:
            eye_region = gray[ey:ey+eh, ex:ex+ew]
            
            # Calculate eye region statistics
            mean_intensity = np.mean(eye_region)
            std_intensity = np.std(eye_region)
            
            # Check for dark regions (common with sunglasses)
            dark_pixels = np.sum(eye_region < 50)
            dark_ratio = dark_pixels / (ew * eh)
            
            # If the eye region has low contrast, is too dark, or has a high ratio of dark pixels
            if (mean_intensity < 50 or std_intensity < 20 or dark_ratio > 0.3):
                return True
                
        return False  # No glasses detected

    def check_eyes_closed(self, face_img):
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Try multiple detection parameters for better accuracy
        eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # If no eyes are detected, they are likely closed
        if len(eyes) == 0:
            return True
            
        # Check each detected eye
        for (ex, ey, ew, eh) in eyes:
            eye_region = gray[ey:ey+eh, ex:ex+ew]
            
            # Calculate eye region statistics
            mean_intensity = np.mean(eye_region)
            std_intensity = np.std(eye_region)
            
            # If the eye region is too dark or has low contrast, it might be closed
            if mean_intensity < 30 or std_intensity < 10:
                return True
                
        return False  # Eyes are open

    def check_mask(self, face_img):
        # Convert to grayscale
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Detect face
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return False
            
        # Get the first face
        (x, y, w, h) = faces[0]
        
        # Calculate the lower half of the face
        lower_face = face_img[int(y + h/2):y + h, x:x + w]
        
        # Convert to grayscale
        lower_face_gray = cv2.cvtColor(lower_face, cv2.COLOR_BGR2GRAY)
        
        # Calculate the average intensity of the lower face
        avg_intensity = np.mean(lower_face_gray)
        
        # If the average intensity is very low or very high, it might indicate a mask
        # This is a simple heuristic and might need adjustment
        if avg_intensity < 50 or avg_intensity > 200:
            return False
            
        return True

    def check_initial_conditions(self, face_img):
        """Check if glasses or mask are present before starting validation"""
        has_glasses = self.check_glasses(face_img)
        has_mask = not self.check_mask(face_img)  # Invert the mask check since we want to know if mask is present
        
        # Only update validation state if we're sure the items are not present
        if not has_glasses:
            self.validation_state['no_glasses'] = True
        if not has_mask:
            self.validation_state['no_mask'] = True
            
        return has_glasses, has_mask

    def validate_capture(self, img, count):
        try:
            faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, img, align = True)
            if len(faces) != 1:
                return False, "Please ensure only one face is visible"
                
            face, (x, y, w, h) = faces[0]
            face_img = img[y:y+h, x:x+w]
            
            # Check initial conditions for glasses and mask
            has_glasses, has_mask = self.check_initial_conditions(face_img)
            
            if count == 0:  # Mask validation (now first)
                if has_mask:
                    # If mask is detected, require it to be removed
                    return False, "Please remove your mask"
                else:
                    # If no mask is detected, mark as passed
                    self.validation_state['no_mask'] = True
                    return True, "No mask detected"
                
            elif count == 1:  # Smile validation
                if self.check_smile(face_img):
                    self.validation_state['smile'] = True
                    return True, "Smile detected"
                return False, "Please smile for the camera"
                
            elif count == 2:  # Eyes closed validation
                # Add a small delay to ensure eyes are properly closed
                time.sleep(0.5)
                if self.check_eyes_closed(face_img):
                    self.validation_state['eyes_closed'] = True
                    return True, "Eyes closed detected"
                return False, "Please close your eyes"
                
            elif count == 3:  # No glasses validation
                # Add a small delay to ensure proper detection
                time.sleep(0.5)
                if has_glasses:
                    # If glasses are detected, require them to be removed
                    return False, "Please remove your glasses"
                else:
                    # If no glasses are detected, mark as passed
                    self.validation_state['no_glasses'] = True
                    return True, "No glasses detected"
            
            # Default case for any other count
            return True, "Proceeding with capture"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def capture(self):
        self.progressBar.setVisible(True)
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 480, 1161, 71)

        user_id = (str(self.userID.text()))
        user_name = (str(self.userName.text()))
        user_name = user_name.upper()

        path = os.path.join(global_ini.parent_dir, str(user_id))
        
        # Remove existing directory and its contents if it exists
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Could not remove existing directory: {str(e)}")
                return

        # Create a new directory
        os.mkdir(path)
        
        count = 0
        last_capture_time = 0  # Track last capture time

        while count < int(global_ini.photo_num):
            current_time = time.time()
            
            # Read and display the current frame
            ret, img = global_ini.cap.read()
            if not ret:
                continue
                
            img = cv2.flip(img,1)
            
            # Create a copy of the image for display with rectangle
            display_img = img.copy()
            
            # Update the display with rectangle
            try:
                faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, display_img, align = True)
                for face, (x, y, w, h) in faces:
                    if w > 130:  # discard small detected faces
                        cv2.rectangle(display_img, (x,y), (x+w,y+h), (255,0,0), 2)
            except:
                pass
                
            # Convert and display the image with rectangle
            img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
            image = qimage2ndarray.array2qimage(img_rgb)
            self.videolabel.setPixmap(QPixmap.fromImage(image))
            
            # Display validation instruction
            if count < len(self.validation_instructions):
                self.messlabel.setText(f"Capture {count + 1}: {self.validation_instructions[count]}")
            else:
                self.messlabel.setText(f"Capture {count + 1}: Please maintain a neutral expression")
            
            # Only process capture if 1 second has passed since last capture
            if current_time - last_capture_time < 1.0:
                QApplication.processEvents()  # Keep the UI responsive
                continue
                
            try:
                faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, img, align = True)
            except:
                faces = []
                
            if len(faces) == 0:
                QApplication.processEvents()  # Keep the UI responsive
                continue  # Skip if no face detected
            
            elif len(faces) == 1:
                # Validate the capture
                is_valid, validation_message = self.validate_capture(img, count)
                if not is_valid:
                    self.messlabel.setText(validation_message)
                    QApplication.processEvents()
                    continue
                    
                for face, (x, y, w, h) in faces:
                    if w > 130:  # discard small detected faces
                        # Save the original image without rectangle
                        cv2.imwrite(path + '/' + str(user_name) + "-" + str(count+1) + ".jpg", img)
                        
                        # Send image to server
                        image_file = path + '/' + str(user_name) + "-" + str(count+1) + ".jpg"
                        
                        with open(image_file, 'rb') as f:
                            img_bytes = f.read()
                        img_b64 = base64.b64encode(img_bytes).decode("utf8")
                        headers = {'content-type': 'application/json', 'Accept':'text/plain'}
                        payload = json.dumps({'image':img_b64, 'username':user_name, 'userid':user_id, 'count':count, 'modify':False})
                        response = requests.post(global_ini.reg_url, data=payload, headers=headers)
                        print(response.text)
                        
                        count += 1
                        self.progressBar.setValue(count)
                        last_capture_time = current_time  # Update last capture time
                        break
            
            QApplication.processEvents()  # Keep the UI responsive
            
        self.messlabel.setText("You Had Successfully Register...")
        self.RegButton.setEnabled(True)
        self.CaptureButton.setEnabled(False)
        self.TrainButton.setEnabled(True)
        self.userID.clear()
        self.userName.clear()
        self.userIC.clear()
        
    def training(self):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 480, 1161, 71)
        
        db_path="datasets"

        def findEmbeddings():
            #find embeddings for employee list
            tic = time.time()
            
            #-----------------------
            pbar = tqdm(range(0, len(employees)), desc='Finding embeddings')
            self.progressBar.setMaximum(len(employees))
            self.progressBar.setVisible(True)
            embeddings = []
            #for employee in employees:
            for index in pbar:
                self.progressBar.setValue(index)
                
                employee = employees[index]
                pbar.set_description("Finding embedding for %s" % (employee.split("/")[-1]))
                
                embedding = []
                #preprocess_face returns single face. this is expected for source images in db.
                img = functions.preprocess_face(img = employee, target_size = (global_ini.input_shape_y, global_ini.input_shape_x), enforce_detection = False, detector_backend = global_ini.detector_backend)
                img_representation = global_ini.model.predict(img)[0,:]

                embedding.append(employee)
                embedding.append(img_representation)
                embeddings.append(embedding)

            self.progressBar.setValue(index+1)
            
            df = pd.DataFrame(embeddings, columns = ['employee', 'embedding'])
            df['distance_metric'] = global_ini.distance_metric

            toc = time.time()

            print("Embeddings found for given data set in ", toc-tic," seconds")
            
            # print(type(embeddings)) # Embedding 是一个list，一张image一个位，# print(embeddings) #jh

            # jh - save embeddings to prevent training everytime
            df.to_pickle("trainer/face_embeddings.pkl")


        employees = []
        #check passed db folder exists
        if os.path.isdir(db_path) == True:
            for r, d, f in os.walk(db_path): # r=root, d=directories, f = files
                for file in f:
                    if ('.jpg' in file):
                        #exact_path = os.path.join(r, file)
                        exact_path = r + "/" + file
                        #print(exact_path)
                        employees.append(exact_path)        

        if len(employees) == 0:
            print("WARNING: There is no image in this path ( ", db_path,") . Training will not be performed.")
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)
            self.messlabel.setText("No Account Registered...")

        if len(employees) > 0:
            findEmbeddings()
            self.messlabel.setText("The Training Process Had Done...")
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)

       
    def closeEvent(self, event):
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 480, 1161, 71)
        if self.CaptureButton.isEnabled():
            close = QMessageBox()
            close.setWindowTitle("Action Required!")
            close.setIcon(QMessageBox.Warning)
            close.setText("Please Press On The <strong>Capture Image</strong> Button...")
            close.setStandardButtons(QMessageBox.Ok)
            close = close.exec()

            if close == QMessageBox.Ok:
                event.ignore() 

        elif self.TrainButton.isEnabled():
            close = QMessageBox()
            close.setWindowTitle("Action Required!")
            close.setIcon(QMessageBox.Warning)
            close.setText("Please Press On The <strong>Perform Training</strong> Button...")
            close.setStandardButtons(QMessageBox.Ok)
            close = close.exec()

            if close == QMessageBox.Ok:
                event.ignore()

        else:
            event.accept()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()