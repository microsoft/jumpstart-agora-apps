#!/usr/bin/env python
from importlib import import_module
import os
import cv2
from flask import Flask, render_template, Response, request, url_for, redirect, session
import socket
import secrets
from datetime import datetime
import json
from openvino.inference_engine import IECore
import time
import numpy as np

app = Flask(__name__)

model_xml = './models/person-detection-retail-0013.xml'
model_bin = './models/person-detection-retail-0013.bin'
video_path = 'https://jumpstartprodsg.blob.core.windows.net/video/agora/supermarket.mp4'

# Load OpenVino model
ie = IECore()
net = ie.read_network(model=model_xml, weights=model_bin)
exec_net = ie.load_network(network=net, device_name="GPU")

# Get input and output node names
input_blob = next(iter(net.input_info))
output_blob = next(iter(net.outputs))

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(get_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/people_count')
def people_count():
    global person_count
    return str(person_count)


def get_frame():
    # replace 'video.mp4' with your video file name
    global person_count
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        frame_count = 0
        total_fps = 0   
        # Read frame from video capture
        ret, frame = cap.read()
        start_time = time.time()
        # Break if end of video

        heatmap = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)

        if not ret:
            break

        # Preprocess frame for input to OpenVino model
        input_shape = net.input_info[input_blob].input_data.shape
        resized_frame = cv2.resize(frame, (input_shape[3], input_shape[2]))
        preprocessed_frame = resized_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
        preprocessed_frame = preprocessed_frame.reshape(1, *preprocessed_frame.shape)

        # Start inference
    
        output = exec_net.infer(inputs={input_blob: preprocessed_frame})
        inference_time = time.time() - start_time

        # Get output and draw on frame
        boxes = output[output_blob][0][0]
        #frame = draw_heatmap(frame, boxes, threshold=0.5)
       
        person_count = 0
        
        for box in boxes:
            if box[2] > 0.5:
                person_count += 1
                x1, y1, x2, y2 = box[3], box[4], box[5], box[6]
                cv2.rectangle(frame, (int(x1 * frame.shape[1]), int(y1 * frame.shape[0])),
                            (int(x2 * frame.shape[1]), int(y2 * frame.shape[0])), (0, 255, 0), 2)                
                xmin = int(x1 * frame.shape[1])
                xmax = int(x2 * frame.shape[1])
                ymin = int(y1 * frame.shape[0])
                ymax = int(y2 * frame.shape[0])
                heatmap[ymin:ymax, xmin:xmax] += 1

        heatmap = cv2.normalize(heatmap, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        # Apply color map to heatmap
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Add heatmap to frame as overlay
        alpha = 0.5
        #cv2.imshow("Heatmap", heatmap)
        cv2.addWeighted(heatmap, alpha, frame, 1 - alpha, 0, frame)
        
        # Display frame with detection boxes
        end_time = time.time()
        
        fps = 1 / (end_time - start_time)
        # print(f"{fps:.3f} FPS")
        # add to total FPS
        total_fps += fps
        # add to total number of frames
        frame_count += 1
        #print(output)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"People Count: {person_count}", (50, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        #print(f"{fps:.3f} FPS")
        #cv2.imshow("Frame", frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
