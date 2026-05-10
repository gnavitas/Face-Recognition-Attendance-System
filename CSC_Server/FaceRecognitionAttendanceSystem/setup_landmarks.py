import os
import urllib.request
import sys

def download_and_extract_landmarks():
    # URL for the facial landmarks predictor (using a GitHub mirror)
    url = "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat"
    output_path = "shape_predictor_68_face_landmarks.dat"
    
    print("Downloading facial landmarks predictor...")
    try:
        # Download the file
        print(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, output_path)
        print("Download complete.")
        
        print(f"Successfully downloaded {output_path}")
        print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    download_and_extract_landmarks() 