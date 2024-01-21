import tkinter as tk
from tkinter import ttk, Menu, filedialog
import os
import cv2
import io
import threading
from PIL import Image, ImageTk
from time import time

from detector import ObjectDetection
from alert_telegram import AlertNotificationTelegram
from app_settings_conf import DetectionAppSetConfig


class ObjectDetectorApp:
    def __init__(self):
        
        self.detector = None
        self.selected_file_path = None
        self.setup_ui()
        
        self.alert_time = 0
        self.detection_conf, self.alert_update_time, self.send_notif, token = DetectionAppSetConfig().get_settings()

        self.alert_tg_notif_bot = AlertNotificationTelegram(token)

    


    def setup_ui(self):
        window_title="Object Detector"
        width=800
        height=600
        self.window = tk.Tk()
        self.window.title(window_title)
        self.window.geometry(f"{width}x{height}")
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.video_frame_width = 640
        self.video_frame_hight = 448

        # Place for video or photo
        self.video_frame = tk.Frame(self.window, bg='black', bd=2, relief="sunken")
        self.video_frame.place(x=50, y=50, width=self.video_frame_width, height=self.video_frame_hight)

        self.video_label = tk.Label(self.video_frame, text="VIDEO", bg='gray', fg='white')
        self.video_label.pack(expand=True, fill='both')

        # Creating a drop-down menu
        menu_bar = Menu(self.window)
        self.window.config(menu=menu_bar)

        # Adding the first settings menu
        settings_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Detection Settings", menu=settings_menu)
        settings_menu.add_command(label="Telegram bot", command=DetectionAppSetConfig.tg_bot_settings_ui)
        settings_menu.add_command(label="Telegram chat id", command=DetectionAppSetConfig.tg_bot_id_settings_ui)
        settings_menu.add_command(label="Confidence lvl", command=DetectionAppSetConfig.confidence_settings_ui)

        # Start and Stop buttons
        buttons_frame = ttk.Frame(self.window)
        buttons_frame.place(x=20, y=505, width=160, height=80)

        start_button = ttk.Button(buttons_frame, text="Start", command=self.start_detection)
        start_button.pack(side='top', pady=5)

        stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_detection)
        stop_button.pack(side='top', pady=5)

        source_frame = ttk.Frame(self.window)
        source_frame.place(x=160, y=510, width=400, height=80)

        source_label = tk.Label(source_frame, text="Source")
        source_label.place(x=0, y=0)

        self.source_var = tk.StringVar()
        source_combobox = ttk.Combobox(source_frame, textvariable=self.source_var, state='readonly', width=12)
        source_combobox['values'] = ('Choose image', 'Choose video', 'Web camera')
        source_combobox.bind('<<ComboboxSelected>>', self.on_source_select)
        source_combobox.place(x=50, y=0)

        # Мітка для відображення шляху вибраного файлу
        self.file_path_label = tk.Label(source_frame, text="", fg="blue")
        self.file_path_label.place(x=0, y=40)

        # Додавання функціоналу для вибору камери
        self.available_cameras = self.detect_cameras()
        self.camera_frame = ttk.Frame(self.window)
        self.camera_label = tk.Label(self.camera_frame, text="Select Camera")
        self.camera_label.place(x=10, y=0)
        self.camera_var = tk.StringVar()
        self.camera_combobox = ttk.Combobox(self.camera_frame, textvariable=self.camera_var, 
                                            values=self.available_cameras, state='readonly', width=12)
        self.camera_combobox.place(x=100, y=0)


    def on_window_close(self):
        self.window.destroy()
        self.alert_tg_notif_bot.updater.stop()
    
    
    def start_detection(self):
        self.detection_conf, self.alert_update_time, self.send_notif, _ = DetectionAppSetConfig().get_settings()
        self.video_label.config(image='')
        chosen_option = self.source_var.get()
        if chosen_option == "Choose image":
            self.camera_frame.place_forget()
            if self.selected_file_path and self.selected_file_path.endswith((".jpg", ".jpeg", ".png")):
                self.detector = ObjectDetection(None, self.detection_conf)
                image = self.detector.process_image(self.selected_file_path, self.video_frame_width, self.video_frame_hight)
                self.update_frame(image)
            else:
                self.file_path_label.config(text="No .jpg .jpeg .png file selected", fg="red")
        elif chosen_option == "Choose video":
            self.camera_frame.place_forget()
            if self.selected_file_path != None and self.selected_file_path.endswith((".mp4", ".avi")):
                self.stop_detection()
                self.detector = ObjectDetection(None, self.detection_conf)
                video_processing_thread = threading.Thread(target=self.detector.process_video, 
                                                           args=(self.selected_file_path, self.update_frame, 
                                                                 self.video_frame_width, self.video_frame_hight))
                video_processing_thread.daemon = True
                video_processing_thread.start()
            else:
                self.file_path_label.config(text="No .mp4 .avi file selected", fg="red")
        elif chosen_option == "Web camera":
            self.file_path_label.config(text="")
            self.stop_detection()
            self.start_video_processing()
        else:
            self.file_path_label.config(text="No source selected", fg="red")

    def stop_detection(self):
        self.window.after(50, lambda: self.video_label.config(image=''))  # clearing the Label widget
        if self.detector:
            self.detector.stop()

    def on_source_select(self, event):
        # A function that is called when an option is selected in a Combobox
        chosen_option = self.source_var.get()
        file_path = None
        if chosen_option == "Choose image":
            self.camera_frame.place_forget()
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        elif chosen_option == "Choose video":
            self.camera_frame.place_forget()
            file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
        elif chosen_option == "Web camera":
            self.camera_combobox.config(values=self.detect_cameras(), state='readonly')  # Activate the drop-down list of cameras
            self.file_path_label.config(text="")
            self.camera_frame.place(x=320, y=510, width=220, height=80)

        if file_path:
            self.selected_file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_path_label.config(text=file_name, fg = 'blue')
        else:
            self.selected_file_path = None
            self.file_path_label.config(text="")

    def detect_cameras(self):
        # Attempting to connect to cameras to determine their number
        index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
        return arr

    def on_camera_select(self):
        # Function to handle camera selection
        selected_camera = self.camera_var.get()
        return selected_camera


    def start_video_processing(self):
        selected_camera = self.on_camera_select()
        if self.on_camera_select() != '':
            capture_index = int(selected_camera)  # Get the index of the selected camera
            self.detector = ObjectDetection(capture_index, self.detection_conf)
            video_thread = threading.Thread(target=self.detector, args=(self.update_frame, self.get_alert))
            video_thread.daemon = True
            video_thread.start()
            
        else:
            # print("No camera selected")
            self.file_path_label.config(text="No camera selected", fg="red")

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)
        self.video_label.config(image=frame)
        self.video_label.image = frame  # saving the link to the image
    
    def send_image_tgbot(self, frame, message):
        if frame is not None:
            # Convert Tkinter PhotoImage to PIL Image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame)
            # Saving the PIL Image to the clipboard
            with io.BytesIO() as camera_image:
                frame_image.save(camera_image, format="PNG")
                camera_image.seek(0)
                self.camera_image_bytes = camera_image.read()
        
        self.alert_tg_notif_bot.send_image(self.camera_image_bytes, message)

    def get_alert(self, class_ids, frame = None):
        if class_ids is not None:
            current_time = time()
            if current_time - self.alert_time >= self.alert_update_time:
                self.alert_time = current_time
                message = f"Alert {class_ids} drone found"
                # print(message)
                self.send_image_tread = threading.Thread(target=self.send_image_tgbot, args = (frame, message))
                self.send_image_tread.daemon = True
                self.send_image_tread.start()
    
    def run(self):
            # Starts the Tkinter main loop
            self.window.mainloop()
    

app = ObjectDetectorApp()
app.run()