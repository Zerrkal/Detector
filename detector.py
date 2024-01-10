import torch
import numpy as np
import cv2
from time import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

class ObjectDetection:
    def __init__(self, capture_index, conf = 0.7):
        # default parameters
        self.capture_index = capture_index
        self.notif_sent = False
        self.running = True

        # model information
        self.model = YOLO("best.pt")
        self.conf = conf

        # visual information
        self.annotator = None
        self.start_time = 0
        self.end_time = 0

        # device information
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def predict(self, im0):
        
        results = self.model(im0, conf = self.conf)
        return results


    def plot_bboxes(self, results, im0):
        class_ids = []
        self.annotator = Annotator(im0, 3, results[0].names)
        boxes = results[0].boxes.xyxy.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        confs = results[0].boxes.conf.cpu().tolist()
        for i, (box, cls) in enumerate(zip(boxes, clss)):
            label = f'{names[int(cls)]} {confs[i]:.2f}'  # Using the index and for probability
            class_ids.append(cls)
            self.annotator.box_label(box, label=label, color=colors(int(cls), True))
        return im0, class_ids

    def __call__(self, frame_update_callback, class_ids_callback = None):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        while self.running:
            self.start_time = time()
            ret, im0 = cap.read()
            if not ret:
                print("Can`t read frame from camera")
                break
            assert ret
            results = self.predict(im0)
            im0, class_ids = self.plot_bboxes(results, im0)

            if len(class_ids) > 0:  # Only send msg If not sent before
                if not self.notif_sent:
                    class_ids_callback(len(class_ids), im0)
                    print("send_email")
                    self.notif_sent = True
            else:
                self.notif_sent = False

            frame_update_callback(im0)  # Frame update in GUI

        cap.release()

    
    def process_image(self, image_path, width=640, height=640):
        im0 = cv2.imread(image_path)
        results = self.predict(im0)
        im0, _ = self.plot_bboxes(results, im0)
        im0 = self.resize_and_pad(im0, width, height)
        return im0
    
    def process_video(self, video_path, frame_update_callback, width=640, height=640):
        cap = cv2.VideoCapture(video_path)
        assert cap.isOpened()
        while self.running:
            ret, im0 = cap.read()
            if not ret:
                break
            results = self.predict(im0)
            im0, _ = self.plot_bboxes(results, im0)
            im0 = self.resize_and_pad(im0, width, height)
            frame_update_callback(im0)
        cap.release()
    
    def resize_and_pad(self, im0, new_width=None, new_height=None):
        """Змінює розмір зображення та додає рамку для збереження відношення сторін"""
        (h, w) = im0.shape[:2]

        #  Calculation of scaling factors
        scale_w = new_width / w if new_width is not None else 1
        scale_h = new_height / h if new_height is not None else 1

        # Selection of the smallest ratio to preserve the aspect ratio
        scale = min(scale_w, scale_h)

        # Resize the image
        new_size = (int(w * scale), int(h * scale))
        resized = cv2.resize(im0, new_size, interpolation=cv2.INTER_AREA)

        # Adding a frame if needed
        if new_width is not None and new_height is not None:
            top = (new_height - new_size[1]) // 2
            bottom = new_height - new_size[1] - top
            left = (new_width - new_size[0]) // 2
            right = new_width - new_size[0] - left
            padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            return padded

        return resized


    def stop(self):
        self.running = False