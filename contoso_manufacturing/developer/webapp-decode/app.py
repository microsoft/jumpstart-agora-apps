from flask import Flask, render_template, Response, request
import os
import cv2

app = Flask(__name__)

# Dictionary mapping video names to their paths
video_paths = {
    'welding': './videos/welding.mp4',
    'pose': './videos/pose.avi',
    'helmet': './videos/helmet.mp4',
}

# Capture video from the mp4 file
camera = None  # Initialized later based on the selected video

# Global variable to keep track of the latest choice of the user
latest_choice = None

def gen_frames(video_name):  
    video_path = video_paths.get(video_name)
    if video_path is None:
        return Response('Video not found', status=404)

    global camera, latest_choice
    if camera is None or camera.get(cv2.CAP_PROP_POS_FRAMES) >= camera.get(cv2.CAP_PROP_FRAME_COUNT) or latest_choice != video_name:
        latest_choice = video_name
        # Create a new video capture object if it's the first request or if the previous video has ended
        camera = cv2.VideoCapture(video_path)

    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)  # reset the video capture object's position to the beginning
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        ## Code for inference
        ## TO-DO

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

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
