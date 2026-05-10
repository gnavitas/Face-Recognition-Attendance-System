import cv2
import time
import configparser as cp
from src.detectors import FaceDetector
from src import DeepFace
from src.commons import functions, distance as dst
from interfaces import database
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('model_initialization.log'),
        logging.StreamHandler()
    ]
)

# Path to config file
filename = 'config.ini'

# Read config file
inifile = cp.ConfigParser()
inifile.read(filename,'UTF-8')

ip = inifile.get("server","ip")
port = inifile.get("server","port")

db_host = inifile.get("db","host")
db_port = inifile.get("db","port")
db_user = inifile.get("db","user")
db_password = inifile.get("db","password")
db_database = inifile.get("db","database")

mydb = database.mydb
mycursor = database.mydb.cursor  # Access cursor as an attribute, not a method

photo_num = inifile.get("photo","number")

machine_code = inifile.get("machine","machine_code")

# ======= Server URL =============
addr = 'http://{}:{}'.format(ip,port)
reg_url = addr + '/api/register'
sync_url = addr + '/api/dataSync'
del_url = addr + '/api/delete'
checksum_url = addr + '/api/checkSum'
# ================================

parent_dir = "datasets"


cap = cv2.VideoCapture(0)

# cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 640
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 480


try:
    model_name = inifile.get("detection","model")
    detector_backend = inifile.get("detection","detector")
    distance_metric = inifile.get("detection","metric")

    logging.info(f"Initializing with model: {model_name}")
    logging.info(f"Detector backend: {detector_backend}")
    logging.info(f"Distance metric: {distance_metric}")

    # Existing model initialization code
    start = time.time()
    face_detector = FaceDetector.build_model(detector_backend)
    end = time.time()
    logging.info(f"Detector backend {detector_backend} built. Time taken: {end-start} seconds")

    start = time.time()
    try:
        model = DeepFace.build_model(model_name)
        end = time.time()
        logging.info(f"Face Recognition Model {model_name} built. Time taken: {end-start} seconds")
    except Exception as model_error:
        logging.error(f"Failed to build model {model_name}")
        logging.error(traceback.format_exc())
        raise

except Exception as e:
    logging.critical("Critical error during initialization")
    logging.critical(traceback.format_exc())
    raise

#========================== Find Model Input Shape =================================
input_shape = functions.find_input_shape(model)
input_shape_x = input_shape[0]
input_shape_y = input_shape[1]


#===================== Config/Set Threshold for Accuracy ==========================
#tuned thresholds for model and metric pair
threshold = dst.findThreshold(model_name, distance_metric)

# Add default logging checkbox configuration
checkBox_logging = False
# In global_initialize.py
mydb = database.mydb
mycursor = mydb.connection.cursor(buffered=True, dictionary=True)