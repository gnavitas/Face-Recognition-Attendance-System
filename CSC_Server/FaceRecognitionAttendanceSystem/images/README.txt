# LINUX SYSTEM #
Need to 'sudo apt-get install mpg321

# Facenet | Facenet512 | VGG-Face | DeepFace | ArcFace | SFace


'Facenet': Google researchers: (99.20%) [128 dimensions]
'Facenet512': Google researchers: (99.65%) [512 dimensions]
'VGG-Face': University of Oxford researchers: (98.78%)
'DeepFace': Facebook researchers: (97.53%)
'ArcFace': Imperial College London and InsightFace researchers: (99.40%)
'SFace': Sigmoid-Constrained Hypersphere Loss for Robust Face Recognition (99.40%)
#https://github.com/opencv/opencv_zoo/tree/master/models/face_recognition_sface
#https://github.com/zhongyy/SFace


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

