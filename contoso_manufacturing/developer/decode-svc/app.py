import cv2
import time
import os
import requests

# Your RTSP stream URL
rtsp_url = os.environ.get("rtsp_url", "rtsp://10.0.0.1:8554")

# Folder where captured frames will be saved
save_path = os.environ.get("save_path", "./frames")

# Folder where captured frames will be saved
inference_url = os.environ.get("inference_url", "http://10.0.0.21:8081")


def capture_frame(rtsp_url, save_path, interval=30):
    """
    Captures a frame from an RTSP stream at the specified interval of seconds.

    Args:
    - rtsp_url (str): URL of the RTSP stream.
    - save_path (str): Path where frames will be saved.
    - interval (int): Time interval in seconds between capturing frames.
    """
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not retrieve frame from stream.")
                break

            # Generate a filename based on the current time
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = os.path.join(save_path, f"frame-{timestamp}.jpg")

            # Save the frame to the file system
            cv2.imwrite(filename, frame)
            print(f"Frame saved: {filename}")

            # Here you can call the function to send the frame to your inference API
            send_frame_to_inference_api(filename)

            # Wait for the specified interval before capturing the next frame
            time.sleep(interval)
    
    finally:
        cap.release()

def send_frame_to_inference_api(image_path):
    """
    Sends the frame to another REST API for inference.

    Args:
    - image_path (str): Path to the image file to be sent.
    """
    url = 'http://your_inference_api_endpoint'  # Change this to your inference API endpoint
    files = {'image': open(image_path, 'rb')}
    response = requests.post(url, files=files)
    
    # Handle the response
    if response.status_code == 200:
        print("Inference successful.")
        # Here you can handle the inference response as needed
    else:
        print("Error in inference request.")



# Make sure the destination folder exists
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Capture frames from the RTSP stream
capture_frame(rtsp_url, save_path, interval=30)
