import torch
import numpy as np
import cv2
from time import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

class ObjectDetection:
    def __init__(self, capture_index):
        # default parameters
        self.capture_index = capture_index
        self.notif_sent = False
        self.running = True

        # model information
        self.model = YOLO("best.pt")
        #self.model.conf = 0.5

        # visual information
        self.annotator = None
        self.start_time = 0
        self.end_time = 0

        # device information
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def predict(self, im0):
        
        results = self.model(im0, conf = 0.25)
        return results

    def display_fps(self, im0):
        self.end_time = time()
        fps = 1 / np.round(self.end_time - self.start_time, 2)
        text = f'FPS: {int(fps)}'
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        gap = 10
        cv2.rectangle(im0, (20 - gap, 70 - text_size[1] - gap), (20 + text_size[0] + gap, 70 + gap), (255, 255, 255), -1)
        cv2.putText(im0, text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    def plot_bboxes(self, results, im0):
        class_ids = []
        self.annotator = Annotator(im0, 3, results[0].names)
        boxes = results[0].boxes.xyxy.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        confs = results[0].boxes.conf.cpu().tolist()
        for i, (box, cls) in enumerate(zip(boxes, clss)):
            label = f'{names[int(cls)]} {confs[i]:.2f}'  # Використання індексу i для вірогідності
            class_ids.append(cls)
            self.annotator.box_label(box, label=label, color=colors(int(cls), True))
        return im0, class_ids

    def __call__(self, frame_update_callback, class_ids_callback = None):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        # frame_count = 0
        while self.running:
            self.start_time = time()
            ret, im0 = cap.read()
            if not ret:
                print("Can`t read frame from camera")
                break
            assert ret
            results = self.predict(im0)
            im0, class_ids = self.plot_bboxes(results, im0)

            if len(class_ids) > 0:  # Only send email If not sent before
                if not self.notif_sent:
                    class_ids_callback(len(class_ids), im0)
                    #send_email(to_email, from_email, len(class_ids))
                    print("send_email")
                    self.notif_sent = True
            else:
                self.notif_sent = False

            # self.display_fps(im0)
            # im0, class_ids = self.plot_bboxes(results, im0)
            frame_update_callback(im0)  # Оновлення кадру в GUI
            # frame_count += 1
            # if cv2.waitKey(5) & 0xFF == 27:
            #     break
        cap.release()
        # cv2.destroyAllWindows()

    
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
            # if cv2.waitKey(1) == ord('q'):
            #     break
        cap.release()
    
    def resize_and_pad(self, im0, new_width=None, new_height=None):
        """Змінює розмір зображення та додає рамку для збереження відношення сторін"""
        (h, w) = im0.shape[:2]

        # Обчислення коефіцієнтів масштабування
        scale_w = new_width / w if new_width is not None else 1
        scale_h = new_height / h if new_height is not None else 1

        # Вибір найменшого коефіцієнта для збереження відношення сторін
        scale = min(scale_w, scale_h)

        # Зміна розміру зображення
        new_size = (int(w * scale), int(h * scale))
        resized = cv2.resize(im0, new_size, interpolation=cv2.INTER_AREA)

        # Додавання рамки, якщо потрібно
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