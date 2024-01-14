import tkinter as tk
from tkinter import ttk
import configparser
import re
import os

class DetectionAppSetConfig:

    @staticmethod
    def read_config():
        filename = 'app_config.conf'
        config = configparser.ConfigParser()
        
        if not os.path.exists(filename):
            # The configuration file does not exist, we create it with default values
            default_settings = {
                'settings': {
                    'alert_update_time': 10,
                    'tg_bot_name' : 't.me/NotificatorTelegram_bot',
                    'token': '6659513814:AAHmExNMl75UQ7DgqAlGY5W-QGG07uRTiMQ',
                    'send_notif' : True,
                    'detection_confidence' : 0.5
                },
                'chat_id':{
                    '385246590' : True
                }
            }
            config.read_dict(default_settings)
            with open(filename, 'w') as configfile:
                config.write(configfile)
        else:
            # The configuration file exists, read it
            config.read(filename)

        return config

    @staticmethod
    def get_settings():
        config = DetectionAppSetConfig.read_config()
        detection_conf = float(config['settings']['detection_confidence'])
        alert_update_time = int(config['settings']['alert_update_time'])
        send_notif = bool(config['settings']['send_notif'])
        token = config['settings']['token']

        return detection_conf, alert_update_time, send_notif, token
    
    @staticmethod
    def get_chat_ids():
        config = DetectionAppSetConfig.read_config()
        # Make sure the 'chat_id' section exists
        if 'chat_id' in config:
            chat_ids = config['chat_id']
        else:
            chat_ids = {}
        # We return the chat_id dictionary, where the keys are chat_id, and the value is their status (True/False)
        return chat_ids
        
    @staticmethod
    def set_chat_id(chat_id, chat_id_status):
        if chat_id:
            config = DetectionAppSetConfig.read_config()
            config['chat_id'] = {chat_id : chat_id_status}
            with open('app_config.conf', 'w') as configfile:
                    config.write(configfile)

    @staticmethod
    def tg_bot_settings_ui():
            settings_window = tk.Toplevel()
            settings_window.title("Telegram Bot Settings")
            settings_window.geometry("400x300")

            config = DetectionAppSetConfig.read_config()
            # Fields for entering settings
            send_notif_var = tk.BooleanVar(value=config.getboolean('settings', 'send_notif'))
            alert_update_time_var = tk.StringVar(value=config.get('settings', 'alert_update_time'))
            token_var = tk.StringVar(value=config.get('settings', 'token'))
            tg_bot_name_var = tk.StringVar(value=config.get('settings', 'tg_bot_name'))

            current_row = 0
            # Adding inscriptions and fields
            tk.Label(settings_window, text="Enable Notifications:").grid(row=current_row, column=0, sticky='w')
            tk.Checkbutton(settings_window, variable=send_notif_var).grid(row=current_row, column=1, sticky='w')
            current_row += 1

            tk.Label(settings_window, text="Alert Update Time:").grid(row=current_row, column=0, sticky='w')
            tk.Entry(settings_window, textvariable=alert_update_time_var, width=30).grid(row=current_row, column=1, sticky='w')
            current_row += 1

            tk.Label(settings_window, text="Telegram Bot Name:").grid(row=current_row, column=0, sticky='w')
            tk.Entry(settings_window, textvariable=tg_bot_name_var, width=30).grid(row=current_row, column=1, sticky='w')
            current_row += 1

            tk.Label(settings_window, text="Token:").grid(row=current_row, column=0, sticky='w')
            tk.Entry(settings_window, textvariable=token_var, width=30).grid(row=current_row, column=1, sticky='w')
            current_row += 1

            def save_settings():
                # Check for a numeric value for alert_update_time
                if not alert_update_time_var.get().isdigit():
                    return

                token_pattern = re.compile("^[0-9]+:[A-Za-z0-9_-]+$")
                if not token_pattern.match(token_var.get()):
                    return
                if not tg_bot_name_var.get().strip():
                    return
                
                # Update configuration
                config.set('settings', 'send_notif', str(send_notif_var.get()))
                config.set('settings', 'alert_update_time', alert_update_time_var.get())
                config.set('settings', 'token', token_var.get())
                config.set('settings', 'tg_bot_name', tg_bot_name_var.get())
                with open('app_config.conf', 'w') as configfile:
                    config.write(configfile)
                settings_window.destroy()

            tk.Button(settings_window, text="Save", command=save_settings).grid(row=current_row, column=1)

    @staticmethod
    def tg_bot_id_settings_ui():
        id_settings_window = tk.Toplevel()
        id_settings_window.title("Telegram Bot Id Settings")
        id_settings_window.geometry("200x300")

        config = DetectionAppSetConfig.read_config()
        chat_id_row = 0

        # Tabs for chat_id
        tab_control = ttk.Notebook(id_settings_window)
        chat_id_tab = ttk.Frame(tab_control)
        tab_control.add(chat_id_tab, text="Chat IDs")
        tab_control.grid(row=chat_id_row, column=0, columnspan=2, pady=10, sticky='w')
        chat_id_row += 1

        def delete_chat_id(chat_id, chat_id_widgets):
            config = DetectionAppSetConfig.read_config()
            if chat_id in config['chat_id']:
                config.remove_option('chat_id', chat_id)
 
                with open('app_config.conf', 'w') as configfile:
                    config.write(configfile)
                # Removing widgets from the interface
                if chat_id in chat_id_widgets:
                    # Delete all widgets of this chat_id
                    for widget in chat_id_widgets[chat_id]:
                        widget.destroy()  # Or widget.grid_forget() if you only want to hide the widgets

                    # Clearing a dictionary entry
                    del chat_id_widgets[chat_id]
                # else:
                #     print(f"Chat ID {chat_id} not found in widgets")


        # Display chat_id
        chat_id_vars = {}
        chat_id_widgets = {}
        
        for chat_id, chat_id_notif in config['chat_id'].items():
            # print(chat_id, chat_id_notif, chat_id_row)
            label_text = tk.Label(chat_id_tab, text="Notify user")
            label_text.grid(row=chat_id_row, column=0, sticky='w')

            chat_id_var = tk.BooleanVar(value=chat_id_notif == 'True')
            checkbox = tk.Checkbutton(chat_id_tab, variable=chat_id_var)
            checkbox.grid(row=chat_id_row, column=1, sticky='w')

            label = tk.Label(chat_id_tab, text=chat_id)
            label.grid(row=chat_id_row, column=2, sticky='w')
            chat_id_vars[chat_id] = chat_id_var
            

            delete_button = tk.Button(chat_id_tab, text="Delete", command=lambda chat_id=chat_id: delete_chat_id(chat_id, chat_id_widgets))
            delete_button.grid(row=chat_id_row, column=3, sticky='w')
            chat_id_widgets[chat_id] = [label_text, checkbox, label, delete_button]
            chat_id_row += 1  #  increment the line for the next chat_id

        def save_id_settings():
            config = DetectionAppSetConfig.read_config()
            # Update status of chat_id
            for username, var in chat_id_vars.items():
                if username in config['chat_id']:
                    config.set('chat_id', username, str(var.get()))
            
            with open('app_config.conf', 'w') as configfile:
                config.write(configfile)
            id_settings_window.destroy()

        tk.Button(id_settings_window, text="Save", command=save_id_settings).grid(row=chat_id_row, column=0)



    @staticmethod
    def confidence_settings_ui():
        confidence_window = tk.Toplevel()
        confidence_window.title("Confidence Level")
        confidence_window.geometry("300x100")

        config = DetectionAppSetConfig.read_config()
        # Confidence level input field
        confidence_var = tk.DoubleVar(value = config.getfloat('settings', 'detection_confidence') * 100)
        confidence_scale = tk.Scale(confidence_window, from_=0, to=100, orient='horizontal', variable=confidence_var)
        confidence_scale.pack()

        def save_confidence():
            # Updating the configuration
            config.set('settings', 'detection_confidence', str(confidence_var.get() / 100))
            with open('app_config.conf', 'w') as configfile:
                config.write(configfile)
            confidence_window.destroy()

        tk.Button(confidence_window, text="Save", command=save_confidence).pack()

