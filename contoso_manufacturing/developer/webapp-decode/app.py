from flask import Flask, render_template, Response, request
import os
import cv2
import json
import numpy as np
from yolov8 import YOLOv8OVMS
from welding import WeldPorosity
from pose_estimator import PoseEstimator
from bolt_detection import BoltDetection

app = Flask(__name__)

latest_choice_detector = None # Global variable to keep track of the latest choice of the user
ovms_url = os.environ.get('OVMS_URL', '')
influx_iframe_url = os.environ.get('INFLUX_URL', '')
adx_iframe_url = os.environ.get('ADX_URL', '')

def reload_config():
    """
    Reloads the configuration file.

    Returns:
        dict: The reloaded configuration file.
    """
    print("Reloading configuration...")
    with open('./config/config_file.json') as config_file:
        return json.load(config_file)

def init_yolo_detector():
    """
    Initializes and returns a YOLOv8OVMS object for object detection.

    Returns:
        YOLOv8OVMS: The initialized YOLOv8OVMS object.
    """
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
    """
    Initializes and returns a YOLOv8OVMS object for safety detection.

    Returns:
        YOLOv8OVMS: The initialized YOLOv8OVMS object.

    Raises:
        KeyError: If the required configuration values are missing.
    """
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
    """
    Initializes the welding detector.

    Returns:
        WeldPorosity: An instance of the WeldPorosity class representing the welding detector.
    """
    model_config = config["weld-porosity-detection"]
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
    """
    Initializes the pose estimator with the specified configuration.

    Returns:
        PoseEstimator: The initialized pose estimator object.
    """
    model_config = config["human-pose-estimation"]
    return PoseEstimator(
        rtsp_url=model_config['rtsp_url'],
        class_names=model_config['class_names'],
        input_shape=model_config['input_shape'],
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="human-pose-estimation",
        ovms_url=ovms_url,
        skip_rate=2,
        default_skeleton=model_config['default_skeleton'],
        colors=model_config['colors']
    )

def init_bolt_detector():
    """
    Initializes the welding detector.

    Returns:
        WeldPorosity: An instance of the WeldPorosity class representing the welding detector.
    """
    model_config = config["bolt-detection"]
    return BoltDetection(
        rtsp_url=model_config['rtsp_url'],
        input_shape=model_config['input_shape'],
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="bolt-detection", 
        ovms_url=ovms_url, 
        verbose=False,
        skip_rate=10
    )

@app.route('/show_iframe')
def show_iframe():
    print("show_iframe")
    url = request.args.get('url', 'https://google.com')
    return render_template('index.html', iframe_url=url)

def gen_frames(video_name): 
    """
    Generate frames from a video stream.

    Args:
        video_name (str): The name of the video.

    Yields:
        bytes: The processed frame in JPEG format.

    Returns:
        None
    """
    global latest_choice_detector  

    # Add a check in case of failed intit model
    if 'latest_choice_detector' not in locals() and 'latest_choice_detector' not in globals():
        latest_choice_detector = None

    # Check if the video name is different from the current model name
    if(latest_choice_detector is None or latest_choice_detector.model_name != video_name):
        # Call the destructor first
        del latest_choice_detector

        # Reload configuration for changes with GitOps
        config = reload_config()

        if video_name == "yolov8n":
            latest_choice_detector = init_yolo_detector()
        elif video_name == "safety-yolo8":
            latest_choice_detector = init_yolo_safety_detector()
        elif video_name == "welding":
            latest_choice_detector = init_bolt_detector()
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
    """
    Stream video frames based on the provided video name parameter.

    Returns:
        Response: The response object containing the video frames.
    """
    video_name = request.args.get('video')
    if video_name is None:
        return Response('Video name parameter is missing', status=400)

    return Response(gen_frames(video_name), mimetype='multipart/x-mixed-replace; boundary=frame')  # stream the video frames

@app.route('/')
def index():
    """
    Render the index.html template with the content of SVG files.

    Returns:
        A rendered HTML template with the content of SVG files passed as variables.
    """
    # Get the paths to the SVG files and load the content
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

@app.route('/iframe')
def get_iframe_url():
    """
    Retrieves the URL for the specified iframe name.

    Returns:
        Response: The response object containing the iframe URL.

    Raises:
        Response: If the iframe name parameter is missing or the iframe URL is not set.
    """
    iframe_name = request.args.get('name')
    if iframe_name is None:
        return Response('Iframe name parameter is missing', status=400)
    
    if iframe_name == 'aimetrics':
        iframe_url = influx_iframe_url
    elif iframe_name == 'infra_monitoring':
        iframe_url = adx_iframe_url

    if iframe_url is None:
        return Response(f'Iframe URL for {iframe_name} is not set', status=400)

    return Response(iframe_url, status=200)

if __name__ == '__main__':
    config = reload_config()
    app.run(debug=False, host="0.0.0.0", port=5001)

# Release the video capture object and close all windows
cv2.destroyAllWindows()
