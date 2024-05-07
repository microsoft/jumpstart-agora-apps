import cv2
import numpy as np
import json
import time
from ovmsclient import make_grpc_client
from tabulate import tabulate
import os
import datetime

class YOLOv8OVMS:
    def __init__(self, rtsp_url, class_names, input_shape, color_palette, confidence_thres, iou_thres, model_name, ovms_url, save_img_loc, skip_rate, verbose=False):
        print(f"Initializing YOLOv8OVMS with RTSP URL: {rtsp_url}")
        self.rtsp_url = rtsp_url
        self.class_names = class_names
        self.input_width, self.input_height = input_shape
        self.color_palette = np.random.uniform(0, 255, size=(len(class_names), 3))
        self.confidence_thres=confidence_thres
        self.iou_thres=iou_thres
        self.model_name=model_name
        self.ovms_url=ovms_url
        self.save_img_loc=save_img_loc
        self.verbose=verbose
        self.frame_number =0
        self.skip_rate=skip_rate

        self.cap = cv2.VideoCapture(rtsp_url)
        self.grpc_client = make_grpc_client(ovms_url)
        
        if not self.cap.isOpened():
            print("Error: Unable to open video source.")
        else:
            # Lee un frame para determinar el tamaño de los frames del video
            ret, frame = self.cap.read()
            if ret:
                self.img_height, self.img_width = frame.shape[:2]
            else:
                print("Failed to grab frame to set image dimensions")
  
    def preprocess(self):
        if(self.verbose):
            print("Preprocessing the frame...")

        ret, img = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return None
        self.img_height, self.img_width = img.shape[:2]  # Actualiza las dimensiones basadas en el frame actual
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.input_width, self.input_height))
        image_data = np.array(img) / 255.0
        image_data = np.transpose(image_data, (2, 0, 1))
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
        return image_data

    def postprocess(self, input_image, output):
        if(self.verbose):
            print("Postprocessing the output...")

        # Transpose and squeeze the output to match the expected shape
        outputs = np.transpose(np.squeeze(output[0]))

        # Get the number of rows in the outputs array
        rows = outputs.shape[0]

        # Lists to store the bounding boxes, scores, and class IDs of the detections
        boxes = []
        scores = []
        class_ids = []

        # Calculate the scaling factors for the bounding box coordinates
        x_factor = self.img_width / self.input_width
        y_factor = self.img_height / self.input_height

        # Iterate over each row in the outputs array
        for i in range(rows):
            # Extract the class scores from the current row
            classes_scores = outputs[i, 4:]

            # Find the maximum score among the class scores
            max_score = np.max(classes_scores)

            # If the maximum score is above the confidence threshold
            if max_score >= self.confidence_thres:
                # Get the class ID with the highest score
                class_id = np.argmax(classes_scores)

                # Extract the bounding box coordinates from the current row
                x, y, w, h = outputs[i, 0:4]

                # Calculate the scaled coordinates of the bounding box
                left = int((x - w / 2) * x_factor)
                top = int((y - h / 2) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)

                # Add the class ID, score, and box coordinates to the respective lists
                class_ids.append(class_id)
                scores.append(max_score)
                boxes.append([left, top, width, height])

        # Apply non-maximum suppression to filter out overlapping bounding boxes
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_thres, self.iou_thres)

        # Check if indices are returned as a numpy array and access them correctly
        if len(indices) > 0:
            indices = indices.flatten()  # This ensures indices are flattened properly
        elif(self.verbose):
            print("No boxes to display after NMS.")

        # Prepare data for tabulate
        table_data = []

        # Iterate over the selected indices after non-maximum suppression
        for i in indices:
            # Get the box, score, and class ID corresponding to the index
            
            box = boxes[i]
            score = scores[i]
            class_id = class_ids[i]

            # Draw the detection on the input image
            self.draw_detections(input_image, box, score, class_id)
            table_data.append([i, box, score, self.class_names[class_id]])

        # Print the table
        headers = ["Index", "Box", "Score", "Class"]
        #self.log(self, str(tabulate(table_data, headers=headers, tablefmt="grid")))
        
        # Return the modified input image
        return input_image

    def draw_detections(self, img, box, score, class_id):
        # Extract the coordinates of the bounding box
        x1, y1, w, h = box

        # Retrieve the color for the class ID
        color = self.color_palette[class_id]

        # Draw the bounding box on the image
        cv2.rectangle(img, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), (0,0,255), 5)

        # Create the label text with class name and score
        label = f"{self.class_names[class_id]}: {score:.2f}"

        # Calculate the dimensions of the label text
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 1)

        # Calculate the position of the label text
        label_x = x1
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 20

        # Draw a filled rectangle as the background for the label text
        cv2.rectangle(img, (label_x, label_y - label_height - 10), (label_x + label_width, label_y + label_height), (0,0,255), cv2.FILLED)

         # Draw the label text on the image
        cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 1, cv2.LINE_AA)

    def run(self):
        if(self.verbose):
            print("Running detection...")

        self.frame_number += 1
        # If mod = 0, i will get the frame and skip it
        if self.frame_number % self.skip_rate == 0:
            self.cap.read()
            return None
        
        image_data = self.preprocess()

        outputs = self.grpc_client.predict({"images": image_data}, self.model_name)
        frame = self.postprocess(self.cap.read()[1], outputs)

        return frame

    def log(self, message):
        """Logs a message with a timestamp if verbose is true."""
        if self.verbose:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} - {message}")
            
    def __del__(self):
        print("Releasing resources...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("Released video capture and destroyed all windows.")