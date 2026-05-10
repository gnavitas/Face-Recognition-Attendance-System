# Face Recognition Attendance System

## Overview

A modern Face Recognition Attendance System that uses computer vision and deep learning models to automatically identify users and log attendance in real time. The system provides a fast, contactless, and automated attendance solution for schools, offices, and organizations.

---

## Technical Stack & Models

### Face Recognition Models

The system supports multiple state-of-the-art facial recognition models for improved accuracy and flexibility:

* **FaceNet**
* **FaceNet512**
* **VGGFace**
* **VGGFace2**
* **ArcFace**

### Technologies Used

* **Python 3.8+**
* **OpenCV (cv2)** – Real-time video capture and image processing
* **dlib** – Face detection and facial landmark extraction
* **face-recognition** – Facial encoding and matching
* **MTCNN** – Face detection
* **MediaPipe** – Face tracking and detection
* **TensorFlow** – Deep learning framework
* **scikit-learn** – Machine learning utilities
* **MySQL (XAMPP)** – Attendance and user database management

---

## Features

### Admin Functions

* Register new users
* Capture facial images for training
* Train and update recognition models
* Configure system settings using `config.ini`
* Manage attendance records and logs

### User Functions

* Automatic face detection and recognition
* Real-time attendance logging
* Contactless attendance process
* Audio feedback for successful recognition

---

## Getting Started

### Run the System

1. Start the server:

```bash
python CSC_Server/server.py
```

2. Start the client application:

```bash
python FaceRecognitionAttendanceSystem/as.py
```

---

## Installation

Install required dependencies:

```bash
pip install -r FaceRecognitionAttendanceSystem/requirements.txt
```

Make sure MySQL/XAMPP is installed and running before starting the system.

---

## Build Executables

You can generate executable files using PyInstaller and the provided `.spec` files:

* `face_recognition_attendance.spec`
* `launcher.spec`

---

## Disclaimer

This project handles biometric data for attendance purposes. Ensure compliance with applicable data privacy and security regulations before deployment.
