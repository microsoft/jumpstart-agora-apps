import argparse

import cv2
import numpy as np
from ovmsclient import make_grpc_client
from tabulate import tabulate

classNames = ['helmet','head','person']


class YOLOv8OVMS:
    """YOLOv8 object detection model class for handling inference and visualization."""

    def __init__(self, input_image, confidence_thres, iou_thres):
        
        self.input_image = input_image
        self.confidence_thres = confidence_thres
        self.iou_thres = iou_thres

        self.color_palette = np.random.uniform(0, 255, size=(len(classNames), 3))

    def draw_detections(self, img, box, score, class_id):

        # Extract the coordinates of the bounding box
        x1, y1, w, h = box

        # Retrieve the color for the class ID
        color = self.color_palette[class_id]

        # Draw the bounding box on the image
        cv2.rectangle(img, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), color, 2)

        # Create the label text with class name and score
        #label = f"{self.classes[class_id]}: {score:.2f}"
        label = f"{classNames[class_id]}: {score:.2f}"

        # Calculate the dimensions of the label text
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

        # Calculate the position of the label text
        label_x = x1
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 10

        # Draw a filled rectangle as the background for the label text
        cv2.rectangle(
            img, (label_x, label_y - label_height), (label_x + label_width, label_y + label_height), color, cv2.FILLED
        )

        # Draw the label text on the image
        cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    def preprocess(self):
        
        # Read the input image using OpenCV
        self.img = cv2.imread(self.input_image)

        # Get the height and width of the input image
        self.img_height, self.img_width = self.img.shape[:2]

        # Convert the image color space from BGR to RGB
        img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

        # Resize the image to match the input shape
        img = cv2.resize(img, (self.input_width, self.input_height))

        # Normalize the image data by dividing it by 255.0
        image_data = np.array(img) / 255.0

        # Transpose the image to have the channel dimension as the first dimension
        image_data = np.transpose(image_data, (2, 0, 1))  # Channel first

        # Expand the dimensions of the image data to match the expected input shape
        image_data = np.expand_dims(image_data, axis=0).astype(np.float32)

        # Return the preprocessed image data
        return image_data

    def postprocess(self, input_image, output):

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
            classes_scores = outputs[i][4:]

            # Find the maximum score among the class scores
            max_score = np.amax(classes_scores)

            # If the maximum score is above the confidence threshold
            if max_score >= self.confidence_thres:
                # Get the class ID with the highest score
                class_id = np.argmax(classes_scores)

                # Extract the bounding box coordinates from the current row
                x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]

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

        if len(indices) > 0:
            indices = indices.flatten()  # This ensures indices are flattened properly
        else:
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
            table_data.append([i, box, score, classNames[class_id]])

        # Print the table
        headers = ["Index", "Box", "Score", "Class"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Return the modified input image
        return input_image

    def main(self):
        """
        Performs inference using an ONNX model and returns the output image with drawn detections.

        Returns:
            output_img: The output image with drawn detections.
        """
        # Store the shape of the input for later use
        input_shape = [1, 3, 640, 640]
        print(input_shape)
        self.input_width = 640
        self.input_height = 640

        # Preprocess the image data
        img_data = self.preprocess()

        client = make_grpc_client("172.18.0.3:8080")
        inputs = { "images": img_data }
        #outputs = client.predict(inputs, "yolov8n", 1)
        outputs = client.predict(inputs, "safety-yolo8", 1)

        # Perform post-processing on the outputs to obtain output image.
        return self.postprocess(self.img, outputs)  # output image

if __name__ == "__main__":
    # Create an argument parser to handle command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", type=str, default="coco_bike.jpg", help="Path to input image.")
    parser.add_argument("--model", type=str, default="yolov8n", help="Model name.")
    parser.add_argument("--conf-thres", type=float, default=0.5, help="Confidence threshold")
    parser.add_argument("--iou-thres", type=float, default=0.5, help="NMS IoU threshold")
    args = parser.parse_args()

    # Create an instance of the YOLOv8 class with the specified arguments
    detection = YOLOv8OVMS(args.img, args.conf_thres, args.iou_thres)

    # Perform object detection and obtain the output image
    output_image = detection.main()

    cv2.imwrite('output_image.jpg', output_image)