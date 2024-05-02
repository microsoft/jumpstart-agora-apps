import cv2
import numpy as np
from ovmsclient import make_grpc_client
import datetime
import json
from pose_decoder import AssociativeEmbeddingDecoder, resize_image
import os
import time

class PoseEstimator:
    def __init__(self, rtsp_url, class_names, input_shape, confidence_thres, iou_thres, model_name, ovms_url, skip_rate, verbose=False):
        print(f"Initializing PoseEstimator with RTSP URL: {rtsp_url}")
        self.rtsp_url = rtsp_url
        self.class_names = class_names
        self.input_width, self.input_height = input_shape
        self.w, self.h = input_shape
        self.confidence_thres=confidence_thres
        self.iou_thres=iou_thres
        self.model_name=model_name
        self.ovms_url=ovms_url
        self.verbose=verbose
        self.frame_number =0
        self.skip_rate=skip_rate
        self.default_skeleton = ((15, 13), (13, 11), (16, 14), (14, 12), (11, 12), (5, 11), (6, 12), (5, 6), (5, 7), (6, 8), (7, 9), (8, 10), (1, 2), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6))
        self.colors = ((255, 0, 0), (255, 0, 255), (170, 0, 255), (255, 0, 85),(255, 0, 170), (85, 255, 0), (255, 170, 0), (0, 255, 0),
            (255, 255, 0), (0, 255, 85), (170, 255, 0), (0, 85, 255), (0, 255, 170), (0, 0, 255), (0, 255, 255), (85, 0, 255),(0, 170, 255))

        self.cap = cv2.VideoCapture(rtsp_url)
        self.grpc_client = make_grpc_client(ovms_url)

        self.decoder = AssociativeEmbeddingDecoder(
            num_joints=17,
            adjust=True,
            refine=True,
            delta=0.5,
            max_num_people=30,
            detection_threshold=0.1,
            tag_threshold=1,
            pose_threshold=confidence_thres,
            use_detection_val=True,
            ignore_too_much=False,
            dist_reweight=True)
        
        if not self.cap.isOpened():
            print("Error: Unable to open video source.")
        else:
            # Lee un frame para determinar el tamaño de los frames del video
            ret, frame = self.cap.read()
            if ret:
                self.img_height, self.img_width = frame.shape[:2]
            else:
                print("Failed to grab frame to set image dimensions")

        self.img_height, self.img_width = frame.shape[:2]

    def preprocess(self, inputs):
        img = resize_image(inputs, (self.w, self.h), keep_aspect_ratio=True)
        h, w = img.shape[:2]
        resize_img_scale = np.array((inputs.shape[1] / w, inputs.shape[0] / h), np.float32)
        pad = (0, self.h - h, 0, self.w - w)
        img = np.pad(img, (pad[:2], pad[2:], (0, 0)), mode='constant', constant_values=0)
        img = img.transpose((2, 0, 1))  # Change data layout from HWC to CHW
        img = img[None]
        meta = {
            'original_size': inputs.shape[:2],
            'resize_img_scale': resize_img_scale
        }
        return {"image": img.astype(np.float32) }, meta

    def postprocess(self, outputs, meta):
        heatmaps = outputs['heatmaps']
        nms_heatmaps = outputs['heatmaps']
        aembds = outputs['2674']
        poses, scores = self.decoder(heatmaps, aembds, nms_heatmaps=nms_heatmaps)
        poses[:, :, :2] *= meta['resize_img_scale'] * 2
        return poses, scores
    
    def draw_poses(self, img, poses, point_score_threshold, draw_ellipses=False):
        if poses.size == 0:
            return img
        
        stick_width = 4

        img_limbs = np.copy(img)
        for pose in poses:
            points = pose[:, :2].astype(np.int32)
            points_scores = pose[:, 2]
            # Draw joints.
            for i, (p, v) in enumerate(zip(points, points_scores)):
                if v > point_score_threshold:
                    cv2.circle(img, tuple(p), 1, self.colors[i], 2)
            # Draw limbs.
            for i, j in self.default_skeleton:
                if points_scores[i] > point_score_threshold and points_scores[j] > point_score_threshold:
                    if draw_ellipses:
                        middle = (points[i] + points[j]) // 2
                        vec = points[i] - points[j]
                        length = np.sqrt((vec * vec).sum())
                        angle = int(np.arctan2(vec[1], vec[0]) * 180 / np.pi)
                        polygon = cv2.ellipse2Poly(tuple(middle), (int(length / 2), min(int(length / 50), stick_width)),
                                                angle, 0, 360, 1)
                        cv2.fillConvexPoly(img_limbs, polygon, self.colors[j])
                    else:
                        cv2.line(img_limbs, tuple(points[i]), tuple(points[j]), color=self.colors[j], thickness=stick_width)
        cv2.addWeighted(img, 0.4, img_limbs, 0.6, 0, dst=img)
        return img
    
    def run(self):
        if(self.verbose):
            print("Running detection...")
        
        output_directory = f'./{self.model_name}_output'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        while True:
            ret, img = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                return None

            inputs, preprocessing_meta = self.preprocess(img)
            outputs = self.grpc_client.predict(inputs, self.model_name)
            result = self.postprocess(outputs, preprocessing_meta)
            if result:
                (poses, scores)  = result
                frame = self.draw_poses(img, poses, self.confidence_thres)
                timestamp = int(time.time())
                filename = os.path.join(output_directory, f'{self.model_name}_{timestamp}.jpg')
                cv2.imwrite(filename, frame)
                print(f"Saved frame to {filename}")

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

if __name__ == "__main__":
    #with open('..\\config_file.json') as config_file:
    with open('config_file.json') as config_file:
        config = json.load(config_file)
    model_config = config["human-pose-estimation"]

    detector = PoseEstimator(
        rtsp_url=model_config['rtsp_url'],
        class_names=model_config['class_names'],
        input_shape=model_config['input_shape'],
        confidence_thres=model_config['conf_thres'],
        iou_thres=model_config['iou_thres'],
        model_name="human-pose-estimation",
        ovms_url="192.168.0.4:31640",
        skip_rate=10
    )
    
    detector.run()
