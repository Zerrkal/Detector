import tkinter as tk
from tkinter import ttk, Menu, filedialog
import os
import cv2
import threading
from detector import ObjectDetection
from PIL import Image, ImageTk

# VIDEO_FRAME_WIDTH = 640
# VIDEO_FRAME_HIGHT = 448

class ObjectDetectorApp:
    def __init__(self, window_title="Object Detector", width=800, height=600):
        self.window = tk.Tk()
        self.window.title(window_title)
        self.window.geometry(f"{width}x{height}")

        self.detector = None
        self.selected_file_path = None
        self.setup_ui()

    def setup_ui(self):
        self.VIDEO_FRAME_WIDTH = 640
        self.VIDEO_FRAME_HIGHT = 448

        # Місце для відео або фото
        self.video_frame = tk.Frame(self.window, bg='black', bd=2, relief="sunken")
        self.video_frame.place(x=50, y=50, width=self.VIDEO_FRAME_WIDTH, height=self.VIDEO_FRAME_HIGHT)

        self.video_label = tk.Label(self.video_frame, text="VIDEO", bg='gray', fg='white')
        self.video_label.pack(expand=True, fill='both')

        # Створення випадаючого меню
        menu_bar = Menu(self.window)
        self.window.config(menu=menu_bar)

        # Додавання першого меню налаштувань
        settings_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Setting 1", command=self.open_settings)
        settings_menu.add_command(label="Setting 2", command=self.open_settings)

        # Додавання другого меню налаштувань
        extra_settings_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Extra", menu=extra_settings_menu)
        extra_settings_menu.add_command(label="Extra 1", command=self.open_settings)
        extra_settings_menu.add_command(label="Extra 2", command=self.open_settings)

        # Кнопки Start та Stop
        buttons_frame = ttk.Frame(self.window)
        buttons_frame.place(x=20, y=505, width=160, height=80)

        start_button = ttk.Button(buttons_frame, text="Start", command=self.start_detection)
        start_button.pack(side='top', pady=5)

        stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop_detection)
        stop_button.pack(side='top', pady=5)

        # Напис "Source" та Combobox для вибору джерела
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
        self.camera_combobox.grid(column=0, row=0)
        self.camera_combobox.place(x=100, y=0)

    def start_detection(self):
        print("Start")
        self.video_label.config(image='')
        chosen_option = self.source_var.get()
        if chosen_option == "Choose image":
            self.camera_frame.place_forget()
            if self.selected_file_path and self.selected_file_path.endswith((".jpg", ".jpeg", ".png")):
                print("ok")
                self.detector = ObjectDetection(None)
                image = self.detector.process_image(self.selected_file_path, self.VIDEO_FRAME_WIDTH, self.VIDEO_FRAME_HIGHT)
                self.update_frame(image)
            else:
                self.file_path_label.config(text="No .jpg .jpeg .png file selected", fg="red")
        elif chosen_option == "Choose video":
            self.camera_frame.place_forget()
            if self.selected_file_path != None and self.selected_file_path.endswith((".mp4", ".avi")):
                self.detector = ObjectDetection(None)
                video_processing_thread = threading.Thread(target=self.detector.process_video, 
                                                           args=(self.selected_file_path, self.update_frame, 
                                                                 self.VIDEO_FRAME_WIDTH, self.VIDEO_FRAME_HIGHT))
                video_processing_thread.start()
            else:
                self.file_path_label.config(text="No .mp4 .avi file selected", fg="red")
        elif chosen_option == "Web camera":
            self.start_video_processing()
        else:
            self.file_path_label.config(text="No source selected", fg="red")


    def stop_detection(self):
        print("Stop")
        self.window.after(100, lambda: self.video_label.config(image=''))  # очищення віджету Label
        # Код для зупинки детекції об'єктів
        if self.detector:
            self.detector.stop()


    def open_settings(self):
        # Код для відкриття налаштувань
        pass

    def on_source_select(self, event):
        # Функція, яка викликається при виборі опції в Combobox
        chosen_option = self.source_var.get()
        if chosen_option == "Choose image":
            self.camera_frame.place_forget()
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            # if selected_file_path:
            #     file_name = os.path.basename(selected_file_path)
            #     file_path_label.config(text=file_name)
        elif chosen_option == "Choose video":
            self.camera_frame.place_forget()
            file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
            # if selected_file_path:
            #     file_name = os.path.basename(selected_file_path)
            #     file_path_label.config(text=file_name)
        elif chosen_option == "Web camera":
            self.camera_combobox.config(state='readonly')  # Активувати випадаючий список камер
            print("Web camera selected")
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
        # Спроба підключитися до камер для визначення їх кількості
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
        # Функція для обробки вибору камери
        selected_camera = self.camera_var.get()
        print("Selected camera:", selected_camera)
        # Тут можна додати код для запуску вибраної камери

    def start_video_processing(self):
        if self.camera_var.get() != '':
            self.detector
            capture_index = int(self.camera_var.get())  # Отримати індекс обраної камери
            self.detector = ObjectDetection(capture_index)
            video_thread = threading.Thread(target=self.detector, args=(self.update_frame,))
            video_thread.start()
        else:
            print("No camera selected")
            self.file_path_label.config(text="No camera selected", fg="red")

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)
        self.video_label.config(image=frame)
        self.video_label.image = frame  # збереження посилання на зображення
    
    
    def run(self):
            """Запускає головний цикл Tkinter."""
            self.window.mainloop()
    

app = ObjectDetectorApp()
app.run()