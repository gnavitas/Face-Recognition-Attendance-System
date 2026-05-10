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


# --------------------------------------Modify Windows--------------------------------------

class modWindow(QDialog):
    def __init__(self):
        super(modWindow, self).__init__()
        loadUi("ui/modify.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        timer = QTimer(self)
        timer.timeout.connect(self.displayPre)
        timer.start(1)
        # Set consistent x-coordinate for messlabel
        self.messlabel.setGeometry(-325, 575, 1161, 71)
        self.messlabel.setAlignment(Qt.AlignCenter)
        self.messlabel.setText("Modify your account")
        self.progressBar.setVisible(False)
        self.ModButton.clicked.connect(self.modify)
        self.RemButton.clicked.connect(self.removeAcc)
        self.TrainButton.clicked.connect(self.training)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        
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

    def check_smile(self, face_img):
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        smiles = self.smile_cascade.detectMultiScale(gray, 1.8, 20)
        return len(smiles) > 0

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

    def displayPre(self):
        ret, img = global_ini.cap.read()
        if not ret:
            return
            
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
        QApplication.processEvents()

    def modify(self):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(int(global_ini.photo_num))
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 575, 1161, 71)
        
        user_id = (str(self.userID.text()))

        path = os.path.join(global_ini.parent_dir, str(user_id))

        if len(str(user_id)) == 0:
            self.progressBar.setVisible(False)
            self.messlabel.setText("Please enter your Employee Number.")

        elif os.path.isdir(path):
            
            user_name = re.sub('-[0-9]', '', os.listdir(path)[0].replace(".jpg", "")) # listdir inside /user_id/ folder and get image name
            
            msg = QMessageBox()
            msg.setWindowTitle("Confirm Modification")
            msg.setText("Are you sure you want to modify "+"<strong>\""+user_name+"\"</strong> ?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)

            x = msg.exec()
            
            if x == QMessageBox.Yes:
                
                shutil.rmtree(path) # remove whole /folder/image.jpg
                os.mkdir(path) # make whole /folder/
                
                self.progressBar.setVisible(True)
                
                count = 0
                last_capture_time = 0  # Track last capture time
                
                while(True):
                    current_time = time.time()
                    
                    if count < len(self.validation_instructions):
                        self.messlabel.setText(f"Capture {count + 1}: {self.validation_instructions[count]}")
                    else:
                        self.messlabel.setText(f"Capture {count + 1}: Please maintain a neutral expression")
                    
                    ret, img = global_ini.cap.read()
                    if not ret:
                        continue
                        
                    img = cv2.flip(img,1)
                    
                    try:
                        faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, img, align = True)
                    except:
                        faces = []
                        
                    if len(faces)==0:
                        self.messlabel.setText("No face detected. Please try again.")
                        QApplication.processEvents()
                        continue
                    
                    elif len(faces)==1:
                        # Only process capture if 1 second has passed since last capture
                        if current_time - last_capture_time < 1.0:
                            QApplication.processEvents()
                            continue
                            
                        # Validate the capture
                        is_valid, validation_message = self.validate_capture(img, count)
                        if not is_valid:
                            self.messlabel.setText(validation_message)
                            QApplication.processEvents()
                            continue
                            
                        for face, (x, y, w, h) in faces:
                            if w > 130: #discard small detected faces                
                                
                                cv2.imwrite(path + '/' + str(user_name) + "-" + str(count+1) + ".jpg", img)
                                
                                # =============== Send image to server =======================
                                image_file = path + '/' + str(user_name) + "-" + str(count+1) + ".jpg"
                                
                                with open(image_file, 'rb') as f:
                                    img_bytes = f.read()
                                img_b64 = base64.b64encode(img_bytes).decode("utf8")
                                headers = {'content-type': 'application/json', 'Accept':'text/plain'}
                                payload = json.dumps({'image':img_b64, 'username':user_name, 'userid':user_id, 'count':count, 'modify':True})
                                response = requests.post(global_ini.reg_url, data=payload, headers=headers)
                                print(response.text)
                                # ============================================================
                                count +=1
                                self.progressBar.setValue(count)
                                last_capture_time = current_time
                                break

                        
                    if count >=int(global_ini.photo_num):
                        self.messlabel.setText("\""+user_name+"\" 's dataset had been successfully modify...")
                        self.TrainButton.setEnabled(True)
                        self.BackButton.setEnabled(False)
                        self.userID.clear()                        
                        break
                    
                    QApplication.processEvents()  # Keep UI responsive
                    
            else:
                self.messlabel.setText("Abort modifying...")
                self.userID.clear()

        elif not len(str(user_id)) == 68:
            self.messlabel.setText("Please try again!")
            self.userID.clear()

        else:
            self.messlabel.setText("Invalid Employee Number!")
            self.userID.clear()
            
    def removeAcc(self):
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 575, 1161, 71)
        user_id = (str(self.userID.text()))
        
        path = os.path.join(global_ini.parent_dir, str(user_id))
        
        if len(str(user_id)) == 0:
            self.messlabel.setText("Insert Employee Number!")
        elif os.path.isdir(path):
            # Check if directory is empty
            dir_contents = os.listdir(path)
            if not dir_contents:
                self.messlabel.setText("No trained pictures found for this User ID.")
                self.userID.clear()
                return
            
            # Extract user name from the first image file
            user_name = re.sub('-[0-9]', '', dir_contents[0].replace(".jpg", "")) # listdir inside /user_id/ folder and get image name
            
            msg = QMessageBox()
            msg.setWindowTitle("Remove Trained Pictures")
            msg.setText("Are you sure you want to remove trained pictures for "+"<strong>\""+user_name+"\"</strong> ?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)

            x = msg.exec()
            
            if x == QMessageBox.Yes:
                # Remove only the files in the directory, not the directory itself
                for filename in dir_contents:
                    file_path = os.path.join(path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f'Failed to delete {file_path}. Reason: {e}')
                
                self.messlabel.setText("Trained pictures for \""+user_name+"\" have been successfully removed.")
                self.TrainButton.setEnabled(True)
                self.BackButton.setEnabled(False)
                self.userID.clear()
            else:
                self.messlabel.setText("Cancel removal...")
                self.userID.clear()                
        elif os.path.isdir(path)!=True:
            self.messlabel.setText("No trained pictures found for this User ID.")
            self.userID.clear()

        elif not len(str(user_id)) == 6:
            self.messlabel.setText("Warning !!! The User ID should be 6 characters... Please Enter Again")
            self.userID.clear()

    def training(self):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 575, 1161, 71)
                
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
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)
            self.messlabel.setText("No Account Registered...")
            print("WARNING: There is no image in this path ( ", db_path,") . Training will not be performed.")

        if len(employees) > 0:
            findEmbeddings()
            self.messlabel.setText("The Training Process Had Done...")
            self.messlabel.move(100, 600)  
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)
        
    def closeEvent(self, event):
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 575, 1161, 71)
        if self.TrainButton.isEnabled():
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

    def update(self):
        # Reset messlabel position
        self.messlabel.setGeometry(-325, 575, 1161, 71)
        user_id = self.userID.text()
        user_name = self.userName.text()
        user_ic = self.userIC.text()

        # Consistency to keep all name upper case
        user_name = user_name.upper()

        if len(str(user_name)) == 0 or len(str(user_id)) == 0  or len(str(user_ic)) == 0:
            self.messlabel.setText("Please fill all the information")
        else:
            sql = "UPDATE emppersonal SET FirstName = %s, IC = %s WHERE EmpNo = %s"
            val = (user_name, user_ic, user_id)
            try:
                global_ini.mycursor.execute(sql, val)
                global_ini.mydb.commit()
                self.messlabel.setText("Successfully Updated")
            except Exception as e:
                QMessageBox.critical(None, "Error", str(repr(e)))
                return

        self.RegButton.setEnabled(False)