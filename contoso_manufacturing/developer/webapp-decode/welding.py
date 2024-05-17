import cv2
import numpy as np
from ovmsclient import make_grpc_client
import datetime

class WeldPorosity:
    def __init__(self, rtsp_url, class_names, input_shape, confidence_thres, iou_thres, model_name, ovms_url, skip_rate, verbose=False):
        print(f"Initializing WeldPorosity with RTSP URL: {rtsp_url}")
        self.rtsp_url = rtsp_url
        self.class_names = class_names
        self.input_width, self.input_height = input_shape
        self.confidence_thres=confidence_thres
        self.iou_thres=iou_thres
        self.model_name=model_name
        self.ovms_url=ovms_url
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
        img = img.astype(np.float32)  # Convert to float32
        img = img.transpose((2, 0, 1))  # Transpose to B, C, H, W format
        img = img[np.newaxis, ...]  # Add batch dimension
        img = img[:, ::-1, :, :]  # Convert color order from RGB to BGR
        
        return img

    def softmax(self, values, axis=None):
        """Normalizes logits to get confidence values along specified axis"""
        exp = np.exp(values)
        return exp / np.sum(exp, axis=axis)
    
    def postprocess(self, input_image, output):
        if(self.verbose):
            print("Postprocessing the output...")

        probs = self.softmax(output - np.max(output))
        probs = np.ravel(probs)  # Flatten the probs array
        top_ind = np.argmax(probs)
        highest_prob = np.max(probs)
        predicted_label = self.class_names[top_ind]
        
        if(self.verbose):
            print("Top prediction: class '{}', probability {:.2f}".format(predicted_label, highest_prob))
        
        label = "Class '{}' - Probability {:.2f}".format(predicted_label, highest_prob)

        # Draw a filled rectangle as the background for the label text
        cv2.rectangle(input_image, (40, 40), (200, 200), (0, 0, 0), cv2.FILLED)
        
        # Draw the label text on the image
        cv2.putText(input_image, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return input_image
    
    def run(self):
        if(self.verbose):
            print("Running detection...")
        
        self.frame_number += 1
        # If mod = 0, i will get the frame and skip it
        if self.frame_number % self.skip_rate == 0:
            self.cap.read()
            return None

        image_data = self.preprocess()
        outputs = self.grpc_client.predict({"image": image_data}, self.model_name)
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