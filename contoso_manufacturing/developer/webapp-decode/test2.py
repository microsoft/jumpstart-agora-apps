import argparse
import cv2
import numpy as np
import json
import os
import time

def load_model_config(config_file, model):
    with open(config_file, 'r') as file:
        config = json.load(file)
    model_config = config.get(model, {})
    class_names = model_config.get("class_names", ["Unknown"])
    input_dim = model_config.get("input_dim", [640, 640])
    return class_names, input_dim

class YOLOv8OVMS:
    def __init__(self, rtsp_url, model, confidence_thres, iou_thres, config_file, output_dir):
        self.rtsp_url = rtsp_url
        self.model = model
        self.confidence_thres = confidence_thres
        self.iou_thres = iou_thres
        self.class_names, (self.input_width, self.input_height) = load_model_config(config_file, model)
        self.color_palette = np.random.uniform(0, 255, size=(len(self.class_names), 3))
        self.cap = cv2.VideoCapture(rtsp_url)
        self.output_dir = os.path.join(output_dir, model)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def preprocess(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame from RTSP stream")
            return None, None
        img = cv2.resize(frame, (self.input_width, self.input_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_data = np.array(img) / 255.0
        image_data = np.transpose(image_data, (2, 0, 1))
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)
        return image_data, frame

    def postprocess(self, frame):
        frame_name = f"{self.model}_frame_{int(time.time())}.jpg"
        cv2.imwrite(os.path.join(self.output_dir, frame_name), frame)
        print(f"Frame saved to {os.path.join(self.output_dir, frame_name)}")

    def run_detection(self):
        try:
            while True:
                img_data, original_frame = self.preprocess()
                if img_data is None:
                    break
                # Placeholder for actual inference and postprocessing
                self.postprocess(original_frame)
        finally:
            self.cap.release()

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

def main():
    parser = argparse.ArgumentParser(description='YOLOv8 object detection from RTSP stream.')
    parser.add_argument('--rtsp', type=str, required=True, help='RTSP stream URL.')
    parser.add_argument('--model', type=str, default='yolov8', help='Model name or path.')
    parser.add_argument('--conf-thres', type=float, default=0.5, help='Confidence threshold for detection.')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IoU threshold for NMS.')
    parser.add_argument('--config-file', type=str, default='model_config.json', help='Path to the model configuration file.')
    parser.add_argument('--output-dir', type=str, default='./output', help='Output directory to save processed frames.')
    args = parser.parse_args()

    yolo = YOLOv8OVMS(
        rtsp_url=args.rtsp,
        model=args.model,
        confidence_thres=args.conf_thres,
        iou_thres=args.iou_thres,
        config_file=args.config_file,
        output_dir=args.output_dir
    )

    yolo.run_detection()

if __name__ == "__main__":
    main()
