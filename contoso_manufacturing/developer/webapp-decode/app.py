from flask import Flask, render_template, Response, request
import os
import cv2
import json
import numpy as np
from yolov8 import YOLOv8OVMS
from welding import WeldPorosity
from pose_estimator import PoseEstimator

app = Flask(__name__)

camera = None  # Initialized later based on the selected video
latest_choice_detector = None # Global variable to keep track of the latest choice of the user
ovms_url = "192.168.0.4:31640"
frame_number = 0
skip_mod = 2 # Define the modulus to skip frames

# Init the config.file.json
with open('config_file.json') as config_file:
    config = json.load(config_file)

def init_yolo_detector():
    model_config = config["yolov8n"]
    color_palette = np.random.uniform(0, 255, size=(len(model_config['class_names']), 3))
    return YOLOv8OVMS(
        rtsp_url=model_config['rtsp_url'],
        class_names=model_config['class_names'],
        input_shape=model_config['input_shape'],
        color_palette=color_palette,
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="yolov8n", 
        ovms_url=ovms_url, 
        save_img_loc=False,
        verbose=False,
        skip_rate=10
    )

def init_yolo_safety_detector():
    model_config = config["safety-yolo8"]
    color_palette = np.random.uniform(0, 255, size=(len(model_config['class_names']), 3))
    return YOLOv8OVMS(
        rtsp_url=model_config['rtsp_url'],
        class_names=model_config['class_names'],
        input_shape=model_config['input_shape'],
        color_palette=color_palette,
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="safety-yolo8", 
        ovms_url=ovms_url, 
        save_img_loc=False,
        verbose=False,
        skip_rate=2
    )

def init_welding_detector():
    model_config = config["weld-porosity-detection"]
    color_palette = np.random.uniform(0, 255, size=(len(model_config['class_names']), 3))
    return WeldPorosity(
        rtsp_url=model_config['rtsp_url'],
        class_names=model_config['class_names'],
        input_shape=model_config['input_shape'],
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="weld-porosity-detection", 
        ovms_url=ovms_url, 
        verbose=False,
        skip_rate=10
    )

def init_pose_estimator():
    model_config = config["human-pose-estimation"]
    return PoseEstimator(
        rtsp_url=model_config['rtsp_url'],
        class_names=model_config['class_names'],
        input_shape=model_config['input_shape'],
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="human-pose-estimation",
        ovms_url="192.168.0.4:31640",
        skip_rate=2
    )

def gen_frames(video_name): 
    global latest_choice_detector  

    if(latest_choice_detector is None or latest_choice_detector.model_name != video_name):
        # Call the destructor first
        del latest_choice_detector
        if video_name == "yolov8n":
            latest_choice_detector = init_yolo_detector()
        elif video_name == "safety-yolo8":
            latest_choice_detector = init_yolo_safety_detector()
        elif video_name == "welding":
            latest_choice_detector = init_welding_detector()
        elif video_name == "human-pose-estimation":
              latest_choice_detector = init_pose_estimator()

    while video_name != "":
        processed_frame = latest_choice_detector.run()
        if processed_frame is not None:
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    video_name = request.args.get('video')
    if video_name is None:
        return Response('Video name parameter is missing', status=400)

    return Response(gen_frames(video_name), mimetype='multipart/x-mixed-replace; boundary=frame')  # stream the video frames

@app.route('/')
def index():
    # Get the paths to to the SVG files and the load the content
    contoso_path = os.path.join(app.root_path, 'static/images', 'contoso.svg')
    with open(contoso_path, 'r') as f:
        contoso = f.read()

    site_enterprise_path = os.path.join(app.root_path, 'static/images', 'site_enterprise.svg')
    with open(site_enterprise_path, 'r') as f:
        site_enterprise = f.read()

    site_path = os.path.join(app.root_path, 'static/images', 'site.svg') 
    with open(site_path, 'r') as f:
        site = f.read()

    enterprise_path = os.path.join(app.root_path, 'static/images', 'enterprise.svg')
    with open(enterprise_path, 'r') as f:
        enterprise = f.read()

    return render_template('index.html', contoso=contoso, site_enterprise=site_enterprise, site=site, enterprise=enterprise)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Release the video capture object and close all windows
camera.release()
cv2.destroyAllWindows()
