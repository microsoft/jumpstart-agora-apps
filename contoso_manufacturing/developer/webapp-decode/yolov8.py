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

        # Track frames and inference processing time for displaying FPS performance metrics 
        self.total_inference_time = 0.0
        self.inference_fps = 0.0
        self.total_fps = 0.0
        self.total_frames = 0
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(rtsp_url)
        self.grpc_client = make_grpc_client(ovms_url)
        
        if not self.cap.isOpened():
            print("Error: Unable to open video source.")
        else:
            # Lee un frame para determinar el tamaño de los frames del video
            ret, frame = self.cap.read()
            if ret:
                self.img_height, self.img_width = frame.shape[:2]
                print(f"Image dimensions: {self.img_width}x{self.img_height}")
            else:
                print("Failed to grab frame to set image dimensions")
  
    def preprocess(self):
        self.log("Preprocessing the frame...")

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
        self.log("Postprocessing the output...")

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

        # Draw the FPS counter on the image
        self.draw_fps(input_image)

        # Print the table
        # headers = ["Index", "Box", "Score", "Class"]
        #self.log(str(tabulate(table_data, headers=headers, tablefmt="grid")))
        
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

        # Calculate the position of the label text; this is the bottom-left corner of the text string
        label_x = x1
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 20

        # Draw a filled rectangle as the background for the label text, plus a 10 pixel border above and below
        cv2.rectangle(img, (label_x, label_y - label_height - 10), (label_x + label_width, label_y + 10), (0,0,255), cv2.FILLED)

         # Draw the label text on the image
        cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 1, cv2.LINE_AA)

    def draw_fps(self, img):

        # Create an array of strings - one for each line of text to display on the image
        label_array = [f"FPS: {self.total_fps:.02f}",
                       f"FPS (inference): {self.inference_fps:.02f}",
                       f"Input: {self.img_width}x{self.img_height}",
                       f"Inferencing: {self.input_width}x{self.input_height}",
                       f"Model: {self.model_name}"]
        
        # Define the font style and size
        font_scale = 1.0
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_thickness = 1
        background_color = (0,0,255)    # red
        font_color = (0, 0, 0)          # black
        pixel_border = 10

        # Define the starting position for the text (30 pixels from the top left corner)
        (label_x, label_y) = (30, 30)

        # Loop through each line of text in the label array and draw it on the image
        for label in label_array:
            # Calculate the dimensions of the label text
            (label_width, label_height), _ = cv2.getTextSize(label, font_face, font_scale, font_thickness)
            self.log(f"Label: {label}, Width: {label_width}, Height: {label_height}")

            # Draw a filled rectangle as the background for the label text, including a border on all sides
            # Draw the label text on the image
            # Update the starting position for the next line, including a pixel_border pixel margin between lines
            cv2.rectangle(img, (label_x - pixel_border, label_y - pixel_border), (label_x + label_width + pixel_border, label_y + label_height + pixel_border), background_color, cv2.FILLED)
            cv2.putText(img, label, (label_x, label_y + label_height), font_face, font_scale, font_color, font_thickness, cv2.LINE_AA)
            label_y += (label_height + 2 * pixel_border)

    def run(self):
        self.log("Running detection...")

        self.frame_number += 1
        # If mod = 0, i will get the frame and skip it
        if ((self.skip_rate > 0) and (self.frame_number % self.skip_rate == 0)):
            self.cap.read()
            return None
        
        # Pre-process the image
        # Perform inference on the preprocessed image; capture the start and end times
        # Post-processing including drawing bounding boxes
        image_data = self.preprocess()
        time1 = time.time()
        outputs = self.grpc_client.predict({"images": image_data}, self.model_name)
        time2 = time.time()
        frame = self.postprocess(self.cap.read()[1], outputs)

        # Update metrics used for FPS calculations
        self.total_inference_time += (time2 - time1)
        self.total_frames += 1

        # Calculate FPS for both the inferencing step and the final feed  
        self.inference_fps = self.total_frames / self.total_inference_time
        self.total_fps = self.total_frames / (time.time() - self.start_time)    # This includes e.g. JPEG encoding in the parent method outside of self.run()
        self.log(f"FPS={self.total_fps} Inference={self.inference_fps:.03f} ({self.total_frames} frames)")

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