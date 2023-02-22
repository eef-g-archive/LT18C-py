# Download this file and move it to the Modules>Addons folder BEFORE running
## NOTE: This file will not work WITHOUT the yolov3.weights file
## NOTE: yolov3.weights is not included in the repository because it is too big for GitHub (200+ MB)
# https://pjreddie.com/media/files/yolov3.weights

import numpy as np
import time
import cv2
import sys
import os


class Yolo_Obj():
    def __init__(self):
        self.dnn_classifier, self.dnn_layers, self.label_names = self.load_yolo_DNN()
        print("Yolo object created")

    def load_yolo_DNN(self):
        script_dir = os.path.dirname(__file__)

        labels_path = os.path.join(script_dir, f'coco.names')
        config_path = os.path.join(script_dir, f'yolov3.cfg')
        weights_path = os.path.join(script_dir, f'yolov3.weights')


        with open(labels_path, 'r') as f:
            dnn_labels = [line.strip('\n') for line in f if line[0] != '#']

        dnn_object = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        dnn_layers = dnn_object.getUnconnectedOutLayersNames()

        return (dnn_object, dnn_layers, dnn_labels)

    def detect_persons(self, img, dnn_object, obj_confidence, nms_threshold):
        """
        Detects COCO objects in an image with an OpenCV Deep Neural Network using
        Non-Maxima Supression to reduce the number of duplicate objects.
        Returns a list of detected objects, each defined as a tuple:
        0. COCO label, as an index number
        1. DNN confidence score
        2. Bounding box for the object
        """

        # Process raw image through the neural network to obtain potential objects
        #  => 1/255 is the scaling factor --> RGB value to a percentage
        #  => (224, 224) is the size of the output blob with smaller sizees being
        #     faster but potentially less accurate. The number came from this
        #     article by Adrian Rosebrock on PyImageSearch and produced fairly
        #     accurate results during some limited testing.

        blob = cv2.dnn.blobFromImage(img, 1/255.0, (224, 224), swapRB=True, crop=False)
        
        # Run the DNN object detection algorithm

        dnn_classifier, dnn_outputlayers = dnn_object
        dnn_classifier.setInput(blob)
        outputs = dnn_classifier.forward(dnn_outputlayers)
        flattened_outputs = [result for layer in outputs for result in layer]

        # We will identify objects by their location (the bounding box), the
        #   confidence score, and then the COCO label assigned by the DNN.
        # We need the image width x height to create the bounding boxes

        boxes = []
        scores = []
        labels = []
        img_h, img_w = img.shape[:2]

        # Each result is a nested list of all the detected objects. At the top
        #   level, we have a list of objects. Within each object, we are given a
        #   list containing the 4 coordinates of a bounding box followed by 80
        #   classification scores. There are 80 scores because our DNN was trained
        #   with 80 objects from the COCO dataset. We need to extract the bounding
        #   box and then identify the highest scoring object.
        # DNN bounding boxes identified by center, width, and height. We'll convert
        #   these to the upper-left coordinates of the box and the width & height.
        # Filter down to only the highest scoring people objects (label #0)

        for result in flattened_outputs:
            bbox = result[:4]
            all_scores = result[5:]
            best_label = np.argmax(all_scores)
            best_score = all_scores[best_label]
            
            if best_score > obj_confidence and best_label == 0:
                cx, cy, w, h = bbox * np.array([img_w, img_h, img_w, img_h])
                x = cx - w / 2
                y = cy - h / 2
                labels.append(best_label)
                scores.append(float(best_score))
                boxes.append([int(x), int(y), int(w), int(h)])

        # The DNN is likely to have identfied the same object multiple times, with
        #   each repeat found in a slightly different, overlapped, region of the
        #   image. We use the Non-Maxima Supression algorithm to detect redundant
        #   objects and return the best fitting bounding box from amongst all of
        #   the candidates.  

        best_idx = cv2.dnn.NMSBoxes(boxes, scores, obj_confidence, nms_threshold)
        if len(best_idx) > 0:
            objects = [(labels[i], scores[i], boxes[i]) for i in best_idx.flatten()]
        else:
            objects = []
        
        return objects

    def process_image(self, img, dnn_object, confidence, threshold):
        """
        Detect persons in an image file using Deep Neural Network object detection
        algorithm. The image file will be downsized to fit within 640x480 before
        it is run through the DNN.
        Returns a new version of the image that has been overlayed with recangular
        bounding boxes and also a list of tuples identifying each object. The tuple
        contains the following three fields:
        0. COCO label, as an index number
        1. DNN confidence score
        2. Bounding box for the object 
        """

        # Resize the image to fit within 640x480 for easier viewing
        height, width = img.shape[:2]
        if width > 640 or height > 640:
            largest_dimension = max(height, width)
            scale_factor = 1 + largest_dimension // 640
            dimensions = (width // scale_factor, height // scale_factor)
            img = cv2.resize(img, dimensions, interpolation = cv2.INTER_AREA)
            height, width = img.shape[:2]

        # Detect all of the objects in this image
        objects = self.detect_persons(img, dnn_object, confidence, threshold)

        # Place a visual bounding box around each object detected in the image
        bgr_red = (0, 0, 255)
        for label, score, (x, y, w, h) in objects:
            cv2.rectangle(img, (x, y), (x+w, y+h), bgr_red, 2)
            #text = f"{label_names[label]}: {100*score:.1f}%"
            #cv2.putText(image, text, (x, y-5), cv2.FONT_HERSHEY_PLAIN, 1, bgr_red, 2)

        return img, objects

    def analyze_frame(self, image, confidence=0.90, threshold=0.3):
        #self.dnn_classifier, self.dnn_layers, self.label_names = self.load_yolo_DNN()
        dnn_object = (self.dnn_classifier, self.dnn_layers)


        img = image
        img, objs = self.process_image(img, dnn_object, confidence, threshold)
        #for label, score, (x, y, w, h) in objs:
        #        print(f'  => {self.label_names[label]}: {100*score:.1f} at ({x},{y})->({x+w},{y+h})')

        return img