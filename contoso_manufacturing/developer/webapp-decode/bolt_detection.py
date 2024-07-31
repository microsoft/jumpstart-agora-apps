import math
from math import atan2
import cv2
import numpy as np
from ovmsclient import make_grpc_client

# GLOBAL Variables
OBJECT_AREA_MIN = 9000
OBJECT_AREA_MAX = 50000
LOW_H = 0
LOW_S = 0
LOW_V = 47
# Thresholding of an Image in a color range
HIGH_H = 179
HIGH_S = 255
HIGH_V = 255
# Lower and upper value of color Range of the object
# for color thresholding to detect the object
LOWER_COLOR_RANGE = (0, 0, 0)
UPPER_COLOR_RANGE = (174, 73, 255)


class BoltDetection:
    def __init__(self, rtsp_url, input_shape, confidence_thres, iou_thres, model_name, ovms_url, skip_rate, verbose=False):
        print(f"Initializing B with RTSP URL: {rtsp_url}")
        self.rtsp_url = rtsp_url
        self.input_width, self.input_height = input_shape
        self.confidence_thres=confidence_thres
        self.iou_thres=iou_thres
        self.model_name=model_name
        self.ovms_url=ovms_url
        self.verbose=verbose
        self.frame_number=0
        self.count_object=0
        self.skip_rate=skip_rate
        self.one_pixel_length = 0.0264583333

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

    def dimensions(self, box):
        """
        Return the length and width of the object.

        :param box: consists of top left, right and bottom left, right co-ordinates
        :return: Length and width of the object
        """
        (tl, tr, br, bl) = box
        x = int(math.sqrt(math.pow((bl[0] - tl[0]), 2) + math.pow((bl[1] - tl[1]), 2)))
        y = int(math.sqrt(math.pow((tl[0] - tr[0]), 2) + math.pow((tl[1] - tr[1]), 2)))

        if x > y:
            return x, y
        else:
            return y, x
    
    def get_orientation(self, contours):
        """
        Gives the angle of the orientation of the object in radians.
        Step 1: Convert 3D matrix of contours to 2D.
        Step 2: Apply PCA algorithm to find angle of the data points.
        Step 3: If angle is greater than 0.5, return_flag is made to True
                else false.
        Step 4: Save the image in "Orientation" folder if it has a
                orientation defect.

        :param contours: contour of the object from the frame
        :return: angle of orientation of the object in radians
        """
        size_points = len(contours)
        # data_pts stores contour values in 2D
        data_pts = np.empty((size_points, 2), dtype=np.float64)
        for i in range(data_pts.shape[0]):
            data_pts[i, 0] = contours[i, 0, 0]
            data_pts[i, 1] = contours[i, 0, 1]
        # Use PCA algorithm to find angle of the data points
        mean, eigenvector = cv2.PCACompute(data_pts, mean=None)
        angle = atan2(eigenvector[0, 1], eigenvector[0, 0])
        return angle

    def detect_orientation(self, frame, contours):
        """
        Identifies the Orientation of the object based on the detected angle.

        :param frame: Input frame from video
        :param contours: contour of the object from the frame
        :return: defect_flag, defect
        """
        defect = "Orientation"
        # Find the orientation of each contour
        angle = self.get_orientation(contours)
        
        # If angle is less than 0.5 then no orientation defect is present
        if angle < 0.5:
            defect_flag = False
        else:
            x, y, w, h = cv2.boundingRect(contours)
            defect_flag = True
            # cv2.putText(frame, "Frame Number : {}".format(self.count_object), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            # cv2.putText(frame, "Defect: {}".format(defect), (5, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            # cv2.putText(frame, "Length (mm): {}".format(self.input_height), (5, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            # cv2.putText(frame, "Width (mm): {}".format(self.input_width), (5, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        return frame, defect_flag, defect

    def detect_color(self, frame, cnt):
        """
        Identifies the color defect W.R.T the set default color of the object.
        Step 1: Increase the brightness of the image.
        Step 2: Convert the image to HSV Format. HSV color space gives more
                information about the colors of the image.
                It helps to identify distinct colors in the image.
        Step 3: Threshold the image based on the color using "inRange" function.
                Range of the color, which is considered as a defect for object, is
                passed as one of the argument to inRange function to create a mask.
        Step 4: Morphological opening and closing is done on the mask to remove
                noises and fill the gaps.
        Step 5: Find the contours on the mask image. Contours are filtered based on
                the area to get the contours of defective area. Contour of the
                defective area is then drawn on the original image to visualize.
        Step 6: Save the image in "color" folder if it has a color defect.

        :param frame: Input frame from the video
        :param cnt: Contours of the object
        :return: color_flag, defect
        """
        defect = "Color"
        color_flag = False
        # Increase the brightness of the image
        cv2.convertScaleAbs(frame, frame, 1, 20)
        # Convert the captured frame from BGR to HSV
        img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Threshold the image
        img_threshold = cv2.inRange(img_hsv, LOWER_COLOR_RANGE, UPPER_COLOR_RANGE)
        # Morphological opening (remove small objects from the foreground)
        img_threshold = cv2.erode(img_threshold, kernel=cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (5, 5)))
        img_threshold = cv2.dilate(img_threshold, kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        contours, hierarchy = cv2.findContours(img_threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        for i in range(len(contours)):
            area = cv2.contourArea(contours[i])
            if 2000 < area < 10000:
                cv2.drawContours(frame, contours[i], -1, (0, 0, 255), 2)
                color_flag = True
        
        if color_flag:
            x, y, w, h = cv2.boundingRect(cnt)
            # cv2.putText(frame, "Frame Number : {}".format(self.count_object), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            # cv2.putText(frame, "Defect: {}".format(defect), (5, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            # cv2.putText(frame, "Length (mm): {}".format(self.input_height), (5, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            # cv2.putText(frame, "Width (mm): {}".format(self.input_width), (5, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        return frame, color_flag, defect

    def detect_crack(self, frame, cnt):
        """
        Identify the Crack defect on the object.
        Step 1: Convert the image to gray scale.
        Step 2: Blur the gray image to remove the noises.
        Step 3: Find the edges on the blurred image to get the contours of
                possible cracks.
        Step 4: Filter the contours to get the contour of the crack.
        Step 5: Draw the contour on the orignal image for visualization.
        Step 6: Save the image in "crack" folder if it has crack defect.

        :param frame: Input frame from the video
        :param cnt: Contours of the object
        :return: defect_flag, defect, cnt
        """
        defect = "Crack"
        defect_flag = False
        low_threshold = 130
        kernel_size = 3
        ratio = 3
        # Convert the captured frame from BGR to GRAY
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.blur(img, (7, 7))
        # Find the edges
        detected_edges = cv2.Canny(img, low_threshold,  low_threshold * ratio, kernel_size)
        # Find the contours
        contours, hierarchy = cv2.findContours(detected_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            for i in range(len(contours)):
                area = cv2.contourArea(contours[i])
                if area > 20 or area < 9:
                    cv2.drawContours(frame, contours, i, (0, 255, 0), 2)
                    defect_flag = True

            if defect_flag:
                x, y, w, h = cv2.boundingRect(cnt)
                # cv2.putText(frame, "Frame Number : {}".format(self.count_object), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                # cv2.putText(frame, "Defect: {}".format(defect), (5, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                # cv2.putText(frame, "Length (mm): {}".format(self.input_height), (5, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                # cv2.putText(frame, "Width (mm): {}".format(self.input_width), (5, 110),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        return frame, defect_flag, defect

    def preprocess(self):
        if(self.verbose):
            print("Preprocessing the frame...")
            
        ret, img = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return None

        # Convert BGR image to HSV color space
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Thresholding of an Image in a color range
        img_threshold = cv2.inRange(img_hsv, (LOW_H, LOW_S, LOW_V),(HIGH_H, HIGH_S, HIGH_V))

        # Morphological opening(remove small objects from the foreground)
        img_threshold = cv2.erode(img_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        img_threshold = cv2.dilate(img_threshold,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

        # Morphological closing(fill small holes in the foreground)
        img_threshold = cv2.dilate(img_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        img_threshold = cv2.erode(img_threshold, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

        # Find the contours on the image
        contours, hierarchy = cv2.findContours(img_threshold, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        return contours, contours
    
    def postprocess(self, frame, contours):
        if(self.verbose):
            print("Postprocessing the output...")

        OBJ_DEFECT = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if OBJECT_AREA_MAX > w * h > OBJECT_AREA_MIN:
                box = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(box)
                height, width = self.dimensions(np.array(box, dtype='int'))
                self.input_height = round(height * self.one_pixel_length * 10, 2)
                self.input_width = round(width * self.one_pixel_length * 10, 2)
                self.count_object += 1
     
                # Check for the orientation of the object
                frame, orientation_flag, orientation_defect = self.detect_orientation(frame, cnt)
                if orientation_flag:
                    value = 1
                    OBJ_DEFECT.append(str(orientation_defect))
                else:
                    value = 0

                # Check for the color defect of the object
                frame, color_flag, color_defect = self.detect_color(frame, cnt)
                if color_flag:
                    value = 1
                    OBJ_DEFECT.append(str(color_defect))
                else:
                    value = 0

                # Check for the crack defect of the object
                frame, crack_flag, crack_defect = self.detect_crack(frame, cnt)
                if crack_flag:
                    value = 1
                    OBJ_DEFECT.append(str(crack_defect))
                else:
                    value = 0

                # Check if none of the defect is found
                if not OBJ_DEFECT:
                    value = 1
                    defect = "No Defect"
                    OBJ_DEFECT.append(defect)
                    #cv2.putText(frame, "Length (mm): {}".format(self.input_height), (5, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                    #cv2.putText(frame, "Width (mm): {}".format(self.input_width),(5, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                else:
                    value = 0
            
            if not OBJ_DEFECT:
                continue

        all_defects = " ".join(OBJ_DEFECT)
        cv2.putText(frame, "Frame Number : {}".format(self.count_object), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.putText(frame, "Defect: {}".format(all_defects), (5, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.putText(frame, "Length (mm): {}".format(self.input_height), (5, 80),  cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.putText(frame, "Width (mm): {}".format(self.input_width), (5, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        return frame
    
    def run(self):
        if(self.verbose):
            print("Running detection...")
        
        self.frame_number += 1
        # If mod = 0, i will get the frame and skip it
        if self.frame_number % self.skip_rate == 0:
            self.cap.read()
            return None

        contours, hierarchy = self.preprocess()
        frame = self.postprocess(self.cap.read()[1], contours)
        return frame

    def __del__(self):
        print("Releasing resources...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("Released video capture and destroyed all windows.")