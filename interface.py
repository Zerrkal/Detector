import tkinter as tk
from tkinter import ttk, Menu, filedialog
import os
import cv2

def start_detection():
    print("Start")
    # Код для запуску детекції об'єктів
    pass

def stop_detection():
    print("Stop")
    # Код для зупинки детекції об'єктів
    pass

def open_settings():
    # Код для відкриття налаштувань
    pass

def on_source_select(event):
    # Функція, яка викликається при виборі опції в Combobox
    chosen_option = source_var.get()
    if chosen_option == "Choose image":
        camera_frame.place_forget()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_path_label.config(text=file_name)
    elif chosen_option == "Choose video":
        camera_frame.place_forget()
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_path_label.config(text=file_name)
    elif chosen_option == "Web camera":
        camera_combobox.config(state='readonly')  # Активувати випадаючий список камер
        print("Web camera selected")
        file_path_label.config(text="")
        camera_frame.place(x=320, y=510, width=220, height=80)
    


def detect_cameras():
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

def on_camera_select():
    # Функція для обробки вибору камери
    selected_camera = camera_var.get()
    print("Selected camera:", selected_camera)
    # Тут можна додати код для запуску вибраної камери


window = tk.Tk()
window.title("Object Detector")
window.geometry("800x600")

# Місце для відео або фото
video_frame = tk.Frame(window, bg='black', bd=2, relief="sunken")
video_frame.place(x=50, y=50, width=700, height=450)

video_label = tk.Label(video_frame, text="VIDEO", bg='gray', fg='white')
video_label.pack(expand=True, fill='both')

# Створення випадаючого меню
menu_bar = Menu(window)
window.config(menu=menu_bar)

# Додавання першого меню налаштувань
settings_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Setting 1", command=open_settings)
settings_menu.add_command(label="Setting 2", command=open_settings)

# Додавання другого меню налаштувань
extra_settings_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Extra", menu=extra_settings_menu)
extra_settings_menu.add_command(label="Extra 1", command=open_settings)
extra_settings_menu.add_command(label="Extra 2", command=open_settings)

# Кнопки Start та Stop
buttons_frame = ttk.Frame(window)
buttons_frame.place(x=20, y=505, width=160, height=80)

start_button = ttk.Button(buttons_frame, text="Start", command=start_detection)
start_button.pack(side='top', pady=5)

stop_button = ttk.Button(buttons_frame, text="Stop", command=stop_detection)
stop_button.pack(side='top', pady=5)

# Напис "Source" та Combobox для вибору джерела
# Фрейм для контролів Source
source_frame = ttk.Frame(window)
source_frame.place(x=160, y=510, width=400, height=80)

source_label = tk.Label(source_frame, text="Source")
source_label.place(x=0, y=0)

source_var = tk.StringVar()
source_combobox = ttk.Combobox(source_frame, textvariable=source_var, state='readonly', width = 12)
source_combobox['values'] = ('Choose image', 'Choose video', 'Web camera')
source_combobox.bind('<<ComboboxSelected>>', on_source_select)
source_combobox.place(x=50, y=0)

# Встановлення пункту за замовчуванням
# source_var.set('Choose File')

# Мітка для відображення шляху вибраного файлу
file_path_label = tk.Label(source_frame, text="", fg="blue")
file_path_label.place(x=0, y=40)

available_cameras = detect_cameras()

# # Створення GUI
# window = tk.Tk()
# window.title("Camera Selector")
# window.geometry("300x100")

# camera_var = tk.StringVar()
# camera_combobox = ttk.Combobox(window, textvariable=camera_var, values=available_cameras, state='readonly')
# camera_combobox.grid(column=0, row=0)
# select_button = ttk.Button(window, text="Select Camera", command=on_camera_select)
# select_button.grid(column=0, row=1)

camera_frame = ttk.Frame(window)
#camera_frame.place(x=320, y=510, width=220, height=80)

camera_label = tk.Label(camera_frame, text="Select Camera")
camera_label.place(x=10, y=0)

camera_var = tk.StringVar()
camera_combobox = ttk.Combobox(camera_frame, textvariable=camera_var, values=available_cameras, state='readonly',width = 12)
camera_combobox.grid(column=0, row=0)
#camera_combobox['values'] = ('Choose image', 'Choose video', 'Web camera')
#camera_combobox.bind('<<ComboboxSelected>>', on_camera_select)
camera_combobox.place(x=100, y=0)

window.mainloop()
